import json
import os
import asyncio
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from forensick import log_event

import ollama

REQS_FILE   = "output/requirements.json"
OUTPUT_FILE = "individual/llm_test_cases.json"

os.makedirs("individual", exist_ok=True)

# 5 requirements selected for individual LLM comparison
SELECTED = [
    "117.130-a-1",
    "117.130-b-1",
    "117.130-b-3",
    "117.130-c-1",
    "117.130-d-1",
]

MODELS = {
    "mistral_full":      "mistral",
    "mistral_quantized": "mistral:7b-instruct-q4_0",
}

SYSTEM_PROMPT = (
    "You are an expert in FDA food safety regulations (21 CFR Part 117). "
    "Generate a single compliance test case for the given regulatory requirement. "
    "Output ONLY valid JSON — no explanation, no markdown fences:\n"
    '{"test_case_id":"TC-XXX","requirement_id":"...","description":"...",'
    '"input_data":"...","expected_output":"...","steps":["..."],"notes":"..."}'
)


def make_prompt(req, tc_id):
    return (
        f"Generate a compliance test case for this FDA requirement.\n\n"
        f"ID: {req['id']}\nSection: {req['section']}\nText: {req['text']}\n\n"
        f"Use \"{tc_id}\" as test_case_id. Return only the JSON object."
    )


def clean_response(text):
    s = text.strip().replace("\\_", "_")
    if s.startswith("```"):
        lines = [l for l in s.split("\n") if not l.strip().startswith("```")]
        s = "\n".join(lines).strip()
    start, end = s.find("{"), s.rfind("}") + 1
    if start != -1 and end > start:
        s = s[start:end]
    try:
        return json.loads(s)
    except Exception as e:
        return {"error": f"parse_failed: {e}", "raw": text}


async def call(model, prompt, timeout=90):
    msgs = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": prompt},
    ]
    try:
        resp = await asyncio.wait_for(
            ollama.AsyncClient().chat(model=model, messages=msgs, options={"temperature": 0.3}),
            timeout=timeout
        )
        return (resp.get("message", {}).get("content", "") or "").strip()
    except asyncio.TimeoutError:
        return '{"error":"timeout"}'
    except Exception as e:
        return f'{{"error":"{e}"}}'


async def main():
    with open(REQS_FILE) as f:
        all_reqs = json.load(f)
    req_map = {r["id"]: r for r in all_reqs}

    results = []
    ctr = 1

    for req_id in SELECTED:
        if req_id not in req_map:
            print(f"skipping {req_id} — not found")
            continue

        req = req_map[req_id]
        print(f"\n{req_id}  |  {req['section']}")
        print(f"  {req['text'][:80]}...")

        for key, model_name in MODELS.items():
            tc_id = f"TC-{ctr:03d}"
            print(f"  [{key}] {tc_id} ... ", end="", flush=True)

            raw    = await call(model_name, make_prompt(req, tc_id))
            parsed = clean_response(raw)
            parsed.setdefault("test_case_id",   tc_id)
            parsed.setdefault("requirement_id", req_id)
            parsed["_model"]      = key
            parsed["_model_name"] = model_name

            status = "error" if "error" in parsed else "ok"
            print(status)
            if status == "ok":
                print(f"     {parsed.get('description','')[:70]}")

            log_event("LLM_TEST_GENERATED",
                      f"model={key} req={req_id} tc={tc_id} status={status}")
            results.append(parsed)
            ctr += 1

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n{len(results)} test cases -> {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())

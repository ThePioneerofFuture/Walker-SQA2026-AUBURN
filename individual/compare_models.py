import json
from collections import Counter

TC_FILE       = "individual/llm_test_cases.json"
ANALYSIS_FILE = "individual/comparison_analysis.json"

REQUIRED = ["test_case_id", "requirement_id", "description", "input_data", "expected_output"]
OPTIONAL = ["steps", "notes"]

# keywords expected in descriptions for each requirement
KEYWORDS = {
    "117.130-a-1": ["hazard", "analysis", "identify", "food", "facility"],
    "117.130-b-1": ["biological", "chemical", "physical", "hazard"],
    "117.130-b-3": ["characteristics", "formulation", "food"],
    "117.130-c-1": ["severity", "probability", "illness", "injury"],
    "117.130-d-1": ["preventive", "control", "minimize", "prevent"],
}


def load():
    with open(TC_FILE) as f:
        return json.load(f)


def to_str(val, n=80):
    return str(val)[:n] if val is not None else ""


def score_tc(tc, req_id):
    coverage     = "error" not in tc
    missing      = [f for f in REQUIRED if not tc.get(f)]
    completeness = len(missing) == 0
    optional     = [f for f in OPTIONAL if tc.get(f)]
    desc         = tc.get("description", "").lower()
    hits         = [k for k in KEYWORDS.get(req_id, []) if k in desc]
    correctness  = len(hits) >= 2

    return {
        "coverage":     coverage,
        "completeness": completeness,
        "correctness":  correctness,
        "missing":      missing,
        "optional":     optional,
        "hits":         hits,
        "description":  to_str(tc.get("description"), 90),
    }


def analyze(tcs):
    by_req = {}
    for tc in tcs:
        model  = tc.get("_model", "unknown")
        req_id = tc.get("requirement_id", "unknown")
        by_req.setdefault(req_id, {})[model] = score_tc(tc, req_id)
    return by_req


def report(analysis):
    W = 72
    print("=" * W)
    print(f"{'LLM TEST CASE COMPARISON':^{W}}")
    print(f"{'mistral (full)  vs  mistral:7b-instruct-q4_0':^{W}}")
    print("=" * W)

    totals = {m: {"coverage": 0, "completeness": 0, "correctness": 0}
              for m in ("mistral_full", "mistral_quantized")}
    n = len(analysis)

    for req_id, models in analysis.items():
        print(f"\n{req_id}")
        print("─" * W)
        for model, d in models.items():
            tag  = "full      " if model == "mistral_full" else "quantized "
            c1   = "✓" if d["coverage"]     else "✗"
            c2   = "✓" if d["completeness"] else "✗"
            c3   = "✓" if d["correctness"]  else "✗"
            print(f"  {tag} coverage:{c1} complete:{c2} correct:{c3}")
            print(f"    {d['description']}...")
            if d["missing"]:  print(f"    missing fields: {d['missing']}")
            if d["optional"]: print(f"    optional present: {d['optional']}")
            if d["hits"]:     print(f"    keyword hits: {d['hits']}")
            for m in totals[model]:
                if d[m]:
                    totals[model][m] += 1

    print(f"\n{'=' * W}")
    print(f"{'SCORES (out of ' + str(n) + ')':^{W}}")
    print("─" * W)
    print(f"  {'metric':<20} {'full':>14} {'quantized':>14}")
    print("  " + "─" * 50)
    for m in ("coverage", "completeness", "correctness"):
        print(f"  {m:<20} {totals['mistral_full'][m]:>9}/{n}     {totals['mistral_quantized'][m]:>6}/{n}")
    print("=" * W)


if __name__ == "__main__":
    tcs      = load()
    analysis = analyze(tcs)
    report(analysis)

    with open(ANALYSIS_FILE, "w") as f:
        json.dump(analysis, f, indent=2)
    print(f"\nanalysis saved -> {ANALYSIS_FILE}")

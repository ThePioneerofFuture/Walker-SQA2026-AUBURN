import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from forensick import log_event

REQS_FILE     = "output/requirements.json"
SELECTED_FILE = "output/selected_rules.json"
OUTPUT_FILE   = "output/test_cases.json"

os.makedirs("output", exist_ok=True)


def load(path):
    with open(path) as f:
        return json.load(f)


# simple scenario templates keyed by section letter
SCENARIOS = {
    "a": "A food manufacturer preparing their initial food safety plan.",
    "b": "A facility receiving a new raw ingredient with no prior hazard data.",
    "c": "An auditor reviewing hazard evaluation records for an existing process.",
    "d": "A regulatory inspector checking whether preventive controls are documented.",
}


def make_tc(req, idx):
    letter = req["id"].split("-")[1]
    text   = req["text"]
    return {
        "test_case_id":    f"TC-{idx:03d}",
        "requirement_id":  req["id"],
        "description":     f"Verify compliance with 21 CFR 117.130 {req['section']}: {text[:90]}",
        "input_data":      SCENARIOS.get(letter, "Food facility subject to 21 CFR Part 117."),
        "expected_output": f"Facility has written documentation satisfying {req['section']}: {text[:120]}",
        "steps": [
            f"Request documentation related to {req['section']}.",
            f"Confirm it explicitly covers: {text[:70]}...",
            "Verify the document is current and signed by a responsible party.",
            "Confirm the documented process was followed during the last production run.",
        ],
        "notes": f"Atomic rule under {req['parent']}. Non-compliance may indicate a gap in the food safety plan."
    }


if __name__ == "__main__":
    all_reqs     = load(REQS_FILE)
    selected_ids = load(SELECTED_FILE)
    req_map      = {r["id"]: r for r in all_reqs}

    tcs = []
    for i, rid in enumerate(selected_ids, 1):
        if rid not in req_map:
            print(f"WARNING: {rid} not in requirements.json, skipping")
            log_event("TEST_CASE_MISSING", f"{rid} not found in requirements")
            continue
        tcs.append(make_tc(req_map[rid], i))

    with open(OUTPUT_FILE, "w") as f:
        json.dump(tcs, f, indent=2)

    log_event("TEST_CASES_GENERATED", f"generated {len(tcs)} test cases")
    print(f"generated {len(tcs)} test cases -> {OUTPUT_FILE}")
    for tc in tcs:
        print(f"  {tc['test_case_id']}  {tc['requirement_id']:<22} {tc['description'][:55]}...")

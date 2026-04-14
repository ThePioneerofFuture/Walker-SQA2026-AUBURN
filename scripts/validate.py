import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from forensick import log_event


def load(path):
    with open(path) as f:
        return json.load(f)


def run():
    reqs      = load("output/requirements.json")
    selected  = load("output/selected_rules.json")
    tcs       = load("output/test_cases.json")
    structure = load("output/expected_structure.json")

    req_ids    = {r["id"] for r in reqs}
    tc_req_ids = {tc["requirement_id"] for tc in tcs}
    ok = True

    log_event("VALIDATION_START", "validate.py started")

    print("-- coverage: selected rules -> test cases --")
    for rid in selected:
        if rid not in tc_req_ids:
            print(f"[FAIL] no test case for {rid}")
            log_event("TEST_CASE_MISSING", f"no test case for {rid}")
            ok = False
        else:
            print(f"[PASS] {rid}")

    print("\n-- integrity: test cases -> requirements --")
    for tc in tcs:
        if tc["requirement_id"] not in req_ids:
            print(f"[FAIL] {tc['test_case_id']} references unknown req {tc['requirement_id']}")
            ok = False
        else:
            print(f"[PASS] {tc['test_case_id']} -> {tc['requirement_id']}")

    print("\n-- structure consistency --")
    parsed_parents = {r["parent"] for r in reqs}
    for pid, children in structure.items():
        if pid not in parsed_parents:
            print(f"[FAIL] structure has unknown parent: {pid}")
            ok = False
        else:
            print(f"[PASS] {pid} -> {children}")

    if ok:
        log_event("VALIDATION_PASSED", "all checks passed")
        print("\nvalidation passed.")
    else:
        log_event("VALIDATION_FAILED", "one or more checks failed")
        print("\nvalidation FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    run()

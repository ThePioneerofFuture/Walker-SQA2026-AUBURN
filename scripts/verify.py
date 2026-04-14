import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from forensick import log_event

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("pip install jsonschema")
    sys.exit(1)

REQ_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "parent", "section", "text", "is_atomic"],
        "properties": {
            "id":        {"type": "string"},
            "parent":    {"type": "string"},
            "section":   {"type": "string"},
            "text":      {"type": "string", "minLength": 5},
            "is_atomic": {"type": "boolean"}
        }
    }
}

TC_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["test_case_id", "requirement_id", "description", "input_data", "expected_output"],
        "properties": {
            "test_case_id":    {"type": "string"},
            "requirement_id":  {"type": "string"},
            "description":     {"type": "string", "minLength": 10},
            "input_data":      {"type": "string"},
            "expected_output": {"type": "string"},
            "steps":           {"type": "array"},
            "notes":           {"type": "string"}
        }
    }
}

STRUCT_SCHEMA = {
    "type": "object",
    "additionalProperties": {"type": "array", "items": {"type": "string"}}
}


def check(filepath, schema, label):
    if not os.path.exists(filepath):
        print(f"[FAIL] {label}: file not found")
        log_event("SCHEMA_VALIDATION_FAILED", f"{label} missing")
        return False
    with open(filepath) as f:
        data = json.load(f)
    try:
        validate(instance=data, schema=schema)
        n = len(data) if isinstance(data, list) else len(data)
        print(f"[PASS] {label} ({n} items)")
        return True
    except ValidationError as e:
        print(f"[FAIL] {label}: {e.message}")
        log_event("SCHEMA_VALIDATION_FAILED", f"{label}: {e.message}")
        return False


if __name__ == "__main__":
    log_event("VERIFICATION_START", "verify.py started")
    results = [
        check("output/requirements.json",       REQ_SCHEMA,    "requirements.json"),
        check("output/test_cases.json",          TC_SCHEMA,     "test_cases.json"),
        check("output/expected_structure.json",  STRUCT_SCHEMA, "expected_structure.json"),
    ]
    if all(results):
        log_event("VERIFICATION_PASSED", "all schema checks passed")
        print("\nverification passed.")
    else:
        log_event("VERIFICATION_FAILED", "schema check(s) failed")
        print("\nverification FAILED.")
        sys.exit(1)

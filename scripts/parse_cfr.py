import re
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from forensick import log_event

INPUT_FILE     = "input/21_CFR_117.130.md"
OUTPUT_FILE    = "output/requirements.json"
STRUCTURE_FILE = "output/expected_structure.json"

os.makedirs("output", exist_ok=True)

# matches lines like "## (a) Requirement to conduct..."
parent_re = re.compile(r"^##\s+\(([a-z])\)", re.IGNORECASE)
# matches lines like "### (a)(1) some inline text"
child_re  = re.compile(r"^###\s+\(([a-z])\)\((\d+)\)\s*(.*)", re.IGNORECASE)


def parse_cfr(filepath):
    reqs = []
    current_parent = None
    text_buf = []
    pending = None

    def flush():
        if pending and text_buf:
            pending["text"] = " ".join(text_buf).strip()
            reqs.append(dict(pending))
        text_buf.clear()

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if parent_re.match(line):
                flush()
                pending = None
                letter = parent_re.match(line).group(1).lower()
                current_parent = f"117.130-{letter}"

            elif child_re.match(line):
                flush()
                m = child_re.match(line)
                letter, num, inline = m.group(1).lower(), m.group(2), m.group(3).strip()
                current_parent = f"117.130-{letter}"
                pending = {
                    "id":        f"117.130-{letter}-{num}",
                    "parent":    current_parent,
                    "section":   f"({letter})({num})",
                    "is_atomic": True,
                    "text":      ""
                }
                text_buf.clear()
                if inline:
                    text_buf.append(inline)

            elif line and not line.startswith("#"):
                if pending:
                    text_buf.append(line)
                else:
                    log_event("REQUIREMENT_SKIPPED", f"line outside section: '{line[:60]}'")

    flush()
    return reqs


def build_structure(reqs):
    struct = defaultdict(list)
    for r in reqs:
        if r["is_atomic"]:
            struct[r["parent"]].append(r["id"].split("-")[-1])
    return dict(struct)


if __name__ == "__main__":
    log_event("PIPELINE_START", "parse_cfr.py started")

    reqs = parse_cfr(INPUT_FILE)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(reqs, f, indent=2)

    struct = build_structure(reqs)
    with open(STRUCTURE_FILE, "w") as f:
        json.dump(struct, f, indent=2)

    log_event("PARSE_COMPLETE", f"parsed {len(reqs)} requirements")

    print(f"parsed {len(reqs)} requirements -> {OUTPUT_FILE}")
    print(f"structure -> {STRUCTURE_FILE}")
    for r in reqs:
        print(f"  {r['id']:<25} {r['text'][:65]}...")

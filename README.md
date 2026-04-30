# Walker-SQA2026-AUBURN

**COMP 6710 — Software Quality Assurance | Auburn University | Spring 2026**

## Project Overview

This project implements a Verification and Validation (V&V) pipeline for **21 CFR Part 117.130**, the FDA regulation governing hazard analysis requirements for food facilities. The system parses the regulation text into atomic, machine-readable rules, generates structured compliance test cases, validates them against a JSON schema, and confirms full traceability from regulation to test through an automated CI pipeline.

The individual component extends this by using two locally-hosted LLMs (full-precision and quantized Mistral 7B via Ollama) to generate test cases for five selected requirements, then compares their outputs across coverage, correctness, completeness, and JSON reliability.

### Objectives
1. Demonstrate automated regulatory parsing — extract atomic rules from CFR markdown into structured JSON
2. Generate traceable compliance test cases linked to specific regulatory requirements
3. Validate all artifacts against a defined schema and confirm coverage integrity
4. Produce a forensic audit log of all pipeline events
5. Compare LLM-generated test cases across two model variants to evaluate quality and reliability trade-offs

---

## Repository Structure

```
input/              Source CFR regulation in markdown format
  21_CFR_117.130.md     21 CFR Part 117.130 (FDA Hazard Analysis)

output/             Generated pipeline artifacts (created on first run)
  requirements.json     Parsed atomic rules (15 requirements)
  selected_rules.json   Subset of rules chosen for test case generation
  test_cases.json       Generated compliance test cases
  expected_structure.json  Parent/child section hierarchy
  forensick_log.json    Audit log of all pipeline events

scripts/            Core pipeline scripts
  parse_cfr.py          Parses CFR markdown → requirements.json + expected_structure.json
  generate_test_cases.py  Generates test cases for selected rules
  verify.py             JSON schema validation of all output artifacts
  validate.py           Content validation: coverage, integrity, structure consistency
  forensick.py          Forensic event logger

individual/         Individual LLM comparison task
  llm_test_generator.py   Queries full and quantized Mistral via Ollama
  compare_models.py       Scores and compares LLM outputs
  comparison_report.md    Written analysis of model comparison
  llm_test_cases.json     Generated LLM test cases (created on run)
  comparison_analysis.json Scored results (created on run)

.github/workflows/  CI configuration
  cfr_validation.yml      GitHub Actions pipeline (runs on push to main)
```

---

## Prerequisites

- Python 3.9 or higher
- `jsonschema` Python package
- [Ollama](https://ollama.com) (only required for the individual LLM task)

---

## Reproducing Locally — macOS

### 1. Clone the repository

```bash
git clone https://github.com/ThePioneerofFuture/Walker-SQA2026-AUBURN.git
cd Walker-SQA2026-AUBURN
```

### 2. Install dependencies

```bash
pip install jsonschema ollama
```

> If you have multiple Python versions, use `pip3` instead of `pip`.

### 3. Run the core V&V pipeline

```bash
python scripts/parse_cfr.py
python scripts/generate_test_cases.py
python scripts/verify.py
python scripts/validate.py
```

All output files are written to `output/`. A forensic audit log is written to `output/forensick_log.json`.

### 4. Run the individual LLM comparison (optional)

Requires Ollama running locally with both Mistral model variants:

```bash
# Start Ollama (if not already running as a background service)
ollama serve &

# Pull the required models
ollama pull mistral
ollama pull mistral:7b-instruct-q4_0

# Run LLM test generation and comparison
python individual/llm_test_generator.py
python individual/compare_models.py
```

Results are written to `individual/llm_test_cases.json` and `individual/comparison_analysis.json`.

---

## Reproducing Locally — Windows

### 1. Clone the repository

Open **Command Prompt** or **PowerShell**:

```powershell
git clone https://github.com/ThePioneerofFuture/Walker-SQA2026-AUBURN.git
cd Walker-SQA2026-AUBURN
```

> If `git` is not installed, download it from [git-scm.com](https://git-scm.com/download/win).

### 2. Install dependencies

```powershell
pip install jsonschema ollama
```

> If `pip` is not found, ensure Python is added to your PATH during installation, or use `python -m pip install jsonschema ollama`.

### 3. Run the core V&V pipeline

```powershell
python scripts\parse_cfr.py
python scripts\generate_test_cases.py
python scripts\verify.py
python scripts\validate.py
```

All output files are written to `output\`. Note: Windows uses backslashes in paths, but Python accepts both.

### 4. Run the individual LLM comparison (optional)

Download and install Ollama for Windows from [ollama.com](https://ollama.com). Ollama runs as a background service automatically after installation.

Open a new terminal window and run:

```powershell
ollama pull mistral
ollama pull mistral:7b-instruct-q4_0

python individual\llm_test_generator.py
python individual\compare_models.py
```

---

## Expected Output

After running the full pipeline, `output/` will contain:

| File | Description |
|------|-------------|
| `requirements.json` | 15 atomic requirements parsed from 21 CFR 117.130 |
| `selected_rules.json` | 10 requirement IDs selected for test case generation |
| `test_cases.json` | Compliance test cases with input data and expected output |
| `expected_structure.json` | Parent/child section hierarchy (a→b→c→d) |
| `forensick_log.json` | Timestamped audit log of all pipeline events |

The pipeline exits with code 0 on success and code 1 if any validation check fails.

---

## CI Pipeline

The pipeline runs automatically on every push to `main` via GitHub Actions (`.github/workflows/cfr_validation.yml`). The workflow:

1. Checks out the repository
2. Sets up Python 3.11
3. Installs `jsonschema`
4. Runs all four pipeline scripts in sequence
5. Uploads the `output/` directory as a build artifact

---

## Forensic Logging

Five event types are recorded to `output/forensick_log.json` during pipeline execution:

| Event | Triggered By |
|-------|-------------|
| `PIPELINE_START` | `parse_cfr.py` on startup |
| `REQUIREMENT_SKIPPED` | Any requirement excluded from parsing |
| `PARSE_COMPLETE` | Successful completion of `parse_cfr.py` |
| `TEST_CASE_MISSING` | `validate.py` finds a selected rule with no test case |
| `LLM_TEST_GENERATED` | Each LLM call in `llm_test_generator.py` |

---

## Individual Task Summary

Five requirements spanning all four parent sections (a–d) of 21 CFR 117.130 were selected for LLM comparison:

| ID | Section | Requirement Summary |
|----|---------|---------------------|
| 117.130-a-1 | (a)(1) | Written hazard analysis for each food type |
| 117.130-b-1 | (b)(1) | Hazard identification: biological, chemical, physical |
| 117.130-b-3 | (b)(3) | Identification considers food characteristics and formulation |
| 117.130-c-1 | (c)(1) | Evaluation of severity and probability of each hazard |
| 117.130-d-1 | (d)(1) | Hazards requiring a preventive control must have one established |

Both models (full Mistral 7B and quantized Mistral 7B at 4-bit) were queried via Ollama at temperature 0.3. See `individual/comparison_report.md` for the full written analysis.

---

## Team

- Isaiah Walker — Auburn University, COMP 6710, Spring 2026

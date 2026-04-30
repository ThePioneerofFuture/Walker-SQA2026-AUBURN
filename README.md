# Walker-SQA2026-AUBURN

COMP 6710 — Software Quality Assurance, Auburn University, Spring 2026

## What this is

V&V pipeline for 21 CFR 117.130 (FDA hazard analysis regulation for food facilities). The idea is to parse the regulation text into atomic, machine-readable rules, generate compliance test cases from those rules, and validate everything through a CI pipeline so it's reproducible and auditable.

The individual portion uses two Mistral variants (full and 4-bit quantized) running locally via Ollama to generate test cases for five selected requirements, then compares their outputs.

## Team
- Isaiah Walker

## Structure

```
input/          source CFR markdown (21 CFR 117.130)
output/         generated artifacts — created when you run the pipeline
scripts/        parse → generate → verify → validate
individual/     LLM test generation and model comparison
.github/        GitHub Actions CI
```

## Running it

You'll need Python 3.9+ and `jsonschema`. That's it for the core pipeline.

```bash
pip install jsonschema
```

Then run the four scripts in order:

```bash
python scripts/parse_cfr.py
python scripts/generate_test_cases.py
python scripts/verify.py
python scripts/validate.py
```

Everything lands in `output/`. The pipeline also runs automatically on every push to main via GitHub Actions.

**On Windows**, use backslashes or just run from the repo root in PowerShell — Python handles both. If `pip` isn't found, try `python -m pip install jsonschema` instead.

## Individual task (LLM comparison)

Requires Ollama running locally. Install it from [ollama.com](https://ollama.com) — it runs as a background service on both Mac and Windows after install.

```bash
ollama pull mistral
ollama pull mistral:7b-instruct-q4_0

python individual/llm_test_generator.py
python individual/compare_models.py
```

On Mac, if Ollama isn't already running as a service: `ollama serve &` first.

Output goes to `individual/llm_test_cases.json` and `individual/comparison_analysis.json`. The written comparison is in `individual/comparison_report.md`.

## What gets generated

After a full pipeline run, `output/` has:

- `requirements.json` — 15 atomic requirements parsed from the CFR
- `selected_rules.json` — the 10 rules used for test case generation
- `test_cases.json` — compliance test cases tied to specific requirements
- `expected_structure.json` — parent/child section hierarchy
- `forensick_log.json` — audit log of pipeline events

Exit code 0 = all checks passed. Exit code 1 = something failed (check stdout for which check).

## Forensic logging

Five events get logged to `output/forensick_log.json`:

- `PIPELINE_START` — parse_cfr.py startup
- `REQUIREMENT_SKIPPED` — requirement excluded from parsing
- `PARSE_COMPLETE` — parse_cfr.py finished successfully
- `TEST_CASE_MISSING` — selected rule has no test case (caught by validate.py)
- `LLM_TEST_GENERATED` — each LLM call in the individual task

## Requirements selected for individual task

Picked five that span all four parent sections (a–d) and range from straightforward documentation rules to more judgment-heavy ones:

| ID | Summary |
|----|---------|
| 117.130-a-1 | Written hazard analysis required for each food type |
| 117.130-b-1 | Hazard ID must cover biological, chemical, and physical hazards |
| 117.130-b-3 | Identification must consider food characteristics and formulation |
| 117.130-c-1 | Evaluation must assess severity and probability of each hazard |
| 117.130-d-1 | Hazards requiring a preventive control must have one established |

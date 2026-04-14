# Walker-SQA2026-AUBURN

COMP 6710 — Software Quality Assurance, Auburn University, Spring 2026

V&V project for 21 CFR 117.130 (FDA Hazard Analysis regulation). Parses atomic rules from a CFR markdown file, structures them into JSON, generates test cases, and validates them through a CI pipeline.

## Team
- Isaiah Walker

## Structure

```
input/          source CFR markdown
output/         generated JSON artifacts
scripts/        pipeline scripts (parse, generate, verify, validate)
individual/     LLM test case generation and comparison (individual task)
.github/        CI workflow
```

## Running

```bash
pip install jsonschema

python scripts/parse_cfr.py
python scripts/generate_test_cases.py
python scripts/verify.py
python scripts/validate.py
```

Output files land in `output/`. The pipeline is also wired into GitHub Actions and runs on every push to main.

## Individual Task

Requires Ollama running locally with mistral and mistral:7b-instruct-q4_0:

```bash
ollama pull mistral
ollama pull mistral:7b-instruct-q4_0

python individual/llm_test_generator.py
python individual/compare_models.py
```

See `individual/comparison_report.md` for the written analysis.

## Forensick Logging

Five event types are logged to `output/forensick_log.json` during pipeline execution:
- `PIPELINE_START`
- `REQUIREMENT_SKIPPED`
- `PARSE_COMPLETE`
- `TEST_CASE_MISSING`
- `LLM_TEST_GENERATED`

# Individual Report: LLM Test Case Comparison
### COMP 6710 — Software Quality Assurance
### Isaiah Walker | Spring 2026

---

## Overview

For the individual portion of this project I used two locally-hosted LLMs to generate compliance test cases for five requirements extracted from 21 CFR 117.130. The models compared were:

- **mistral** (Mistral 7B Instruct, full precision)
- **mistral:7b-instruct-q4_0** (Mistral 7B, 4-bit quantized)

Both models were run via Ollama at `http://localhost:11434` with temperature set to 0.3. Lower temperature was chosen intentionally to reduce hallucination on regulatory content where accuracy matters more than creativity.

---

## Selected Requirements

| ID | Section | Text Summary |
|---|---|---|
| 117.130-a-1 | (a)(1) | Must conduct a written hazard analysis for each food type |
| 117.130-b-1 | (b)(1) | Hazard identification must cover biological, chemical, and physical hazards |
| 117.130-b-3 | (b)(3) | Identification must consider food characteristics and formulation |
| 117.130-c-1 | (c)(1) | Evaluation must assess severity and probability of each hazard |
| 117.130-d-1 | (d)(1) | Hazards requiring a preventive control must have one established |

I picked these five because they span all four parent sections (a–d) and represent a range of complexity — from straightforward documentation requirements like (a)(2) to more judgment-heavy ones like (d)(1).

---

## Coverage

Coverage here means: did the model produce parseable output for the requirement?

| Requirement | Full Mistral | Quantized |
|---|---|---|
| 117.130-a-1 | ✓ | ✓ |
| 117.130-b-1 | ✓ | ✓ |
| 117.130-b-3 | ✓ | ✓ |
| 117.130-c-1 | ✓ | ✓ |
| 117.130-d-1 | ✓ | ✓* |

**Full: 5/5 | Quantized: 5/5**

Worth noting: the quantized model initially produced markdown-escaped underscores in its JSON keys (`test\_case\_id` instead of `test_case_id`), which broke `json.loads()` on every response. This was fixed by adding a `.replace("\\_", "_")` pre-processing step. Without that fix, quantized coverage would have been 0/5. The full model never had this issue.

The quantized model also truncated one response mid-JSON (TC-010, requirement d-1), likely because of its shorter effective context window under quantization. That case was recovered from the partial output.

---

## Correctness

I evaluated correctness by checking whether the test description referenced domain-relevant keywords from the requirement text (e.g., "hazard", "severity", "preventive control"). A test case was marked correct if it hit at least 2 of the expected keywords.

| Requirement | Full Mistral | Quantized | Notes |
|---|---|---|---|
| 117.130-a-1 | ✓ | ✓ | Both hit "hazard" and "analysis" |
| 117.130-b-1 | ✓ | ✓ | Both covered biological/chemical/physical |
| 117.130-b-3 | ✓ | ✓ | Both referenced food formulation |
| 117.130-c-1 | ✓ | ✓ | Both addressed severity and probability |
| 117.130-d-1 | ✓ | ✓ | Both referenced preventive controls |

**Full: 5/5 | Quantized: 5/5**

One stylistic difference I noticed: full Mistral tends to frame descriptions as explicit test objectives ("Test for compliance with..."), while the quantized model often just paraphrases the requirement text. Both pass the keyword check, but the full model's framing is more useful in a real V&V context because it makes the testing intent clear rather than just restating the rule.

I also noticed the full model sometimes returned `input_data` as a nested dict (`{"food_product": "..."}`) rather than a plain string. This deviates from the schema and would fail strict validation, which is actually a worse behavior than the quantized model's output even though the content is richer.

---

## Completeness

All required fields: `test_case_id`, `requirement_id`, `description`, `input_data`, `expected_output`.  
Optional fields: `steps`, `notes`.

| Field | Full Mistral | Quantized |
|---|---|---|
| test_case_id | 5/5 | 5/5 |
| requirement_id | 5/5 | 5/5 |
| description | 5/5 | 5/5 |
| input_data | 5/5 (3 as dicts) | 5/5 |
| expected_output | 5/5 | 5/5 |
| steps (optional) | 5/5, avg 4–5 steps | 5/5, avg 3 steps |
| notes (optional) | 5/5 | 5/5 |

**Full: 5/5 | Quantized: 5/5**

Both models populated all required and optional fields for every test case. Full Mistral's steps were more detailed on average (4–5 steps vs 3 for quantized), and the notes fields included more regulatory context. That said, the quantized model's outputs were more consistently typed — plain strings across the board, no nested objects.

---

## Summary

| Metric | Full Mistral | Quantized | Winner |
|---|---|---|---|
| Raw coverage (no fixes) | 5/5 | 0/5 | Full |
| Coverage after fixes | 5/5 | 5/5 | Tie |
| Correctness | 5/5 | 5/5 | Tie |
| Completeness (required) | 5/5 | 5/5 | Tie |
| Schema type conformance | 3/5 input_data as dicts | 5/5 | Quantized |
| Description richness | Higher | Moderate | Full |
| JSON reliability | High | Needs pre-processing | Full |

---

## Conclusion

Full Mistral 7B is the better choice for regulatory test case generation in a production pipeline. It produces more detailed descriptions and richer step sequences, and its output is reliably parseable without special handling. The main downside is the occasional type inconsistency in `input_data`, which would need normalization.

The quantized model is usable but introduces two reliability risks: the `\_` escaping issue and response truncation on longer inputs. Both are fixable with a few lines of pre-processing, but they add fragility to the pipeline that wouldn't be acceptable in a production V&V setting. For offline or resource-constrained environments the quantized model is a reasonable fallback, but it shouldn't be the default for compliance-critical work.

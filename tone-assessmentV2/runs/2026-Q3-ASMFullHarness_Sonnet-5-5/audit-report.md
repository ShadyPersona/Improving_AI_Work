# Audit Report: 2026-Q3-ASMFullHarness_Sonnet-5-5

Model: claude-sonnet-5-5 | Operator: Danny George | Template: CSA Template.md (default) | Source: ASM_-_Cloud_Security_Assessment_2026-Q3-af90d34e.docx

## Outcome

- Final status: G4 pass; deterministic G5 pass on iteration 1; step 06 adversarial judgment review pass; no punch-out triggered; run certifiable.
- Deliverable: `ASM_-_Cloud_Security_Assessment_2026-Q3_toned.docx` (the source DOCX edited in place so template styles, tables, screenshots and footers are preserved).
- Hashes (SHA-256): draft.md `21ff166722ac2bb6f45107dd4c123a21a62c97b8be0d55db6e645bc47e32e24a`; toned.md `244b3cbf227c9b165912fd0718376437a78ed1827adc154b5d2fb934c5c4fa97`; tone-changes.json `c04763826a48b5a60c06e92555b7ab651dcc92b3640f3c35f0c6114c2046f745`; deliverable `1f2836b80fcb3e0489e55f72b248d23acf8e9921d25a426571ec2cd27b30b209`.

## Steps executed

1. Setup: DOCX converted to `inputs/draft.md` (20 headings, 14 harness-counted table matches; mammoth page markers removed; the Secure Score screenshot alt text that had leaked into the Control Movement heading was restored to a separate image line).
2. G4 (deterministic, harness): draft readable, template readable, run-state present, template heading structure extractable (26 headings): all pass.
3. Step 05 (tone consistency): one pass; outputs `toned.md` and `tone-changes.json`.
4. G5 deterministic layer (harness): D1 to D6 all pass (0 banned-pattern hits over prose and table cells; all factual tokens traceable to the draft; 54 records; 14/14 tables).
5. Step 06 judgment review: pass (below). Deliverable assembled.

## G5 adversarial review

| Check | Result | Basis |
|---|---|---|
| 1 Assessment quality | pass | Headings 20/20 match the template order; the draft was already conclusion-first, so edits targeted quarter anchoring, tense, fragments, contractions, comma splices and evidence-gap integration; a conclusion paragraph was added to Identity and Access (the only section without one), built only from conclusions already in the draft; Security Awareness call-out untouched. |
| 2 Substance freeze | pass | No numeric, date, percentage, CIS or NIST token added or dropped (deterministic diff); every record has `facts_changed: false`; no new fact, cause or outcome introduced; draft errors were logged as observations rather than corrected. |
| 3 Change accountability | pass | Schema valid; 54 records (26 table-row, 28 prose); 14/14 tables in `tables_reviewed`; 9 observations; every changed table line equals an `after` value. |
| 4 Punch-out closure | pass | No punch-out triggered; `certifiable: true`; no bypass attempt. |

### Residual items accepted by the reviewer (not G5 failures)

- A few present-tense reporting verbs remain beside the converted past-tense observations (for example "Defender reports full achievement", "Q3 reports 436 out of 588 users", "Two incidents are High severity"). Standing attributions and open-record statuses were left in present tense.
- One Status cell in Active Recommendations ("One High and two Medium active paths.") remains evidence shorthand, which the step 05 table rules permit.
- Two table header labels ("Current Weaknesses", "Current exposed / total") and a few uses of "current" with a named context were left as drafted because the draft defines them against Q2.
- Observations in `tone-changes.json` need human review, notably the draft typo "AMS’s" (client is ASM), the removed unfinished sentence fragment in Identity and Access, and two table cells whose text does not match their rows.

## Punch-outs

None raised. A (missing content) did not fire; E (loop exhaustion) did not fire. G5 loop counter finished at 1 of 2.

## Tone-change statistics

Total edits: 54 (28 prose, 26 table-row). Table rows reviewed: 14 tables (26 rows edited).

By assessment_function:

- evidence_interpretation: 22
- evidence_limitation: 9
- quarter_movement: 8
- recommendation_traceability: 6
- professional_tone: 5
- template_structure: 2
- cross_signal_synthesis: 1
- executive_conclusion: 1

By style_marker:

- complete_sentences: 11
- evidence_integration: 8
- temporal_precision: 8
- sentence_discipline: 7
- grammar: 6
- punctuation: 3
- tense: 3
- plain_language: 2
- template_formatting: 2
- active_framing: 1
- assessment_first: 1
- banned_patterns: 1
- template_structure: 1

## Narrative and structural changes applied

- Anchored observed measurements to Q3 and moved them to past tense in the Executive Summary, Posture Summary, Control Movement, Identity, Endpoint, Data Protection and AI sections.
- Replaced raw evidence-gap fragments ("...: It was not available.") with complete sentences in prose and tables.
- Converted the internal labels "Regressed since Q2" and "Improved since Q2" into complete sentences.
- Removed contractions (the only deterministic banned-pattern hit in the draft).
- Added the theme title and restored the list marker on the Key Risk Themes bullets.
- Added an Identity and Access conclusion paragraph; split the Defender screenshot from its paragraph in markdown (the DOCX already held them separately).
- Table structure, row order, columns, and all reference columns were left unchanged.

## Audit trail

Per-run audit files written by the harness: `audit/run-2026-Q3-ASMFullHarness_Sonnet-5-5.jsonl`, `audit/guardrails-2026-Q3-ASMFullHarness_Sonnet-5-5.jsonl`, `audit/success-2026-Q3-ASMFullHarness_Sonnet-5-5.md` (written at finalization), `audit/punchout-2026-Q3-ASMFullHarness_Sonnet-5-5.md` (not created: no punch-out).
Step 05 metering (harness estimate): see `audit/run-2026-Q3-ASMFullHarness_Sonnet-5-5.jsonl`.

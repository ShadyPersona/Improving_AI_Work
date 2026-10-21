# Audit Report — 2026-Q3-HHAFullHarness_Sonnet5-5

Client: Hialeah Housing Authority (HHA) — Cloud Security Assessment 2026-Q3
Deliverable: `Hialeah_Housing_Authority_Cloud_Security_Assessment_2026-Q3.docx` (original layout, styles, and all 6 embedded images preserved; recorded edits applied in place)

## Steps executed
1. Setup: uploaded DOCX converted to `inputs/draft.md`; template `CSA Template.md` verified (`bc452ab9…dd67`); `harness.py` hash verified (`bbd77403…6576`).
2. G4 (harness): pass on iteration 1 — draft readable, template readable, run-state present, template headings extractable.
3. Step 05 (tone consistency): `toned.md` and `tone-changes.json` produced.
4. G5 deterministic pre-checks (harness): D1–D6 all pass on iteration 1.
5. Step 06 adversarial judgment review: pass (see below).

## Guardrail results
- G4: pass.
- G5 D1 g4-sentinel: pass. D2 schema-valid: pass. D3 banned-patterns: 0 hits over prose and table cells. D4 substance-freeze: all factual tokens traceable to draft (0 new, 0 dropped). D5 change-accountability: 67 records; 12/12 tables reviewed. D6 punch-out closure: pass (none triggered).

## G5 adversarial judgment review
1. Assessment quality: pass. Headings match the template order. Substantive sections lead with the condition, carry quarter movement (Q1 to Q2 to Q3), significance, qualification, and a recommended response. Positive findings are calibrated (for example, Identity 98.48% does not establish deployed Entra ID P2 policies). Not-assessed domains state the limitation and its consequence. Security Awareness content was preserved unchanged.
2. Substance freeze: pass. `toned.md` is `draft.md` with the 67 recorded edits applied, so no unrecorded change exists. No number, date, percentage, CIS or NIST reference, finding title, or recommendation changed.
3. Change accountability: pass. All 67 records carry `facts_changed: false`; 38 are table-row edits; 12 of 12 draft tables appear in `tables_reviewed`; 10 distinct `assessment_function` values, 8 of them analytical.
4. Punch-out closure / certifiability: pass. No punch-out triggered; run is certifiable.

## Punch-outs
None raised.

## Tone-change statistics
- Records: 67 (29 prose, 38 table rows).
- By assessment_function: evidence_limitation 23, evidence_interpretation 10, recommendation_traceability 7, historical_context 7, quarter_movement 6, template_structure 6, professional_tone 2, executive_conclusion 2, security_significance 2, cross_signal_synthesis 2.
- By style_marker: complete_sentences 21, assessment_first 9, sentence_discipline 7, template_formatting 6, temporal_precision 5, grammar 4, tense 3, active_framing 3, qualification_discipline 2, significance_calibration 2, client_significance 1, actionable_recommendations 1, explanatory_style 1, terminology 1, recommendation_traceability 1.

## Narrative and structural changes applied
- Conclusion-first rewrites of the Executive Summary, Posture Summary, Key Risk Themes, Control Movement, and each Security Signal Review domain.
- Verbless evidence-gap fragments in table cells rewritten as complete sentences (21 records).
- Vague temporal terms ("current", "currently", "now") replaced with Q3 anchors.
- Informal phrasing in the Executive Summary ("staying on top of their security posture") replaced with a calibrated conclusion.
- Recommendation titles in Active Recommendations bolded per the template convention (6 records).
- Table structure frozen; no row or column added, removed, or reordered.

## Observations for human review (tone-changes.json `observations`, 9)
- Identity table control points (10/10, 9/9, 8/8, 4/4, 0/1, two 7/7) do not reconcile to the reported 65/66 on their own (confirm).
- Risk-policy row (complete due to Entra Security Defaults) versus Identity prose (no applicable license; does not establish Entra ID P2 policies) (confirm).
- Security Awareness call-out names ASM rather than HHA (correct in draft).
- Security Awareness call-out says discovery confirms access to multiple AI services, while the AI section states no AI usage evidence was available; it also names identity recovery as a topic the Identity section does not discuss (confirm).
- Template status format MM.DD.YYYY and identification format YYYY.QQ not supplied in draft (accept deviation).
- No separate conclusion paragraph in the Endpoint, Cloud Workload, and AI sections (accept deviation).
- Domain Posture introduction says no prior indicator is carried forward, while the template says indicators are carried forward (accept deviation).
- Evidence-gap vocabulary varies (Not assessed, not provided, unavailable, Not Available) (confirm).

## Run notes
- `harness.config.json` was not on the mirror when G4 and the first step record were written, so the `audit/run-2026-Q3-HHAFullHarness_Sonnet5-5.jsonl` step-05 record carries the harness default model name rather than `claude-sonnet-5-5`, and an empty operator. The config was added to the mirror afterwards. Audit records are harness-authored and were not edited.
- The aggregate logs (`guardrails.jsonl`, `success-log.md`, `punchout-log.md`) were seeded on the mirror from the cloud copies before any append, so earlier runs' rows and recorded human decisions were preserved.

## End-to-end outcome
G4 pass; G5 pass; no punch-outs; certifiable; final deliverable emitted.

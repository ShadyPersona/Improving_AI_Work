# Audit Report — 2026-Q3-IRONTRAXFullHarness

## Run summary
- Run ID: 2026-Q3-IRONTRAXFullHarness
- Source: Irontrax_-_Cloud_Security_Assessment_2026-Q3-7219d6e6.docx (converted to `inputs/draft.md`)
- Template: CSA Template.md (checksum verified)
- Harness: harness.py, hash 68566740e6e489cc17456a68e902f7239ef8ce0ecd06353b164a94825884c4c8
- Steps executed: 05-tone-consistency (2 iterations), 06-adversarial-review (Phase 1 judgment; Phase 2 finalization)

## Guardrail results

### G4 inbound gate (iteration 1) — PASS
- draft readable (draft.md sha256 f1d3d0a6ae22bc1d21042797c8e78d9b3ecefa07f8ae877c4ec8fd40d258eedd)
- template readable (sha256 49dbd928c511a05529441fde6dbe66fb1eea425214f4fb89b5ccc3c0e905c8d1)
- run-state.json present
- template heading structure extractable (26 headings)

### G5 deterministic checks
| Iteration | Check | Result | Detail |
|---|---|---|---|
| 1 | D1-g4-sentinel | pass | |
| 1 | D2-schema-valid | pass | builtin-mini-validator |
| 1 | D3-banned-patterns | **fail** | line 215: 'My' (Exchange role names "My Custom Apps", "My Marketplace Apps", "My ReadWriteMailbox Apps" matched as first-person pronoun) |
| 1 | D4-substance-freeze | pass | all factual tokens traceable to draft |
| 1 | D5-change-accountability | pass | 38 records; 12/12 tables |
| 1 | D6-punchout-closure | pass | |
| 2 | D1-g4-sentinel | pass | |
| 2 | D2-schema-valid | pass | builtin-mini-validator |
| 2 | D3-banned-patterns | pass | 0 hits over prose and table cells |
| 2 | D4-substance-freeze | pass | all factual tokens traceable to draft |
| 2 | D5-change-accountability | pass | 39 records; 12/12 tables |
| 2 | D6-punchout-closure | pass | |

Loop-back: one G5 failure (D3) returned to step 05. Fix: the 6.3.1 row was changed to the exact Exchange role identifiers (MyCustomApps, MyMarketplaceApps, MyReadWriteMailboxApps). The role names are unchanged, only the spacing. The row was recorded as change record 39 (style_marker banned_patterns, facts_changed false), and the table's rows_edited was updated to 3. G5 loop counter: 2 of loop_max 2 (iteration counter); no loop exhaustion.

### Additional verification performed by the agent
- Every table line in toned.md is either verbatim from draft.md or the `after` of a recorded row-level change (checked programmatically; 0 mismatches).
- All prose `before`/`after` strings in tone-changes.json match draft.md / toned.md.
- Numeric tokens: every figure (e.g., 39.33%, 38.6%, 105/267, 105/272, 96.72%, 89.39%, 23.35%, 0%, 59/61, 54.41%) is preserved. Repeated Q1/Q2 score sentences were consolidated into one sentence ("Data at 0% and Apps at 23.35% in all three quarters"), which keeps the values and their quarter scope.

### G5 adversarial judgment (Phase 1, items 1–5)
- (a) Template conformance: section order and headings follow the template. Four `[image]` placeholders remain where the source DOCX embedded images; the final DOCX needs the original images restored or an explicit decision to omit them.
- (b) Analytical depth: Executive Summary, Posture Summary, Control Movement, Identity, Data Protection, Detection, and Recommendations are conclusion-first with significance and calibration. Endpoint, Cloud Workload, and AI sections state supported conclusions about the evidence gap and the data needed; they do not infer posture. Security Awareness call-out preserved unchanged (exempt).
- (c) Quarterly thesis: movement is anchored to Q1/Q2/Q3. Identity movement (89.39% to 96.72%) is recorded as unattributable. Score trends are described as flat. Post-quarter evidence is not presented as Q3 progress.
- (d) Cross-signal synthesis: Key Risk Themes and the Data Protection/Collaboration section relate identity, data protection, email/collaboration, and detection signals.
- (e)/(f) Editorial: third-person, formal, no banned patterns (0 hits). Caveat density is high: "not established", "not assessed", and "do not establish" recur across sections. This is faithful to the evidence but could be read as defensive caveat-stacking. Flagged as advisory, not a hard fail.
- Substance freeze: no hard failure found. All 39 records have facts_changed false.
- Change accountability: 39 records; assessment_function coverage includes executive_conclusion (3), quarter_movement (3), evidence_interpretation (5), evidence_limitation (19), security_significance (2), recommendation_traceability (4), cross_signal_synthesis (1), historical_context (1), professional_tone (1). Coverage is analytical, not template-only.

Judgment result: PASS, with advisory items (image placeholders; caveat density).

### Punch-outs
- A_missing_content: not triggered
- E_loop_exhaustion: not triggered
- No approvals or human decisions were recorded or required.

### Certifiability
- run-state.json: certifiable true, non_certifiable_reasons empty
- tone-changes.json: certifiable true

## Tone-change statistics (tone-changes.json, 39 records)
- facts_changed true: 0
- style_marker: complete_sentences 20; sentence_discipline 7; significance_calibration 2; temporal_precision 2; assessment_first 2; narrative 1; client_significance 1; cadence 1; active_framing 1; plain_language 1; banned_patterns 1
- assessment_function: evidence_limitation 19; evidence_interpretation 5; recommendation_traceability 4; executive_conclusion 3; quarter_movement 3; security_significance 2; cross_signal_synthesis 1; historical_context 1; professional_tone 1
- tables_reviewed: 12 of 12; rows_edited total 29
- observations: 8 (cross_reference 1, total_reconciliation 1, terminology 1, template_deviation 5), none corrected

## Narrative and structural changes applied
- Executive Summary, Posture Summary, Control Movement paragraph 1, Identity paragraphs 1–2, Data paragraphs 1–2 rewritten conclusion-first.
- Narrative table cells converted from fragments to complete sentences.
- Table structure, row count, and column layout unchanged.

## Open items for the human reviewer
1. Four `[image]` placeholders: restore the original images in the final DOCX, or decide to omit them.
2. Observations (not corrected; for confirmation or correction in the draft): awareness-guidance cross-reference; Identity component total (58 vs 59 of 61); quarter-label formats; template status format; domain indicators; exposure table "Not available" values; Security Awareness single-cell structure; the four image placeholders.

## End-to-end outcome
G4 passed. G5 deterministic checks passed on iteration 2. G5 judgment passed with advisory items. No punch-outs. Run certifiable. Final deliverable assembly is the subject of the Phase 2 step.

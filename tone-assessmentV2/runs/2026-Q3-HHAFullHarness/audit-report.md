# Audit Report: 2026-Q3-HHAFullHarness

## Steps executed
- Step 05 (tone rewrite): `toned.md` and `tone-changes.json` produced by revised build (78 recorded edits). Step 05 done marker created.
- Step 06 (G5 adversarial review and finalize): this report and the final .DOCX.

## Guardrail results
Deterministic G5 (harness `g5_check`, re-run read-only on the revised output):
- D1 g4-sentinel: pass
- D2 schema-valid: pass
- D3 banned-patterns: pass (0 hits over prose and table cells)
- D4 substance-freeze: pass (all factual tokens traceable to draft)
- D5 change-accountability: pass (78 records; 12/12 tables)
- D6 punchout-closure: pass

G4 passed (`.g4-passed` present). Harness loop counter G5 = 1 (first-pass iteration of the revised output).

## Judgment review (G5 layer 2)
- Assessment quality: each substantive section opens with a conclusion (Posture Summary, Identity, Endpoint, Data Protection, Cloud Workload, AI, Detection). Movement claims are anchored to Q2 and Q3 with the scoring events dated.
- Substance freeze: a sentence-level traceability check against `inputs/draft.md` found every figure, finding, and recommendation traceable. Reworded sentences are calibrations of draft statements, not new facts, causes, or outcomes.
- Change accountability: every edit records location, before, after, style_marker, reason, assessment_function, and facts_changed (false on all 78).
- Punch-out closure: no punch-out triggered (A_missing_content false, E_loop_exhaustion false).

Limitations of the review:
- Not every table cell was rewritten. Header, separator, and label cells are carried forward from the draft unchanged.
- The draft's Security Awareness box refers to "ASM" where the rest of the report refers to HHA. The text is unchanged because the substance freeze prohibits editing draft content.

## Tone-change statistics (tone-changes.json)
- Total edits: 78. Tables reviewed: 12 of 12. Observations: 7. Certifiable: true.
- By style_marker: table_cell_full_sentence 29; qualification_sentence_split 17; imperative_to_subject 17; conclusion_first_narrative 10; caption_full_sentence 2; list_punctuation_clarity 1; terminology_hha 1; scope_qualification 1.
- By assessment_function: evidence_limitation 23; recommendation_traceability 16; evidence_interpretation 11; historical_context 9; executive_conclusion 7; security_significance 6; cross_signal_synthesis 2; quarter_movement 2; template_structure 2.

## Punch-outs
None triggered. No human decision required.

## Outcome
G5 passed (deterministic and judgment layers). Run certifiable. Final deliverable emitted in `runs/2026-Q3-HHAFullHarness/`.

# Audit Report — Run 2026-Q3-IronTraxFullHarness_Sonnet-5-5

**Client:** Irontrax — Cloud Security Assessment 2026: Q3
**Operator:** Danny George
**Model:** claude-sonnet-5-5 (per harness.config.json)
**Outcome:** G5 PASSED (iteration 1 of loop_max 2). No punch-out triggered. Run certifiable: true.

## Steps executed

| Step | Result |
|------|--------|
| Setup | Uploaded DOCX converted to `inputs/draft.md`. Template `CSA Template.md` verified (content match). `harness.py` hash verified as bbd7740337712f689ecba079f2026a32104ab60154f45b34a16bf81ebe5c6576. |
| G4 (inputs → tone) | Pass: draft readable, template readable, run-state.json present, template heading structure extractable. |
| 05 Tone consistency | `toned.md` and `tone-changes.json` produced. |
| G5 deterministic (tone → review) | Pass: D1–D6 all pass. |
| 06 Adversarial review | Judgment review passed (see below). Deliverable assembled. |

## G5 deterministic checks (harness)

| Check | Result | Detail |
|-------|--------|--------|
| D1-g4-sentinel | pass | .g4-passed present |
| D2-schema-valid | pass | builtin-mini-validator |
| D3-banned-patterns | pass | 0 hits over prose and table cells |
| D4-substance-freeze | pass | all factual tokens traceable to draft |
| D5-change-accountability | pass | 50 records; 12/12 tables |
| D6-punchout-closure | pass | no punch-out triggered |

## G5 adversarial judgment review (step 06)

1. **Assessment quality — pass.** Headings match the template 20 of 20, in order. Each substantive section leads with a conclusion, states Q3 evidence, and calibrates positive findings (a Completed status is treated as a Microsoft signal, not proof of operating effectiveness). Quarter movement is anchored to Q1, Q2, and Q3, with unattributed movement stated explicitly. The Security Awareness call-out was carried forward verbatim.
2. **Substance freeze — pass.** Every number, date, percentage, CIS and NIST reference, and finding is unchanged. Edits added no fact, cause, or outcome that is absent from the draft.
3. **Change accountability — pass.** 50 records, all `facts_changed: false`. All 12 draft tables are in `tables_reviewed`; 17 table rows were edited and each is recorded line by line. 11 observations are recorded for human review.
4. **Certifiability and punch-out closure — pass.** No punch-out triggered. No bypass attempt occurred.

## Tone-change statistics

Records by `assessment_function`: template_structure 14, evidence_interpretation 9, quarter_movement 6, recommendation_traceability 6, evidence_limitation 5, historical_context 4, security_significance 3, cross_signal_synthesis 2, executive_conclusion 1.

Records by `style_marker`: template_formatting 14, complete_sentences 12, temporal_precision 5, tense 5, grammar 5, client_significance 2, explanatory_style 1, qualification_discipline 1, significance_calibration 1, actionable_recommendations 1, sentence_discipline 1, banned_patterns 1, template_structure 1.

Analytical coverage: 36 of 50 records carry an analytical `assessment_function`.

## Narrative and structural changes applied

- **Conversion artifacts normalized:** page-boundary markers were removed, figures were separated from paragraph text, and 11 tables had their empty converter header rows replaced by a single header and separator. The Security Awareness call-out table was left verbatim. No cell content changed through normalization.
- **Executive Summary, Control Movement, Identity, Data Protection:** undated references ("current", "currently") were replaced with named quarters, and observed measurements moved to past tense.
- **Key Risk Themes:** four action-only bullets now state what each theme covers before the recommended response.
- **Identity:** two sentences with grammar defects were repaired, and an overclaim ("ensures ... as secure as Microsoft controls suggest") was replaced with a statement of what validation can establish.
- **Data Protection:** a run-on licensing sentence was split, and the closing recommendation now states its rationale (the connected data-egress exposure).
- **Endpoint and Vulnerabilities:** a closing paragraph was assembled solely from conclusions already stated in the section (flagged as an observation for confirmation).
- **Tables:** verbless or semicolon-joined fragments in narrative cells were rewritten as complete sentences in the Domain Posture, Identity, Active Recommendations, and CIS tables. Reference and evidence-label columns were not rewritten.

## Observations requiring human review (never corrected)

| Type | Location | Action |
|------|----------|--------|
| total_reconciliation | Identity evidence table: itemized points sum to 58 earned and 58 available, versus 59/61 reported | confirm |
| cross_reference | Data Protection closing paragraph cites Active Recommendations 1–4, but DLP appears in none of them | confirm |
| cross_reference | AI section says the awareness guidance addresses impersonation verification, but the Security Awareness call-out covers cloud misconfigurations and shadow APIs | correct in draft |
| cross_reference | Data Protection paragraph 1 states Irontrax holds Microsoft Business Standard, while Posture Summary says license flags are unverified; licensing phrase is ambiguous | confirm |
| terminology | Evidence-status wording differs across tables ("CIS not tested", "Exact CIS configuration not assessed", "Not assessed") | confirm |
| terminology | "To address" / "Open" / "open"; "flagged licensed" / "Have license" | confirm |
| template_deviation | Identified and Status column formats differ from template (YYYY.QQ and MM.DD.YYYY dates) | accept deviation |
| template_deviation | Executive Summary and section introductions replace template boilerplate; Key Risk Themes is a bulleted list | accept deviation |
| template_deviation | Endpoint section had no conclusion paragraph; one was assembled from existing statements | confirm |
| terminology | CIS 6.3.1 Microsoft role names ("My ..." prefix) were restated because the first-person scan flags the word "My" | confirm |
| template_deviation | Draft structure normalized (page markers, header shells, split tables) | accept deviation |

## Punch-outs

None raised. None required.

## End-to-end outcome

G5 passed on iteration 1. The run is certifiable. The final deliverable was emitted as `Irontrax_-_Cloud_Security_Assessment_2026-Q3_toned.docx`, produced by applying the recorded edits to the uploaded DOCX in place. Its content was verified identical to `toned.md` (0 differing lines, 20 headings, all 7 embedded images preserved).

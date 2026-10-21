# Audit Report — 2026-Q3-PunchOutETest-r2

**Run type:** harness TEST run (punch-out E, bypass guard, resume-G4 verification). Every halt and failure in this run's history was expected.

## Steps executed
1. G4 (iteration 1, draft sha256 `31ce5d93…1da23`): pass.
2. Step 05 (twice): `toned.md` carried one deliberate first-person edit ("We recommend…", recorded in `tone-changes.json`).
3. G5 deterministic, iterations 1 and 2: fail on D3-banned-patterns (`line 28: 'We'`). The harness escalated to punch-out E ("G5 loop_max reached").
4. Bypass test while E was open: both attempts blocked; recorded bypass attempt, so the run is permanently non-certifiable.
5. Human decision recorded for E by Danny George at 2026-10-21T16:48:49Z: "approve retry — banned pattern was a deliberate test fixture".
6. Draft edited (first line of Executive Summary replaced with "This is to verify C"); `drive --resume`; G4 re-run (iteration 1, new draft sha256 `617a2f17…ee5a0`): pass.
7. Bypass test after closure: `skipped: true` (no gate failure).
8. Step 05 (clean, no banned patterns); G5 deterministic: pass on D1–D6 (0 banned-pattern hits, all factual tokens traceable to draft, 12 records, 13/13 tables reviewed).
9. Step 06 judgment review (this document).

## Tone-change statistics (clean step 05)
- Records: 12; `facts_changed: true`: 0; table rows edited: 7 across 13 tables reviewed; observations: 7.
- By style_marker: sentence_discipline 3, grammar 3, banned_patterns 1, temporal_precision 1, active_framing 1, consultant_voice 1, complete_sentences 1, punctuation 1.
- By assessment_function: professional_tone 3, evidence_interpretation 2, recommendation_traceability 2, evidence_limitation 2, security_significance 1, quarter_movement 1, historical_context 1.

## Step 06 G5 judgment
- Substance freeze, change accountability and banned-pattern checks passed deterministically.
- Scope note: this is a minimal-edit test fixture, not a full analytical rewrite. The Executive Summary first paragraph was replaced by the operator-supplied test sentence ("This is to verify C"), which is a test artifact and not client-ready prose. The result is a working artifact for review only.

## Certifiability and outcome
- `run-state.json`: `certifiable: false`; reasons "G5 loop_max reached" and "bypass attempt recorded".
- Punch-out E is two-key closed (approved flag plus human-decision row for this run_id).
- A recorded bypass attempt makes the run permanently non-certifiable. **No client deliverable (.docx) was emitted.** Expected terminal state: awaiting_human with no open punch-outs; finalization is not possible for this run.

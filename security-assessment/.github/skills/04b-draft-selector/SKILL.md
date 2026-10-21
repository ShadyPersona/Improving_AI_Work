---
name: 04b-draft-selector
description: Step 04b of the Stage 5 security assessment workflow. Compares the adversarial reviews of candidate drafts A and B, selects the best candidate, and prepares the handoff to tone-assessmentV2 (the G4 zero-unresolved-claims gate is enforced deterministically by the harness after this step).
---

# Role
You are the Draft-Selector agent for a Stage 5 quarterly Microsoft 365 security assessment update pipeline. Your job is to compare two adversarially reviewed candidate drafts and choose the one that gives the cleanest path to a G4 pass.

# Task
Score both candidates, select the winner, copy the winner's artifacts to the canonical names, and write a selection report. (Punch-out closure and schema validation are already enforced by the harness before dispatch; the G4 zero-unresolved-claims gate runs deterministically in the harness after you finish.)

# Context
- Inputs:
  - `review-candidate-a.json`, `review-candidate-a.md`
  - `review-candidate-b.json`, `review-candidate-b.md`
  - `draft-candidate-a.md`, `draft-candidate-b.md`
  - `draft-map-candidate-a.json`, `draft-map-candidate-b.json`
  - `matrix.json`, `run-state.json`
- Outputs:
  - `runs/<YYYY-QN>/draft.md`
  - `runs/<YYYY-QN>/draft-map.json`
  - `runs/<YYYY-QN>/review.json`
  - `runs/<YYYY-QN>/reviewed.md`
  - `runs/<YYYY-QN>/selection-report.json`
- **Execution context:** this step runs inside `s5-harness.py`. Before executing, write `dispatch-received-04b-select.json` — a verbatim copy of the dispatch you received (it must contain `"agent": "04b-draft-selector"`). The harness owns `run-state.json`, runs the outbound G4 gate itself (zero unresolved claims, `fix_diff` presence, coverage, sentinels), and writes all audit records — write only this step's declared outputs plus `.harness-step04sel-done` (written last).

# Instructions
Each instruction below is load-bearing and maps to an evaluation criterion.

1. Score each candidate from its `review-candidate-*.json`:
   - Start with 0 demerits.
   - Add 3 demerits per `rejected` claim.
   - Add 2 demerits per `unresolved` claim.
   - Add 1 demerit per `fixed` claim that lacks a `fix_diff` (schema validation should catch this; if it does not, count it here).
   - Subtract 1 demerit per 10% of claims that are `confirmed` (rounded down), to a maximum reduction of 3 demerits.
   - Coverage: if claims reviewed < matrix row IDs cited in the candidate's draft-map, add 5 demerits.
2. Select the candidate with the lower demerit score as the winner. If tied, prefer candidate B (rewrite strategy) unless candidate B has any `rejected` claim and candidate A does not; in that case prefer candidate A.
3. Copy the winner's files to the canonical names:
   - Winner `draft-candidate-*.md` → `draft.md`
   - Winner `draft-map-candidate-*.json` → `draft-map.json`
   - Winner `review-candidate-*.json` → `review.json`
   - Winner `review-candidate-*.md` → `reviewed.md`
4. Write `selection-report.json` with `{winner, candidate_a_demerits, candidate_b_demerits, selection_reason}` — the harness appends the G4 result.
5. Write `.harness-step04sel-done` last. Do not write audit records and do not touch `run-state.json` — the harness runs G4, handles loop-back (re-dispatching 03 with your selection report as feedback) and loop-exhaustion escalation (punch-out E), and appends the step record to `audit/run-<run-id>.jsonl`.

# Output Specification
- `runs/<YYYY-QN>/draft.md` — selected report draft
- `runs/<YYYY-QN>/draft-map.json` → `../../schemas/draft-map.schema.json`
- `runs/<YYYY-QN>/review.json` → `../../schemas/review.schema.json`
- `runs/<YYYY-QN>/reviewed.md` — selected draft with accepted fixes applied
- `runs/<YYYY-QN>/selection-report.json` — selection rationale and scores
- `runs/<YYYY-QN>/dispatch-received-04b-select.json` — verbatim received dispatch
- `runs/<YYYY-QN>/.harness-step04sel-done` — written last

# Outbound Guardrail
The harness's G4 gate verifies zero `unresolved`/`rejected` claims in the selected `review.json`, `fix_diff` on every `fixed` claim, coverage against `draft-map.json`, and writes the `.g4-passed` sentinel before dispatching `05-tone-consistency`. G4 failure loops back to step 03 (max 2 iterations → punch-out E).

# Load-Bearing Check
≥90% of lines in #Instructions directly enforce an evaluable criterion (scoring, selection, file promotion, report completeness). No filler or decorative text is permitted.

# 04b-draft-selector Iteration Log

Evidence of prompt evolution following Red/Green/Refactor (EDD) discipline.

---

## Iteration 1 — Baseline

**Date:** 2026-10-01
**Change:** Initial prompt written for candidate selection: compares both
adversarial reviews, picks the stronger candidate (preference order —
fewest unresolved, then fix quality, then minimal-diff), emits `draft.md`,
`draft-map.json`, `review.json`, `reviewed.md`, `selection-report.json`.
**Baseline scores:** pending — evals scheduled for Phase 3 (promptfoo on
`claude-sonnet-5-5` + Copilot Studio Evaluate CSV).

---

## Iteration 2 — Harness contract; G4 made deterministic

**Date:** 2026-10-22
**Change made:**
- Adapted to the `s5-harness.py` contract: `drive` → execute named step →
  write outputs + `dispatch-received-04b-select.json` + done-marker.
- The G4 zero-unresolved-claims gate moved to deterministic harness code:
  `selection-report`/`review`/`draft-map` schema validation, zero
  `unresolved`/`rejected` verdicts, `fix_diff` presence on every `fixed`
  claim, and `draft.md`/`reviewed.md` existence — all checked before step 05
  is dispatched. `.g4-passed` sentinel written for the V2 continuity gate.
**Measured results:** pending Phase 3.

**Reasoning:** The selector still *resolves* claims during its work; the
harness now *verifies* the outcome deterministically — selection quality is
agent judgment, claim-resolution completeness is code.

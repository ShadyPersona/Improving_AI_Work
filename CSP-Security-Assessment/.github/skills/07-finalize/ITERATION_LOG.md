# Iteration Log — 07-finalize

## Iteration 1 (2026-11-03) — Split from combined 06

**Change:** Finalization was extracted from `06-adversarial-review`
(previously "Adversarial Review & Finalize") into a dedicated step 07,
matching the split tone-assessmentV2 shipped in its certified Stage-4
resubmission. 06 now emits only `g5-verdict.json` (pass) or
`g5-judgment.md` (fail); 07 owns deliverable assembly + `audit-report.md`.

**Why:** a reviewer that also packages its own pass is a weaker control —
a dedicated adversarial reviewer in its own context plus a separate
packager is the structure the Stage-5 "adversarial review in its own
context" criterion examines. It also produced V2's strongest evidence:
`step07-precondition-failure.md` showing the finalize agent refusing to
emit a deliverable on a non-certifiable run.

**Measured result:** structural change only at creation — the three-case
eval set (`evals/07-finalize.csv`) covers pass, certifiable=false stop,
and missing-verdict stop. First measured E2E pending first API run.

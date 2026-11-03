# 07-finalize Iteration Log (V2)

Evidence of prompt evolution following Red/Green/Refactor (EDD) discipline.

---

## Iteration 2 — Artifact Inlining + First Production Finalization

**Date:** 2026-11-03
**Problem:** The step-07 prompt referenced `toned.md`, `g5-verdict.json`, `run-state.json`, and audit artifacts by path; the executing agent has no filesystem access, so finalize inputs were not readable — a latent gap until an E2E run first reached step 07.
**Change:** `harness.py build_prompt` inlines `toned.md`, `tone-changes.json`, `run-state.json`, and `g5-verdict.json` into the step-07 prompt as `=== ARTIFACT ===` blocks.
**Eval status:** Suite unchanged: **5/5 pass** — `eval-m5K-2026-11-03T01:36:31`. First measured production execution on `2026-Q3-TEAMDAKS-E2ERun-Fireworks-DeepSeek-01`: emitted `Team-Daks-Cloud-Security-Assessment-2026-Q3.md` plus `audit-report.md` with explicit gate-precondition verification; harness recorded `finalized`, `certifiable: true`.

---

## Iteration 1 — Split from 06-adversarial-review

**Date:** 2026-10-27
**Problem:** The Stage 4 examiner found the pipeline thin — step 06 performed both adversarial review and finalization, giving the workflow only two LLM steps and blurring the reviewer's role. Finalization is a packaging job, not a review job.
**Change:** Created `07-finalize` as a dedicated third step. Step 06 now emits only `g5-verdict.json` (pass) or `g5-judgment.md` (fail); step 07 assembles the client deliverable and `audit-report.md` after the verdict exists and punch-outs have two-key closure. Added criteria: gate precondition check, packaging-only deliverable assembly, audit-report with explicit punchout-log closure citations, success reporting to the harness.
**Design decisions:**
- The deliverable is assembled verbatim from `toned.md` — no content edits; packaging only.
- `audit-report.md` must cite the specific `audit/punchout-log.md` rows (run_id, decision, resolved-by, resolved-at) used to verify closure, or state that no punch-outs triggered.
- The step emits nothing when preconditions fail — no deliverable, no done marker.
**Eval status:** `evals/promptfooconfig.yaml` created (F1–F5); first execution **5/5 pass** — `eval-m5K-2026-11-03T01:36:31` (Sonnet 5.5).

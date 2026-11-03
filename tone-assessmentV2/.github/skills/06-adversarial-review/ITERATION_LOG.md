# 06-adversarial-review Iteration Log (V2)

Evidence of prompt evolution following Red/Green/Refactor (EDD) discipline.

---

## Iteration 10 — Prior-Step Artifacts Inlined + First Measured Verdict

**Date:** 2026-11-03
**Problem:** The step-06 prompt referenced `toned.md`, `tone-changes.json`, `run-state.json`, and audit artifacts by path — but the executing agent has no filesystem access, so the review inputs were not actually readable. Earlier E2E attempts never reached step 06, so this gap was latent until the provider trail (Anthropic 504s → Haiku/Ollama gate failures) produced a valid step-05 output.
**Change:** `harness.py build_prompt` now inlines `toned.md`, `tone-changes.json`, and `run-state.json` into the step-06 prompt (and `g5-verdict.json` into step 07) as `=== ARTIFACT ===` blocks — same treatment as the schema inlining added for step 05.
**Design decisions:**
- A reviewer cannot adversarially review artifacts it cannot read; inline, don't reference.
- No `SKILL.md` change — the review criteria were already correct; this fixed prompt delivery.
**Eval status:** Suite unchanged: **11/11 pass** — `eval-ods-2026-11-03T01:35:22`. First measured production verdict on `2026-Q3-TEAMDAKS-E2ERun-Fireworks-DeepSeek-01`: `result: pass` on all seven checks including the new PHI/confidentiality and semantic substance-freeze lenses, with two documented non-failure observations (inherited `Q2026 3` formatting deviation; missing optional screenshots).

---

## Iteration 9 — Review-Only Split to `07-finalize` (Measured)

**Date:** 2026-10-27
**Problem:** The Stage 4 examiner found step 06 was both the adversarial reviewer and the finalizer ("pipeline is thin", Step Count 2 / Agent Count 2), and that the PHI/confidentiality exposure lens and semantic substance-freeze check were absent from the adversarial role.
**Change:** `SKILL.md` rewritten as a review-only agent: on pass it emits `g5-verdict.json` (structured verdict); on fail it emits `g5-judgment.md` — it never produces the client deliverable or `audit-report.md` (those moved to new step `07-finalize`). Added two new adversarial lenses: (a) **PHI / confidentiality** — flags any content a client should not see (internal annotations, identifiers tied to individuals, leaked context, verbatim `tone-changes.json` records); (b) **semantic substance freeze** — flags re-based/renormalized metrics, re-scoped findings, and re-interpreted severities that survive lexical token-preservation checks (motivated by the `2026-Q3-PunchOutETest` slip where 100% vs 98.48% passed token checks).
**Design decisions:**
- The deterministic G5 checks stay in `harness.py` post-step-05; this agent runs the independent adversarial judgment layer so the verdict does not rest on step 05's self-reports alone.
- Fail closed: if required inputs are missing, the agent emits `g5-judgment.md` (never auto-approves).
**Eval status:** Baseline before this change: **9/9 pass** (`eval-5cm-2026-10-21T03:52:22` on the pre-change suite). `evals/promptfooconfig.yaml` retargeted to the review-only contract and extended: E10 (semantic substance freeze: re-based metric), E11 (PHI/confidentiality exposure), E12 (evidence-based verdict only). After-result: **11/11 pass** — `eval-ods-2026-11-03T01:35:22` (Sonnet 5.5). Delta: 9/9 pre-change → 11/11 post-change with the new E10–E12 cases.

---

## Iteration 8 — Criterion Mapping + Regression Capture (Measured)

**Date:** 2026-10-27
**Problem:** The Stage 4 examiner counted only part of the instruction set as load-bearing; the log recorded zero measured before/after prompt-side iterations and omitted the `2026-Q3-PunchOutETest` G5 failures; stale "blocked until ANTHROPIC_API_KEY" lines persisted in iterations 1–5 even though the suite ran 2026-10-21.
**Change:** Every instruction unit in `SKILL.md` now carries a `[criterion: <name>]` tag (see Criterion mapping table; 100% of units mapped). Stale status lines corrected to reference the executed 2026-10-21 suite. Regressions recorded: `2026-Q3-PunchOutETest` G5 attempts 1 and 2 (substance freeze + change accountability, 2026-10-18), `run-20261018` audit reconstruction (`audit_integrity_note` provenance documented in `audit/AUDIT-INTEGRITY-NOTE.md`), and `2026-Q3-IRONTRAX` iteration-1 table-fragment failure.
**Eval status:** Baseline before this change: **9/9 pass** (`eval-5cm-2026-10-21T03:52:22`). After this change: suite is 11 cases; **11/11 pass** — `eval-ods-2026-11-03T01:35:22`.

---

## Iteration 7 — Sonnet 5.5 Migration + Eval Re-execution

**Date:** 2026-10-21
**Problem:** After the workflow migrated to `claude-sonnet-5-5`, the eval suite initially failed several cases. Diagnosis: Sonnet enforces G5 *more strictly* than Haiku — the E6 happy-path fixture's `toned.md` lacked the analytical depth (conclusion-first, significance, cross-signal synthesis) the G5 assessment-quality check demands, so the intended pass case correctly failed. Phrasing also differed (`G5 FAIL` vs `FAIL — G5`, etc.).
**Change:** No `SKILL.md` changes. E6 fixture `toned.md` enriched to carry genuine analytical facts; `run_id` added to the fixture and the run-id assertion folded into the rubric; regexes widened to case-insensitive `G5.*(?:FAIL|failure)|(?:FAIL|failure).*G5` shapes; E4 regex widened; the success-log expectation corrected (the harness — not the step — writes success-log).
**Design decisions:**
- The failures were fixture/assertion fidelity issues, not skill defects — Sonnet's stricter G5 enforcement is a *feature* confirmation of the gate.
**Eval status:** `promptfoo eval` executed 2026-10-21 on `anthropic:messages:claude-sonnet-5-5`. **9 passed / 0 failed / 0 errors** (`eval-5cm-2026-10-21T03:52:22`).

---

## Iteration 6 — Promptfoo Eval Execution on Haiku 4.5

**Date:** 2026-10-21
**Problem:** The 06 eval config shared the same execution problems as 05: no Devin provider, Windows command-line limit for `exec:` providers, and deprecated `temperature` issues. In addition, the success-case test fixture (E6) contained a `tone-changes.json` record that referenced a source sentence not present in `draft.md`, causing the G5 substance-freeze check to fail even on an intended pass case.
**Change:** Reused the shared custom promptfoo provider `.github/skills/promptfoo-anthropic-provider.js`. Updated the 06 config to use it for generation and the standard Anthropic provider for grading. Replaced exact-string `G5 failure` / `STOP` assertions with `regex` patterns that match Haiku 4.5's varied output phrasing. Corrected the E6 success-case inputs so `draft.md`, `toned.md`, and `tone-changes.json` are mutually consistent and demonstrate assessment-quality synthesis.
**Design decisions:**
- No changes to `SKILL.md`; the provider gives eval-only execution context and the fixtures are aligned with the skill's quality bar.
- Use regex assertions because Haiku 4.5 emits G5 results as `G5 FAIL`, `G5 FAILED`, `Result: FAIL`, `RUN NOT FINALIZED`, etc.
**Eval status:** `promptfoo eval` executed 2026-10-21. **9 passed / 0 failed / 0 errors** using `anthropic:messages:claude-haiku-4-5-20251001`.

---

## Iteration 5 — G5 Two-Key Certifiability Check

**Date:** 2026-10-21
**Problem:** Punch-out closure verified only `approved: true` in `run-state.json` — a self-granted flag would pass. The PunchOutATest-Bypass run exposed that approvals could be asserted without a logged human decision.
**Change:** G5 check 4 (punch-out closure) upgraded to a certifiability and two-key closure check: `approved: true` AND a matching `audit/punchout-log.md` row for the same `run_id` (decision, resolved by, resolved at). `certifiable: false` without closure evidence, recorded bypass attempts (permanent), and `tone-changes.json` marked `"certifiable": false` are all G5 hard fails. Success criterion now requires `certifiable: true`.
**Eval status:** Covered by E9 self-approval-rejection case; suite first executed 2026-10-21 — see Iterations 6–7 for measured results (9/9 on Haiku 4.5 and Sonnet 5.5).

## Iteration 4 — G5 Expanded to Review Table Cells

**Date:** 2026-10-21
**Problem:** Step 05 was updated to review tables, but G5 did not yet explicitly scan table cells or verify table edits in `tone-changes.json`.
**Change:** Updated G5 assessment-quality check to scan table captions, row labels, and narrative cells for banned patterns, vague temporal terms, and sentence discipline. Updated substance-freeze check to cover factual tokens inside tables. Updated change-accountability check to require `tables_reviewed` and `observations` arrays and to verify table edits row by row. A draft table missing from `tables_reviewed` is now a G5 failure.
**Design decisions:**
- Keeps 06 as the adversarial reviewer that independently challenges 05's table handling.
- Factual tokens inside tables remain protected by the substance freeze.
**Eval status:** Covered by E1–E7 and the E8 table-substance-freeze case (added in this iteration); suite first executed 2026-10-21 — see Iterations 6–7 for measured results (9/9 on Haiku 4.5 and Sonnet 5.5).

## Iteration 3 — G5 Client-Consultative Quality Check

**Date:** 2026-10-21
**Problem:** The client-consultative writing standard was added to step 05, but G5 did not yet explicitly evaluate whether the output read as consultant guidance rather than audit/Secure Score commentary.
**Change:** Updated the G5 assessment-quality check in `SKILL.md` to include a **client-consultative quality** clause: sections lead with supported conclusions, technical findings are interpreted for the client, Microsoft/CIS/NIST inputs are supporting rather than narrative voice, prose is concise consultative without defensive caveat-stacking, and every substantive domain answers what was assessed, what changed, why it matters, and what's next.
**Design decisions:**
- Preserved all existing G5 rigor (assessment depth, substance freeze, change accountability, punch-out closure).
- Added the new checks as an explicit subsection so the adversarial reviewer can cite them.
**Eval status:** Added E7 to `evals/promptfooconfig.yaml` to verify a G5 failure blocks delivery; suite first executed 2026-10-21 — see Iterations 6–7 for measured results (9/9 on Haiku 4.5 and Sonnet 5.5).

## Iteration 2 — Refactor 06 as Adversarial Review & Finalize

**Date:** 2026-10-21
**Problem:** Stage 4 certification expects adversarial review agents that independently challenge prior-step outputs. `06-finalize` was performing adversarial review implicitly through its inbound G5 checks, but the skill name and role did not make that explicit.
**Change:** Renamed skill to `06-adversarial-review`. Rewrote role to "Adversarial Review & Finalize agent." Split instructions into Phase 1 (G5 adversarial review) and Phase 2 (finalization on pass). Updated success criterion and output spec to require logging on both pass and fail. Updated orchestrator, `WORKFLOW.md`, `README.md`, `templates/run-state.json`, and evals.
**Design decisions:**
- Finalization is blocked until G5 passes and all triggered punch-outs are approved.
- Failure logs must still be written so the end-to-end success rate has an accurate denominator.
**Eval status:** Added E7 to `evals/promptfooconfig.yaml`; suite first executed 2026-10-21 — see Iterations 6–7 for measured results (9/9 on Haiku 4.5 and Sonnet 5.5).

## Iteration 1 — Align G5 with the Assessment-Synthesis Model

**Date:** 2026-10-14
**Change:** V2 fork. G5 assessment-quality check now scores `toned.md` against the professional and analytical standards defined in step 05 (conclusion-first elements, quarterly thesis, cross-signal synthesis, voice, tense, terminology, cadence, hedging, explanatory structures, banned patterns, language correctness and sensitivity) instead of prior-report conventions. Assessment-depth requirement kept: an unchanged or word-patched `toned.md` fails even with zero banned patterns. Inputs reduced to `toned.md`, `draft.md`, `template`, `tone-changes.json`, `run-state.json`, audit artifacts.
**Eval status:** Suite first executed 2026-10-21 — see Iterations 6–7 for measured results (9/9 on Haiku 4.5 and Sonnet 5.5).

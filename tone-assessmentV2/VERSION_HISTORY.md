# Version History — tone-assessmentV2

This document records the design lineage of the tone-assessment workflow for Stage 4 certification. It maps major versions to Git commits, iteration logs, and eval coverage.

---

## V1 — tone-assessment/

**Commit range:** `27fd016` → `5096a1e` → `62c76b5`

**Design:**
- Two-step workflow: `05-tone-consistency` → `06-finalize`.
- Four inputs: `draft.md`, `template`, `report-prev-quarter`, `report-2-quarters-ago`.
- Step 05 derived the target voice by reading two prior-quarter reports and matching their style.
- Guardrails: G4 input completeness, G5 tone/structure/fact check.
- Punch-outs: missing content (A) and loop exhaustion (E).

**Why archived:** The prior-report input model conflicted with the goal of producing a self-contained assessment. The agent sometimes retrieved the V1 skill while the V2 README governed, causing ambiguous instructions.

**Artifacts:** Archived in Git history; last V1 commit is `62c76b5`.

---

## V2 — tone-assessmentV2/

**Commit:** `bb8f307` (replace V1 with V2) → `2ed166d` (refactor 06 into adversarial review)

**Design:**
- Two-step workflow: `05-tone-consistency` → `06-adversarial-review`.
- Two inputs: `draft.md` (factual source) and `template` (structural authority).
- Step 05 is an **assessment synthesizer**: it converts telemetry/control data into conclusion-led, quarter-over-quarter security analysis while freezing every fact.
- Step 06 is an **adversarial reviewer + finalizer**: it independently challenges 05’s output via G5, then assembles the deliverable only on pass.
- Guardrails:
  - G4: input-completeness gate (before 05).
  - G5: assessment quality, substance freeze, change accountability, punch-out closure (between 05 and 06).
- Punch-outs:
  - A: missing content when the template requires a section the draft lacks.
  - E: loop exhaustion when G4 or G5 fails twice.

### V2 major changes

| Change | Date | Where documented |
|---|---|---|
| V2 fork: drop prior-quarter reports; apply professional standards directly | 2026-10-14 | `05-tone-consistency/ITERATION_LOG.md` Iteration 1 |
| Assessment-synthesis overhaul: seven-element checklist, quarterly thesis, cross-signal synthesis, extended `tone-changes.json` | 2026-10-15 | `05-tone-consistency/ITERATION_LOG.md` Iteration 2 |
| Security Awareness exemption | 2026-10-21 | `05-tone-consistency/ITERATION_LOG.md` Iteration 3 |
| Language correctness and sensitivity standards | 2026-10-21 | `05-tone-consistency/ITERATION_LOG.md` Iteration 4 |
| Sentence discipline and active framing | 2026-10-21 | `05-tone-consistency/ITERATION_LOG.md` Iteration 5 |
| Client-consultative writing standard | 2026-10-21 | `05-tone-consistency/ITERATION_LOG.md` Iteration 6 |
| Align G5 with assessment-synthesis model | 2026-10-14 | `06-adversarial-review/ITERATION_LOG.md` Iteration 1 |
| Refactor 06 as Adversarial Review & Finalize | 2026-10-21 | `06-adversarial-review/ITERATION_LOG.md` Iteration 2 |
| G5 client-consultative quality check | 2026-10-21 | `06-adversarial-review/ITERATION_LOG.md` Iteration 3 |
| Tables in scope for consultative review | 2026-10-21 | `05-tone-consistency/ITERATION_LOG.md` Iteration 7 |
| G5 expanded to review table cells | 2026-10-21 | `06-adversarial-review/ITERATION_LOG.md` Iteration 4 |
| Certifiability flag + two-key punch-out closure | 2026-10-21 | `05-tone-consistency/ITERATION_LOG.md` Iteration 8; `06-adversarial-review/ITERATION_LOG.md` Iteration 5 |
| Custom promptfoo provider + Haiku 4.5 eval execution | 2026-10-21 | `05-tone-consistency/ITERATION_LOG.md` Iteration 9; `06-adversarial-review/ITERATION_LOG.md` Iteration 6 |

### Eval coverage

| Skill | Eval file | Cases |
|---|---|---|
| 05-tone-consistency | `evals/promptfooconfig.yaml` | E1 G4 failure, E2 synthesis, E3 condition/evidence/implication, E4 substance freeze, E5 missing-content punch-out, E6 edit logging, E7 consultative rewrite, E8 table rewrite, E9 non-certifiable marking |
| 06-adversarial-review | `evals/promptfooconfig.yaml` | E1 assessment-quality failure, E2 substance-freeze failure, E3 change-accountability failure, E4 unapproved punch-out, E5 no depth, E6 success, E7 G5 blocks finalization, E8 table-cell meaning shift, E9 self-granted punch-out rejection |

**Eval execution status:** Executed 2026-10-21 with the custom provider `.github/skills/promptfoo-anthropic-provider.js`. **05-tone-consistency: 9/9 pass (`eval-odI-2026-10-21T03:39:47`, `claude-sonnet-5-5`). 06-adversarial-review: 9/9 pass (`eval-5cm-2026-10-21T03:52:22`, `claude-sonnet-5-5`).** Prior execution on `claude-haiku-4-5-20251001` the same date also passed 9/9 on both; the evals were re-run on Sonnet to match the production model. To reproduce, copy `evals/.env.example` to `evals/.env`, add `ANTHROPIC_API_KEY` and `ANTHROPIC_BASE_URL`, and run `promptfoo eval` in each skill's `evals/` directory.

---

## Stage 4 resubmission — the harness era (2026-10-21)

**Commit:** `2499cdf` (single-file orchestrator, per-run audit trail, Sonnet 5.5) plus subsequent harness revisions, current hash `3d1afdf5503b68ec784d09ac2d97a81b3808e7b80f2c34bf78f5576d3d4d0f7a` (`python harness.py hash`).

The first Stage 4 submission (`Danny-George-Stage4.zip`) failed on three infrastructure gaps: no executable harness, non-deterministic guardrails, and `null` per-step metering. The resubmission closes all three plus the incomplete punch-out bypass evidence:

| Change | Date | Where |
|---|---|---|
| `harness.py` — single stdlib-only orchestrator (`drive`, `run`, `verify`, `manifest`, `rebuild-logs`, `embed`, `hash`, `check-g4`, `check-g5`, `bypass-test`, `record-decision`); skill texts embedded, end-to-end execution without manual step invocation | 2026-10-21 | `harness.py` |
| G4/G5 guardrails implemented as deterministic code inside the harness — schema validation, banned-pattern regex, substance-freeze token diff, `.g4-passed`/`.harness-step05-done` sentinels — running at the gate edges before the step-06 judgment layer | 2026-10-21 | `harness.py`, `audit/guardrails-*.jsonl` |
| Per-run audit files (`run-<run-id>.jsonl`, `guardrails-<run-id>.jsonl`, `success-<run-id>.md`, `punchout-<run-id>.md`) + shared aggregates rebuilt by `rebuild-logs` | 2026-10-21 | `audit/` |
| Per-step metering populated — `tokens_in`/`tokens_out`/`cost_usd`/`metering_method` on every step record. Runtime exposes no usage API (verified by agent-side inspection: no `usage` objects, session logs, env vars, or commands); calibrated estimate `chars/1.75` (measured Sonnet ratios 1.57–1.82 chars/token on 05/06 workloads), `session_log_path` drop-in for real usage | 2026-10-21 | `harness.py (meter_step)`, `harness.config.json` |
| `bypass-test` — systematic punch-out bypass evidence (no-approval continuation + forged approval flag, both blocked while open; `skipped` once closed) | 2026-10-21 | `harness.py`, `audit/punchout-*.md` |
| `record-decision` — verbatim human punch-out closures written by the harness (agent never sets `approved:true` itself) | 2026-10-21 | `harness.py` |
| `--resume` re-runs G4 on the modified draft; E trigger rows written at all three loop_max paths; recorded bypass attempt marks run permanently `certifiable:false` | 2026-10-21 | `harness.py` |
| Terminal states: `done/finalized` or `done/non-finalizable` (closed punch-outs but permanently non-certifiable — no open decision remains) | 2026-10-21 | `harness.py`, `WORKFLOW.md` |
| `audit/success-report.md` — derived report splitting production runs (8/8 finalized) from deliberate gate-test runs (4/4 halted as designed) | 2026-10-21 | `rebuild_logs` |

**Gate-evidence runs:** `2026-Q3-PunchOutAETest` (punch-out A trigger + blocked bypass + human closure; E blocked bypass) and `2026-Q3-PunchOutETest-r2` (E trigger row at escalation, two blocked bypass paths, verbatim closure, resume→G4 re-check, `skipped` re-test, clean 05/06 pass, `non-finalizable` terminal state) together demonstrate every punch-out behavior. `PunchOutETest-r2`'s halt was a deliberately planted banned pattern caught by the deterministic D3 gate.

---

## Git tags

- `tone-assessment-v1` → `62c76b5`
- `tone-assessment-v2` → current `HEAD`

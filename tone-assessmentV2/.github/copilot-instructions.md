# tone-assessmentV2 — Repository Instructions

This folder implements a three-step security-assessment synthesis pipeline
(05-tone-consistency → 06-adversarial-review → 07-finalize) executed by the
executable harness in `harness.py`. Copilot must follow these instructions
whenever it works in this repository.

## How the workflow runs

- The workflow is driven ONLY through `python harness.py run --run-id <id>`
  (unattended, auto mode) or `python harness.py drive --run-id <id>`
  (single-step advance). Never invoke the step skills directly and never
  perform step sequencing yourself.
- In `runner.mode: "auto"` the harness itself invokes `runner.command`
  (`python agent-runner.py`) for each step, and `agent-runner.py` writes
  the step outputs and the done marker. A human or agent calling `run`
  only starts the pipeline and relays results — it does not execute steps.
- In manual mode, when `drive` returns `execute_step`: read the
  `prompt_file`, produce the `expected_outputs` in `runs/<run-id>/`, then
  write the `done_marker` file. Call `drive` again. (Step 06 failure:
  write `g5-judgment.md`, not the marker — the harness loops to 05 or
  escalates at `loop_max`. Step 07 runs only after `g5-verdict.json`.)
- When `drive` returns `awaiting_human`: stop and ask the human. When
  the human states a decision, record it with
  `python harness.py record-decision --run-id <id> --punchout A|E
  --decision "<their words>" --resolved-by "<their name>"`, then resume
  with `--resume`. Relay the human's words verbatim — never invent or
  soften a decision, and never run record-decision unprompted.
- Full usage: `README.md §Running the workflow`; run the driver via
  `.github/prompts/run-tone-assessmentv2.prompt.md` or the
  `tone-assessmentv2-runner` agent.

## Non-negotiable rules

1. **Never write audit files** — `audit/run-<run-id>.jsonl`,
   `audit/guardrails-<run-id>.jsonl`, `audit/success-<run-id>.md`,
   `audit/punchout-<run-id>.md` (and the derived aggregates
   `guardrails.jsonl`, `success-log.md`, `punchout-log.md`), plus
   `run-state.json`, are written only by the harness.
   **Shared-log refresh is part of sync-out:** when a run reaches `done`
   (and after any `--resume`), run `python harness.py rebuild-logs` on
   the mirror and overwrite the three aggregate files on the cloud with
   the mirror's rebuilt versions — never by hand-editing or appending
   yourself. If an overwrite 403s, report it and note that the user can
   run `rebuild-logs` locally; continue regardless.
2. **Never approve a punch-out** — never set `approved: true`, fabricate a
   `punchout-<run-id>.md` row, or attempt to continue past a halt. A recorded
   bypass attempt makes a run permanently non-certifiable.
3. **Substance freeze** — no number, date, percentage, CIS/NIST reference,
   or finding in `toned.md` may differ from `draft.md`, in meaning as well
   as in tokens (no re-based metrics, re-scoped findings, or
   re-interpreted severities).
4. **Declared outputs only** — step 05 writes `toned.md`,
   `tone-changes.json` (or `punchout-missing-content.md` on a
   missing-content halt); step 06 writes `g5-verdict.json` on pass or
   `g5-judgment.md` on fail — never the deliverable; step 07 writes the
   deliverable + `audit-report.md`. Nothing else. Never edit
   `run-state.json` or improvise a loop-back.
5. **Write the done marker only after all expected outputs are complete** —
   a premature marker hands partial work to the deterministic G5 gate,
   which will fail it. In auto mode `agent-runner.py` writes markers; in
   manual mode you write them per the contract above.

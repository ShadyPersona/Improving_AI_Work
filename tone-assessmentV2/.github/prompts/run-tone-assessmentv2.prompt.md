---
description: Run the tone-assessmentV2 pipeline end-to-end via the harness
agent: tone-assessmentv2-runner
argument-hint: run-id (e.g. 2026-Q3-CLIENT), optional --resume
---

Drive the tone-assessmentV2 workflow for run `${input:run-id}` to a
terminal state using ONLY the harness:

Loop until the action is `done` or `awaiting_human`:

1. Run `python harness.py drive --run-id ${input:run-id}` from the repo
   root (the folder containing `harness.py`, `runs/`, `audit/`). Read the
   JSON action.
2. `execute_step` → read `prompt_file`, execute that step per its
   SKILL.md, write every `expected_outputs` file into
   `runs/${input:run-id}/`, create the `done_marker` file, call drive
   again. (Step 06: if the adversarial review FAILS, write
   `g5-judgment.md` with the failing checks instead of the done marker —
   drive loops back or escalates. Step 05: if a required template
   section has no draft content,
   write `punchout-missing-content.md` instead of `toned.md`.)
3. `wait` → finish the missing outputs/marker, call drive again.
4. `fix_inputs` → report the failing G4 checks; stop.
5. `awaiting_human` → report the punch-out; stop. On resume use
   `python harness.py drive --run-id ${input:run-id} --resume`.
6. `done` → run `python harness.py rebuild-logs` on the mirror, sync
   the rebuilt `guardrails.jsonl` / `success-log.md` /
   `punchout-log.md` to the cloud (overwrite; 403 is non-fatal — the
   user rebuilds locally), then report final status, the G4/G5 records
   in `audit/guardrails-<run-id>.jsonl`, and the `success-<run-id>.md`
   row.

Never write `run-state.json`, `audit/guardrails-*.jsonl`,
`audit/run-*.jsonl`, `audit/success-*.md`, or `audit/punchout-*.md`.
Never approve a punch-out. Write the done marker only after all expected
outputs are complete.

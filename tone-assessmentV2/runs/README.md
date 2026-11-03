# runs/

One directory per workflow run, named by run ID, e.g. `runs/2026-Q3-IRONTRAX/`.
Run IDs are supplied by the user; they may include quarter, client, or test suffix.
All working artifacts live inside the run directory — never in the repo root.

```
runs/2026-Q3-IRONTRAX/
├── inputs/
│   ├── draft.md              # the ONE document being edited (input to step 05)
│   └── template.*            # optional override — default is ../CSA Template.docx
├── toned.md                  # step 05 output
├── tone-changes.json         # step 05 output → ../schemas/tone-changes.schema.json
├── g5-verdict.json           # step 06 output (pass) — OR
├── g5-judgment.md            # step 06 output (fail)
├── audit-report.md           # step 07 output (run summary)
├── <deliverable>.md          # step 07 output (final client deliverable)
├── run-state.json            # seeded from templates/, updated by the harness
├── .harness-stepNN-prompt.md # assembled prompt dispatched per step
└── .harness-stepNN-done      # done markers written by the runner, consumed by the harness
```

`tone-changes.json` must validate against `../schemas/tone-changes.schema.json` — the guardrails check this at the G5 handoff. The schema requires `tables_reviewed` and `observations` arrays in addition to `changes`, and `certifiable: false` marks outputs of non-certifiable runs.

`run-state.json` carries `certifiable` and `non_certifiable_reasons`: any punch-out trigger, loop_max exhaustion, or recorded bypass attempt flips it `false`; only a human decision logged in `../audit/punchout-log.md` can restore it.

Cross-run evidence (punch-outs, guardrail results, success log, per-step audit records) lives in `../audit/`, which accumulates across runs.

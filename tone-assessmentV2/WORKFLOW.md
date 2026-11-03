# Workflow Definition — Assessment Synthesis & Finalize Pipeline (V2)

A three-step sequential workflow that takes ONE report draft through
security-assessment synthesis — converting telemetry and control data into
conclusion-led quarter-over-quarter analysis under a strict substance
freeze (professional writing standards + an authoritative template) — an
independent adversarial review, and final delivery, with
one fail-closed deterministic guardrail on every handoff, human punch-out
gates, and a structured audit trail. Fully self-contained in this folder —
no paths, files, or skills outside `tone-assessmentV2/` are referenced.

## Pipeline

```
[inputs: draft.md + template]
        │
        ▼  G4 (input-completeness gate — deterministic, harness.py (g4_check))
05-tone-consistency ──G5──▶ 06-adversarial-review ──▶ 07-finalize → [deliverable]
        │        ▲           │                            │
        │        └─ deterministic pre-checks (harness.py (g5_check))
        └── missing-content ─────────┴── punch-out → human sign-off → resume
```

**Execution:** the workflow is executed by the harness
(`harness.py`, `python harness.py run --run-id <id>`) — executable code that
drives the `run-state.json` state machine, invokes each step through
`runner.command` (`python agent-runner.py` in `runner.mode: "auto"` — the
agent CLI that calls the configured model/agent endpoint), runs the
deterministic gate checks, and writes all audit records. The step-06
adversarial agent is the judgment layer on top of the deterministic G5
edge; step 07 performs packaging only, after the verdict passes.

## Inputs

`draft.md` is placed in `runs/<run-id>/inputs/` before the run starts.
The template defaults to the repo-root `CSA Template.docx`
(`default_template` in `harness.config.json`); `inputs/template.*` may
override it per run. Exactly ONE document is modified; the template is
read-only.

| # | Source | Role |
|---|--------|------|
| 1 | `inputs/draft.md` | The document being edited — the only file rewritten |
| 2 | `CSA Template.docx` (default) or `inputs/template.*` | AUTHORITATIVE for section order, headings, formatting, required elements; wins every conflict |
| 3 | `run-state.json` | Copied from `templates/` at run start; loop counters + punch-out flags |

## Step Contract

Each step MUST run its inbound guardrail check and append the result to
`audit/guardrails-<run-id>.jsonl` before doing any work. A failed gate halts the
workflow.

## Run Layout

- Working artifacts live in `runs/<run-id>/` (see `runs/README.md`).
- `templates/run-state.json` tracks `loop_counters` (G4/G5, max 2) and
  punch-out `approved` status.
- `tone-changes.json` MUST validate against `schemas/tone-changes.schema.json` —
  schema validation is what makes the guardrails deterministic.
- Cross-run evidence lives in `audit/` — authoritative records are
  per-run (`run-<run-id>.jsonl`, `guardrails-<run-id>.jsonl`,
  `success-<run-id>.md`, `punchout-<run-id>.md`); the shared files
  (`guardrails.jsonl`, `success-log.md`, `punchout-log.md`) are
  aggregate views regenerated via `python harness.py rebuild-logs`.

| Step | Skill | Consumes | Produces |
|------|-------|----------|----------|
| 05 | tone-consistency | `draft.md`, `template` | `toned.md`, `tone-changes.json` |
| 06 | adversarial-review | `toned.md`, `draft.md`, `template`, `tone-changes.json`, `run-state.json`, audit artifacts | `g5-verdict.json` (pass) or `g5-judgment.md` (fail) |
| 07 | finalize | `toned.md`, `g5-verdict.json`, `tone-changes.json`, `run-state.json`, audit artifacts | Final report, `audit-report.md` |

## Guardrails

Guardrails sit **between** workflow steps (and inbound on step 05) — they are
deterministic checks run before the next agent is allowed to proceed, not
review performed inside a step. All are automated and implemented as
executable code:

- **G4** is enforced by `harness.py (g4_check)`: file existence and
  readability, SHA-256 per input, run-state presence, template heading
  extraction. A pass writes `.g4-passed` (sentinel file with input hashes)
  which the G5 gate requires before step 06 may run.
- **G5** has two layers: `harness.py (g5_check)` runs
  fail-closed pre-checks before the adversarial agent — JSON-schema
  validation of `tone-changes.json`, banned-pattern/sentence regex over
  `toned.md` including table cells (`banned_patterns.txt`), a
  substance-freeze factual-token diff against `draft.md`,
  change-accountability checks (`facts_changed`, `tables_reviewed`
  coverage, analytical `assessment_function` coverage), and the two-key
  punch-out closure check — then step 06 performs the judgment-based
  adversarial review (assessment quality, substance freeze semantics,
  accountability) on top.

### G4 — inputs → tone (Input-Completeness Gate, enforced by step 05)
- Both input files exist and are readable; SHA-256 recorded per file.
- `run-state.json` present; template yields an extractable section/heading
  structure.
- Missing/unreadable input = hard fail, no `toned.md` produced.
- Failure → increment `loop_counters.G4`; at `loop_max` (2) escalate to
  human via punch-out E in `audit/punchout-<run-id>.md`.

### G5 — tone → adversarial-review (Adversarial Review Gate: Assessment Quality, Substance Freeze & Accountability, enforced by step 06)
- Assessment-quality check — did the rewrite produce real analysis:
  `toned.md` conforms to the template AND every substantive section is
  conclusion-first assessment (condition, quarter movement, evidence,
  significance, qualification, recommended response, calibration); domains with
  comparable evidence carry an explicit quarter-over-quarter thesis
  (preceding vs current condition, material movement, attribution,
  carried-in unresolved and newly material findings — post-quarter
  evidence never presented as reporting-quarter progress); related
  controls are synthesized into assessment themes before individual
  controls are discussed; professional and client-consultative standards
  met (voice, tense, terminology, cadence, hedging, banned patterns
  absent, spelling/grammar/punctuation correct, inclusive and neutral
  language, no sensitive geopolitical references); every sentence has a
  clear subject and verb and states one idea, including inside table
  narrative cells; semicolons connect only closely related clauses;
  evidence gaps are integrated as supporting context, not left as raw
  fragments; scope is stated in plain language; every substantive finding
  or risk is paired with a concrete client action; sections lead with
  supported conclusions rather than methodology or evidence limitations;
  technical findings are interpreted for the client rather than restated;
  concise consultative prose without defensive caveat-stacking; every
  substantive domain answers what was assessed, what changed, why it
  matters, and what's next; significance is tied to the client's business
  risk; movement claims are temporally anchored; positive findings are
  calibrated with their limitations; no noun stacks or product-vendor
  grammar remain; table captions, row labels, and narrative cells are
  reviewed for banned patterns, vague temporal terms, and sentence
  discipline; every draft table is accounted for in
  `tone-changes.json#tables_reviewed`. A data-first, unchanged, merely
  word-patched, or table-unreviewed draft fails even with zero banned
  patterns present.
- Substance freeze check (two layers): every number, date, percentage,
  measurement, finding title, CIS/NIST reference, classification outcome,
  piece of evidence, and recommendation in `toned.md` — including those
  inside tables — must exist in `draft.md` unchanged (token diff); and a
  semantic check verifies every entity/measurement/finding/recommendation
  in `draft.md` is present in `toned.md` with the same client-facing
  meaning (and vice versa) — a dropped finding, merged finding with
  shifted scope, re-based metric, or re-attributed cause fails even when
  every token matches. Re-written/re-scoped evidence, invented facts in
  narrative framing, shifted table-cell meaning, or meaning-shifting
  paraphrase fails.
- PHI/confidentiality-exposure check: `toned.md` must not carry PHI/PII,
  credentials or secrets, internal-only artifacts (harness internals,
  audit paths, agent prompts), or another client's tenant data — any
  exposure is a hard fail regardless of other results.
- Change accountability: every draft→toned edit recorded in
  `tone-changes.json` (schema-validated) with `reason`,
  `assessment_function`, and `facts_changed: false`; table edits verified
  row by row; every draft table listed in `tables_reviewed`; draft issues
  surfaced in `observations`. A change log with no analytical
  `assessment_function` coverage fails.
- Certifiability & punch-out closure (two-key): every `triggered: true`
  punch-out must have `approved: true` AND a `punchout-<run-id>.md` row for the
  same `run_id` (human decision, resolved by, resolved at). A flag without
  the log row is a self-granted approval. Any `certifiable: false` without
  closure evidence = hard fail — STOP for human sign-off.
- Step 06 acts as the adversarial reviewer of step 05 only — on pass it
  emits `g5-verdict.json`; the deliverable is assembled by step 07 after
  the verdict and closure checks pass.
- Failure → loop back to step 05 (max 2 iterations → human escalation).

## Punch-Out Points

Explicit human decision points where the workflow must stop for sign-off:

| ID | Trigger | Raised by | File | Human decision |
|----|---------|-----------|------|----------------|
| A | template requires a section/element `draft.md` has no content for | step 05 | `audit/punchout-missing-content.md` | provide content / drop section / defer |
| E | G4 or G5 loop exhaustion (max 2) | G4/G5 | `audit/punchout-<run-id>.md` | human resolves stalled input/tone directly |

A punch-out halt is a manual "punch to human" — distinct from an automated
guardrail failure, which fails the workflow without human involvement.

**Certifiability:** `run-state.json` carries `certifiable` and
`non_certifiable_reasons`. The flag flips `false` when any punch-out
triggers, when G4 or G5 reaches `loop_max`, or when any bypass attempt
occurs. A recorded bypass attempt makes `certifiable: false` permanent.
Other `false` states restore only through a recorded human decision in
`audit/punchout-<run-id>.md` (matching `run_id`, decision, resolved by,
resolved at) cited as `closure_evidence` — never by the agent alone.
Approvals never carry across `run_id`s. Outputs produced while
non-certifiable are marked `"certifiable": false` in `tone-changes.json`
and no deliverable may be emitted.

**Bypass testing (required evidence):** after each punch-out fires, someone
must attempt to continue the workflow without approval and confirm the gate
blocks them. `harness.py (bypass_test)` performs this systematically
(`python harness.py bypass-test --run-id <id> --punchout A|E`): it attempts
(a) continuation with no approval and (b) a forged `approved: true` flag
with no log row, confirms both are blocked by the two-key check, records
the attempt and result in `audit/punchout-<run-id>.md` (see `bypass test
performed` / `bypass result` columns), and marks the run permanently
non-certifiable. Punch-out points never tested do NOT qualify.

## Audit Trail

`audit/run-<run-id>.jsonl` — one record per step:

```json
{"step": "05-tone-consistency", "model": "...", "input_hashes": {...}, "output_hashes": {...},
 "tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0, "metering_method": "session_log|estimated-*",
 "environment": "...", "operator": "...", "initiated_by": "harness|manual",
 "guardrail_inbound": {"id": "G4", "result": "pass"}}
```

Each record identifies the step, model, input/output content hashes, token
counts, and cost — any failure traces to its exact origin step, with
per-step model/token/cost coverage across the whole pipeline. Metrics are
written by `harness.py (meter_step)`: real usage parsed from a configured agent
session log (`metering.session_log_path`), or a labeled local estimate —
`metering_method` records which source produced the numbers; fields are
never `null`.

## End-to-End Success Metric

A run succeeds iff:
1. G5 passes (assessment quality, substance freeze, change accountability,
   punch-out closure),
2. every triggered punch-out is resolved with a recorded human decision,
3. the final report is emitted,
4. the run is certifiable (`certifiable: true`; all `non_certifiable_reasons`
   resolved by recorded human decisions), and
5. the run result is appended to `audit/success-<run-id>.md` and step records to
   `audit/run-<run-id>.jsonl`.

Per-run result appended to `audit/success-<run-id>.md`:

```
| date | run id | result | punch-outs | iterations | notes |
```

`result` is one of: `pass` (all five success conditions met), `fail`
(guardrail or step failure before loop exhaustion), `halted` (punch-out or
loop_max escalation — awaiting human decision), `stopped` (human-directed
stop). No other values are written.

`run-state.json` `status` reaches a terminal state of `finalized` or
`non-finalizable` (all punch-outs closed but `certifiable` permanently
false — e.g. a recorded bypass attempt; no human decision remains).
Intermediate states: `in-progress`, `needs-g4`, `needs-step05`,
`needs-step06`, `needs-step07`, `awaiting-human`, `escalated`, `stopped`,
`failed`.

`audit/success-report.md` is a derived summary (`rebuild-logs`) that
splits production runs from gate-test runs (run-ids containing `Test`,
where `halted` is the expected pass state) and computes the rates.

Success rate = successful runs / total runs, measured across the full
workflow start to finish and tracked quarter over quarter to show stability
or improvement.

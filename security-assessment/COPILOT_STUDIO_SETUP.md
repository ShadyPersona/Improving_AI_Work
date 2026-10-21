# Copilot Studio Setup & Wiring Guide

This guide explains how to build and wire the 9-agent Stage 5 security
assessment system inside **Copilot Studio**, using the **SharePoint connector**
for file I/O and the **Evaluate** tab for per-agent testing.

## Prerequisites

- [ ] A Copilot Studio environment where you can create agents.
- [ ] A SharePoint site/document library where the run artifacts will live.
- [ ] Permission for Copilot Studio to read/write that SharePoint library.
- [ ] The contents of `security-assessment/security-assessment/` uploaded or
  synced to the SharePoint library.

## Step 1 — Prepare the SharePoint run workspace

Create a document library and folder structure that matches the repo layout:

```
security-assessment/
├── .github/
│   ├── skills/               # source-of-truth SKILL.md files
│   ├── security-assessment-orchestrator.agent.md
│   └── copilot-studio/agent-definitions/
├── schemas/
├── templates/
│   └── run-state.json
├── runs/
│   └── <YYYY-QN>/            # created per quarter
│       ├── inputs/
│       │   ├── prior-report.docx
│       │   ├── history-report.docx
│       │   ├── defender-export-folder/
│       │   ├── cis.pdf
│       │   └── nist.pdf
│       └── run-state.json    # copied from templates/run-state.json
└── audit/
    ├── guardrails.jsonl      # append-only
    ├── punchout-*.md         # created when triggered
    ├── success-log.md        # append-only
    └── run-YYYYMMDD.jsonl    # append-only
```

> **Tip:** Keep the repo folder read-only for humans except for `runs/` and
> `audit/`. Sub-agents only need write access to the current run folder and
> `audit/`.

## Step 2 — Create the agents

Create one Copilot Studio agent per row below. For each agent, copy the
content of the linked `SKILL.md` into its **system instructions / prompt**.

| # | Agent name in Copilot Studio | Source prompt | Notes |
|---|---|---|---|
| 1 | `Security Assessment Orchestrator` | `.github/security-assessment-orchestrator.agent.md` | Top-level entry point; has no tools except the ability to call `00-coordinator` |
| 2 | `00-coordinator` | `.github/skills/00-coordinator/SKILL.md` | Dispatch-only; no tools |
| 3 | `01-ingest` | `.github/skills/01-ingest/SKILL.md` | Add SharePoint connector read action |
| 4 | `02-findings-matrix` | `.github/skills/02-findings-matrix/SKILL.md` | Add SharePoint connector read/write actions |
| 5 | `03-draft-update` | `.github/skills/03-draft-update/SKILL.md` | Add SharePoint connector read/write actions; accepts `candidate_id` and `strategy` parameters |
| 6 | `04-adversarial-review-candidate-a` | `.github/skills/04-adversarial-review-candidate-a/SKILL.md` | Add SharePoint connector read/write actions |
| 7 | `04-adversarial-review-candidate-b` | `.github/skills/04-adversarial-review-candidate-b/SKILL.md` | Add SharePoint connector read/write actions; must be a **different agent** from candidate-a |
| 8 | `04b-draft-selector` | `.github/skills/04b-draft-selector/SKILL.md` | Add SharePoint connector read/write actions |
| 9 | `05-tone-consistency` | `.github/skills/05-tone-consistency/SKILL.md` | Copied unchanged from `tone-assessmentV2`; SharePoint connector read/write |
| 10 | `06-adversarial-review` | `.github/skills/06-adversarial-review/SKILL.md` | Copied unchanged from `tone-assessmentV2`; SharePoint connector read/write |

> **Important:** Do not combine `04-adversarial-review-candidate-a` and
> `04-adversarial-review-candidate-b` into one agent. They must be separate so
> each candidate is reviewed in its own isolated context.

### Agent configuration checklist (per agent)

- [ ] Name matches the table above.
- [ ] System prompt is copied from the linked `SKILL.md` file.
- [ ] The SharePoint connector is added.
- [ ] The agent can read files from the current run folder (`runs/<YYYY-QN>/`).
- [ ] The agent can read files from `schemas/` and `audit/`.
- [ ] The agent can write files to the current run folder and `audit/`.
- [ ] The agent does **not** have web browsing or other unrelated tools unless
  the skill explicitly requires them. (Each sub-agent DOES need the code
  sandbox — it runs `python s5-harness.py` locally.)

## Step 3 — Add the SharePoint connector

For every agent except `00-coordinator`:

1. Open the agent in Copilot Studio.
2. Go to **Actions** → **Add action**.
3. Search for **SharePoint** and add the connector.
4. Configure at least these actions:
   - **Get file content** (read a file by path/URL)
   - **Get file metadata** (check existence)
   - **Create file** / **Update file** (write outputs)
   - **List folder** (list files in the Defender export folder)
5. Set the connection to the SharePoint site/document library.

> **Scope:** Each agent only needs access to the single document library. Do not
> give agents access to the entire tenant.

## Step 4 — Wire the orchestrator to the coordinator

1. Open the **Security Assessment Orchestrator** agent.
2. Under **Actions**, add the `00-coordinator` agent as a connected agent —
   this is the orchestrator's **only** connected agent.
3. The orchestrator is a thin relay (system prompt:
   `.github/security-assessment-orchestrator.agent.md`):
   - Receive the run ID from the user.
   - Feed each `python s5-harness.py drive --run-id <id>` action to
     `00-coordinator` verbatim.
   - Relay the coordinator's dispatch/halt result back to the user.
   - On HALT/`awaiting-human`, present the punch-out file and wait — the
     human records the decision via `record-decision` inside a sub-agent's
     sandbox.
4. The orchestrator has **no SharePoint connector and no tools** — it can
   never do real work, which is what makes it counterfeit-proof.

## Step 5 — Wire the coordinator to every sub-agent

1. Open the `00-coordinator` agent.
2. Under **Actions**, add each sub-agent as a connected agent:
   - `01-ingest`
   - `02-findings-matrix`
   - `03-draft-update`
   - `04-adversarial-review-candidate-a`
   - `04-adversarial-review-candidate-b`
   - `04b-draft-selector`
   - `05-tone-consistency`
   - `06-adversarial-review`
3. Ensure the coordinator has **no SharePoint actions and no other tools** —
   connected-agent dispatch verbs only.
4. The coordinator's job: receive the harness's `execute_step` action (which
   carries `dispatch.agent` + `dispatch.inputs`), invoke exactly that agent,
   and return its result. It never decides sequencing itself — the harness
   FSM does, and every emitted dispatch is verified against it.

## Step 6 — Sub-agent wiring table

Use this table to configure each sub-agent's expected inputs and outputs.

| Agent | Inputs it reads from SharePoint | Outputs it writes to SharePoint | Parameters |
|---|---|---|---|
| `01-ingest` | `runs/<run>/inputs/*` | `runs/<run>/inventory.json`, `evidence-index.json`, `style-profile.json` | `run_id` |
| `02-findings-matrix` | `runs/<run>/inventory.json`, `evidence-index.json`, `style-profile.json`, `inputs/*` | `runs/<run>/matrix.json`, `audit/punchout-*.md`, `audit/guardrails.jsonl`, `audit/run-*.jsonl` | `run_id` |
| `03-draft-update` | `runs/<run>/matrix.json`, `inputs/prior-report.docx`, `run-state.json`, `audit/punchout-*.md` | `runs/<run>/draft-candidate-{id}.md`, `draft-map-candidate-{id}.json`, `audit/*` | `run_id`, `candidate_id`, `strategy` |
| `04-adversarial-review-candidate-a` | `runs/<run>/draft-candidate-a.md`, `draft-map-candidate-a.json`, `matrix.json`, `inputs/defender-export-folder`, `inputs/prior-report.docx` | `runs/<run>/review-candidate-a.json`, `review-candidate-a.md`, `audit/*` | `run_id` |
| `04-adversarial-review-candidate-b` | `runs/<run>/draft-candidate-b.md`, `draft-map-candidate-b.json`, `matrix.json`, `inputs/defender-export-folder`, `inputs/prior-report.docx` | `runs/<run>/review-candidate-b.json`, `review-candidate-b.md`, `audit/*` | `run_id` |
| `04b-draft-selector` | `runs/<run>/review-candidate-*.json`, `review-candidate-*.md`, `draft-candidate-*.md`, `draft-map-candidate-*.json`, `matrix.json`, `run-state.json` | `runs/<run>/draft.md`, `draft-map.json`, `review.json`, `reviewed.md`, `selection-report.json`, `audit/*` | `run_id` |
| `05-tone-consistency` | `runs/<run>/draft.md`, `inputs/prior-report.docx`, `run-state.json` | `runs/<run>/toned.md`, `tone-changes.json`, `audit/*` | `run_id` |
| `06-adversarial-review` | `runs/<run>/toned.md`, `draft.md`, `inputs/prior-report.docx`, `run-state.json`, `tone-changes.json` | `runs/<run>/final-report.md`, `audit-report.md`, updated `audit/success-log.md`, `audit/*` | `run_id` |

> Every agent also reads `schemas/*.schema.json` for validation.

## Step 7 — Runtime sequence (harness-driven)

When a user says *"Run 2026-Q4"*:

1. **Orchestrator** receives `run_id = 2026-Q4` and relays the first
   `drive` to `00-coordinator`.
2. The **dispatched sub-agent** (starting with `01-ingest`) runs, in its
   sandbox:
   ```
   python s5-harness.py drive --run-id 2026-Q4
   ```
   The harness returns an `execute_step` action naming the step, writes the
   prompt file, and blocks until the agent writes outputs +
   `dispatch-received-<step>.json` + `.harness-step<NN>-done`.
3. Each subsequent `drive` call runs the inbound gate, verifies the
   recorded dispatch, meters the step, and emits the next dispatch.
4. Repeat until the harness returns `ACTION: DONE` (`finalized` or
   `non-finalizable`) or `awaiting-human`.

### Handling HALT / awaiting-human

On an open punch-out the harness returns `awaiting-human` and writes the
punch-out file. The human reviews it, then records the decision inside a
sub-agent's sandbox:

```
python s5-harness.py record-decision --run-id <id> --punchout <A-F> `
    --decision "<verbatim>" --resolved-by "<name>"
python s5-harness.py drive --run-id <id> --resume
```

`--resume` re-runs the gate where the run halted (`halted_at_gate`), so the
run picks up exactly where it stopped. Agents never set `approved: true` —
the two-key rule is enforced by the harness.

### Handling loop-back

When a gate fails under `loop_max` the harness re-dispatches the producing
step automatically (loop counters live in `run-state.json`); at
`loop_max` it triggers punch-out E instead of looping forever.

## Step 8 — Import the evaluation CSVs

1. In Copilot Studio, go to the **Evaluate** tab for the agent you are testing.
2. Click **Import** and choose the matching CSV from `evals/`:
   - `00-coordinator.csv`
   - `01-ingest.csv`
   - `02-findings-matrix.csv`
   - `03-draft-update.csv`
   - `04-adversarial-review-candidate-a.csv`
   - `04-adversarial-review-candidate-b.csv`
   - `04b-draft-selector.csv`
   - `05-tone-consistency.csv`
   - `06-adversarial-review.csv`
3. Map the columns:
   - `inputs` → input text (or as a parameter)
   - `expected_outputs` → expected response text
   - `expected_guardrail_result` → pass/fail check
4. Run the evaluation and iterate on the agent prompt until it passes.

> **Tip:** Start with `00-coordinator`, `01-ingest`, and `02-findings-matrix`
> before testing the candidate-selection loop.

## Step 9 — End-to-end dry run

Use an existing run from `tone-assessmentV2` (e.g., `2026-Q3-IRONTRAX`) as a test
input set:

1. Copy the inputs into `runs/2026-Q4-TEST/inputs/`.
2. Copy `templates/run-state.json` to `runs/2026-Q4-TEST/run-state.json`.
3. Start the orchestrator with `run_id = 2026-Q4-TEST`.
4. Step through the agents until `ACTION: DONE`.
5. Inspect `runs/2026-Q4-TEST/audit-report.md` and `audit/success-log.md`.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `dispatch-verification` gate fails | Coordinator invoked the wrong agent, or the agent didn't record `dispatch-received-<step>.json` verbatim | Check `audit/run-<id>.jsonl` `dispatch_expected` vs `dispatch_emitted` |
| Sub-agent can't find file | SharePoint path mismatch | Use the exact paths from the wiring table + `tool_manifest.allowed_paths` |
| Candidate reviews look identical | Same agent used for A and B | Verify they are separate agent definitions with separate prompts and manifests |
| Step not dispatched after outputs written | Missing `.harness-step<NN>-done` marker | Marker must be written last, after all outputs |
| `awaiting-human` won't clear | Punch-out lacks a recorded decision | Use `record-decision` — agents cannot set `approved: true` |
| 05/06 fail on punch-outs | `F_missing_content` or `E_loop_exhaustion` missing from run-state | Use the merged `templates/run-state.json` |

## Checklist before first real run

- [ ] All 9 agents created in Copilot Studio.
- [ ] Each agent's system prompt matches its `SKILL.md`.
- [ ] Orchestrator has no tools; its only connected agent is `00-coordinator`.
- [ ] Coordinator has no tools or connectors; only connected-agent calls to
  the eight sub-agents.
- [ ] SharePoint connector added to all sub-agents, scoped per
  `tool_manifest` (`allowed_paths`/`disallowed_paths`).
- [ ] Each sub-agent can run `python s5-harness.py` in its sandbox.
- [ ] `s5-harness.py`, `s5-harness.config.json`, `schemas/`, `templates/`,
  and `s5-harness.sha256` are in the SharePoint library the agents mirror.
- [ ] `run-state.json` merged template copied into the run folder.
- [ ] Per-agent evaluations (Studio Evaluate CSV + promptfoo) imported and
  passing.
- [ ] Mis-dispatch smoke test: a wrong-agent `dispatch-received` is
  rejected by the next `drive` call.
- [ ] End-to-end dry run completes; `audit/run-<id>.jsonl` has a metered
  record per invocation and `guardrails-<id>.jsonl` one G1–G5 record per
  gate.

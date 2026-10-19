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
- [ ] The agent does **not** have web browsing, code execution, or other
  unrelated tools unless the skill explicitly requires them.

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
2. Under **Actions**, add the `00-coordinator` agent as a connected agent.
3. In the orchestrator's system prompt, instruct it:
   - Receive the run ID from the user.
- Read the current `run-state.json` summary (via SharePoint or pass it as
  context).
- Invoke `00-coordinator` with the run-state summary.
- Parse the coordinator's output.
- If `ACTION: DISPATCH`, invoke the named agent with the listed inputs.
- If `ACTION: HALT`, stop and ask the human to resolve the punch-out.
- If `ACTION: DONE`, summarize the result and stop.

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
3. Ensure the coordinator has **no SharePoint actions** and **no other tools**.
4. The coordinator's only output should be a text block telling the orchestrator
   which agent to call next.

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

## Step 7 — Orchestrator runtime sequence

When a user says *"Run 2026-Q4"*:

1. **Orchestrator** receives `run_id = 2026-Q4`.
2. **Orchestrator** invokes `00-coordinator` with the current `run-state.json` summary.
3. **Coordinator** returns:
   ```
   ACTION: DISPATCH
   AGENT: 01-ingest
   INPUTS: runs/2026-Q4/inputs/prior-report.docx; ...
   ```
4. **Orchestrator** invokes `01-ingest` with those inputs.
5. `01-ingest` writes outputs and updates `run-state.json.current_step` to `02-findings-matrix`.
6. **Orchestrator** re-invokes `00-coordinator`.
7. Repeat until coordinator returns `ACTION: DONE` or `ACTION: HALT`.

### Handling HALT

If the coordinator returns:

```
ACTION: HALT
REASON: Punch-out <ID> is triggered and awaiting human approval.
```

The orchestrator stops, tells the user which punch-out file to review, and waits
for the user to confirm the file is updated and `run-state.json` is approved.
Then it re-invokes the coordinator.

### Handling loop-back

If the draft-selector fails G4 and `loop_counters.G4 < loop_max`, it sets
`current_step` back to `03-draft-update`. The coordinator will dispatch
`03-draft-update` again. The agent should use the existing `selection-report.json`
as feedback to improve the next candidate.

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
| Coordinator returns wrong agent | `current_step` not passed correctly | Ensure orchestrator feeds the full run-state summary to the coordinator |
| Sub-agent can't find file | SharePoint path mismatch | Use the exact paths from the wiring table |
| Candidate reviews look identical | Same agent used for A and B | Verify they are separate agent definitions with separate prompts |
| Draft-selector never loops back | `loop_counters.G4` not incremented | Check that the selector writes the updated run-state back to SharePoint |
| 05/06 fail on punch-outs | `A_missing_content` or `E_loop_exhaustion` not in run-state | Use the merged `templates/run-state.json` |

## Checklist before first real run

- [ ] All 9 agents created in Copilot Studio.
- [ ] Each agent's system prompt matches its `SKILL.md`.
- [ ] Orchestrator has no direct tools; only connected-agent actions.
- [ ] Coordinator has no tools or connectors; only connected-agent actions.
- [ ] SharePoint connector added to all sub-agents.
- [ ] SharePoint paths tested for read and write.
- [ ] `run-state.json` merged template copied into the run folder.
- [ ] Per-agent CSV evaluations imported and passing.
- [ ] End-to-end dry run completes without unapproved punch-outs.
- [ ] `audit/guardrails.jsonl` shows one G1–G5 record per executed step.

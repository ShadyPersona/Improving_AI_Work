# Security Assessment Workflow — Stage 5

Multi-agent pipeline that updates a client's quarterly Microsoft 365 security
assessment from Defender exports, then passes the best candidate draft through
the Stage 4 `tone-assessmentV2` synthesis agents to produce the final client
deliverable.

**Output:** an updated quarterly assessment report with professional
security-assessment tone, under a substance freeze, with a fail-closed guardrail
on every handoff, human punch-out gates, adversarial candidate selection, and a
full audit trail.

Start here: [`WORKFLOW.md`](./WORKFLOW.md)

## Inputs (5 per run)

| # | Source | Role |
|---|---|---|
| 1 | Previous quarter's report | Baseline document to update (format + content) |
| 2 | Report from two quarters ago | Historical context & update methodology |
| 3 | Defender export folder | Authoritative current-quarter security state |
| 4 | CIS M365 Foundations Benchmark PDF | Framework reference validation |
| 5 | NIST CSF 2.0 (CSWP.29) PDF | Framework reference validation |

## Layout

```
security-assessment/
├── WORKFLOW.md          # pipeline definition, step contract, guardrails G1–G5, punch-outs
├── README.md            # this file
├── VERSION_HISTORY.md   # design lineage and Stage 5 migration
├── .github/
│   ├── skills/          # source-of-truth prompts for every agent
│   │   ├── 00-coordinator
│   │   ├── 01-ingest
│   │   ├── 02-findings-matrix
│   │   ├── 03-draft-update          # parameterized: candidate_id + strategy
│   │   ├── 04-adversarial-review-candidate-a
│   │   ├── 04-adversarial-review-candidate-b
│   │   ├── 04b-draft-selector
│   │   ├── 05-tone-consistency      # copied unchanged from tone-assessmentV2
│   │   └── 06-adversarial-review    # copied unchanged from tone-assessmentV2
│   ├── security-assessment-orchestrator.agent.md  # Copilot Studio orchestrator manifest
│   └── copilot-studio/
│       └── agent-definitions/       # exported agent definitions (one per agent)
├── schemas/             # JSON Schemas every artifact must validate against
├── templates/           # run-state.json seed — copy into each new run dir
├── runs/                # one directory per quarterly run (see runs/README.md)
└── audit/               # cross-run evidence: punch-outs, guardrails.jsonl, success-log, run-*.jsonl
```

## Runtime architecture (Copilot Studio)

This workflow is implemented as a set of connected agents in **Copilot Studio**.

| Agent | Purpose | Isolation |
|---|---|---|
| `00-coordinator` | Dispatch-only: decides the next agent and its inputs | No file or content tools |
| `01-ingest` | Parse and validate the 5 inputs | Scoped to ingest |
| `02-findings-matrix` | Build the findings matrix | Scoped to findings matrix |
| `03-draft-update` | Generate one candidate draft (called twice: `minimal` and `rewrite`) | Scoped to draft update |
| `04-adversarial-review-candidate-a` | Review candidate A | **Isolated adversarial context** |
| `04-adversarial-review-candidate-b` | Review candidate B | **Isolated adversarial context** |
| `04b-draft-selector` | Compare reviews, select best candidate, run G4 | Scoped to selection |
| `05-tone-consistency` | Assessment synthesis + G4 input check | Copied from tone-assessmentV2 |
| `06-adversarial-review` | G5 adversarial review + final deliverable | Copied from tone-assessmentV2 |

The orchestrator agent (`.github/security-assessment-orchestrator.agent.md`) has
no direct tools; it invokes `00-coordinator`, which returns the next agent to
call.

## Running a quarter

1. Create a SharePoint document library (or folder) for the run.
2. Create `runs/<YYYY-QN>/` and copy `templates/run-state.json` into it.
3. Place the 5 inputs in `runs/<YYYY-QN>/inputs/`.
4. Open the Copilot Studio **Security Assessment Orchestrator** agent and provide
the run ID.
5. The orchestrator invokes `00-coordinator`, which reads the run-state summary
and returns the next agent to invoke.
6. Invoke that agent. It reads/writes files via the **SharePoint connector**.
7. Repeat steps 5–6 until the coordinator returns `ACTION: DONE` or `ACTION: HALT`.
8. If HALT, resolve the punch-out file in `audit/`, update `run-state.json`, and
resume from step 5.

## Candidate selection flow

```
matrix.json
    │
    ├──► 03-draft-update (candidate_id=a, strategy=minimal) ──► draft-candidate-a.md
    │
    └──► 03-draft-update (candidate_id=b, strategy=rewrite) ──► draft-candidate-b.md
            │
            ├──► 04-adversarial-review-candidate-a ──► review-candidate-a.json
            │
            └──► 04-adversarial-review-candidate-b ──► review-candidate-b.json
                    │
                    ▼
            04b-draft-selector
                    │
                    ▼
            draft.md + review.json + selection-report.json
                    │
                    ▼
            05-tone-consistency ──► toned.md + tone-changes.json
                    │
                    ▼
            06-adversarial-review ──► final report + audit-report.md
```

## Punch-out legend

| ID | Triggered when | Human decides |
|---|---|---|
| A | findings can't be validated by current data | still-present / removed / defer |
| B | CIS/NIST reference mappings changed | approve each change |
| C | findings classified `regressed` | confirm evidence supports it |
| D | report sections added/removed | approve/reject each change |
| E | G4 or G5 loop exhausted (2 iterations) | resolve directly |

## Evaluations (Copilot Studio Evaluate tab)

Evaluations are run inside Copilot Studio using the **Evaluate** tab with CSV
datasets. Promptfoo is not used.

Each agent has its own CSV test set. Example columns:

```csv
run_id,agent_name,strategy,inputs,expected_outputs,expected_guardrail_result
```

See `evals/` for sample CSVs (to be created per implementation phase).

## Artifact ↔ schema map

| Artifact | Schema | Produced by | Checked by |
|---|---|---|---|
| `inventory.json` | `schemas/inventory.schema.json` | 01 | G1 |
| `evidence-index.json` | `schemas/evidence-index.schema.json` | 01 | G1 |
| `style-profile.json` | `schemas/style-profile.schema.json` | 01 | G1 |
| `matrix.json` | `schemas/matrix.schema.json` | 02 | G2 |
| `draft-candidate-a.md` / `draft-candidate-b.md` | (markdown) | 03 | G3 |
| `draft-map-candidate-a.json` / `draft-map-candidate-b.json` | `schemas/draft-map.schema.json` | 03 | G3 |
| `review-candidate-a.json` / `review-candidate-b.json` | `schemas/review.schema.json` | 04a / 04b | 04b-selector |
| `selection-report.json` | (new schema to be added) | 04b-selector | — |
| `draft.md` | (markdown) | 04b-selector | G4 |
| `draft-map.json` | `schemas/draft-map.schema.json` | 04b-selector | G4 |
| `review.json` | `schemas/review.schema.json` | 04b-selector | G4 |
| `toned.md` | (markdown) | 05 | G5 |
| `tone-changes.json` | `schemas/tone-changes.schema.json` | 05 | G5 |

## Stage 5 certification map

| Stage 5 artifact | Where it lives |
|---|---|
| Dispatch-only coordinator | `.github/skills/00-coordinator/SKILL.md` + `.github/security-assessment-orchestrator.agent.md` |
| Sub-agents scoped to one workflow | `.github/skills/01-06*/SKILL.md` each define a narrow scope |
| Adversarial review in own context | `04-adversarial-review-candidate-a`, `04-adversarial-review-candidate-b`, and `06-adversarial-review` are separate agents |
| Version-controlled repository | All SKILL.md files + schemas + orchestrator manifest + exported agent definitions |
| Stage 4 continuity | Unchanged `05-tone-consistency` and `06-adversarial-review` from `tone-assessmentV2`; existing G1–G5 guardrails and audit formats preserved |

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
Copilot Studio setup: [`COPILOT_STUDIO_SETUP.md`](./COPILOT_STUDIO_SETUP.md)

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
├── COPILOT_STUDIO_SETUP.md  # how to build and wire the agents in Copilot Studio
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

## How the system works

This is a **human-supervised, multi-agent pipeline** built in **Copilot Studio**.
The human retrieves the Defender exports and places all five inputs in a
SharePoint run folder. After that, the system executes a fixed sequence of
specialized agents. Each agent has a narrow job, runs an inbound guardrail before
doing work, and appends a structured record to the audit trail.

The key design choice is **candidate selection**: instead of producing one draft
and hoping it passes review, the pipeline produces **two drafts** — one minimal
update and one deeper rewrite — reviews each in isolation, then selects the
stronger candidate before tone-assessment synthesis.

### The 9 agents

| Agent | Job | Why it is separate |
|---|---|---|
| `00-coordinator` | Decides which agent runs next | Must not do real work or access files; only dispatch |
| `01-ingest` | Validate and index the 5 inputs | Scoped to ingestion only |
| `02-findings-matrix` | Build the quarter-over-quarter matrix | Scoped to matrix construction |
| `03-draft-update` | Produce **one** candidate draft | Called twice with different parameters; still scoped to drafting |
| `04-adversarial-review-candidate-a` | Break candidate A against evidence | **Isolated adversarial context** |
| `04-adversarial-review-candidate-b` | Break candidate B against evidence | **Isolated adversarial context** |
| `04b-draft-selector` | Compare reviews, pick winner, run G4 | Scoped to selection only |
| `05-tone-consistency` | Assessment synthesis + G4 input check | Copied unchanged from `tone-assessmentV2` |
| `06-adversarial-review` | G5 review + final deliverable assembly | Copied unchanged from `tone-assessmentV2` |

## Data flow

```
Human places inputs in SharePoint:
  runs/<YYYY-QN>/inputs/
    ├── prior-report.docx
    ├── history-report.docx
    ├── defender-export-folder/
    ├── cis.pdf
    └── nist.pdf

Run starts with templates/run-state.json copied to
  runs/<YYYY-QN>/run-state.json

Step 01 — Ingest
  Inputs:  the 5 inputs above
  Outputs: runs/<YYYY-QN>/inventory.json
           runs/<YYYY-QN>/evidence-index.json
           runs/<YYYY-QN>/style-profile.json

Step 02 — Findings Matrix
  Inputs:  ingest outputs + inputs
  Outputs: runs/<YYYY-QN>/matrix.json
           (may trigger punch-outs A or C)

Step 03 — Draft Update (runs twice)
  Call A:  candidate_id=a, strategy=minimal
  Call B:  candidate_id=b, strategy=rewrite
  Inputs:  matrix.json + prior-report.docx + approved punch-outs + run-state.json
  Outputs: runs/<YYYY-QN>/draft-candidate-a.md  + draft-map-candidate-a.json
           runs/<YYYY-QN>/draft-candidate-b.md  + draft-map-candidate-b.json

Step 04a — Adversarial Review Candidate A
  Inputs:  draft-candidate-a.md + draft-map-candidate-a.json + matrix.json + exports
  Outputs: runs/<YYYY-QN>/review-candidate-a.json + review-candidate-a.md
           (may trigger punch-outs B or D)

Step 04b — Adversarial Review Candidate B
  Inputs:  draft-candidate-b.md + draft-map-candidate-b.json + matrix.json + exports
  Outputs: runs/<YYYY-QN>/review-candidate-b.json + review-candidate-b.md
           (may trigger punch-outs B or D)

Step 04b — Draft Selector
  Inputs:  both reviews + both drafts/maps + matrix.json + run-state.json
  Outputs: runs/<YYYY-QN>/draft.md
           runs/<YYYY-QN>/draft-map.json
           runs/<YYYY-QN>/review.json
           runs/<YYYY-QN>/reviewed.md
           runs/<YYYY-QN>/selection-report.json
  Gate:    G4 zero-unresolved-claims check

Step 05 — Tone Consistency
  Inputs:  draft.md + prior-report.docx (as template) + run-state.json
  Outputs: runs/<YYYY-QN>/toned.md
           runs/<YYYY-QN>/tone-changes.json

Step 06 — Adversarial Review Final
  Inputs:  toned.md + draft.md + prior-report.docx + run-state.json + tone-changes.json
  Outputs: final client deliverable
           runs/<YYYY-QN>/audit-report.md
           updated audit/success-log.md
```

## How context is kept separate

Stage 5 requires adversarial review to happen in its own context — the reviewer
must not see the producing agent's reasoning or conversation history.

In this design, separation is enforced by architecture, not by prompt text alone:

1. **Each agent is a separate Copilot Studio agent.** The platform starts a fresh
   conversation/context for every invocation.
2. **The coordinator passes only explicit inputs.** It never forwards a previous
   agent's full conversation or reasoning.
3. **Adversarial agents have no access to the drafter's prompt.** They receive
   only the candidate draft, its draft-map, the matrix, and the Defender exports.
4. **Candidate A and candidate B are reviewed by different agent definitions.**
   Even if Copilot Studio reuses some runtime infrastructure, the two reviewer
   prompts are distinct agents, so candidate B's review cannot leak into
   candidate A's context.
5. **The final `06-adversarial-review` is also separate from `05-tone-consistency`.**
   It reviews `toned.md`, not its own output.

This satisfies the Stage 5 requirement: a dedicated adversarial agent reviews
each output in its own context window.

## Why 9 agents instead of 7

A 7-agent design would merge candidate-A review, candidate-B review, and the
selector into one step. That would break Stage 5:

- If the same adversarial agent reviewed both candidates, the second review
  could inherit context from the first.
- The selector is a different job — comparing two adversarial outputs and
  making a deterministic choice — and must be auditable in its own right.

Using 9 agents keeps adversarial contexts isolated and makes every step
independently evaluable.

## Runtime architecture (Copilot Studio)

The orchestrator agent (`.github/security-assessment-orchestrator.agent.md`) has
**no direct tools**. It invokes `00-coordinator`, which returns the next agent to
call. The orchestrator then dispatches that agent. All file access happens inside
sub-agents via the **SharePoint connector**.

```
User asks: "Run 2026-Q4"
        │
        ▼
Security Assessment Orchestrator
        │
        ▼
00-coordinator  ──►  returns next agent name + inputs
        │
        ▼
[sub-agent]  reads/writes SharePoint
        │
        ▼
(repeat until DONE or HALT)
```

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

See `COPILOT_STUDIO_SETUP.md` for the exact agent-creation and wiring steps.

## Candidate selection flow (compact view)

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
            04b-draft-selector ──► draft.md + review.json + selection-report.json
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

Each agent has its own CSV test set in `evals/`. Example columns:

```csv
run_id,agent_name,strategy,inputs,expected_outputs,expected_guardrail_result
```

Import the relevant CSV for the agent you are testing, map the columns, and run
the evaluation.

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
| `selection-report.json` | `schemas/selection-report.schema.json` | 04b-selector | — |
| `draft.md` | (markdown) | 04b-selector | G4 |
| `draft-map.json` | `schemas/draft-map.schema.json` | 04b-selector | G4 |
| `review.json` | `schemas/review.schema.json` | 04b-selector | G4 |
| `toned.md` | (markdown) | 05 | G5 |
| `tone-changes.json` | `schemas/tone-changes.schema.json` | 05 | G5 |

## Stage 5 certification map

| Stage 5 artifact | Where it lives |
|---|---|
| Dispatch-only coordinator | `.github/skills/00-coordinator/SKILL.md` + `.github/security-assessment-orchestrator.agent.md` |
| Sub-agents scoped to one workflow | `.github/skills/*/SKILL.md` each define a narrow scope |
| Adversarial review in own context | `04-adversarial-review-candidate-a`, `04-adversarial-review-candidate-b`, and `06-adversarial-review` are separate agents |
| Version-controlled repository | All `SKILL.md` files + schemas + orchestrator manifest + exported agent definitions |
| Stage 4 continuity | Unchanged `05-tone-consistency` and `06-adversarial-review` from `tone-assessmentV2`; existing G1–G5 guardrails and audit formats preserved |
| No CLI shells for runtime inference | Runtime is Copilot Studio; coordinator has no shell/terminal tools |

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
Operator setup: [`DEPARTMENT-SETUP.md`](./DEPARTMENT-SETUP.md)  
Azure provisioning: [`AZURE-SETUP.md`](./AZURE-SETUP.md)

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
├── s5-harness.py        # executable orchestrator: FSM, deterministic G1–G5 gates,
│                        # dispatch verification, metering, punch-out state machine,
│                        # bypass-test, record-decision, audit writes
├── s5-harness.config.json  # metering, model registry, per-step expected outputs
├── s5-harness.sha256    # SHA-256 of s5-harness.py (regenerate: s5-harness.py hash)
├── checksums.sha256     # hash-verified inputs (extend to S5 files)
├── templates/           # run-state.json template + prompt template
├── WORKFLOW.md          # pipeline definition, step contract, gates G1–G5, punch-outs
├── README.md            # this file
├── VERSION_HISTORY.md   # design lineage and Stage 5 migration
├── s5-harness.py        # FSM, deterministic gates G1–G5, metering, punch-outs
├── agent-runner.py      # per-step executor: one subprocess = one API call
├── .github/
│   ├── skills/          # source-of-truth prompts for every agent
│   │   ├── 00-coordinator
│   │   ├── 01-ingest
│   │   ├── 02-findings-matrix
│   │   ├── 03-draft-update          # parameterized: candidate_id + strategy
│   │   ├── 04-adversarial-review-candidate-a
│   │   ├── 04-adversarial-review-candidate-b
│   │   ├── 04b-draft-selector
│   │   ├── 05-tone-consistency      # copied from tone-assessmentV2
│   │   ├── 06-adversarial-review    # G5 judgment layer → g5-verdict.json
│   │   └── 07-finalize              # deliverable + audit-report.md
├── schemas/             # JSON Schemas every artifact must validate against
├── templates/           # run-state.json seed — copy into each new run dir
├── runs/                # one directory per quarterly run (see runs/README.md)
└── audit/               # cross-run evidence: punch-outs, guardrails.jsonl, success-log, run-*.jsonl
```

## How the system works

This is a **human-supervised, multi-agent pipeline** executed by
`s5-harness.py` plus `agent-runner.py`. The human places all five inputs in
`runs/<run-id>/inputs/`. After that, the harness executes a fixed sequence of
specialized agent steps — each step is one isolated model invocation
(Azure OpenAI by default). Each agent has a narrow job, the harness runs an
inbound deterministic guardrail before dispatching it, and the harness appends
a structured record to the audit trail for every step and gate.

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

1. **Each step is a separate API invocation.** Every agent runs as a fresh
   `agent-runner.py` call — a brand-new context window with no message
   history from any prior step.
2. **The coordinator passes only explicit inputs.** The harness inlines
   only the declared input artifacts into each step prompt — never a
   previous step's reasoning or conversation.
3. **Adversarial agents have no access to the drafter's prompt.** They receive
   only the candidate draft, its draft-map, the matrix, and the Defender exports.
4. **Candidate A and candidate B are reviewed by different agent definitions.**
   Distinct skill prompts (`04-...-a`, `04-...-b`) and distinct invocations —
   candidate B's review cannot leak into candidate A's context.
5. **The final `06-adversarial-review` is also separate from `05-tone-consistency`.**
   It reviews `toned.md`, not its own output — and `07-finalize` is a third
   context that only packages, never reviews.

This satisfies the Stage 5 requirement: a dedicated adversarial agent reviews
each output in its own context window.

## Provider history — why the runner is provider-agnostic

The original design targeted Copilot Studio: an orchestrator agent relaying
to a dispatch-only coordinator calling connected sub-agents. Phased testing
(`COPILOT_STUDIO_SETUP.md` era, evidence in `runs/setup-*` and audit logs)
proved Copilot Studio agents have no execution surface — they cannot write
run artifacts, produce byte-exact `dispatch-received` receipts, or accept a
prompt and return deterministic outputs. Agent flows and workflows were
evaluated and rejected for the same reason plus a 100-second tool-response
limit that cannot carry a 30K-token synthesis step.

The pivot copied tone-assessmentV2's proven pattern: the harness is the
coordinator; `agent-runner.py` executes each step as one isolated API call.
The department standard is **Azure OpenAI with Microsoft Entra ID auth** —
all prompts and completions (Defender exports, client reports) stay inside
the org's Microsoft tenant; Azure's data-privacy terms mean no model
training on customer data and no access by OpenAI or other customers.
Other providers (Fireworks, Anthropic, Ollama) remain available for
non-client testing via `AGENT_PROVIDER`.

## Why 9 agents instead of 7

A 7-agent design would merge candidate-A review, candidate-B review, and the
selector into one step. That would break Stage 5:

- If the same adversarial agent reviewed both candidates, the second review
  could inherit context from the first.
- The selector is a different job — comparing two adversarial outputs and
  making a deterministic choice — and must be auditable in its own right.

Using 9 agents keeps adversarial contexts isolated and makes every step
independently evaluable.

## Runtime architecture (harness + API runner)

`s5-harness.py` is the dispatch-only coordinator AND the sequencing truth:
its FSM decides transitions, emits the `dispatch.agent` for each step, runs
the deterministic gates, meters every invocation, and writes every audit
record. It has no inference of its own — dispatch verbs only.
`agent-runner.py` is the per-step executor: one subprocess call = one
isolated model invocation that returns the step's outputs as a JSON file
map, which the runner writes into the run directory.

```
Operator: python s5-harness.py run --run-id 2026-Q4
        │
        ▼
s5-harness.py  ──►  FSM emits execute_step {step, dispatch.agent, prompt_file}
        │
        ▼
agent-runner.py (subprocess — runner.command)
   sends inlined prompt+inputs to Azure OpenAI (Entra ID auth)
   writes returned file map: outputs + dispatch-received + done-marker
        │
        ▼
harness consumes outputs → deterministic gate → next dispatch
(repeat until finalized, non-finalizable, or awaiting-human)
```

**Dispatch verification:** the invoked agent records the dispatch it received
verbatim in `dispatch-received-<step>.json`; the next `drive` call compares it
against the FSM's expected dispatch. A wrong dispatch is a logged gate failure
and the wrongly-named agent's outputs are refused — so "dispatch-only
coordinator" is enforced in code, not just prompt text.

## Running a quarter

1. Configure the runner (see `DEPARTMENT-SETUP.md`): `AGENT_PROVIDER=azure`,
   `AGENT_BASE_URL=<deployment chat-completions URL>`, `HARNESS_MODEL=<deployment>`,
   plus Entra auth (`az login` or service-principal env vars).
2. Create `runs/<YYYY-QN>/inputs/` and place the 5 inputs in it (`prior-report`,
   `history-report`, `defender-export-folder/`, `cis`, `nist` — text formats:
   `.md`/`.txt`/`.csv`/`.json`; convert `.docx`/`.pdf` to text first).
3. `python s5-harness.py run --run-id <id>` — the harness drives every step
   through `agent-runner.py` and the gates until `finalized`,
   `non-finalizable`, or `awaiting_human`.
4. On `awaiting_human`: a human reviews the punch-out file, then records the
   decision — `python s5-harness.py record-decision --run-id <id>
   --punchout <letter> --decision "<verbatim>" --resolved-by "<name>"` — and
   resumes with `python s5-harness.py run --run-id <id>` (or `drive --resume`
   for a single advance). Agents never approve punch-outs.

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
| A | findings can't be validated by current data (G2) | still-present / removed / defer |
| B | CIS/NIST reference mappings changed (G3) | approve each change |
| C | findings classified `regressed` (G2) | confirm evidence supports it |
| D | report sections added/removed (G3) | approve/reject each change |
| E | any gate hits loop_max (2) | resolve directly |
| F | template section has no draft content (G4→05) | provide content / drop / defer |

Closures require `record-decision` (decision text + resolver name — the
two-key rule). `bypass-test` proves neither attack path (continue without
approval, forge `approved: true`) can advance the pipeline; a recorded
bypass permanently marks the run `non-finalizable`.

## Evaluations

Each agent has a CSV test set in `evals/` (columns: `run_id, agent_name,
inputs, expected_outputs, expected_guardrail_result, expected_punchouts`).
These were authored for Copilot Studio's Evaluate tab and are retained as
the declared per-step eval evidence; the Copilot Studio runner that
executed them no longer exists, so conversion to promptfoo (the pattern
used by the certified Stage-4 evals in `tone-assessmentV2/`) is a tracked
follow-up.

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
| Custom harness | `s5-harness.py` — FSM, deterministic gates, metering, punch-outs |
| Dispatch-only coordinator | `.github/skills/00-coordinator/SKILL.md` (dispatch verbs only) + FSM-verified dispatches in `audit/run-<id>.jsonl` (`dispatch_expected` vs `dispatch_emitted`) |
| Sub-agents scoped to one workflow | `.github/skills/*/SKILL.md` + `manifest.yaml` `agents[]` scoping (each step only receives its declared inputs inlined) |
| Adversarial review in own context | `04-...-a`, `04-...-b`, `06` are separate agent definitions and separate API invocations — a fresh context per call; A's reviewer never receives B's artifacts |
| Version-controlled repository | Repo `ShadyPersona/Improving_AI_Work` (private): skills, schemas, manifests, harness, audit trail |
| Stage 4 continuity | `05`/`06` are the Stage-4 skill texts; V2 G4b/G5 gates embedded in s5-harness; certified V2 harness (`3d1afdf5`) untouched |
| Audit trail | `audit/run-<id>.jsonl` (per-invocation model/tokens/cost + dispatch fields), `guardrails-<id>.jsonl`, `punchout-<id>.md`, `success-<id>.md` |
| No CLI shells for runtime inference | `agent-runner.py` subprocess dispatches real model calls to Azure OpenAI (Entra ID); inference is a genuine model invocation, not a shell shim — the harness owns only dispatch/audit |

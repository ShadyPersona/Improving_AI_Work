# tone-assessmentV2

Self-contained two-step workflow that performs **security-assessment
synthesis** on ONE report draft (`draft.md`) — converting telemetry and
control data into conclusion-led quarter-over-quarter analysis — under a
strict substance freeze, then assembles the final deliverable.
**No dependencies outside this folder.**

V2 differs from `tone-assessment/`: the agent is a security-assessment
synthesizer applying professional analytical + writing standards directly —
no prior-quarter reports are required as inputs, and success is measured by
assessment quality (conclusion-led analysis, quarterly thesis, cross-signal
synthesis) and client-consultative usefulness, not polished language alone.

## Layout

```
tone-assessmentV2/
├── README.md                  ← this file (guide to the artifacts)
├── WORKFLOW.md                ← workflow definition (pipeline, guardrails, punch-outs, success metric)
├── .github/skills/
│   ├── 05-tone-consistency/
│   │   ├── SKILL.md           ← step 05 agent prompt (enforces inbound G4)
│   │   ├── ITERATION_LOG.md   ← eval-driven prompt evolution (EDD evidence)
│   │   └── evals/promptfooconfig.yaml
│   ├── 06-adversarial-review/
│   │   ├── SKILL.md           ← step 06 agent prompt (G5 adversarial review + finalize on pass)
│   │   ├── ITERATION_LOG.md
│   │   └── evals/promptfooconfig.yaml
│   └── tone-assessmentv2-orchestrator/
│       └── SKILL.md           ← single-file orchestrator for agent use (combines 05 + 06 + workflow)
├── schemas/
│   └── tone-changes.schema.json   (step 05 output contract, checked at G5)
├── harness.py                 ← executable workflow harness — ONE self-contained
│                                stdlib-only file: pipeline state machine, deterministic
│                                G4/G5 validators (schema+banned patterns embedded),
│                                per-step metering, bypass-test mode. No pip needed.
├── harness.sha256             ← copy-integrity checksum (`python harness.py hash`)
├── harness.config.json        ← optional overrides (model, price table, loop_max)
├── templates/run-state.json   ← loop counters + punch-out flags + certifiable status
├── runs/README.md             ← per-run directory layout (run-id named, 2 inputs)
└── audit/                     ← cross-run evidence (append-only)
    ├── run-<run-id>.jsonl         (per-run step records: model, hashes, tokens, cost)
    ├── guardrails-<run-id>.jsonl  (per-run gate records)
    ├── success-<run-id>.md        (per-run result row)
    ├── punchout-<run-id>.md       (per-run halts, bypass tests, human decisions)
    ├── guardrails.jsonl           (aggregate view — regenerate: python harness.py rebuild-logs)
    ├── punchout-log.md            (aggregate view)
    ├── punchout-missing-content.md
    └── success-log.md             (aggregate view: end-to-end results + success rate)
```

## Inputs per run

1. `runs/<run-id>/inputs/draft.md` — the document being edited (the only file modified; required per run)
2. `template` — authoritative for structure/formatting; wins conflicts. Defaults to the repo-root **`CSA Template.md`** (text extract of `CSA Template.docx`; `default_template` in `harness.config.json`); place `inputs/template.*` in a run only to override it for that run.

## Stage 4 artifact map

| Required artifact | Where it lives |
|-------------------|----------------|
| Workflow definition | `WORKFLOW.md` + `harness.py` — the harness is executable orchestration code that runs the pipeline end-to-end: `python harness.py run --run-id <id>` |
| Guardrails | `WORKFLOW.md` §Guardrails; deterministic code in `harness.py` (G4 file/hash/template checks + `.g4-passed` sentinel; G5 schema, banned-pattern, substance-freeze, accountability, and two-key punch-out checks) runs at the gate edges before the step-06 adversarial agent |
| Punch-out evidence | `audit/punchout-<run-id>.md` + `audit/punchout-missing-content.md` — human decision points with bypass-test columns; `run-state.json` blocks unapproved punch-outs; `python harness.py bypass-test` performs and logs systematic bypass attempts |
| End-to-end success rate | `audit/success-<run-id>.md` rows aggregated into `audit/success-log.md` — full-workflow result per run + cumulative rate; standardized result values: `pass` / `fail` / `halted` / `stopped` |
| Audit trail | `audit/guardrails-<run-id>.jsonl` + `audit/run-<run-id>.jsonl` — per-step model, hashes, tokens, cost; failure traceable to origin step. Metering comes from the harness (`harness.py (meter_step)`): a configured agent session log when available, otherwise a local estimate labeled via `metering_method` — never null. |

## Running the workflow

The harness executes the pipeline end-to-end. It is a single
stdlib-only file — copy `harness.py` anywhere the folder structure
(`runs/`, `audit/`, `templates/`, `.github/skills/`) exists, verify with
`python harness.py hash` against `harness.sha256`, and run:

```powershell
# no dependencies — runs on a bare Python 3.10+ install

# 1. place draft.* in runs/<run-id>/inputs/  (template defaults to ./CSA Template.md)
# 2. agent-runtime mode: the executing agent calls drive repeatedly;
#    each call returns the next action — no manual step invocation:
python harness.py drive --run-id <run-id>
#    (or, foreground mode: python harness.py run --run-id <run-id>)
# 3. if a punch-out halts the run, record the human decision in
#    audit/punchout-<run-id>.md + run-state.json, then:
python harness.py drive --run-id <run-id> --resume
```

The harness owns orchestration, gate sequencing, and logging; the agent
executes each step against the run directory. Configure the agent runner
(`manual` or `command` mode) in `harness.config.json`.

### Regenerating embedded artifacts

The SKILL.md files and `CSA Template.md` are *sources of truth* — the
copies inside `harness.py` are generated. After editing:

```powershell
python harness.py embed          # after editing a .github/skills/*/SKILL.md
python harness.py template-md    # after editing CSA Template.docx
python harness.py hash > harness.sha256          # refresh copy-integrity hash
# refresh checksums.sha256 for any changed verified file (currently CSA Template.md)
```

## Stage 4 certification guide

For an examiner reviewing this workflow, the evidence lives in:

| Stage 4 artifact | File to inspect |
|---|---|
| Workflow definition | `WORKFLOW.md` |
| Adversarial review agent | `.github/skills/06-adversarial-review/SKILL.md` Phase 1 |
| Guardrail logs | `audit/guardrails-*.jsonl` (per-run; aggregate: `audit/guardrails.jsonl`) |
| Punch-out evidence | `audit/punchout-*.md` + `audit/punchout-log.md` (aggregate) |
| End-to-end success rate | `audit/success-*.md` + `audit/success-log.md` (aggregate) |
| Per-step audit trail | `audit/run-*.jsonl` |
| Prompt evolution / EDD | `.github/skills/05-tone-consistency/ITERATION_LOG.md`, `.github/skills/06-adversarial-review/ITERATION_LOG.md` |
| Version lineage | `VERSION_HISTORY.md` + Git tags `tone-assessment-v1` and `tone-assessment-v2` |

**Note:** Promptfoo evals and real Copilot runs require populated API keys. The evals were executed 2026-10-21 (9/9 pass on both skills); real Copilot run records are in `audit/` and `runs/`.

## Evals

Each skill ships a Promptfoo config under `evals/`. The configs use a custom
provider (`.github/skills/promptfoo-anthropic-provider.js`) that loads the full
`SKILL.md`, injects the test inputs, and calls the Anthropic Messages API
through the proxy configured via `ANTHROPIC_BASE_URL` and `ANTHROPIC_API_KEY`.

Run from the skill's `evals/` directory after copying `.env.example` to `.env`
and filling in the key/base URL:

```powershell
cd .github/skills/05-tone-consistency/evals
promptfoo eval

cd .github/skills/06-adversarial-review/evals
promptfoo eval
```

**Latest results (2026-10-21, `claude-haiku-4-5-20251001`):**

| Skill | Pass / Fail / Error |
|---|---|
| 05-tone-consistency | **9 / 0 / 0** |
| 06-adversarial-review | **9 / 0 / 0** |

Record the summary in the corresponding `ITERATION_LOG.md`.


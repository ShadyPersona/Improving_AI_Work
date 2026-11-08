# Workflow Definition — Quarterly Security Assessment Update (Stage 5)

Converts the monolithic "update quarterly security assessment" skill into a
sequential multi-agent pipeline driven by `s5-harness.py` — a single-file,
stdlib-only executable orchestrator that owns sequencing, deterministic
G1–G5 gates, the punch-out state machine, metering, and every audit write.
The final tone-assessment synthesis reuses the Stage 4 `tone-assessmentV2`
step agents (`05-tone-consistency`, `06-adversarial-review`) — Stage 4
continuity preserved verbatim.

## Execution model

```
[user] → orchestrator agent (thin entry; zero tools — relays actions only)
            │
   00-coordinator (dispatch verbs ONLY — invokes the named sub-agent)
            │
   s5-harness.py drive — deterministic FSM: names the next step, writes the
            │  prompt file, runs the inbound gate, records metering/audit
            ▼
   sub-agents 01–07 — each a separate API invocation via agent-runner.py
   in its own fresh context; executes only the named step, writes outputs
   + dispatch-received-<step>.json + done-marker
```

The **harness owns all sequencing truth**. The coordinator receives the
harness's dispatch action (`execute_step` + `dispatch.agent`) and invokes
exactly that agent — the invoked agent records the dispatch it received
verbatim, and the harness validates it against the FSM. A wrong dispatch is
a logged gate failure and the wrongly-named agent's outputs are rejected.
This makes "dispatch-only coordinator" demonstrable, not asserted.

## Pipeline

```
[inputs]
   │
   ▼
01-ingest ──G1──▶ 02-findings-matrix ──G2──▶ 03-draft-update (candidate A, minimal)
                                                 │
                                                 ▼
                                   03-draft-update (candidate B, rewrite)
                                                 │
                                                 ▼
                                   04-adversarial-review-candidate-a ──G3a──▶
                                                 │
                                                 ▼
                                   04-adversarial-review-candidate-b ──G3b──▶ 04b-draft-selector
                                                                                 │
                                                                                 ▼
                                                                   G4 ──▶ 05-tone-consistency ──G5──▶ 06-adversarial-review → [deliverable]
   │
   ▼
[human punch-out resolution when needed — record-decision + drive --resume]
```

## Inputs

| # | Source | Path under `runs/<run-id>/inputs/` |
|---|---|---|
| 1 | Previous quarter's report (baseline) | `prior-report.*` |
| 2 | Report from two quarters ago (history) | `history-report.*` |
| 3 | Current-quarter Defender export folder | `defender-export-folder/` |
| 4 | CIS Microsoft 365 Foundations Benchmark | `cis.*` |
| 5 | NIST CSF 2.0 reference | `nist.*` |

The agent reduces .docx/.pdf inputs to markdown text before the first
`drive` call (conversion is an agent step, not harness code).

## Step Contract

Each sub-agent: (1) writes `dispatch-received-<step>.json` — a verbatim copy
of the dispatch instruction it received, containing
`"agent": "<its own name>"`; (2) executes only the step named by the
harness's prompt file; (3) writes only its declared outputs plus a
`.harness-step<NN>-done` marker, written last. The harness runs the inbound
gate, writes the step record, and dispatches the next step. Agents never
touch `run-state.json` or any audit file.

| Step | Agent | Consumes | Produces |
|---|---|---|---|
| 00 | coordinator | harness dispatch action | `runner.command` subprocess invocation (no files) |
| 01 | ingest | All 5 input sources | `inventory.json`, `evidence-index.json`, `style-profile.json` |
| 02 | findings-matrix | ingest outputs + reports + exports | `matrix.json` |
| 03a | draft-update | matrix + prior report + closed A/C | `draft-candidate-a.md`, `draft-map-candidate-a.json` (strategy=minimal) |
| 03b | draft-update | same | `draft-candidate-b.md`, `draft-map-candidate-b.json` (strategy=rewrite) |
| 04a | adversarial-review-candidate-a | candidate A + evidence | `review-candidate-a.json`, `review-candidate-a.md` |
| 04b | adversarial-review-candidate-b | candidate B + evidence | `review-candidate-b.json`, `review-candidate-b.md` |
| 04sel | draft-selector | both reviews + both drafts/maps | `draft.md`, `draft-map.json`, `review.json`, `reviewed.md`, `selection-report.json` |
| 05 | tone-consistency | `draft.md` + template | `toned.md`, `tone-changes.json` |
| 06 | adversarial-review | `toned.md` + run state | Final report, `audit-report.md` |

Every step record in `audit/run-<run-id>.jsonl` carries
`dispatch_expected` vs `dispatch_emitted`, model, input/output SHA-256
hashes, `tokens_in`/`tokens_out`/`cost_usd`, and `metering_method` —
never null.

## Guardrails (deterministic — executable code in s5-harness.py)

| Gate | Position | Deterministic checks |
|---|---|---|
| G1 | after 01 | dispatch-verified; all 5 inputs present; `inventory`/`evidence-index`/`style-profile` schema-valid; 5 source roles catalogued; sha256 recorded; ≥1 export file; every export domain-mapped; section map present |
| G2 | after 02 | dispatch-verified; `matrix` schema; every row has `evidence_path` or `unable-to-validate`; **triggers A** (unable-to-validate rows) and **C** (regressed rows) — gate fails until two-key closed |
| G3a/G3b | after each 04 review | dispatch-verified; `draft-map` + `review` schemas; ≥1 matrix row per mapped section; CIS/NIST ref diff vs prior report → **triggers B**; section-heading (H2+) diff vs prior report → **triggers D** |
| G4 | after 04sel | dispatch-verified; `selection-report`, `review`, `draft-map` schemas; zero `unresolved`/`rejected` claims; every `fixed` verdict has `fix_diff`; `draft.md`/`reviewed.md` present; `.g4-passed` sentinel written |
| G5 | after 05 | dispatch-verified; D1 `.g4-passed` sentinel; D2 `tone-changes` schema; D3 banned-pattern regex; D4 substance-freeze factual-token diff; D5 change accountability; D6 two-key punch-out closure across all six punch-outs |

All gates run as code inside `s5-harness.py` before the next step is
dispatched — agent judgment is a layer on top, not the gate itself.

## Punch-Out Points (six — new system's taxonomy)

| ID | Key | Trigger | Raised by | File | Human decision |
|---|---|---|---|---|---|
| A | `A_unable_to_validate` | findings can't be validated by current data | G2 | `audit/punchout-unable-to-validate.md` | still-present / removed / defer |
| B | `B_framework_mappings` | CIS/NIST reference mappings changed | G3 | `audit/punchout-framework-mappings.md` | approve each change |
| C | `C_regressions` | findings classified `regressed` | G2 | `audit/punchout-regressions.md` | confirm evidence supports it |
| D | `D_structure_changes` | report sections added/removed | G3 | `audit/punchout-structure-changes.md` | approve/reject each change |
| E | `E_loop_exhaustion` | any gate hits loop_max (2) | any gate | `audit/punchout-log.md` | resolve directly |
| F | `F_missing_content` | template section has no draft content | G4→05 | `audit/punchout-missing-content.md` | provide content / drop / defer |

Taxonomy rationale (Phase-0 review): A–D are Stage-5-native (the V2 system
had none of them). F keeps the V2 missing-content mechanism, renamed from
"A" to avoid collision. E is universal loop-exhaustion at any loop_max'd
gate. Coordinator mis-dispatch is deliberately NOT a punch-out — it is a
deterministic gate failure logged to `guardrails.jsonl`; the coordinator
cannot reach the punch-out machinery.

Every halt, bypass test, and human decision is recorded in
`audit/punchout-<run-id>.md` (per-run) and `audit/punchout-log.md`
(aggregate). Human closures go through
`python s5-harness.py record-decision --run-id <id> --punchout <letter>
--decision "<verbatim>" --resolved-by "<name>"` — agents never set
`approved: true`. `bypass-test` performs the two-path systematic bypass
(no-approval continuation + forged approval flag) while a punch-out is
open; a recorded bypass permanently marks the run `certifiable: false`.

## Run states

`in-progress → needs-stepNN ⇄ needs-GN → finalized | non-finalizable |
awaiting-human | escalated`

- `finalized` — run completed and is certifiable.
- `non-finalizable` — terminal: all punch-outs closed but `certifiable` is
  permanently false (e.g., a recorded bypass attempt). Valid terminal
  state; nothing left for a human to decide.
- `awaiting-human` — an open punch-out awaits a recorded decision.
- `--resume` re-runs the gate where the run halted (`halted_at_gate`),
  re-checking whatever changed during the halt.

## Audit Trail

Per-run files (all harness-written, agent never authors them):

- `audit/run-<run-id>.jsonl` — one record per agent invocation: step,
  model, `dispatch_expected`/`dispatch_emitted`, input/output hashes,
  `tokens_in`, `tokens_out`, `cost_usd`, `metering_method`,
  `guardrail_inbound`, plus `human-decision` events
- `audit/guardrails-<run-id>.jsonl` — per-gate records (G1–G5) with
  per-check results and iteration numbers
- `audit/success-<run-id>.md`, `audit/punchout-<run-id>.md`

Aggregates (`rebuild-logs` regenerates after every drive call):
`guardrails.jsonl`, `success-log.md`, `punchout-log.md`,
`success-report.md` (production vs gate-test split).

Metering disclosure: the runtime is inspected for a real usage source
first (`metering.session_log_path` in `s5-harness.config.json`); absent
one, figures are a calibrated deterministic estimate (chars/1.75, measured
against Sonnet output ratios of 1.57–1.82 chars/token; error band ≈ ±20%)
labeled `estimated-chars1.75` per record.

## Stage 5 Guarantees

1. **Dispatch-only coordinator:** `00-coordinator` (the harness FSM) has no
   file, search, terminal, or browser tools and no inference of its own —
   only dispatch verbs (`runner.command` subprocess per step). Its emitted
   dispatch is verified deterministically against the FSM on every step.
2. **Scoped sub-agents:** each step receives only its declared input
   artifacts inlined in the prompt (`_STEP_ARTIFACT_INPUTS`) — e.g.,
   candidate-A's reviewer never receives candidate-B's artifacts.
3. **Adversarial review in its own context:** `04-...-a`, `04-...-b`, and
   `06` are separate agent definitions and separate API invocations — every
   call is a fresh context window with no producer-agent history.
4. **Version control:** all prompts, schemas, manifests, the harness, and
   audit artifacts are committed to `Improving_AI_Work`.
5. **Stage 4 continuity:** `05`/`06` are the unchanged Stage-4 skill
   texts; the V2 gates (G4b/G5) are embedded in `s5-harness.py`; the
   standalone V2 harness (`3d1afdf5`) remains the certified Stage-4
   artifact.

## Evidence Rules (carried from the source skill)

1. Current-quarter Defender exports are authoritative for CURRENT STATE.
2. Previous quarter's report is authoritative for what was previously
   reported.
3. Two-quarters-ago report is for historical context and update
   methodology only.
4. CIS/NIST references are authoritative for framework mappings and
   terminology.
5. Never assume a previously documented condition still exists; never
   assume a recommendation was implemented without current-quarter
   evidence.
6. Distinguish: `confirmed by current data` / `not observed in current
   data` / `unable to validate from the provided data`.
7. No fabricated findings, metrics, configurations, dates, scores,
   percentages, framework mappings, or recommendations.

## End-to-End Success Metric

A run succeeds iff:
1. G5 passes with zero unresolved claims,
2. every triggered punch-out is resolved with a recorded human decision,
3. `certifiable` remains `true`, and
4. the final report is emitted.

Per-run result appended to `audit/success-log.md`
(`pass` / `fail` / `halted` / `stopped`); `audit/success-report.md`
computes the production vs gate-test split. Success rate = finalized
production runs / total production runs, tracked quarter over quarter.

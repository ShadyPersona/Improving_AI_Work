# Workflow Definition — Quarterly Security Assessment Update (Stage 5)

Converts the monolithic "update quarterly security assessment" skill into a
sequential multi-agent pipeline with one fail-closed deterministic guardrail on
every handoff, human punch-out gates, a dedicated adversarial candidate-selection
step, and a structured audit trail. The final tone-assessment synthesis is
performed by the unchanged Stage 4 `tone-assessmentV2` agents (`05-tone-consistency`
and `06-adversarial-review`).

## Pipeline

```
[inputs]
   │
   ▼
[00-coordinator] ──► 01-ingest ──G1──▶ 02-findings-matrix ──G2──▶ 03-draft-update (candidate A, minimal)
   │                                                                                │
   │                                                                                ▼
   │                                                                    03-draft-update (candidate B, rewrite)
   │                                                                                │
   │                                                                                ▼
   │                                                                    04-adversarial-review-candidate-a
   │                                                                                │
   │                                                                                ▼
   │                                                                    04-adversarial-review-candidate-b
   │                                                                                │
   │                                                                                ▼
   │                                                                    04b-draft-selector ──G4──▶ 05-tone-consistency ──G5──▶ 06-adversarial-review → [deliverable]
   │
   ▼
[human punch-out resolution when needed]
```

The coordinator dispatches one agent at a time based on `run-state.json`. It does
not read file contents or perform work.

## Inputs

| # | Source | Placeholder |
|---|---|---|
| 1 | Previous quarter's report (baseline) | `<PRIOR_REPORT>` |
| 2 | Report from two quarters ago (history) | `<HISTORY_REPORT>` |
| 3 | Current-quarter Defender export folder | `<DEFENDER_EXPORT_FOLDER>` |
| 4 | CIS Microsoft 365 Foundations Benchmark PDF | `<CIS_PDF>` |
| 5 | NIST CSF 2.0 reference PDF (NIST.CSWP.29) | `<NIST_PDF>` |

## Step Contract

Each sub-agent MUST run its inbound guardrail check and append the result to
`audit/guardrails.jsonl` before doing any work. A failed gate halts the
workflow.

## Run Layout

- Working artifacts live in `runs/<YYYY-QN>/` (see `runs/README.md`).
- Each run begins by copying `templates/run-state.json` into the run dir; it
tracks `loop_counters` (G4/G5, max 2), `certifiable` status, and all punch-out
`approved` states.
- Every JSON artifact MUST validate against `schemas/<name>.schema.json` —
schema validation is what makes the guardrails deterministic.
- Cross-run evidence lives in `audit/` (punch-outs, guardrails.jsonl,
success-log.md, run-*.jsonl).

| Step | Agent | Consumes | Produces |
|---|---|---|---|
| 00 | coordinator | `run-state.json` summary | next agent name + inputs |
| 01 | ingest | All 5 input sources | `inventory.json`, `evidence-index.json`, `style-profile.json` |
| 02 | findings-matrix | ingest outputs + reports + exports | `matrix.json` |
| 03 | draft-update | matrix + prior report + approved punch-outs A/C | `draft-candidate-a.md` + `draft-map-candidate-a.json` (strategy=minimal) |
| 03 | draft-update | same | `draft-candidate-b.md` + `draft-map-candidate-b.json` (strategy=rewrite) |
| 04a | adversarial-review-candidate-a | candidate A + evidence | `review-candidate-a.json`, `review-candidate-a.md` |
| 04b | adversarial-review-candidate-b | candidate B + evidence | `review-candidate-b.json`, `review-candidate-b.md` |
| 04b-selector | draft-selector | both reviews + both drafts/maps | `draft.md`, `draft-map.json`, `review.json`, `reviewed.md`, `selection-report.json` |
| 05 | tone-consistency | `draft.md`, prior report as template, `run-state.json` | `toned.md`, `tone-changes.json` |
| 06 | adversarial-review | `toned.md`, all audit artifacts | Final report, `audit-report.md`, updated `audit/success-log.md` |

## Guardrails

### G1 — ingest → matrix (Input Completeness Gate, hard fail)
- All 5 input sources resolved, SHA-256 hash recorded in `inventory.json`;
Defender export folder contains ≥1 file.
- `evidence-index.json` maps every Defender export file to a security domain —
an unmapped export fails the gate.
- Prior report's section map and `style-profile.json` were extracted.
- Not waivable: missing input halts the workflow.

### G2 — matrix → draft (Evidence Citation Gate + Punch-outs A & C)
- Schema validation of `matrix.json`: every row has an evidence file path OR
classification `unable-to-validate`; required fields present (section,
finding, prior state, evidence, classification, CIS ref, NIST ref).
- **Punch-out A:** any `unable-to-validate` rows → write
`audit/punchout-unable-to-validate.md` → halt for human sign-off.
- **Punch-out C:** any `regressed` rows → write
`audit/punchout-regressions.md` → halt for human confirmation.
- Drafting is blocked until every generated punch-out file is signed off.

### G3 — candidate drafts → candidate reviews (Structural & Framework Reference Gate + Punch-outs B & D)
- CIS/NIST references extracted from each candidate draft vs prior report and
diffed; changed/added mappings → **Punch-out B** (`audit/punchout-framework-mappings.md`).
- Structural diff of each candidate draft headings vs prior report; added/removed
sections → **Punch-out D** (`audit/punchout-structure-changes.md`).
- Each `draft-map-candidate-*.json` must reference ≥1 matrix row per section —
orphan prose is a hard fail.

### G4 — draft-selector → tone (Zero Unresolved Claims Gate)
- The selected `review.json` must have every claim as `confirmed` or `fixed`.
- Every `fixed` claim carries a `fix_diff`.
- Coverage check: claims reviewed ≥ matrix row IDs cited in `draft-map.json`.
- Unresolved claims increment the G4 loop counter. At `loop_max` (2), escalate to
human via `audit/punchout-log.md`.

### G4b — tone-consistency inbound (Input Completeness Gate)
- `draft.md` and template (prior report) exist and are readable.
- The template yields an extractable section/heading structure.
- Failure = hard stop before any editing.

### G5 — tone-consistency → adversarial-review-final (Tone & Assessment-Quality Gate)
- Assessment-quality check: `toned.md` meets conclusion-first, substance-freeze,
change-accountability, and certifiability criteria (defined in
`05-tone-consistency/SKILL.md`).
- Fact-preservation diff: every number, date, percentage, CIS/NIST reference,
and finding title in `toned.md` must exist in `draft.md`.
- Punch-out closure: every triggered punch-out is approved with matching
`closure_evidence`.
- Failure → loop back to step 05 (max 2 iterations → human escalation).

## Punch-Out Points

| ID | Trigger | Raised by | File | Human decision |
|---|---|---|---|---|
| A | findings can't be validated by current data | G2 | `audit/punchout-unable-to-validate.md` | still-present / removed / defer |
| B | CIS/NIST reference mappings changed | G3 | `audit/punchout-framework-mappings.md` | approve each change |
| C | findings classified `regressed` | G2 | `audit/punchout-regressions.md` | confirm evidence supports it |
| D | report sections added/removed | G3 | `audit/punchout-structure-changes.md` | approve/reject each change |
| E | G4/G5 loop exhausted (2 iterations) | G4/G5 | `audit/punchout-log.md` | resolve directly |

Every halt, bypass test, and human decision is recorded in
`audit/punchout-log.md`.

## Stage 5 Guarantees

1. **Dispatch-only coordinator:** `00-coordinator` has no file, search, terminal,
or browser tools. It only emits the next agent name and inputs.
2. **Scoped sub-agents:** Each agent has a narrow system prompt and only the
inputs/outputs defined above.
3. **Adversarial review in its own context:** `04-adversarial-review-candidate-a`,
`04-adversarial-review-candidate-b`, and `06-adversarial-review` each run in
isolation. They receive only the candidate draft and evidence, not the
producing agent's reasoning.
4. **Version control:** All agent prompts (`SKILL.md`), schemas, the orchestrator
manifest, and exported agent definitions are committed.
5. **Stage 4 continuity:** The unchanged `05-tone-consistency` and
`06-adversarial-review` agents from `tone-assessmentV2` preserve their G4/G5
audit behavior.

## Evidence Rules (carried from the source skill)

1. Current-quarter Defender exports are authoritative for CURRENT STATE.
2. Previous quarter's report is authoritative for what was previously reported.
3. Two-quarters-ago report is for historical context and update methodology only.
4. CIS/NIST PDFs are authoritative for framework references and terminology.
5. Never assume a previously documented condition still exists; never assume a
recommendation was implemented without current-quarter evidence.
6. Distinguish: `confirmed by current data` / `not observed in current data` /
`unable to validate from the provided data`.
7. No fabricated findings, metrics, configurations, dates, scores,
percentages, framework mappings, or recommendations.

## Audit Trail

`audit/run-YYYYMMDD.jsonl` — one record per step:

```json
{"step": "03-draft-update", "model": "...", "input_hashes": {...}, "output_hashes": {...},
"tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0, "finding_ids": ["F-001"],
"guardrail_inbound": {"id": "G2", "result": "pass"}}
```

Any failure must be traceable to its exact origin step.

## End-to-End Success Metric

A run succeeds iff:
1. G5 passes with zero unresolved claims,
2. every triggered punch-out is resolved with a recorded human decision,
3. `certifiable` remains `true`, and
4. the final report is emitted.

Per-run result appended to `audit/success-log.md`:

```
| date | run id | result | punch-outs | iterations | notes |
```

Success rate = successful runs / total runs, tracked quarter over quarter.

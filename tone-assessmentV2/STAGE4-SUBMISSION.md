# Stage 4 Resubmission — Changes Since the Previous FAIL Determination

**Date:** 2026-11-03
**Harness hash:** `ca71cd71997ac763b165154037c1651cd87613bd6e655492ecf06a403101d380` (`python harness.py hash`; refreshed automatically after every state transition)
**Model:** configured via `HARNESS_MODEL` / `harness.config.json` `model`.
The agent CLI is provider-agnostic — `AGENT_PROVIDER` accepts
`copilot-studio` | `openai` (and OpenAI-compatible endpoints such as
Fireworks AI) | `azure` | `ollama` | `anthropic`. The certified E2E
run below executed on Fireworks `deepseek-v4p1-flash`; step-level
resilience (`AGENT_RETRIES`, `AGENT_TIMEOUT`, `AGENT_MAX_TOKENS`,
`AGENT_REASONING_EFFORT`, Ollama `AGENT_NUM_CTX`/`AGENT_NUM_THREAD`/
`AGENT_THINK`) is configurable via environment variables.

## Automated harness (Artifact 1)

`harness.py` is now a real executor, not a state machine that waits for
hand-made done markers. On `action == "execute_step"` it spawns the
configured agent CLI — `runner.command` (`python agent-runner.py`,
`runner.mode: "auto"`) — via `subprocess`, passing
`HARNESS_RUN_ID`/`HARNESS_STEP`/`HARNESS_PROMPT_FILE`/`HARNESS_RUN_DIR`/
`HARNESS_DONE_MARKER`/`HARNESS_EXPECTED_OUTPUTS`, and captures
stdout/stderr into `audit/run-<run-id>.jsonl`. `agent-runner.py` is a
stdlib-only, provider-agnostic agent CLI
(`AGENT_PROVIDER` = `copilot-studio` | `openai` | `azure` | `ollama` |
`anthropic`; `AGENT_API_KEY`; `AGENT_BASE_URL`; `HARNESS_MODEL`) that sends
the assembled step prompt, parses a JSON file-map response, writes the
declared outputs into the run directory, and creates the done marker only
when every expected output exists — never when `g5-judgment.md` or
`punchout-missing-content.md` is produced. The Copilot Studio agent may be
the entry point that calls `python harness.py run`, but the harness is
always the orchestrator and the agent CLI is always invoked via
`runner.command`. Step prompts now inline every artifact the model
needs — the `tone-changes.schema.json` output contract and, for
steps 06/07, the prior-step outputs (`toned.md`, `tone-changes.json`,
`run-state.json`, `g5-verdict.json`) — because the agent has no
filesystem access and earlier runs proved that file paths alone are
not readable context.

Subcommands: `drive`, `run`, `verify`, `manifest`, `rebuild-logs`, `embed`,
`template-md`, `hash`, `check-g4`, `check-g5`, `bypass-test`,
`record-decision`.

## Three-step pipeline (structural strengthening)

Step count and agent count are now 3:

| Step | Agent | Role | Tracked outputs |
|---|---|---|---|
| 05 | `05-tone-consistency` | Synthesis `draft.md` → `toned.md` + `tone-changes.json` | `toned.md`, `tone-changes.json` |
| 06 | `06-adversarial-review` | G5 judgment layer only — no deliverable work | `g5-verdict.json` (pass) / `g5-judgment.md` (fail) |
| 07 | `07-finalize` | Deliverable + `audit-report.md`, only after 06's verdict and two-key punch-out closure | `audit-report.md` + final deliverable |

The split answers the "step 06 is both reviewer and finalizer" finding and
gives the adversarial reviewer its own role. `run-state.json` handles the
new `needs-step07` state; `EMBEDDED_SKILLS` covers 05/06/07.

## Deterministic guardrails (Artifact 2)

G4 and the deterministic G5 layer (D1 sentinel, D2 schema, D3
banned-pattern regex, D4 substance-freeze token diff, D5 change
accountability, D6 two-key punch-out closure) still run as executable code
inside `harness.py` at the gate edges, before step 06's judgment layer.
Step 06 additionally runs two new adversarial lenses: a **PHI /
confidentiality exposure** check and a **semantic substance-freeze**
check (re-based/renormalized metrics, re-scoped findings, re-interpreted
severities that survive token diffs — motivated by the
`2026-Q3-PunchOutETest` slip where 100%-of-evaluated vs 98.48%-of-total
passed token checks).

## Punch-out evidence (Artifact 3)

- The four 2026-10-20 `GATE FAILURE` bypass rows are explained in
  `audit/AUDIT-INTEGRITY-NOTE.md` §2: genuine bypasses against an
  intermediate harness version; fixed by wiring `punchout_log_has_closure`
  into every gate path in commit `2499cdf`.
- Re-tested on the current hash 2026-10-27: `bypass-test` against both
  `2026-Q3-PunchOutATest` (A) and `2026-Q3-PunchOutETest` (E) — both
  attack paths recorded `blocked` (newest rows in `punchout-log.md`).
- Production-run bypass applicability is disclosed in §2 of the integrity
  note: no production run has a triggered punch-out; the same two-key code
  path gates production finalization.

## End-to-end success rate (Artifact 4)

`audit/success-report.md` now counts every run, including the previously
omitted `2026-Q3-IRONTRAX`, `2026-Q3-TeamDaks`,
`2026-Q3-TEAMDAKSFullHarness` (stalled at needs-step06, counted as halted),
and the 2026-10-18 gate-test runs:

- **Production: 11/12 finalized** (1 halted — `TEAMDAKSFullHarness` never
  completed step 06); the newest finalized production run is
  `2026-Q3-TEAMDAKS-E2ERun-Fireworks-DeepSeek-01` (see below)
- **Gate-test: 0/7 finalized — 7 halted at their intended gates**
- **Trend (≥2 reporting periods):** 2026-10-17/18 pre-harness runs 2/2
  finalized (IRONTRAX, TeamDaks); 2026-10-20/21 harness runs 8/9
  finalized (TEAMDAKSFullHarness stalled); 2026-11-03 unattended
  provider-driven E2E run finalized end-to-end.
- **Aggregate freshness:** `rebuild-logs` runs automatically after
  every state transition (no manual step to keep
  `success-log.md`/`success-report.md`/`guardrails.jsonl` in lockstep),
  and `harness.sha256` is refreshed in the same hook.

## Audit trail (Artifact 5)

- `audit/AUDIT-INTEGRITY-NOTE.md` discloses every reconstruction and
  correction: the `run-20261018.jsonl` rebuild (recycle-bin item
  identified), the `log_corrected` paraphrase disclosure in
  `runs/2026-Q3-PunchOutETest/run-audit-entries.jsonl`, the
  chars4/chars1.75 metering-label reconciliation, the null-metering
  backfill record, and the step-05 model-attribution correction for
  `2026-Q3-HHAFullHarness_Sonnet5-5` — all via appended correction
  records; logs are append-only.
- **Metering disclosure:** unchanged — deterministic `chars/1.75`
  estimate disclosed per record (`metering_method`), switching to
  `session_log` automatically when `metering.session_log_path` is
  configured.

## Prompt artifacts and measured iterations

- `05-tone-consistency/SKILL.md`: every instruction unit carries a
  `[criterion: <name>]` tag with a full criterion-mapping table (100% of
  units mapped — above the 90% load-bearing threshold); instructions for
  `observations` locations, `facts_changed` evidence, `tables_reviewed`
  completeness, quarterly review, and cross-signal synthesis hardened.
- `06-adversarial-review/SKILL.md`: rewritten review-only with the same
  per-instruction criterion tagging.
- `ITERATION_LOG.md` for 05 and 06: measured before/after iterations with
  eval IDs, stale "blocked until API key" statuses corrected, and all
  regressions recorded (including the `2026-Q3-PunchOutETest` G5 failures
  and the IRONTRAX table-fragment regression). `07-finalize` has its own
  iteration log documenting the split.

## Supporting evidence

- Promptfoo evals: **13/13** on 05 (`eval-bFm-2026-11-03T01:33:26`),
  **11/11** on 06 (`eval-ods-2026-11-03T01:35:22`), **5/5** on 07
  (`eval-m5K-2026-11-03T01:36:31`), all executed 2026-11-03 on
  `claude-sonnet-5-5` against the post-change skills; before/after
  deltas recorded in each `ITERATION_LOG.md`.
- Unattended end-to-end harness run:
  **`2026-Q3-TEAMDAKS-E2ERun-Fireworks-DeepSeek-01`** — `python
  harness.py run` executed steps 05 → 06 → 07 unattended via
  `runner.command`; deterministic G5 passed; the step-06 judgment layer
  returned `result: pass` on all seven checks
  (`runs/2026-Q3-TEAMDAKS-E2ERun-Fireworks-DeepSeek-01/g5-verdict.json`);
  `run-state.json` shows `certifiable: true`, zero punch-outs,
  `status: finalized`; deliverable
  `Team-Daks-Cloud-Security-Assessment-2026-Q3.md` and `audit-report.md`
  emitted. Provider: Fireworks AI `deepseek-v4p1-flash`.
  Prior attempts (`E2ERun`–`E2ERun-4`) are preserved as failure
  evidence — each failure mode maps to a shipped fix in
  `audit/AUDIT-INTEGRITY-NOTE.md` §5.
- Version lineage: `VERSION_HISTORY.md`, commits `2499cdf` → `d448d90` →
  `b8f39d8` → this resubmission commit (see `git log`).

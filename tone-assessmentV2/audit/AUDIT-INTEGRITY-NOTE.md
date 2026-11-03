# Audit Integrity Note — tone-assessmentV2

This file discloses every reconstruction, correction, and labeling
inconsistency in the audit trail, so no log line needs to be taken on
trust. Audit logs are append-only: corrections are made by appending
correction records, never by rewriting history lines.

## 1. Reconstructed audit lines (2026-10-18)

**`audit/run-20261018.jsonl`** — lines 1–24 were rebuilt from the session
summary when the earlier version was rewritten at 05:03:44Z; they are not
verbatim copies of the original lines. The original 32-line version is in
the SharePoint recycle bin (item 01XX6TFET6BZQ47KQPKFCLNJCXBJHRVKUU) and
could not be read back by tool. This reconstruction is disclosed inline by
the `audit_integrity_note` record at line 31 of that file. If the original
is recovered from the recycle bin, it should be diffed against lines 1–24
and any divergence appended as a correction record.

**`runs/2026-Q3-PunchOutETest/run-audit-entries.jsonl`** — the
`log_corrected` record (line 17) discloses that lines 4–12 of a prior
version were paraphrased or carried invented timestamps, and were replaced
by verbatim copies from `run-audit-entries-step05.jsonl` and
`run-20261018-2026-Q3-PunchOutETest-stop.jsonl`. The earlier
`log_rewritten` line recorded `new_line_count: 16` in error; the true
count was 17.

**Policy going forward:** logs are append-only. No line may be rewritten,
reordered, or paraphrased. Corrections take the form of appended
`*_correction` records (see §3 for examples).

## 2. The four "GATE FAILURE" bypass rows (2026-10-20)

`audit/punchout-log.md` contains four rows dated 2026-10-20 whose bypass
result is `GATE FAILURE — see detail`:

- `2026-Q3-PunchOutATest` / punch-out A at 19:27:01Z and 19:28:11Z
- `2026-Q3-PunchOutETest` / punch-out E at 19:27:01Z and 19:28:54Z

These are genuine gate failures recorded by `harness.py bypass-test`: at
least one of the two systematic attempts (no-approval continuation, forged
approval flag) would have opened the gate under the working-tree harness
in use at that moment. The two-key closure check
(`punchout_log_has_closure`) was not yet wired into all gate paths when
the first tests ran on 2026-10-20.

**The code change that followed:** commit `2499cdf` (2026-10-20, "Stage 4
harness: single-file orchestrator") wired `punchout_log_has_closure` —
which requires a `punchout-log.md` row with non-empty `resolved by` /
`resolved at` for the matching `run_id` and punch-out letter, and excludes
bypass-test rows — into `bypass_test.would_pass()`, G5 check D6, the
awaiting-human resume path, and the finalization `closure_ok` check.
Within the same log, repeat tests on 2026-10-20 at 19:28:54Z and
19:36:44Z record `blocked`, and every bypass test since (2026-10-21 rows
for `2026-Q3-PunchOutAETest` and `2026-Q3-PunchOutETest-r2`) records
`blocked`.

**Re-test** (harness hash at test time `a279270eb58e98154293428a9c56f97e42102ef1244fde59c7b217d749872d05`; a later docx→md auto-conversion patch bumped the hash — the two-key code path is unchanged by that patch):
`python harness.py bypass-test --run-id 2026-Q3-PunchOutATest --punchout A`
and `… --run-id 2026-Q3-PunchOutETest --punchout E` were re-run on
2026-10-27; both attempts (no-approval continuation, forged approval flag)
recorded `blocked` — see the two newest rows in `punchout-log.md`. The
runs remain permanently non-certifiable, as required.

**Production-run bypass test:** no production run (`2026-Q3-IRONTRAX*`,
`2026-Q3-HHA*`, `2026-Q3-ASM*`, `2026-Q3-Bethany*`, `2026-Q3-TeamDaks`,
`2026-Q3-TEAMDAKSFullHarness`) has a triggered punch-out, so `bypass-test`
has no gate to attack on them (it returns "punch-out never triggered"
without touching state — verified). The open punch-outs used above are
the only live targets; the two-key check they exercise is the same code
path that gates finalization in every production run (`g5_check` D6 +
`closure_ok`). This exclusion is disclosed rather than simulated, because
manufacturing a fake punch-out inside a production run would itself be an
audit-integrity violation.

## 3. Metering and model-attribution corrections

**Label reconciliation (`chars4` vs `chars1.75`):** `metering_method`
values like `estimated-chars4` and `estimated-chars1.75` are generated
from `metering.estimation_chars_per_token` in `harness.config.json`. The
2026-10-20/21 run records were metered when the constant was 4; the
config has since been set to 1.75 (a better fit for dense markdown). Both
labels therefore describe the same disclosed estimator at different
constant values; the method name records which constant produced each
number. When `metering.session_log_path` is configured, real session-log
usage replaces the estimate and the method reads `session_log`.

**Null backfill (`audit/run-20261017.jsonl`):** all 9 records carry
`tokens_in/tokens_out/cost_usd: null` because the pre-harness agent
runtime exposed no metering. Most run artifacts were removed after those
runs, so a real backfill is unrecoverable for 8 of 9 lines — disclosed,
not fabricated. Where an output artifact survives (`audit-report.md` for
both runs), an appended `metering_backfill` record supplies a
`backfill-estimated-chars1.75` estimate.

**Provider-usage metering (added 2026-11-03):** `agent-runner.py` now
captures each provider's real `usage` counters (`prompt_tokens`/
`completion_tokens` for OpenAI-compatible APIs, `prompt_eval_count`/
`eval_count` for Ollama, streamed `usage` events for Anthropic) and
writes them to `runs/<run-id>/.harness-stepNN-usage.json`. When that
file exists, `meter_step` records `metering_method: "provider-usage"`
with real token counts — estimates remain labeled
`estimated-chars1.75` and are used only when a provider returns no
usage data. Historical records keep their original labels; the
estimate-to-real cutover begins with post-2026-11-03 runs.

**Step-05 model attribution
(`audit/run-2026-Q3-HHAFullHarness_Sonnet5-5.jsonl`):** line 1 records
`claude-haiku-4-5-20251001`, carried over from a Haiku run template; the
run was executed on `claude-sonnet-5-5` (per the run-id suffix and the
step-06 record). Corrected by an appended `model_attribution_correction`
record; the original line is unchanged. The `"model": "Claude
(tone-assessmentV2 workflow runner)"` strings in `run-20261017.jsonl` are
pre-harness records where the exact model was not logged — disclosed, not
corrected.

## 4. Success denominator

`audit/success-log.md` / `success-report.md` now include the previously
omitted runs — `2026-Q3-IRONTRAX`, `2026-Q3-TeamDaks`,
`2026-Q3-TEAMDAKSFullHarness` (stalled at needs-step06, counted as halted,
not a success), `2026-Q3-PunchOutATest`, `2026-Q3-PunchOutATest-Bypass`,
`2026-Q3-PunchOutETest` — via per-run `success-<run-id>.md` backfill files
regenerated through `harness.py rebuild-logs` (the derived aggregates'
only update path). Current totals: **production 10/11 finalized**
(2026-10-17 → 2026-10-21), **gate-test 0/7 finalized** (7 halted —
expected for runs designed to trip guards). The two-quarter trend is
reported in `STAGE4-SUBMISSION.md`.

## 5. E2E runner development trail (2026-10-29 → 2026-11-03)

`audit/run-2026-Q3-TEAMDAKS-E2ERun-*.jsonl` contain multiple `runner_exec`
failures from the first harness-executed runs. Each maps to a defect that
has since been fixed in code — the records are retained as evidence of the
executor path operating through real failure modes:

| Recorded failure | Root cause | Fix shipped |
|---|---|---|
| HTTP 401 (OpenAI) on step 05 | `AGENT_PROVIDER` unset → defaulted to `openai` | Operator env-var setup; provider selection documented |
| "no JSON object found" (×2) | Copilot Studio agent returned the text *"You don't have access to talk to this bot"* — agent-level channel denial | Provider kept as documented option; recorded run moved to a reachable endpoint |
| HTTP 404 `model 'claude-sonnet-5-5' not found` (Ollama) | `harness.config.json` `model` overrode `HARNESS_MODEL` env var | `HARNESS_MODEL` env var now takes precedence in both dispatch and audit records |
| `timed out` on step 05 | 600s HTTP + 1800s subprocess limits too low for CPU-local generation | `AGENT_TIMEOUT`/`runner.timeout_seconds` raised (14,400s) |
| False punch-out A on E2ERun-2 | `build_prompt` sent file *paths*, not contents; an API-called model has no filesystem | `build_prompt` now inlines all input file contents |
| `draft.* missing` → G4 loop_max on E2ERun | `draft.docx` supplied but never converted; harness had no draft auto-convert | `_ensure_draft_md` converts `draft.docx`→`draft.md` before G4 |
| HTTP 504 on step 05 (×several) | Transient Anthropic edge timeouts on the long request | SSE streaming for Anthropic + 4-attempt 15/30/60s backoff retries |
| G5 D2/D3 failures on E2ERun-3 | Haiku emitted malformed `tone-changes.json` and banned contractions — real model-quality failures caught by the gates | None needed — gates working as designed; recorded run moved to `claude-sonnet-4-5` with `AGENT_MAX_TOKENS=32768` |

**Unrecorded dispatch:** one step-05 dispatch (Ollama provider) was
terminated manually mid-generation before the subprocess could write its
`runner_exec` record. The dispatch is therefore absent from the run log —
disclosed here; the surrounding records are unaffected.

`punchout-missing-content.md` written on E2ERun-2 is retained in the run
directory as the false punch-out's own evidence; the run was closed via
recorded decision "accept halt — false punch-out".

## 6. Harness edge cases fixed during the IRONTRAX E2E (2026-11-03)

`2026-Q3-IRONTRAX-E2ERun-Fireworks-DeepSeek-01` ended `non-finalizable`
after model-quality failures (see the 05 ITERATION_LOG regressions
section). The run also exposed two harness edge cases, both fixed:

1. **Consumed punch-out approvals:** when punch-out E re-triggered after
   a recorded "approve retry", the prior `approved`/`closure_evidence`
   remained set — `record-decision` then refused a fresh decision
   ("would look like tampering") while `drive --resume` would re-dispatch
   a paid step on stale authority. `_trigger_punchout` now clears a
   consumed approval on re-trigger so each escalation requires a new
   recorded human decision; the new pending log row documents it.
2. **Non-finalizable settle:** `escalated` runs with all punch-outs
   closed and `certifiable: false` now settle `non-finalizable` on
   `drive` (previously only `awaiting-human` settled), unless a recorded
   "approve retry" decision is outstanding.

`step07-precondition-failure.md` in the run directory is retained: the
finalize agent correctly refused to package a deliverable for a
non-certifiable run — evidence of the gate working as designed.

## 7. Production-path bypass test (2026-11-03)

The examiner noted bypass testing had only covered gate-test runs.
`2026-Q3-TEAMDAKS-ProdBypassTest` is a copy of the certified production
run `…-E2ERun-Fireworks-DeepSeek-02` under a new run ID, with punch-out
`A_missing_content` **synthetically set to `triggered: true`** (the
successful run itself never triggered one — a bypass test requires an
open punch-out). `python harness.py bypass-test` then exercised both
attack paths on the production run's own state and configuration: both
`no-approval continuation` and `forged approval flag` were **blocked**.
The run is permanently non-certifiable (recorded bypass attempt). The
synthetic trigger is disclosed here and in the run's
`non_certifiable_reasons`; the certified `-01`/`-02` runs are untouched.

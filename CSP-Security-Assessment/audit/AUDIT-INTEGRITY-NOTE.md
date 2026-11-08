# Audit Integrity Note — Stage 5 (CSP Security Assessment)

Same convention as `tone-assessmentV2/audit/AUDIT-INTEGRITY-NOTE.md`:
audit records are append-only. Corrections and mechanism changes are
disclosed here, not retro-edited into existing rows.

## 1. Runtime cutover (2026-11-03)

The runner switched from manual Copilot-Studio execution to
`agent-runner.py` API dispatch (`runner.mode: auto` in
`s5-harness.config.json`). Copilot Studio could not execute the pipeline —
agents have no artifact/filesystem surface (blockers documented in the
deleted `COPILOT_STUDIO_SETUP.md`; the setup-run evidence remains under
`runs/setup-*`). Department-standard provider: **Azure OpenAI with
Microsoft Entra ID auth** — prompts and completions stay inside the org
tenant.

Records written before this cutover carry `"environment":
"copilot-studio"`; records after carry `"environment": "runner-api"`. The
label change is a provenance marker, not a mechanism change.

## 2. Metering

`meter_step` now prefers `runs/<run-id>/.harness-stepNN-usage.json`
(provider's real `usage` counters) when present → `metering_method:
"provider-usage"`. `session_log` and `estimated-chars1.75` remain as
labeled fallbacks. Historical records keep their original method labels.

`price_usd_per_1k_tokens` now reflects the Azure deployment's rates
(GPT-4.1-class, $0.002/$0.008 per 1K). Earlier records priced at the prior
Anthropic-tier default ($0.003/$0.015) keep their values — disclosed, not
rewritten.

## 3. Punch-out re-trigger fix

`_trigger_punchout` now resets `approved`/`closure_evidence` when an
already-closed punch-out re-triggers — a consumed approval must not carry
to a new trigger (parity with the fix shipped in tone-assessmentV2 after
the IRONTRAX incident where a stale approval would have burned paid
retries). No historical run hit this path.

## 4. Step split (06 → 06 + 07)

The former combined `06-adversarial-review` (review + finalize) was split:
06 emits `g5-verdict.json`/`g5-judgment.md` only; 07 emits the deliverable
and `audit-report.md` under precondition checks. EXPECTED_OUTPUTS and the
FSM changed accordingly; prior runs' `audit-report.md`-as-step-06 records
describe the old combined step and remain accurate for their era.

## 5. Copilot removals

Deleted as dead configuration: `.github/copilot-instructions.md`,
`.github/copilot-studio/agent-definitions/` (9 manifests),
`.github/security-assessment-orchestrator.agent.md`,
`COPILOT_STUDIO_SETUP.md`. The decision trail is preserved in
`VERSION_HISTORY.md`, `runs/setup-*` evidence, and this note.
`evals/*.csv` retain their Copilot Studio Evaluate format — declared
provenance; promptfoo conversion is a tracked follow-up.

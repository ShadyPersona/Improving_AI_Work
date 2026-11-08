# Department Setup — Running the Pipeline

For CSP operators. Assumes your admin completed `AZURE-SETUP.md` and gave you
the deployment URL.

## One-time environment setup (PowerShell)

```powershell
$env:AGENT_PROVIDER = "azure"
$env:AGENT_BASE_URL = "https://<resource>.openai.azure.com/openai/deployments/csp-assess/chat/completions?api-version=2024-10-21"
$env:HARNESS_MODEL  = "csp-assess"
$env:AGENT_MAX_TOKENS = "32768"
```

**Authentication — pick one:**

- *Interactive (recommended for manual runs):* `az login` once — the runner
  calls `az account get-access-token` itself when it needs a token.
- *Service principal (automation):* set `AZURE_TENANT_ID`,
  `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` in your environment (from a secret
  store — never in files).
- *API key (legacy only):* `AGENT_API_KEY` — only works if the resource's
  admin left local auth enabled; Entra is preferred.

Other providers still work for non-client testing (`openai`, `ollama`,
`anthropic` — same env-var pattern as tone-assessmentV2). **Client data must
only go to the `azure` provider.**

## Per-quarter run

```powershell
cd <repo>/CSP-Security-Assessment

mkdir "runs\2026-Q4\inputs"
# place the 5 inputs in runs\2026-Q4\inputs\ as text:
#   prior-report, history-report, defender-export-folder\, cis, nist
# (.docx/.pdf must be converted to .md/.txt first — the model receives
#  inlined file contents, binaries are skipped and listed in the prompt)

python s5-harness.py run --run-id 2026-Q4
```

The harness dispatches each step through `agent-runner.py` — you will see
`execute_step`/`runner executed step NN`/`wait` lines until `finalized`,
`non-finalizable`, or `awaiting_human`.

## Human decisions (punch-outs)

When a run halts `awaiting_human`, review the file named in the detail
(`audit/punchout-*.md`), then:

```powershell
python s5-harness.py record-decision --run-id 2026-Q4 --punchout <letter> --decision "<your verbatim decision>" --resolved-by "<your name>"
python s5-harness.py run --run-id 2026-Q4
```

A `record-decision` only ever takes effect for the run's *current* trigger —
if a gate re-triggers, the harness asks for a fresh decision. Agents can
never approve their own punch-outs.

## Outputs

- Deliverable + `audit-report.md` in `runs/<id>/`
- Step/gate records: `audit/run-<id>.jsonl`, `audit/guardrails-<id>.jsonl`
- Success row: `audit/success-<id>.md` + `audit/success-log.md`
- Real token usage per step: `metering_method: provider-usage` in the run
  records (falls back to a labeled estimate only if the provider reports
  nothing)

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `runner.command failed` / HTTP 401 | `az login` expired or missing role — re-login or check `Cognitive Services OpenAI User` |
| HTTP 403 immediately | IP allowlist (DP-E) doesn't include your egress IP |
| `step NN` retries forever | model returning malformed file map — check `runs/<id>/agent-raw-stepNN.txt` |
| Prompt says "binary inputs not inlined" | convert that `.pdf`/`.docx` to text in `inputs/` and re-run |
| `awaiting_human` on every `--resume` | a punch-out re-triggered — record a fresh decision for the new trigger |

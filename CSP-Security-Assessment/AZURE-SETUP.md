# Azure Setup — CSP Security Assessment Pipeline

Step-by-step provisioning for the Azure OpenAI runtime the pipeline uses.
Assumes: an Azure subscription where you hold Owner/Contributor, `az` CLI
installed, and permission to create app registrations. ~1 hour total, mostly
portal/CLI waits.

Decision points are marked **DP-A** through **DP-F** — each is a choice that
changes the system; record what you picked.

## Phase 0 — Access check (~5 min)

1. `az login` → `az account show` — confirm the right subscription
   (`az account set -s <id>` if several).
2. `az provider register -n Microsoft.CognitiveServices`, then
   `az provider show -n Microsoft.CognitiveServices --query registrationState`
   — must reach `Registered`.
3. **DP-A — Azure OpenAI access:** try a resource creation (Phase 1, step 5).
   If rejected pending an access-request approval, submit the form and wait —
   nothing else works until approved.

## Phase 1 — Resource group + OpenAI resource (~10 min)

4. `az group create -n rg-csp-security-assessments -l eastus2`
5. **DP-B — region:** pick a region that (a) offers GPT-4.1/4o Standard
   deployments and (b) satisfies client residency requirements (US confirmed
   acceptable). Check first:
   `az cognitiveservices account list-models -l <region>`.
6. `az cognitiveservices account create -n aoai-csp-assess -g rg-csp-security-assessments -l eastus2 --kind OpenAI --sku S0 --custom-domain aoai-csp-assess`
   — `--custom-domain` is **required** for Entra ID auth.
7. Verify: `az cognitiveservices account show -n aoai-csp-assess -g rg-csp-security-assessments --query properties.endpoint` — save this URL.

## Phase 2 — Model deployment (~5 min)

8. **DP-C — model + SKU:** default `gpt-4.1` on `GlobalStandard` (routes to
   available capacity, still in-tenant). If a client contract requires
   region-pinned processing, use `Standard` or `DataZoneStandard` instead.
   List versions:
   `az cognitiveservices account list-models -l eastus2 --query "[?model.name=='gpt-4.1']"`.
9. `az cognitiveservices account deployment create -n aoai-csp-assess -g rg-csp-security-assessments --deployment-name csp-assess --model-name gpt-4.1 --model-version "<latest>" --model-format OpenAI --sku-capacity 20 --sku-name GlobalStandard`
   (~15–30K TPM is plenty: ~9 sequential calls/run, ~60K in / 45K out tokens).
   Deployment name `csp-assess` is what `HARNESS_MODEL` becomes.
10. Verify: `az cognitiveservices account deployment list -n aoai-csp-assess -g rg-csp-security-assessments` → `Succeeded`.

## Phase 3 — Identity (Entra ID) (~15 min)

11. Create the automation service principal:
    `az ad sp create-for-rbac -n sp-csp-assess-runner` — save `appId`,
    `password`, `tenant` immediately; store in Key Vault or env vars only —
    **never in the repo**.
12. Least-privilege roles:
    - Operators + SP — `Cognitive Services OpenAI User` (data-plane inference
      only; cannot manage the resource or view keys):
      `az role assignment create --assignee <appId-or-user-object-id> --role "Cognitive Services OpenAI User" --scope <resource-id>`
    - Deployment admins — `Cognitive Services OpenAI Contributor`.
13. Verify the token path before disabling keys:
    - SP: POST `https://login.microsoftonline.com/<tenant>/oauth2/v2.0/token`
      with `grant_type=client_credentials`, `scope=https://cognitiveservices.azure.com/.default`
    - Interactive: `az account get-access-token --scope https://cognitiveservices.azure.com/.default`
    Then a real call: `POST <endpoint>/openai/deployments/csp-assess/chat/completions?api-version=2024-10-21`
    with `Authorization: Bearer <token>` → expect a completion, not 401.
14. **DP-D — disable key auth** (only after step 13 verifies):
    `az cognitiveservices account update -n aoai-csp-assess -g rg-csp-security-assessments --set properties.disableLocalAuth=true`
    Entra-only is the cleaner posture; leave `false` only if a legacy tool
    still needs keys (then keep keys in Key Vault + rotate — flag as a
    compliance note).

## Phase 4 — Network (~10 min)

15. **DP-E — network model:**
    - *IP allowlist (guide default):*
      `az cognitiveservices account update ... --set properties.networkAcls.defaultAction=Deny`
      plus `properties.networkAcls.ipRules` entries for each operator/office
      egress IP (`{"value":"<ip>/32"}`).
    - *Private Endpoint:* only if client/policy demands no public endpoint —
      the runner then needs VNet egress/VPN. Defer unless required.

## Phase 5 — Guardrails on the Azure side (~10 min)

16. **DP-F — content filters:** keep the default filter ON. Assessment text
    can occasionally trip exploit/violence categories — handle flagged output
    per case; do not create a permissive default filter.
17. Monitoring: diagnostic settings → Log Analytics (`AuditEvent`, request
    metrics, `Trace`) in the same RG. Prompt/completion bodies are NOT logged
    by default — the pipeline's own `audit/run-<id>.jsonl` usage records are
    the audit trail.
18. Cost guardrail: `az consumption budget create` on the RG (~$25/month
    is ample) + action-group email alert at 80%.
19. Compliance bookmarking for client conversations: prompts/completions are
    not used to train models, are not accessible to OpenAI or other
    customers, and are covered by the existing Microsoft Products & Services
    DPA — no separate agreement. Abuse-monitoring human review can be opted
    out via the modified-access request if a contract requires.

## Phase 6 — Hand-off to operators

20. Give each operator the values in `DEPARTMENT-SETUP.md`:
    `AGENT_PROVIDER=azure`, `AGENT_BASE_URL=<endpoint>/openai/deployments/csp-assess/chat/completions?api-version=2024-10-21`,
    `HARNESS_MODEL=csp-assess`, `AGENT_MAX_TOKENS=32768`, plus their auth
    choice (SP env vars or `az login`).

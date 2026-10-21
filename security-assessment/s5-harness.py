"""Stage-5 security-assessment harness — SINGLE-FILE executable orchestration.

Runs the 9-agent pipeline end-to-end:
  00-coordinator (dispatch-only) ->
  01-ingest -> G1 -> 02-findings-matrix -> G2 ->
  03-draft-update (candidate a) -> 03-draft-update (candidate b) ->
  04-adversarial-review-candidate-a -> G3a ->
  04-adversarial-review-candidate-b -> G3b ->
  04b-draft-selector -> G4 -> 05-tone-consistency -> G5 -> 06-adversarial-review

Deterministic G1–G5 gates run as code at every handoff. Punch-outs
A–F halt the run for a recorded human decision. Per-step token/cost
metering and all audit writes are harness-owned. Standard library only —
no pip, no network, no packages.

Usage (from the folder containing runs/, audit/, templates/, schemas/):

  python s5-harness.py drive --run-id <id>            advance one step;
                                                      prints a JSON action
  python s5-harness.py drive --run-id <id> --resume   resume after human closure
  python s5-harness.py run   --run-id <id>            foreground loop
  python s5-harness.py check-g1 .. check-g5 --run-id <id>
  python s5-harness.py bypass-test --run-id <id> --punchout A|B|C|D|E|F
  python s5-harness.py record-decision --run-id <id> --punchout <letter>
      --decision "<the human's words>" --resolved-by "<name>"
  python s5-harness.py hash                           print this file's SHA-256

Copy integrity: `python s5-harness.py hash` vs s5-harness.sha256.
"""
import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Embedded data
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent

DEFAULT_CONFIG = {
    "runner": {"mode": "manual", "command": "", "timeout_seconds": 1800},
    "model": "claude-sonnet-5-5",
    "price_usd_per_1k_tokens": {"input": 0.003, "output": 0.015},
    "metering": {"session_log_path": None,
                 "estimation_chars_per_token": 1.75},
    "loop_max": 2,
    "operator": "",
    "default_template": "CSA Template.md",
}

# Phase-0 taxonomy: six punch-outs. A–D are Stage-5-native (new system,
# new punch-outs). E is universal loop-exhaustion. F is V2's missing-content
# mechanism renamed to avoid colliding with A.
PUNCHOUTS = {
    "A_unable_to_validate": {"letter": "A", "label": "unable-to-validate",
                             "file": "audit/punchout-unable-to-validate.md"},
    "B_framework_mappings": {"letter": "B", "label": "framework-mappings",
                             "file": "audit/punchout-framework-mappings.md"},
    "C_regressions": {"letter": "C", "label": "regressions",
                      "file": "audit/punchout-regressions.md"},
    "D_structure_changes": {"letter": "D", "label": "structure-changes",
                            "file": "audit/punchout-structure-changes.md"},
    "E_loop_exhaustion": {"letter": "E", "label": "loop-exhaustion",
                          "file": "audit/punchout-log.md"},
    "F_missing_content": {"letter": "F", "label": "missing-content",
                          "file": "audit/punchout-missing-content.md"},
}
LETTER_TO_KEY = {v["letter"]: k for k, v in PUNCHOUTS.items()}


def _po_entry(key):
    return {"triggered": False, "file": PUNCHOUTS[key]["file"],
            "approved": False, "closure_evidence": None,
            "bypass_attempt": None}


RUN_STATE_TEMPLATE = {
    "run_id": "<run-id>",
    "current_step": "01-ingest",
    "initiated_by": "harness",
    "operator": "",
    "loop_counters": {"G1": 0, "G2": 0, "G3": 0, "G4": 0, "G5": 0},
    "loop_max": 2,
    "certifiable": True,
    "non_certifiable_reasons": [],
    "punchouts": {k: _po_entry(k) for k in PUNCHOUTS},
    "status": "in-progress",
}

BANNED_PATTERNS = [
    r"\b(I|we|our|us|me|my)\b",
    r"\b\w+(n't|'re|'ve|'ll|'d|'s)\b",
    r"\b(it is important to note|it should be noted|needless to say|as mentioned earlier)\b",
    r"\b(best-in-class|world-class|cutting-edge|state-of-the-art|industry-leading|top-notch)\b",
    r"\b(recently|currently|this period|nowadays|lately)\b",
    r"\b(always|never|everyone|no one)\b(?!\s+(user|account|device))",
    r"\b(leverage|synergy|robust solution|holistic)\b",
]

TONE_CHANGES_SCHEMA = {
    "type": "object",
    "required": ["changes", "tables_reviewed", "observations"],
    "properties": {
        "certifiable": {"type": "boolean"},
        "changes": {"type": "array", "items": {
            "type": "object",
            "required": ["location", "before", "after", "style_marker",
                         "reason", "assessment_function", "facts_changed"]}},
        "tables_reviewed": {"type": "array"},
        "observations": {"type": "array"},
    },
}

# === EMBEDDED SKILLS (regenerate: python s5-harness.py embed) ===
EMBEDDED_SKILLS = {
    "01": '---\nname: 01-ingest\ndescription: Step 01 of the quarterly security assessment workflow. Enumerates and validates all five input sources, producing inventory.json, evidence-index.json, and style-profile.json.\n---\n\n# Role\nYou are the Ingest agent for a quarterly Microsoft 365 security assessment update pipeline. Your only job is to establish the ground-truth artifacts that every downstream step will verify against.\n\n# Task\nProcess the five provided inputs and emit three validated JSON artifacts in `runs/<YYYY-QN>/`:\n1. `inventory.json` — catalog every input source with SHA-256 hashes and extract the prior report\'s section map.\n2. `evidence-index.json` — catalog every file in the Defender export folder and map it to a security domain.\n3. `style-profile.json` — extract the prior report\'s writing style markers for later tone enforcement.\n\n# Context\n- This step has no inbound guardrail; it creates the truth downstream gates check.\n- **Execution context:** this step runs inside `s5-harness.py`. Before executing, write `dispatch-received-01-ingest.json` — a verbatim copy of the dispatch you received (it must contain `"agent": "01-ingest"`). The harness executes the outbound G1 gate itself, owns `run-state.json`, and writes all audit records — write only this step\'s declared outputs plus the `.harness-step01-done` marker (written last).\n- Every artifact must validate against `../../schemas/<name>.schema.json`; the harness verifies this at G1 and halts on failure.\n- Inputs:\n  - `<PREVIOUS QUARTER\'S REPORT>` — baseline document to update\n  - `<2 QUARTERS AGO REPORT>` — historical context / update methodology reference\n  - `<DEFENDER EXPORT FOLDER LOCATION>` — current-quarter authoritative data\n  - `<CIS_Microsoft_365_Foundations_Benchmark PDF LOCATION>` — framework reference\n  - `<NIST.CSWP.29 PDF LOCATION>` — framework reference\n\n# Instructions\nEach instruction below is load-bearing and maps to an evaluation criterion.\n\n1. Resolve every input path. Record each source in `inventory.json.sources` with `{path, sha256, role}` where role is one of `prior-report`, `history-report`, `defender-export`, `cis-ref`, `nist-ref`. If any source is missing or unreadable, stop and report it — the harness records the G1 failure.\n2. Enumerate every file in the Defender export folder. Write the list to `inventory.json.export_files` and map each file to a security domain in `evidence-index.json.files` using `{path, sha256, domain, description}`. Valid domains: `secure-score`, `identities`, `devices`, `email-collab`, `endpoints`, `vulnerabilities`, `policies`, `alerts`, `other`. Any unmapped file is a G1 failure.\n3. Extract the prior report\'s section map as an ordered list of headings, subsections, and metric blocks into `inventory.json.section_map` using `{heading, order, subsections}`.\n4. Extract the prior report\'s style profile into `style-profile.json` with `voice`, `tense`, `sentence_style`, `phrasing_conventions`, `formatting_conventions`, and `banned_patterns`.\n5. Validate every emitted JSON file against its schema in `../../schemas/`. A schema violation is a G1 failure.\n6. Write `.harness-step01-done` last. Do not write audit records — the harness appends the step record (model, hashes, tokens, cost, gate result) to `audit/run-<run-id>.jsonl` and the G1 record to `audit/guardrails-<run-id>.jsonl`.\n\n# Output Specification\n- `runs/<YYYY-QN>/inventory.json` → `../../schemas/inventory.schema.json`\n- `runs/<YYYY-QN>/evidence-index.json` → `../../schemas/evidence-index.schema.json`\n- `runs/<YYYY-QN>/style-profile.json` → `../../schemas/style-profile.schema.json`\n- `runs/<YYYY-QN>/dispatch-received-01-ingest.json` — verbatim received dispatch\n- `runs/<YYYY-QN>/.harness-step01-done` — written last\n\n# Outbound Guardrail\nStep 02 (G1) will verify: all five sources hashed, export folder non-empty, every export file domain-mapped, section map present, and style profile present. Any missing item causes a hard fail.\n\n# Load-Bearing Check\n≥90% of lines in #Instructions directly enforce an evaluable criterion (input resolution, export mapping, section extraction, style extraction, schema validation, audit logging). No filler or decorative text is permitted.\n',
    "02": '---\nname: 02-findings-matrix\ndescription: Step 02 of the quarterly security assessment workflow. Runs inbound guardrail G1, then builds the quarter-over-quarter findings matrix (matrix.json) that drives all downstream steps.\n---\n\n# Role\nYou are the Findings-Matrix agent for a quarterly Microsoft 365 security assessment update pipeline. Your job is to compare the prior report against current-quarter evidence and produce a single authoritative matrix that downstream steps use to draft and review the report.\n\n# Task\nBuild `runs/<YYYY-QN>/matrix.json`: one row per finding/recommendation/observation from the prior report, classified by current-quarter evidence. (Inbound G1 has already been enforced deterministically by the harness.)\n\n# Context\n- **Execution context:** this step runs inside `s5-harness.py`. Before executing, write `dispatch-received-02-findings-matrix.json` — a verbatim copy of the dispatch you received (it must contain `"agent": "02-findings-matrix"`). The harness runs G1 deterministically before dispatching this step, runs G2 after it, owns `run-state.json`, and writes all audit and punch-out records — write only `matrix.json` plus the `.harness-step02-done` marker (written last).\n- Inputs: `inventory.json`, `evidence-index.json`, prior report, two-quarters-ago report, Defender export folder.\n- Outputs: `matrix.json` validated against `../../schemas/matrix.schema.json`.\n- Classifications: `improved`, `regressed`, `unchanged`, `resolved`, `newly-identified`, `unable-to-validate`.\n- The harness detects `unable-to-validate` rows (→ punch-out A) and `regressed` rows (→ punch-out C) at G2 and writes the punch-out files and trigger flags itself.\n\n# Instructions\nEach instruction below is load-bearing and maps to an evaluation criterion.\n\n1. Parse the prior report\'s `section_map` and enumerate every finding, recommendation, metric, and security observation as a candidate matrix row.\n2. Compare the prior report against the two-quarters-ago report to infer the established update methodology: how resolved findings were handled, how historical context was preserved, and the expected level of detail.\n3. For each candidate row, locate current-quarter evidence using `evidence-index.json`. If no evidence exists, classify the row as `unable-to-validate`.\n4. Populate each row with `{id, section, finding, prior_state, evidence_path, current_state, classification, update_required, cis_ref, nist_ref}`. The `id` must match pattern `F-[0-9]{3,}`.\n5. Enforce the evidence rule: every row must have an `evidence_path` unless its classification is `unable-to-validate`. Never infer remediation, improvement, regression, or new findings without evidence. Never fabricate metrics, dates, or framework mappings.\n6. Validate `matrix.json` against `../../schemas/matrix.schema.json`. A schema violation fails the harness\'s outbound G2 gate.\n7. Classify honestly — the harness deterministically detects `unable-to-validate` rows (→ punch-out A) and `regressed` rows (→ punch-out C) at G2, writes the punch-out files, and sets the trigger flags. You never write punch-out files or touch `run-state.json`.\n8. Write `.harness-step02-done` last. Do not write audit records — the harness appends the step record to `audit/run-<run-id>.jsonl` and the G2 record to `audit/guardrails-<run-id>.jsonl`.\n\n# Output Specification\n- `runs/<YYYY-QN>/matrix.json` → `../../schemas/matrix.schema.json`\n- `runs/<YYYY-QN>/dispatch-received-02-findings-matrix.json` — verbatim received dispatch\n- `runs/<YYYY-QN>/.harness-step02-done` — written last\n\n# Outbound Guardrail\nThe harness\'s G2 gate schema-validates `matrix.json`, triggers punch-outs A/C on their classifications, and blocks step 03 until every triggered punch-out is closed by a recorded human decision.\n\n# Load-Bearing Check\n≥90% of lines in #Instructions directly enforce an evaluable criterion (enumeration, methodology inference, evidence lookup, classification, anti-fabrication, schema validation, honest classification). No filler or decorative text is permitted.\n',
    "03": '---\nname: 03-draft-update\ndescription: Step 03 of the quarterly security assessment workflow. Produces one candidate updated report draft using either a minimal-update or a rewrite strategy (inbound G2 and punch-outs A & C are enforced deterministically by the harness before this step runs), controlled by a candidate_id parameter.\n---\n\n# Role\nYou are the Draft-Update agent for a quarterly Microsoft 365 security assessment update pipeline. Your job is to turn the findings matrix into a single candidate updated report draft, using the strategy and candidate identifier supplied by the coordinator.\n\n# Task\nProduce one candidate draft and its draft-map by updating the prior report section-by-section using the matrix and the human decisions recorded on punch-outs A/C. (Inbound G2 — schema validation plus open-punch-out blocking — has already been enforced deterministically by the harness; it never dispatches this step while A or C is open.)\n\n# Context\n- **Execution context:** this step runs inside `s5-harness.py`. Before executing, write `dispatch-received-03-draft-{candidate_id}.json` — a verbatim copy of the dispatch you received (it must contain `"agent": "03-draft-update"` and your `candidate_id`). The harness owns `run-state.json`, runs the outbound G3 gates after each review step, and writes all audit/punch-out records — write only this step\'s declared outputs plus the done-marker (`.harness-step03-done`, written last).\n- Inputs: `matrix.json`, prior report, `run-state.json` (read-only — for approved punch-out decisions), plus two parameters carried in the harness dispatch:\n  - `candidate_id`: either `a` or `b`\n  - `strategy`: either `minimal` or `rewrite`\n- Outputs:\n  - `runs/<YYYY-QN>/draft-candidate-{candidate_id}.md`\n  - `runs/<YYYY-QN>/draft-map-candidate-{candidate_id}.json`\n- `draft-map-candidate-{candidate_id}.json` must validate against `../../schemas/draft-map.schema.json`.\n\n# Instructions\nEach instruction below is load-bearing and maps to an evaluation criterion.\n\n1. Read `candidate_id` and `strategy` from the harness dispatch parameters. If either is missing or invalid, stop and report it — the harness records the failure. (The harness has already schema-validated `matrix.json` and confirmed every triggered punch-out A/C is closed before dispatching you — do not re-check approvals.)\n2. For each section in the prior report\'s section map, update the prose, metrics, and evidence from the matrix rows that belong to that section.\n3. Apply the requested `strategy`:\n   - `minimal`: preserve the prior report\'s wording and structure as much as possible. Change only metrics, evidence references, dates, and classification-derived states.\n   - `rewrite`: produce a stronger assessment-narrative framing. Lead with supported conclusions, interpret evidence for the client, and ensure every substantive finding answers what was assessed, what changed, why it matters, and what\'s next. Still preserve prior-report headings and order.\n4. Apply human decisions from closed punch-outs: mark `still-present` items accordingly, remove `removed` items, and defer `defer` items with an explicit note.\n5. Do not insert internal classification labels ("Regressed", "Improved", "Unable to validate") as literal report text unless that exact convention exists in the prior report.\n6. Distinguish states in prose as: confirmed by current data, not observed in current data, or unable to validate (defer-marked items only).\n7. Emit `draft-map-candidate-{candidate_id}.json` mapping each report section heading to the matrix row IDs used; every section must reference ≥1 row.\n8. Validate `draft-map-candidate-{candidate_id}.json` against `../../schemas/draft-map.schema.json`. A schema violation fails the harness\'s outbound G3 gate.\n9. Write `.harness-step03-done` last. Do not write audit records — the harness appends the step record to `audit/run-<run-id>.jsonl`.\n\n# Output Specification\n- `runs/<YYYY-QN>/draft-candidate-{candidate_id}.md` — candidate report draft\n- `runs/<YYYY-QN>/draft-map-candidate-{candidate_id}.json` → `../../schemas/draft-map.schema.json`\n- `runs/<YYYY-QN>/dispatch-received-03-draft-{candidate_id}.json` — verbatim received dispatch\n- `runs/<YYYY-QN>/.harness-step03-done` — written last\n\n# Outbound Guardrail\nThe harness\'s G3 gates (run after each candidate\'s adversarial review) diff `draft-candidate-{candidate_id}.md` section headings against the prior report, diff CIS/NIST references, and verify the draft-map has ≥1 matrix row per section. Orphan prose is a hard fail; heading/reference diffs trigger punch-outs B/D.\n\n# Load-Bearing Check\n≥90% of lines in #Instructions directly enforce an evaluable criterion (parameter validation, G2 validation, punch-out approval, strategy application, section update, punch-out application, label suppression, state distinction, draft-map coverage, schema validation, audit logging). No filler or decorative text is permitted.\n',
    "04a": '---\nname: 04-adversarial-review-candidate-a\ndescription: Adversarial reviewer for candidate draft A in the Stage 5 candidate-selection workflow. Runs in its own isolated context and produces review-candidate-a.json and review-candidate-a.md.\n---\n\n# Role\nYou are an adversarial reviewer for a quarterly Microsoft 365 security assessment update pipeline. Your job is to BREAK candidate draft A by re-deriving every factual claim from the Defender exports, not to approve it. You operate in your own context and must not consider how or by whom candidate A was produced.\n\n# Task\nProduce `runs/<YYYY-QN>/review-candidate-a.json` and `runs/<YYYY-QN>/review-candidate-a.md` by verifying every claim in `draft-candidate-a.md` against the evidence.\n\n# Context\n- **Execution context:** this step runs inside `s5-harness.py` in your own isolated agent context — you have no access to candidate-B artifacts. Before executing, write `dispatch-received-04-review-a.json` — a verbatim copy of the dispatch you received (it must contain `"agent": "04-adversarial-review-candidate-a"`). The harness runs the G3 structural/reference diffs and schema checks deterministically after you finish, owns `run-state.json`, and writes all audit/punch-out records — write only this step\'s declared outputs plus `.harness-step04a-done` (written last).\n- Inputs: `draft-candidate-a.md`, `draft-map-candidate-a.json`, `matrix.json`, Defender export files, prior report.\n- Outputs: `review-candidate-a.json` validated against `../../schemas/review.schema.json`, and `review-candidate-a.md`.\n- Any unresolved or rejected claim is recorded in the review; the downstream Draft-Selector decides what to do with it.\n\n# Instructions\nEach instruction below is load-bearing and maps to an evaluation criterion.\n\n1. For every claim in `draft-candidate-a.md` (metric, score, percentage, date, configuration statement, finding status), re-derive the value directly from the Defender exports. Do not trust the draft.\n2. Challenge every `resolved`, `unchanged`, and `improved` statement: demand current-quarter evidence. If no evidence exists, flag it.\n3. Flag fabrications: any finding, metric, date, or recommendation not traceable to both a matrix row and an evidence file must receive verdict `rejected` or `unresolved`.\n4. Flag stale framework references: any CIS/NIST citation that does not match the approved mappings must receive verdict `rejected` or `unresolved`.\n5. Emit `review-candidate-a.json` with one verdict per claim: `{claim_id, matrix_id, verdict, evidence_path, fix_diff, note}`. Verdicts are `confirmed`, `fixed`, `unresolved`, or `rejected`. `fix_diff` is REQUIRED when verdict is `fixed`.\n6. Apply all `fixed` verdicts to produce `review-candidate-a.md`. Do not apply `unresolved` or `rejected` verdicts.\n7. Validate `review-candidate-a.json` against `../../schemas/review.schema.json`. A schema violation fails the harness\'s outbound G3 gate.\n8. Write `.harness-step04a-done` last. Do not write audit records — the harness appends the step record and G3 gate record, and triggers punch-outs B/D itself when its diffs fire.\n\n# Output Specification\n- `runs/<YYYY-QN>/review-candidate-a.json` → `../../schemas/review.schema.json`\n- `runs/<YYYY-QN>/review-candidate-a.md` — candidate A draft with accepted fixes applied\n- `runs/<YYYY-QN>/dispatch-received-04-review-a.json` — verbatim received dispatch\n- `runs/<YYYY-QN>/.harness-step04a-done` — written last\n\n# Outbound Guardrail\nThe Draft-Selector step will compare `review-candidate-a.json` with `review-candidate-b.json`, select the better candidate, and run the G4 zero-unresolved-claims gate on the winner.\n\n# Load-Bearing Check\n≥90% of lines in #Instructions directly enforce an evaluable criterion (claim re-derivation, state challenge, fabrication flagging, stale reference flagging, verdict schema, fix application, schema validation). No filler or decorative text is permitted.\n',
    "04b": '---\nname: 04-adversarial-review-candidate-b\ndescription: Adversarial reviewer for candidate draft B in the Stage 5 candidate-selection workflow. Runs in its own isolated context and produces review-candidate-b.json and review-candidate-b.md.\n---\n\n# Role\nYou are an adversarial reviewer for a quarterly Microsoft 365 security assessment update pipeline. Your job is to BREAK candidate draft B by re-deriving every factual claim from the Defender exports, not to approve it. You operate in your own context and must not consider how or by whom candidate B was produced.\n\n# Task\nProduce `runs/<YYYY-QN>/review-candidate-b.json` and `runs/<YYYY-QN>/review-candidate-b.md` by verifying every claim in `draft-candidate-b.md` against the evidence.\n\n# Context\n- **Execution context:** this step runs inside `s5-harness.py` in your own isolated agent context — you have no access to candidate-A artifacts. Before executing, write `dispatch-received-04-review-b.json` — a verbatim copy of the dispatch you received (it must contain `"agent": "04-adversarial-review-candidate-b"`). The harness runs the G3 structural/reference diffs and schema checks deterministically after you finish, owns `run-state.json`, and writes all audit/punch-out records — write only this step\'s declared outputs plus `.harness-step04b-done` (written last).\n- Inputs: `draft-candidate-b.md`, `draft-map-candidate-b.json`, `matrix.json`, Defender export files, prior report.\n- Outputs: `review-candidate-b.json` validated against `../../schemas/review.schema.json`, and `review-candidate-b.md`.\n- Any unresolved or rejected claim is recorded in the review; the downstream Draft-Selector decides what to do with it.\n\n# Instructions\nEach instruction below is load-bearing and maps to an evaluation criterion.\n\n1. For every claim in `draft-candidate-b.md` (metric, score, percentage, date, configuration statement, finding status), re-derive the value directly from the Defender exports. Do not trust the draft.\n2. Challenge every `resolved`, `unchanged`, and `improved` statement: demand current-quarter evidence. If no evidence exists, flag it.\n3. Flag fabrications: any finding, metric, date, or recommendation not traceable to both a matrix row and an evidence file must receive verdict `rejected` or `unresolved`.\n4. Flag stale framework references: any CIS/NIST citation that does not match the approved mappings must receive verdict `rejected` or `unresolved`.\n5. Emit `review-candidate-b.json` with one verdict per claim: `{claim_id, matrix_id, verdict, evidence_path, fix_diff, note}`. Verdicts are `confirmed`, `fixed`, `unresolved`, or `rejected`. `fix_diff` is REQUIRED when verdict is `fixed`.\n6. Apply all `fixed` verdicts to produce `review-candidate-b.md`. Do not apply `unresolved` or `rejected` verdicts.\n7. Validate `review-candidate-b.json` against `../../schemas/review.schema.json`. A schema violation fails the harness\'s outbound G3 gate.\n8. Write `.harness-step04b-done` last. Do not write audit records — the harness appends the step record and G3 gate record, and triggers punch-outs B/D itself when its diffs fire.\n\n# Output Specification\n- `runs/<YYYY-QN>/review-candidate-b.json` → `../../schemas/review.schema.json`\n- `runs/<YYYY-QN>/review-candidate-b.md` — candidate B draft with accepted fixes applied\n- `runs/<YYYY-QN>/dispatch-received-04-review-b.json` — verbatim received dispatch\n- `runs/<YYYY-QN>/.harness-step04b-done` — written last\n\n# Outbound Guardrail\nThe Draft-Selector step will compare `review-candidate-a.json` with `review-candidate-b.json`, select the better candidate, and run the G4 zero-unresolved-claims gate on the winner.\n\n# Load-Bearing Check\n≥90% of lines in #Instructions directly enforce an evaluable criterion (claim re-derivation, state challenge, fabrication flagging, stale reference flagging, verdict schema, fix application, schema validation). No filler or decorative text is permitted.\n',
    "04sel": '---\nname: 04b-draft-selector\ndescription: Step 04b of the Stage 5 security assessment workflow. Compares the adversarial reviews of candidate drafts A and B, selects the best candidate, and prepares the handoff to tone-assessmentV2 (the G4 zero-unresolved-claims gate is enforced deterministically by the harness after this step).\n---\n\n# Role\nYou are the Draft-Selector agent for a Stage 5 quarterly Microsoft 365 security assessment update pipeline. Your job is to compare two adversarially reviewed candidate drafts and choose the one that gives the cleanest path to a G4 pass.\n\n# Task\nScore both candidates, select the winner, copy the winner\'s artifacts to the canonical names, and write a selection report. (Punch-out closure and schema validation are already enforced by the harness before dispatch; the G4 zero-unresolved-claims gate runs deterministically in the harness after you finish.)\n\n# Context\n- Inputs:\n  - `review-candidate-a.json`, `review-candidate-a.md`\n  - `review-candidate-b.json`, `review-candidate-b.md`\n  - `draft-candidate-a.md`, `draft-candidate-b.md`\n  - `draft-map-candidate-a.json`, `draft-map-candidate-b.json`\n  - `matrix.json`, `run-state.json`\n- Outputs:\n  - `runs/<YYYY-QN>/draft.md`\n  - `runs/<YYYY-QN>/draft-map.json`\n  - `runs/<YYYY-QN>/review.json`\n  - `runs/<YYYY-QN>/reviewed.md`\n  - `runs/<YYYY-QN>/selection-report.json`\n- **Execution context:** this step runs inside `s5-harness.py`. Before executing, write `dispatch-received-04b-select.json` — a verbatim copy of the dispatch you received (it must contain `"agent": "04b-draft-selector"`). The harness owns `run-state.json`, runs the outbound G4 gate itself (zero unresolved claims, `fix_diff` presence, coverage, sentinels), and writes all audit records — write only this step\'s declared outputs plus `.harness-step04sel-done` (written last).\n\n# Instructions\nEach instruction below is load-bearing and maps to an evaluation criterion.\n\n1. Score each candidate from its `review-candidate-*.json`:\n   - Start with 0 demerits.\n   - Add 3 demerits per `rejected` claim.\n   - Add 2 demerits per `unresolved` claim.\n   - Add 1 demerit per `fixed` claim that lacks a `fix_diff` (schema validation should catch this; if it does not, count it here).\n   - Subtract 1 demerit per 10% of claims that are `confirmed` (rounded down), to a maximum reduction of 3 demerits.\n   - Coverage: if claims reviewed < matrix row IDs cited in the candidate\'s draft-map, add 5 demerits.\n2. Select the candidate with the lower demerit score as the winner. If tied, prefer candidate B (rewrite strategy) unless candidate B has any `rejected` claim and candidate A does not; in that case prefer candidate A.\n3. Copy the winner\'s files to the canonical names:\n   - Winner `draft-candidate-*.md` → `draft.md`\n   - Winner `draft-map-candidate-*.json` → `draft-map.json`\n   - Winner `review-candidate-*.json` → `review.json`\n   - Winner `review-candidate-*.md` → `reviewed.md`\n4. Write `selection-report.json` with `{winner, candidate_a_demerits, candidate_b_demerits, selection_reason}` — the harness appends the G4 result.\n5. Write `.harness-step04sel-done` last. Do not write audit records and do not touch `run-state.json` — the harness runs G4, handles loop-back (re-dispatching 03 with your selection report as feedback) and loop-exhaustion escalation (punch-out E), and appends the step record to `audit/run-<run-id>.jsonl`.\n\n# Output Specification\n- `runs/<YYYY-QN>/draft.md` — selected report draft\n- `runs/<YYYY-QN>/draft-map.json` → `../../schemas/draft-map.schema.json`\n- `runs/<YYYY-QN>/review.json` → `../../schemas/review.schema.json`\n- `runs/<YYYY-QN>/reviewed.md` — selected draft with accepted fixes applied\n- `runs/<YYYY-QN>/selection-report.json` — selection rationale and scores\n- `runs/<YYYY-QN>/dispatch-received-04b-select.json` — verbatim received dispatch\n- `runs/<YYYY-QN>/.harness-step04sel-done` — written last\n\n# Outbound Guardrail\nThe harness\'s G4 gate verifies zero `unresolved`/`rejected` claims in the selected `review.json`, `fix_diff` on every `fixed` claim, coverage against `draft-map.json`, and writes the `.g4-passed` sentinel before dispatching `05-tone-consistency`. G4 failure loops back to step 03 (max 2 iterations → punch-out E).\n\n# Load-Bearing Check\n≥90% of lines in #Instructions directly enforce an evaluable criterion (scoring, selection, file promotion, report completeness). No filler or decorative text is permitted.\n',
    "05": '---\nname: 05-tone-consistency\ndescription: Step 05 of the tone-assessmentV2 workflow. Performs an assessment-narrative synthesis of ONE report draft (inbound G4 is enforced deterministically by the harness before this step runs) — converting telemetry dumps into quarter-over-quarter security analysis within the template\'s structure, across prose AND tables — never altering facts — producing toned.md and tone-changes.json.\n---\n\n# Role\nYou are the Tone-Consistency EDITOR for a Microsoft 365 security assessment report pipeline — a professional editor and assessment synthesizer, not a style matcher. You perform a comprehensive assessment synthesis of exactly ONE document — `draft.md`. "Style only" means the SUBSTANCE is frozen — every fact, finding, measurement, recommendation, control reference, and client meaning is preserved — NOT that the wording must stay close to the draft. You are expected to substantially revise prose, and to review and correct table text, wherever professional and analytical standards demand it.\n\n# Task\nG4 has already been enforced deterministically by the harness — proceed directly to synthesis and produce `runs/<run-id>/toned.md` and `runs/<run-id>/tone-changes.json`. Only `draft.md` is ever rewritten; the template is read-only. "The document" means every paragraph, list, heading, AND every table cell.\n\n**Execution context:** this step runs inside `s5-harness.py` (`python s5-harness.py run`). The harness executes the deterministic G4 gate itself, owns `run-state.json` status transitions, and writes all per-run audit records (`audit/run-<run-id>.jsonl`, `audit/guardrails-<run-id>.jsonl`, `audit/success-<run-id>.md`, `audit/punchout-<run-id>.md`) — write only this step\'s declared outputs (`toned.md`, `tone-changes.json`, and `punchout-missing-content.md` on a missing-content halt) into the run directory.\n\n# Inputs\nAll inputs live in `runs/<run-id>/inputs/`:\n\n| # | File | Role |\n|---|------|------|\n| 1 | `draft.md` | The document being edited — the ONLY file modified. If supplied as .docx, convert to markdown first; record the SHA-256 of both the source file and the converted `draft.md` |\n| 2 | `template` | AUTHORITATIVE for structure: section order, headings, formatting conventions, table layouts, required elements. Wins every conflict |\n\n# Context\n- Outputs: `toned.md` and `tone-changes.json`, validated against `../../schemas/tone-changes.schema.json`.\n- G4 is enforced deterministically by `s5-harness.py (g4_check)` and logged by the harness before this step runs — do not re-run it.\n- Guardrail failures are handled by the harness (loop-back to this step, max 2 iterations, then human escalation) — on a re-invocation, fix what the G5 failure reported.\n- `<run-id>` is the run ID supplied by the user. All audit logging (`audit/run-<run-id>.jsonl`, `audit/guardrails-<run-id>.jsonl`, `audit/success-<run-id>.md`, `audit/punchout-<run-id>.md`) is written by the harness — this step writes only its declared outputs.\n\n# Instructions\nEach instruction below is load-bearing and maps to an evaluation criterion.\n\n## A. Gate and structural target\n1. **G4 was already enforced deterministically by the harness** — do not re-run input checks. Template provenance: the template placed in `runs/<run-id>/inputs/` by the operator is confirmed by definition — never substitute another file. **Certifiability discipline:** `certifiable`/`non_certifiable_reasons` in `run-state.json` are maintained by the harness and are write-once downward — the flag may flip `false` on a punch-out or bypass attempt but may never be set back to `true` except by a recorded human decision (see 11).\n2. **Derive the structural target from the template:** required section order, headings, formatting conventions, required elements, and every table\'s column layout and cell conventions (bold titles, status formats, header rows). Classify each template placeholder as **required** or **optional**; a placeholder marked `IF AVAILABLE`, `OPTIONAL`, or equivalent is optional.\n\n## B. Prose synthesis\n3. **Assessment-narrative evaluation** — BEFORE rewriting, evaluate every substantive assessment section for analytical depth. A section fails if it primarily reproduces source data, product recommendations, scores, control statuses, export fields, or framework mappings without explaining their security significance. For each section, confirm all applicable elements (checks for the section as a whole, not a mandatory sentence sequence), then rewrite data-first passages into conclusion-first prose:\n   - **Condition** — what the evidence establishes about the present security posture.\n   - **Quarter movement** — what materially changed, improved, regressed, or remained unresolved during the assessment period.\n   - **Evidence** — the specific supplied observations supporting the conclusion.\n   - **Significance** — why the condition matters to the client\'s security posture and business risk. Every substantive paragraph makes the "so what" explicit, grounded in the evidence. If the evidence supports only an operational, configuration, or prioritization conclusion, state that — do not invent a business-impact statement.\n   - **Qualification** — what cannot be concluded from the available evidence.\n   - **Recommended response** — what action should be taken and why.\n   - **Calibration** — for every positive control state, state what it does and does not prove; for every risk, state what is known and unknown. Do not upgrade "control enabled" to "risk resolved" unless the evidence supports it.\n\n   Tables, scores, export values, Microsoft recommendations, and CIS/NIST mappings are data, not analysis; the prose around a table must interpret it. However, table captions, row labels, and narrative cells within a table must also be reviewed for sentence discipline, consultative tone, and client usefulness (see Section C).\n\n   Explicit failure conditions: data without conclusion, metrics without significance, findings without quarterly context, recommendations without analytical traceability, positive findings without calibrated limitations.\n   - **Security Awareness exemption:** sections or call-out boxes whose heading (case-insensitive) matches "Security Awareness" are EXCLUDED from the conclusion-first rewrite and from table-cell rewriting. Preserve content and facts unchanged; apply only template formatting alignment and banned-pattern removal. Do not infer quarter movement, significance, or cross-theme relationships for this content.\n4. **Quarterly review requirement** — for each domain with comparable historical evidence, determine: (a) preceding-quarter condition; (b) current-quarter condition; (c) material movement; (d) attribution — verified improvement/regression, scoring or measurement movement, or unattributable; (e) carried-in unresolved findings; (f) newly material findings; (g) post-quarter evidence that must not be presented as reporting-quarter progress. Anchor every movement claim to the specific quarter or observation period; avoid "recently," "currently," "this period" unless the evidence names the date — this applies to table cells as well as prose. Where comparison is unsupported, say so explicitly; never manufacture movement.\n5. **Cross-signal synthesis** — synthesize related evidence into themes (authentication and privileged access; legacy authentication and access-policy enforcement; information protection and classification; external collaboration and data egress; endpoint exposure and vulnerability management; logging, detection, and response readiness). Explain relationships among signals before individual controls. Preserve individual control values and references as supporting evidence, normally in tables.\n6. **Professional and client-consultative standards** — apply throughout, to prose and table text alike. The report is a client-facing consultant\'s security assessment, not an audit, attestation, compliance report, or Secure Score commentary.\n   - **Narrative arc:** the document reads as one coherent story of the quarter — where posture stood, what improved, regressed, or remained unresolved, and what it means next. Transitions and cross-section context come ONLY from facts in `draft.md`.\n   - **Voice:** third-person, formal, consultative.\n   - **Tense:** past tense for observed states and measurements during the quarter; present tense for standing facts, current-state descriptions, and recommendations.\n   - **Concise, explanatory prose:** expand telegraphic sentences only where the draft under-explains; never leave a bare metric unexplained when the draft contains the context.\n   - **Clarity and cadence:** declarative sentences, one claim per sentence, no run-ons, no fragments.\n   - **Terminology:** precise security vocabulary; one name per finding, control, framework, and evidence status across the whole document, including every table.\n   - **Hedging:** state supported conclusions directly; state uncertainty only when it changes the conclusion, scope, severity, movement interpretation, or response; do not repeat a limitation merely to demonstrate rigor.\n   - **Banned patterns:** first person, contractions, colloquialisms, filler, marketing language, unqualified superlatives, unexplained jargon.\n   - **Explanatory style:** finding = condition → evidence → implication; recommendation = action → rationale. If the draft supplies only part of a structure, complete the sentence without inventing the missing substance.\n   - **Client-consultative standard:** lead with the supported conclusion, then evidence, then why it matters, then the next step. Do not lead with methodology, scoring mechanics, evidence limitations, or framework mappings unless they determine the conclusion. Tables carry detailed control evidence and mappings; prose explains posture, significance, priorities, and next steps without duplicating table contents. Every substantive domain leaves the reader knowing (1) the assessment, (2) what changed, (3) why it matters, (4) what to do next.\n   - **Plain voice over noun stacks:** break up Microsoft-style noun stacks and product-vendor grammar; write normal English with clear subjects and verbs.\n   - **Sentence discipline and active framing:** one idea per sentence; semicolons only between closely related clauses; evidence gaps integrated as context ("validate service owners, as deployment evidence was not available"), never left as raw fragments ("X: not available"); scope stated in plain language; every substantive finding or risk paired with a concrete client action.\n   - **Language correctness and sensitivity:** correct US English spelling, grammar, and punctuation; inclusive, people-first language; neutral assessor perspective with no attributed intent or blame; no sensitive geopolitical references or contentious framing.\n\n## C. Table review (mandatory — every table, every row)\n7. **Inventory and review every table.** Before handoff, list every table in `draft.md` (location, purpose, row count) and review each row. A table carried forward without row-level review fails this step even if the prose is complete. Record in `tone-changes.json` (see 13) which tables were reviewed and left unchanged.\n8. **Table cell standards.** Classify each column, then apply:\n   - **Evidence-label columns** (e.g., "Defender / Secure Score control evidence") and **reference columns** (CIS IDs, NIST IDs, Level, quarter labels, priority numbers): shorthand is permitted; do not rewrite values; correct only spelling and banned patterns.\n   - **Metric shorthand** such as `Identity 96.72% (59/61)` or `DLP 0/5, To address` is permitted where it is the cell\'s evidence.\n   - **Narrative columns** (Interpretation, Assessment interpretation, Description, Details, Status narrative): every sentence has a subject and a verb. Verbless evidence-gap fragments are prohibited — "Resources and business scope not established." becomes "Resources and business scope were not established."; "No exposure metrics; no comparison can be made." becomes "No exposure metrics were provided, so no comparison can be made." Split semicolon-joined action and rationale into separate sentences. Replace comma splices.\n   - All banned patterns, vague temporal terms, and terminology rules in 6 apply to every narrative cell.\n   - **Status and evidence vocabulary** is consistent across all tables (e.g., do not mix "Not assessed", "CIS not tested", and "Exact CIS configuration not assessed" unless the draft establishes that they mean different things; if the meaning is unclear, keep the wording and record an observation under 10).\n9. **Table structure is frozen.** Do not add, remove, merge, split, or reorder rows or columns, and do not move content between cells. Apply template table conventions (header row, bold recommendation titles) where they do not alter content. Where the template requires a format the draft cannot supply (e.g., `MM.DD.YYYY - <STATUS>` with no per-item dates in the draft), retain the draft value and record a template deviation in `tone-changes.json` `observations`.\n10. **Table–prose consistency check (detect, never fix).** For every control, score, point value, status, quarter, and CIS/NIST reference that appears in both a table and prose, confirm the values match. Where a table provides components of a reported total (e.g., control points within a category score), reconcile them. Also check that cross-references between sections are accurate (e.g., a sentence describing the topic of the awareness guidance matches the awareness content). Do NOT correct mismatches — they are substance. Record each one as an observation (see 13) for human review.\n\n## D. Placeholders, labels, and punch-out\n11. **Missing-content punch-out.** If the template requires a **required** section or element that `draft.md` has no content for, do NOT fabricate content: write `punchout-missing-content.md` into the run directory describing the missing section and the decision options (provide content / drop section / defer), and STOP — do not produce `toned.md`. The harness detects the punch-out file, sets `triggered: true` + `certifiable: false` in `run-state.json`, and records the halt in `audit/punchout-log.md`. **Optional** placeholders (see 2) never trigger a punch-out: omit the placeholder, and do not insert a stand-in sentence such as "Evidence was not provided" when the gap is already stated in the section.\n    - **No continuation while unapproved.** No continuation — for any reason, including a direct human instruction — is permitted while a punch-out is `triggered: true` and `approved: false`. Verbally "approving" in chat, or writing `approved: true` without a matching `audit/punchout-log.md` row, is a self-granted approval and a G5 hard fail downstream.\n    - **Certifiability discipline (all punch-outs and guardrails).** `certifiable` becomes `false` whenever: a punch-out triggers (A or E); a G4 or G5 loop reaches `loop_max`; or any bypass attempt occurs — any continuation directed or attempted past a gate, halt, or `loop_max`. A recorded bypass attempt makes `certifiable: false` **permanent**; there is no restore path for it. Other `false` states may be restored only by: (a) a `audit/punchout-log.md` row with matching `run_id`, non-empty `human decision`, `resolved by`, and `resolved at`; then (b) setting `certifiable: true`, `approved: true`, and `closure_evidence` citing that row. Approvals never carry across `run_id`s; a decision is valid only for the run it was made under. A "stop" decision leaves the run dead (`certifiable: false`, `status: stopped`). The skill provides no human-waiver path for a G5 hard fail — a human decision to accept a violation produces a **non-certifiable** result, not a waived pass.\n    - **Non-certifiable outputs.** If outputs are produced while `certifiable: false`, `tone-changes.json` MUST carry top-level `"certifiable": false`. `toned.md` is then a working artifact for review only — no deliverable may be emitted for this run.\n12. **Internal classification labels.** Do not carry literal internal classification labels ("Regressed", "Improved", "Unable to validate") into `toned.md` as report text unless that exact convention exists in the template. If the draft contains such labels, preserve them as `observations` under 13 rather than silently deleting them.\n\n## E. Substance freeze and accountability\n13. **Record every edit in `tone-changes.json`.**\n    - One record per prose edit and one record per edited **table row**. Each record MUST include:\n      - `location` — section › subsection; for tables, `Section › <table name> › row: <first-cell text>`;\n      - `before` / `after` — the original and rewritten text (for tables, the full markdown row line);\n      - `style_marker` — the convention applied (e.g., `template_structure`, `template_formatting`, `narrative`, `voice`, `tense`, `cadence`, `terminology`, `hedging`, `explanatory_style`, `banned_patterns`, `client_significance`, `temporal_precision`, `significance_calibration`, `plain_voice`, `spelling`, `grammar`, `punctuation`, `inclusive_language`, `neutral_perspective`, `geopolitical_sensitivity`, `sentence_discipline`, `complete_sentences`, `scope_clarity`, `evidence_integration`, `active_framing`, `actionable_recommendations`, `assessment_first`, `consultant_voice`, `plain_language`, `qualification_discipline`, `narrative_evidence_balance`, `client_usefulness`, `table_interpretation`);\n      - `reason` — one sentence stating what the edit accomplished analytically;\n      - `assessment_function` — `executive_conclusion`, `quarter_movement`, `cross_signal_synthesis`, `evidence_interpretation`, `security_significance`, `evidence_limitation`, `recommendation_traceability`, `historical_context`, `template_structure`, or `professional_tone`;\n      - `facts_changed` — boolean; must be `false`. Any `true` is a substance-freeze violation and a G5 hard fail.\n    - Add a top-level `tables_reviewed` array: one entry per draft table with `location`, `purpose`, `rows`, `rows_edited`.\n    - Add a top-level `observations` array: one entry per item from 9 and 10 with `location`, `type` (`table_prose_mismatch`, `total_reconciliation`, `cross_reference`, `terminology`, `template_deviation`), `detail`, and `action_required` ("confirm", "correct in draft", or "accept deviation").\n    - Add a top-level `certifiable` boolean mirroring `run-state.json` (see 11): `false` when outputs were produced while the run is non-certifiable.\n14. **HARD CONSTRAINT — substance freeze.** Wording may change; substance may not. Every number, date, percentage, finding title, CIS/NIST reference, classification outcome, measurement, recommendation, piece of evidence, and client-facing meaning — in prose AND tables — remains identical to `draft.md`. Evidence is quoted or faithfully restated, never re-written, re-scoped, or re-cast. Narrative framing may add interpretation, transitions, and context but no fact, cause, event, or outcome absent from the draft. Errors and inconsistencies found in the draft are reported under 13 `observations`, never corrected.\n15. **Validate and self-check before handoff.**\n    - Validate `tone-changes.json` against `../../schemas/tone-changes.schema.json`.\n    - Confirm `toned.md` has no net change in factual tokens versus `draft.md`.\n    - Run the banned-pattern, vague-temporal, and fragment checks over **prose and table cells** (Security Awareness excluded). Any hit is fixed before handoff.\n    - Confirm every table line in `toned.md` is either verbatim from `draft.md` or the `after` of a row-level record.\n16. **Do not write audit records.** The harness appends the step record to `audit/run-<run-id>.jsonl` (with model, hashes, tokens, cost, and the inbound gate result) and the G4 record to `audit/guardrails-<run-id>.jsonl`. This step\'s only outputs are the files below.\n\n# Output Specification\n- `runs/<run-id>/toned.md` — synthesized assessment draft (only file rewritten)\n- `runs/<run-id>/tone-changes.json` — edits (prose and table rows), `tables_reviewed`, `observations`; validated against `../../schemas/tone-changes.schema.json`\n- `runs/<run-id>/punchout-missing-content.md` — only when instruction 11 fires (write and stop; no `toned.md`)\n\n# Outbound Guardrail\nStep 06-adversarial-review (G5) scores `toned.md` for assessment quality — conclusion-first analysis per section, an explicit quarter-over-quarter thesis, cross-signal synthesis — plus template conformance and a substance-freeze diff against `draft.md`. G5 scans table cells with the same banned-pattern, temporal, and sentence-discipline checks as prose, and verifies table edits line by line against `tone-changes.json`. It rejects any record with `facts_changed: true`, any unrecorded table edit, and any draft table missing from `tables_reviewed`. A `toned.md` that is data-first, stylistically unchanged, word-patched, or that carries draft tables forward unreviewed fails even with zero banned patterns in the prose. Step 06 also refuses to finalize any run whose `run-state.json` or `tone-changes.json` shows `certifiable: false` without a matching human-decision row in `audit/punchout-log.md`.\n\n# Load-Bearing Check\n≥90% of lines in #Instructions directly enforce an evaluable criterion (template provenance, structural target, assessment-narrative evaluation, quarterly review, cross-signal synthesis, professional and client-consultative standards, table inventory, table cell standards, table structure freeze, table–prose consistency, missing-content punch-out and certifiability discipline, label handling, edit recording, substance freeze, self-check). No filler or decorative text is permitted.\n',
    "06": '---\nname: 06-adversarial-review\ndescription: Step 02 of the tone-assessment workflow. Runs the inbound G5 adversarial review gate (assessment quality, substance freeze, change accountability, punch-out closure) over step 05\'s output, then assembles the final client deliverable and closes the audit trail.\n---\n\n# Role\nYou are the **Adversarial Review & Finalize agent** for the tone-assessmentV2 pipeline. Your first responsibility is to independently challenge the output of step 05 — `toned.md` and `tone-changes.json` — against the G5 guardrails. Only after G5 passes and all punch-outs are resolved do you assemble the final client deliverable and close the audit trail.\n\n# Task\nRun the G5 adversarial review gate. If G5 passes, finalize the run by emitting the final report and `audit-report.md` into the run directory, then write `.harness-step06-done`. If G5 fails, write `g5-judgment.md` into the run directory listing the specific failing check(s) — do NOT write the done marker or the deliverable — and call `drive` again; the harness loops back to step 05 or escalates to punch-out E at `loop_max`.\n\n**Execution context:** this step runs inside `s5-harness.py` (`python s5-harness.py run`). Deterministic G5 pre-checks (schema, banned patterns, substance-freeze token diff, accountability, two-key punch-out closure) run as executable code before you are invoked — your review is the judgment layer on top. The harness owns `run-state.json` transitions and writes all per-run audit records (`audit/run-<run-id>.jsonl`, `audit/guardrails-<run-id>.jsonl`, `audit/success-<run-id>.md`, `audit/punchout-<run-id>.md`; the shared aggregate logs are derived via `python s5-harness.py rebuild-logs`) — write only the final deliverable and `audit-report.md`.\n\n# Context\n- Inputs: `toned.md`, `draft.md`, `template`, `tone-changes.json`, `run-state.json`, all audit artifacts — all inside this workflow\'s `runs/<YYYY-QN>/` and `audit/` directories.\n- Outputs: final client deliverable and `audit-report.md` — written into `runs/<run-id>/`. All audit files (`audit/run-<run-id>.jsonl`, `audit/guardrails-<run-id>.jsonl`, `audit/success-<run-id>.md`, `audit/punchout-<run-id>.md`) are written by the harness, never by this step.\n- G5 has two layers: deterministic pre-checks in `s5-harness.py (g5_check)` (executed by the harness before this step is invoked) and the adversarial judgment review performed here. Both are logged by the harness.\n- A run succeeds iff G5 passes, every triggered punch-out is two-key closed, the final report is emitted, and the run is certifiable — the harness records the result.\n\n# Instructions\nEach instruction below is load-bearing and maps to an evaluation criterion.\n\n## Phase 1 — G5 Adversarial Review (must pass before finalizing)\n\n1. Run G5 assessment-quality check — did the rewrite actually produce assessment-quality analysis throughout, not merely violate no style rules: score `toned.md` for (a) conformance to the template (required sections present and ordered, headings and formatting matched); (b) analytical depth — every substantive assessment section is conclusion-first, containing the applicable elements: condition, quarter movement, evidence, significance, qualification, recommended response, calibration — and no section merely reproduces source data, scores, export fields, or framework mappings without security significance — data without conclusion, metrics without significance, findings without quarterly context, and recommendations without analytical traceability are each a G5 failure condition (except any section titled "Security Awareness" case-insensitively, which is exempt from the conclusion-first/synthesis requirement but still subject to the substance freeze and banned-pattern checks); significance is explicitly tied to the client\'s business risk ("so what"); movement claims are temporally anchored to the specific quarter/observation period; positive findings are calibrated with their limitations and risks with their known/unknown scope; no Microsoft-style noun stacks or product-vendor grammar remain; (c) quarterly thesis — for each domain with comparable evidence, the report establishes preceding-vs-current-quarter condition, material movement, attribution (verified improvement/regression, measurement movement, or unattributable), carried-in unresolved findings, and newly material findings, and never presents post-quarter evidence as reporting-quarter progress; where comparison is unsupported it says so explicitly; (d) cross-signal synthesis — related controls are analyzed as themes (authentication/privileged access, legacy auth/access-policy, information protection, external collaboration/data egress, endpoint exposure/vulnerability management, logging/detection/response readiness) with relationships explained before individual controls; (e) professional editorial quality — third-person formal consultative voice, consistent tense, precise terminology, declarative cadence, hedged/evidence-attributed claims, banned patterns absent; spelling, grammar, and punctuation conventions correct; inclusive and neutral language; no sensitive geopolitical references or contentious framing; every sentence has a clear subject and verb and states one idea; semicolons connect only closely related clauses; evidence gaps are integrated as supporting context, not left as raw fragments; scope is stated in plain language; every substantive finding or risk is paired with a concrete client action; (f) client-consultative quality — the document reads as consultant guidance, not audit/Secure Score commentary; sections lead with supported conclusions rather than methodology or evidence limitations; technical findings are interpreted for the client; Microsoft recommendations/CIS/NIST are supporting inputs, not the narrative voice; concise consultative prose without defensive caveat-stacking; every substantive domain answers what was assessed, what changed, why it matters, and what\'s next, grounded in the evidence; table captions, row labels, and narrative cells are also checked for banned patterns, vague temporal terms, and sentence discipline; A `toned.md` that is data-first, stylistically unchanged, still terse/list-like, only superficially word-patched, or that carries draft tables forward unreviewed is a G5 failure even if no banned pattern is present. Log the result to `audit/guardrails.jsonl`.\n2. Run G5 substance freeze check: extract every number, date, percentage, measurement, finding title, CIS/NIST reference, classification outcome, piece of evidence, and recommendation from `toned.md` — including those inside tables, charts, and embedded evidence blocks; each must exist in `draft.md` unchanged. Any new/altered factual token, any evidence that was re-written or re-scoped, any narrative framing that introduces a fact/cause/outcome absent from `draft.md`, any table row or cell whose meaning has shifted, or a paraphrase that shifts the client-facing meaning of a finding or recommendation — is a G5 failure.\n3. Run G5 change-accountability check: `tone-changes.json` must validate against `../../schemas/tone-changes.schema.json` and contain both `tables_reviewed` and `observations` arrays. Every edit between `draft.md` and `toned.md` must be recorded with `location`, `before`, `after`, `style_marker`, `reason`, `assessment_function`, and `facts_changed`. Table edits are verified row by row against `tone-changes.json`; any unrecorded table row rewrite is a G5 failure. Every draft table must appear in `tables_reviewed`. Any record with `facts_changed: true` is a hard fail. Coverage check: the set of `assessment_function` values must demonstrate assessment-quality synthesis across the report — a change log consisting only of `template_structure`/`professional_tone` records indicates no analytical rewrite occurred and is a G5 failure. An unrecorded edit is a G5 failure.\n4. On G5 failure: report `G5 failure` and the specific failing check(s) — do NOT loop back, update `run-state.json`, or write audit files. The harness increments `loop_counters.G5`, decides loop-back vs. punch-out-E escalation, and records the failure.\n5. Run G5 certifiability and punch-out closure check (the deterministic layer checks this first; re-verify as the adversarial reviewer — a self-granted approval that slipped through is still a hard fail here) — a two-key check, both artifacts required. For every punch-out in `run-state.json` with `triggered: true`: (a) `approved: true` AND `closure_evidence` citing a `audit/punchout-log.md` row for the same `run_id` with non-empty `human decision`, `resolved by`, and `resolved at`. An `approved: true` flag without the matching log row is a self-granted approval and a G5 hard fail. A decision recorded under a different `run_id` does not count — approvals never carry across runs. If `run-state.json` `certifiable` is `false`: (b) verify `non_certifiable_reasons` is non-empty and each reason is either resolved by a logged human decision (restored `certifiable: true` with `closure_evidence`) or still open — any open reason with `certifiable: true` is a G5 hard fail. A recorded `bypass_attempt` makes the run permanently non-certifiable — there is no restore path; no deliverable may be emitted and the result is a non-certifiable run. The skill provides no human-waiver path for a G5 hard fail. Any unapproved triggered punch-out, any `certifiable: false` output without closure evidence, or `tone-changes.json` marked `"certifiable": false` is a G5 hard fail — STOP and wait for human sign-off.\n\n## Phase 2 — Finalization (run only after Phase 1 passes)\n\n6. Assemble `toned.md` into the final client deliverable using the template\'s delivery format (file type, naming, front matter).\n7. Write `audit-report.md` summarizing the run: steps executed, guardrail results, punch-outs raised and resolved, tone-change statistics (edits by style_marker and assessment_function coverage), narrative/structural changes applied, and end-to-end outcome.\n8. Success criterion: a run counts as end-to-end successful iff G5 passed, the run is certifiable (`certifiable: true` with all `non_certifiable_reasons` resolved), every triggered punch-out was resolved with a recorded human decision, and the final report was emitted. The harness appends the result to `audit/success-<run-id>.md` and the final step record to `audit/run-<run-id>.jsonl` — never write these yourself.\n\n# Output Specification\n- Final client deliverable (report file, template delivery format) — only when Phase 1 passes\n- `runs/<YYYY-QN>/audit-report.md` — run summary, including G5 adversarial review result\n\n# Outbound Guardrail\nThere is no downstream gate. The G5 adversarial review inside this step is the final quality checkpoint before delivery.\n\n# Load-Bearing Check\n≥90% of lines in #Instructions directly enforce an evaluable criterion (G5 adversarial review assessment quality, G5 substance freeze, G5 change accountability, failure reporting, punch-out closure, final deliverable assembly, audit-report, success criterion). No filler or decorative text is permitted.\n',
}
# === END EMBEDDED SKILLS ===

# Pipeline steps: id -> (agent name, expected outputs, skill dir)
STEP_AGENTS = {
    "01": "01-ingest",
    "02": "02-findings-matrix",
    "03a": "03-draft-update",
    "03b": "03-draft-update",
    "04a": "04-adversarial-review-candidate-a",
    "04b": "04-adversarial-review-candidate-b",
    "04sel": "04b-draft-selector",
    "05": "05-tone-consistency",
    "06": "06-adversarial-review",
}
SKILLS = {
    "01": ROOT / ".github" / "skills" / "01-ingest" / "SKILL.md",
    "02": ROOT / ".github" / "skills" / "02-findings-matrix" / "SKILL.md",
    "03": ROOT / ".github" / "skills" / "03-draft-update" / "SKILL.md",
    "04a": ROOT / ".github" / "skills" /
        "04-adversarial-review-candidate-a" / "SKILL.md",
    "04b": ROOT / ".github" / "skills" /
        "04-adversarial-review-candidate-b" / "SKILL.md",
    "04sel": ROOT / ".github" / "skills" / "04b-draft-selector" / "SKILL.md",
    "05": ROOT / ".github" / "skills" / "05-tone-consistency" / "SKILL.md",
    "06": ROOT / ".github" / "skills" / "06-adversarial-review" / "SKILL.md",
}
EXPECTED_OUTPUTS = {
    "01": ["inventory.json", "evidence-index.json", "style-profile.json",
           "dispatch-received-01.json"],
    "02": ["matrix.json", "dispatch-received-02.json"],
    "03a": ["draft-candidate-a.md", "draft-map-candidate-a.json",
            "dispatch-received-03a.json"],
    "03b": ["draft-candidate-b.md", "draft-map-candidate-b.json",
            "dispatch-received-03b.json"],
    "04a": ["review-candidate-a.json", "review-candidate-a.md",
            "dispatch-received-04a.json"],
    "04b": ["review-candidate-b.json", "review-candidate-b.md",
            "dispatch-received-04b.json"],
    "04sel": ["draft.md", "draft-map.json", "review.json", "reviewed.md",
              "selection-report.json", "dispatch-received-04sel.json"],
    "05": ["toned.md", "tone-changes.json", "dispatch-received-05.json"],
    "06": ["audit-report.md", "dispatch-received-06.json"],
}
# FSM order: status -> (gate before it, step it executes)
STEP_FLOW = ["01", "02", "03a", "03b", "04a", "04b", "04sel", "05", "06"]
GATE_BEFORE = {"01": None, "02": "G1", "03a": "G2", "03b": None,
               "04a": None, "04b": "G3a", "04sel": "G3b",
               "05": "G4", "06": "G5"}
DONE_MARKER = {s: f".harness-step{s}-done" for s in STEP_FLOW}
VALID_RESULTS = ("pass", "fail", "halted", "stopped")

# ---------------------------------------------------------------------------
# Common helpers
# ---------------------------------------------------------------------------


def load_config():
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    p = ROOT / "s5-harness.config.json"
    if p.exists():
        for k, v in json.loads(p.read_text(encoding="utf-8")).items():
            cfg[k] = v
    return cfg


def run_dir(run_id):
    return ROOT / "runs" / run_id


def state_path(run_id):
    return run_dir(run_id) / "run-state.json"


def load_state(run_id):
    state = json.loads(state_path(run_id).read_text(encoding="utf-8"))
    # Normalize legacy/partial states: fill missing counters + punch-outs
    lc = state.setdefault("loop_counters", {})
    for g in ("G1", "G2", "G3", "G4", "G5"):
        lc.setdefault(g, 0)
    po = state.setdefault("punchouts", {})
    for key in PUNCHOUTS:
        po.setdefault(key, _po_entry(key))
    return state


def save_state(run_id, state):
    state_path(run_id).write_text(json.dumps(state, indent=2) + "\n",
                                  encoding="utf-8")


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(path):
    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def init_run(run_id, operator=""):
    rd = run_dir(run_id)
    rd.mkdir(parents=True, exist_ok=True)
    (rd / "inputs").mkdir(exist_ok=True)
    (ROOT / "audit").mkdir(exist_ok=True)
    if not state_path(run_id).exists():
        template = ROOT / "templates" / "run-state.json"
        state = (json.loads(template.read_text(encoding="utf-8"))
                 if template.exists() else
                 json.loads(json.dumps(RUN_STATE_TEMPLATE)))
        for key in PUNCHOUTS:
            state.setdefault("punchouts", {}).setdefault(key, _po_entry(key))
        state["run_id"] = run_id
        state["initiated_by"] = "harness"
        state["operator"] = operator
        save_state(run_id, state)
    return rd


def find_input(run_id, stem):
    inputs = run_dir(run_id) / "inputs"
    if not inputs.exists():
        return None
    matches = sorted(inputs.glob(f"{stem}.*"),
                     key=lambda p: (p.suffix != ".md", p.name))
    return matches[0] if matches else None


def defender_files(run_id):
    d = run_dir(run_id) / "inputs" / "defender-export-folder"
    return sorted(p for p in d.glob("**/*") if p.is_file()) if d.exists() else []


def _utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

# ---------------------------------------------------------------------------
# Audit writers
# ---------------------------------------------------------------------------


def append_step_record(run_id, record):
    record.setdefault("ts", _utcnow())
    record.setdefault("run_id", run_id)
    with (ROOT / "audit" / f"run-{run_id}.jsonl").open(
            "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def append_guardrail_record(run_id, gate, result, checks,
                            iteration=None, note=None):
    rec = {"run_id": run_id, "gate": gate,
           "result": result, "checks": checks, "ts": _utcnow()}
    if iteration is not None:
        rec["iteration"] = iteration
    if note:
        rec["note"] = note
    with (ROOT / "audit" / f"guardrails-{run_id}.jsonl").open(
            "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def append_success_log(run_id, result, punchouts, iterations, notes):
    if result not in VALID_RESULTS:
        raise ValueError(f"bad result {result!r}")
    row = (f"| {_today()} | {run_id} | {result} | {punchouts} | "
           f"{iterations} | {notes} |\n")
    with (ROOT / "audit" / f"success-{run_id}.md").open(
            "a", encoding="utf-8") as f:
        f.write(row)


def append_punchout_log(run_id, punchout, trigger, bypass_performed,
                        bypass_result, decision="", resolved_by="",
                        resolved_at=""):
    row = (f"| {_today()} | {run_id} | {punchout} | {trigger} | "
           f"{bypass_performed} | {bypass_result} | {decision} | "
           f"{resolved_by} | {resolved_at} |\n")
    with (ROOT / "audit" / f"punchout-{run_id}.md").open(
            "a", encoding="utf-8") as f:
        f.write(row)


def punchout_log_has_closure(run_id, letter=None):
    for name in ("punchout-log.md", f"punchout-{run_id}.md"):
        log = ROOT / "audit" / name
        if not log.exists():
            continue
        for line in log.read_text(encoding="utf-8").splitlines():
            if not line.strip().startswith("|"):
                continue
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cols) < 9 or cols[1] != run_id \
                    or not cols[7] or not cols[8] \
                    or "bypass test" in cols[3].lower():
                continue
            if letter and not cols[2].startswith(f"{letter}:"):
                continue
            return True
    return False


def rebuild_logs():
    out = {}
    agg = ROOT / "audit" / "guardrails.jsonl"
    existing = set(agg.read_text(encoding="utf-8").splitlines()) \
        if agg.exists() else set()
    added = 0
    with agg.open("a", encoding="utf-8") as f:
        for pf in sorted((ROOT / "audit").glob("guardrails-*.jsonl")):
            for line in pf.read_text(encoding="utf-8").splitlines():
                if line.strip() and line not in existing:
                    f.write(line + "\n")
                    existing.add(line)
                    added += 1
    out["guardrails.jsonl"] = added

    for per_run, aggregate in (("success-*.md", "success-log.md"),
                               ("punchout-*.md", "punchout-log.md")):
        agg = ROOT / "audit" / aggregate
        existing = set(agg.read_text(encoding="utf-8").splitlines()) \
            if agg.exists() else set()
        added = 0
        with agg.open("a", encoding="utf-8") as f:
            for pf in sorted((ROOT / "audit").glob(per_run)):
                if pf.name in ("punchout-missing-content.md",
                               "punchout-unable-to-validate.md",
                               "punchout-regressions.md",
                               "punchout-framework-mappings.md",
                               "punchout-structure-changes.md"):
                    continue
                for line in pf.read_text(encoding="utf-8").splitlines():
                    if line.strip().startswith("|") and line not in existing:
                        f.write(line + "\n")
                        existing.add(line)
                        added += 1
        out[aggregate] = added
    _rebuild_success_report()
    return {"appended_rows": out}


def _rebuild_success_report():
    log = ROOT / "audit" / "success-log.md"
    prod, test = [], []
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            if not line.strip().startswith("|"):
                continue
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cols) < 3 or cols[1].lower() in ("run id", "run-id",
                                                   "---", ""):
                continue
            (test if "test" in cols[1].lower() else prod).append(line)
    header = ("| date | run id | result | punch-outs | iterations "
              "| notes |\n|---|---|---|---|---|---|\n")
    pp = sum(1 for r in prod if "| pass |" in r)
    ph = sum(1 for r in prod if "| halted |" in r)
    tp = sum(1 for r in test if "| pass |" in r)
    th = sum(1 for r in test if "| halted |" in r)
    lines = ["# Success Report (derived — regenerated by rebuild-logs)",
             "",
             "Gate-test runs (run-ids containing 'Test') deliberately",
             "trip guards; 'halted' is the expected pass state for them.",
             "",
             f"## Production runs — {pp} finalized / {len(prod)} "
             f"records ({ph} halted)", "", header]
    lines += prod or ["(none)"]
    lines += ["", f"## Gate-test runs — {tp} finalized / {len(test)} "
              f"records ({th} halted — expected)", "", header]
    lines += test or ["(none)"]
    lines.append("")
    (ROOT / "audit" / "success-report.md").write_text(
        "\n".join(lines), encoding="utf-8")

# ---------------------------------------------------------------------------
# Metering — never null; method always disclosed
# ---------------------------------------------------------------------------


def _estimate_tokens(text, chars_per_token):
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text)), "estimated-tiktoken"
    except Exception:
        cpt = max(1, chars_per_token)
        return max(1, round(len(text) / cpt)), f"estimated-chars{cpt:g}"


def _usage_from_session_log(path):
    if not path or not Path(path).exists():
        return None
    tin = tout = 0
    found = False
    for line in Path(path).read_text(encoding="utf-8",
                                     errors="replace").splitlines():
        if not line.strip().startswith("{"):
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        usage = rec.get("usage") or rec.get("tokenUsage") or {}
        i = (usage.get("input_tokens") or usage.get("prompt")
             or usage.get("prompt_tokens"))
        o = (usage.get("output_tokens") or usage.get("completion")
             or usage.get("completion_tokens"))
        if isinstance(i, int) and isinstance(o, int):
            tin += i
            tout += o
            found = True
    return (tin, tout) if found else None


def meter_step(config, step_prompt, step_output):
    mcfg = config.get("metering", {})
    usage = _usage_from_session_log(mcfg.get("session_log_path"))
    if usage:
        tokens_in, tokens_out, method = usage[0], usage[1], "session_log"
    else:
        cpt = mcfg.get("estimation_chars_per_token", 1.75)
        tokens_in, _ = _estimate_tokens(step_prompt, cpt)
        tokens_out, method = _estimate_tokens(step_output, cpt)
    price = config.get("price_usd_per_1k_tokens", {})
    cost = (tokens_in / 1000 * price.get("input", 0)
            + tokens_out / 1000 * price.get("output", 0))
    return {"tokens_in": tokens_in, "tokens_out": tokens_out,
            "cost_usd": round(cost, 6), "metering_method": method}

# ---------------------------------------------------------------------------
# Mini schema validator (subset: type/required/properties/enum/items)
# ---------------------------------------------------------------------------


def _mini_validate(instance, schema, path="$"):
    errors = []
    t = schema.get("type")
    if t:
        ok = (
            (t == "object" and isinstance(instance, dict)) or
            (t == "array" and isinstance(instance, list)) or
            (t == "string" and isinstance(instance, str)) or
            (t == "boolean" and isinstance(instance, bool)) or
            (t == "integer" and isinstance(instance, int)
             and not isinstance(instance, bool)) or
            (t == "number" and isinstance(instance, (int, float))
             and not isinstance(instance, bool)))
        if not ok:
            return [f"{path}: expected {t}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in enum")
    if t == "object":
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}.{req}: required")
        for key, subschema in schema.get("properties", {}).items():
            if key in instance:
                errors += _mini_validate(instance[key], subschema,
                                         f"{path}.{key}")
    if t == "array":
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: fewer than {schema['minItems']} items")
        if "items" in schema:
            for i, item in enumerate(instance):
                errors += _mini_validate(item, schema["items"], f"{path}[{i}]")
    return errors


def _load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, str(exc)


def _schema_file(name):
    p = ROOT / "schemas" / f"{name}.schema.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _schema_check(instance, name):
    """Validate `instance` against schemas/<name>.schema.json (or embedded
    subset for tone-changes). Returns (errors, validator_name)."""
    schema = _schema_file(name)
    if schema is None and name == "tone-changes":
        schema = TONE_CHANGES_SCHEMA
    if schema is None:
        return [], "no-schema-file"
    try:
        import jsonschema
        jsonschema.validate(instance, schema)
        return [], "jsonschema"
    except ImportError:
        return _mini_validate(instance, schema), "builtin-mini-validator"
    except Exception as exc:
        return [getattr(exc, "message", str(exc))], "jsonschema"


def _verify_dispatch(run_id, step):
    """Dispatch-verification check: the sub-agent must record the dispatch
    instruction it received (dispatch-received-<step>.json); its `agent`
    field must equal the FSM's expected agent for this step. A mismatch is
    a deterministic gate failure — the coordinator cannot smuggle work to
    an unapproved agent."""
    rd = run_dir(run_id)
    f = rd / f"dispatch-received-{step}.json"
    if not f.exists():
        return {"check": "dispatch-verified", "result": "fail",
                "detail": f"{f.name} missing — sub-agent did not record "
                          f"the dispatch instruction it received"}
    data, err = _load_json(f)
    if err:
        return {"check": "dispatch-verified", "result": "fail",
                "detail": f"{f.name} not valid JSON: {err}"}
    expected = STEP_AGENTS[step]
    got = data.get("agent")
    if got != expected:
        return {"check": "dispatch-verified", "result": "fail",
                "detail": f"coordinator dispatched '{got}' but FSM "
                          f"expected '{expected}' — outputs rejected"}
    return {"check": "dispatch-verified", "result": "pass",
            "agent": got}


# ---------------------------------------------------------------------------
# G1 — ingest gate (after step 01)
# ---------------------------------------------------------------------------

_REQUIRED_SOURCES = {"prior-report", "history-report", "defender-export",
                     "cis-ref", "nist-ref"}
_VALID_DOMAINS = {"secure-score", "identities", "devices", "email-collab",
                  "endpoints", "vulnerabilities", "policies", "alerts",
                  "other"}


def g1_check(run_id):
    rd = run_dir(run_id)
    checks = [_verify_dispatch(run_id, "01")]

    # Source files present in inputs/
    for stem, label in (("prior-report", "prior-report"),
                        ("history-report", "history-report")):
        p = find_input(run_id, stem)
        checks.append({"check": f"input:{label}", "result":
                       "pass" if p and p.stat().st_size else "fail",
                       "file": p.name if p else f"inputs/{stem}.* missing"})
    for stem, label in (("cis", "cis-ref"), ("nist", "nist-ref")):
        p = find_input(run_id, stem)
        checks.append({"check": f"input:{label}", "result":
                       "pass" if p and p.stat().st_size else "fail",
                       "file": p.name if p else f"inputs/{stem}.* missing"})
    n_export = len(defender_files(run_id))
    checks.append({"check": "input:defender-export",
                   "result": "pass" if n_export else "fail",
                   "files": n_export})

    # Step-01 outputs + schema
    inv, _ = _load_json(rd / "inventory.json") \
        if (rd / "inventory.json").exists() else (None, "missing")
    idx, _ = _load_json(rd / "evidence-index.json") \
        if (rd / "evidence-index.json").exists() else (None, "missing")
    sp, _ = _load_json(rd / "style-profile.json") \
        if (rd / "style-profile.json").exists() else (None, "missing")
    for name, data in (("inventory", inv), ("evidence-index", idx),
                       ("style-profile", sp)):
        if data is None:
            checks.append({"check": f"schema:{name}", "result": "fail",
                           "detail": f"{name}.json missing or invalid"})
            continue
        errors, validator = _schema_check(data, name)
        checks.append({"check": f"schema:{name}",
                       "result": "fail" if errors else "pass",
                       "validator": validator,
                       "detail": "; ".join(errors[:8]) if errors else ""})

    if isinstance(inv, dict):
        roles = {s.get("role") for s in inv.get("sources", [])
                 if isinstance(s, dict)}
        checks.append({"check": "all-5-sources-catalogued",
                       "result": "pass" if _REQUIRED_SOURCES <= roles
                       else "fail",
                       "detail": "" if _REQUIRED_SOURCES <= roles
                       else f"missing roles: "
                            f"{sorted(_REQUIRED_SOURCES - roles)}"})
        bad_hash = [s.get("path", "?") for s in inv.get("sources", [])
                    if not re.fullmatch(r"[0-9a-f]{64}",
                                        str(s.get("sha256", "")))]
        checks.append({"check": "source-hashes-recorded",
                       "result": "fail" if bad_hash else "pass",
                       "detail": "; ".join(bad_hash[:5]) if bad_hash else ""})
        checks.append({"check": "export-files-enumerated",
                       "result": "pass" if inv.get("export_files")
                       else "fail"})
        checks.append({"check": "section-map-present",
                       "result": "pass" if inv.get("section_map")
                       else "fail"})

    if isinstance(idx, dict):
        unmapped = [f.get("path", "?") for f in idx.get("files", [])
                    if f.get("domain") not in _VALID_DOMAINS]
        checks.append({"check": "all-exports-domain-mapped",
                       "result": "fail" if unmapped else "pass",
                       "detail": "; ".join(unmapped[:5]) if unmapped else ""})

    return {"result": "pass" if all(c["result"] == "pass" for c in checks)
            else "fail", "checks": checks}


# ---------------------------------------------------------------------------
# G2 — matrix gate (after step 02); triggers punch-outs A and C
# ---------------------------------------------------------------------------


def _write_punchout_file(run_id, key, title, rows):
    p = ROOT / PUNCHOUTS[key]["file"]
    lines = [f"# Punch-out {PUNCHOUTS[key]['letter']}: {title}",
             f"run: {run_id}", f"triggered: {_utcnow()}", "",
             "The harness flagged the following — a human decision is",
             "required before the pipeline continues:", ""]
    lines += rows
    lines.append("")
    p.write_text("\n".join(lines), encoding="utf-8")


def _matrix_rows(run_id):
    data, _ = _load_json(run_dir(run_id) / "matrix.json")
    return data.get("rows", []) if isinstance(data, dict) else []


def g2_check(run_id, state):
    rd = run_dir(run_id)
    checks = [_verify_dispatch(run_id, "02")]

    data, err = _load_json(rd / "matrix.json") \
        if (rd / "matrix.json").exists() else (None, "missing")
    if err:
        checks.append({"check": "matrix-present", "result": "fail",
                       "detail": f"matrix.json: {err}"})
        return {"result": "fail", "checks": checks,
                "triggered": {}}
    errors, validator = _schema_check(data, "matrix")
    checks.append({"check": "schema:matrix",
                   "result": "fail" if errors else "pass",
                   "validator": validator,
                   "detail": "; ".join(errors[:8]) if errors else ""})
    if errors:
        return {"result": "fail", "checks": checks,
                "triggered": {}}

    rows = data.get("rows", [])
    no_evidence = [r.get("id", "?") for r in rows
                   if not r.get("evidence_path")
                   and r.get("classification") != "unable-to-validate"]
    checks.append({"check": "every-row-has-evidence-or-uv",
                   "result": "fail" if no_evidence else "pass",
                   "detail": "; ".join(no_evidence[:8]) if no_evidence
                   else ""})

    # Punch-out detection — deterministic, harness-owned
    triggered = {}
    uv = [r for r in rows if r.get("classification") == "unable-to-validate"]
    if uv:
        _trigger_punchout(state, "A_unable_to_validate",
                          "matrix rows classified unable-to-validate")
        if not state["punchouts"]["A_unable_to_validate"]["triggered_file"]:
            _write_punchout_file(
                run_id, "A_unable_to_validate",
                "findings that cannot be validated by current data",
                [f"- {r.get('id','?')} ({r.get('section','?')}): "
                 f"{r.get('finding','?')}" for r in uv])
        triggered["A"] = uv
    reg = [r for r in rows if r.get("classification") == "regressed"]
    if reg:
        _trigger_punchout(state, "C_regressions",
                          "matrix rows classified regressed")
        if not state["punchouts"]["C_regressions"]["triggered_file"]:
            _write_punchout_file(
                run_id, "C_regressions",
                "findings classified regressed — confirm the evidence "
                "supports each regression",
                [f"- {r.get('id','?')} ({r.get('section','?')}): "
                 f"{r.get('finding','?')}" for r in reg])
        triggered["C"] = reg

    # Gate result: triggered punch-outs must be two-key closed to pass
    blocked = [k for k in ("A_unable_to_validate", "C_regressions")
               if state["punchouts"][k]["triggered"]
               and not _closed(run_id, k, state)]
    checks.append({"check": "punch-outs-A-C-closed",
                   "result": "fail" if blocked else "pass",
                   "detail": ("awaiting closure: " + ", ".join(blocked)
                              if blocked else
                              "no open punch-outs at G2")})
    return {"result": "fail" if any(c["result"] == "fail" for c in checks)
            else "pass", "checks": checks, "triggered": triggered}


# ---------------------------------------------------------------------------
# G3 — candidate review gate (after each 04 reviewer); punches B and D
# ---------------------------------------------------------------------------

_CIS_NIST_RE = re.compile(
    r"\bCIS[\s-]?\d+(?:\.\d+)*\b|\bNIST[\s-]?[A-Z]{2}(?:\.[A-Z0-9-]+)*\b",
    re.IGNORECASE)
_HEADING = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)
_SECTION_HEADING = re.compile(r"^#{2,6}\s+\S", re.MULTILINE)


def _headings_of(path):
    """Section headings only (H2+) — the document title (H1) is not a
    structural element and must not trip punch-out D."""
    if not path or not path.exists():
        return set()
    return {h.strip().lower() for h in
            _SECTION_HEADING.findall(path.read_text(
                encoding="utf-8", errors="replace"))}


def _refs_of(path):
    if not path or not path.exists():
        return set()
    return {m.upper() for m in
            _CIS_NIST_RE.findall(path.read_text(
                encoding="utf-8", errors="replace"))}


def g3_check(run_id, state, cand):
    rd = run_dir(run_id)
    step = f"04{cand}"
    checks = [_verify_dispatch(run_id, step)]

    dm, _ = _load_json(rd / f"draft-map-candidate-{cand}.json") \
        if (rd / f"draft-map-candidate-{cand}.json").exists() \
        else (None, "missing")
    if dm is None:
        checks.append({"check": f"schema:draft-map-{cand}", "result": "fail",
                       "detail": "draft-map missing or invalid"})
    else:
        errors, validator = _schema_check(dm, "draft-map")
        checks.append({"check": f"schema:draft-map-{cand}",
                       "result": "fail" if errors else "pass",
                       "validator": validator,
                       "detail": "; ".join(errors[:8]) if errors else ""})
        # every mapped section references >=1 matrix row
        secs = dm.get("sections") or dm.get("mapping") or {}
        if isinstance(secs, dict):
            orphans = [k for k, v in secs.items() if not v]
        else:
            orphans = [s.get("heading") or s.get("section", "?")
                       for s in secs if isinstance(s, dict)
                       and not (s.get("matrix_ids") or
                                s.get("matrix_rows") or s.get("rows"))]
        checks.append({"check": f"draft-map-{cand}-coverage",
                       "result": "fail" if orphans else "pass",
                       "detail": ("sections with no matrix row: "
                                  + ", ".join(orphans[:8]) if orphans
                                  else "every section references >=1 row")})

    rv, _ = _load_json(rd / f"review-candidate-{cand}.json") \
        if (rd / f"review-candidate-{cand}.json").exists() \
        else (None, "missing")
    if rv is None:
        checks.append({"check": f"schema:review-{cand}", "result": "fail",
                       "detail": "review-candidate missing or invalid"})
    else:
        errors, validator = _schema_check(rv, "review")
        checks.append({"check": f"schema:review-{cand}",
                       "result": "fail" if errors else "pass",
                       "validator": validator,
                       "detail": "; ".join(errors[:8]) if errors else ""})

    prior = find_input(run_id, "prior-report")
    cand_path = rd / f"draft-candidate-{cand}.md"

    # Punch-out B: CIS/NIST mapping changes vs the prior report
    new_refs = sorted(_refs_of(cand_path) - _refs_of(prior))
    if new_refs:
        _trigger_punchout(state, "B_framework_mappings",
                          "framework mappings changed vs prior report")
        if not state["punchouts"]["B_framework_mappings"]["triggered_file"]:
            _write_punchout_file(
                run_id, "B_framework_mappings",
                f"CIS/NIST references added or changed in candidate "
                f"{cand} — approve each change",
                [f"- {r} (new in draft-candidate-{cand}.md)"
                 for r in new_refs])

    # Punch-out D: structural heading changes vs the prior report
    prior_h, cand_h = _headings_of(prior), _headings_of(cand_path)
    added, removed = sorted(cand_h - prior_h), sorted(prior_h - cand_h)
    if added or removed:
        _trigger_punchout(state, "D_structure_changes",
                          "report sections added or removed vs prior report")
        if not state["punchouts"]["D_structure_changes"]["triggered_file"]:
            _write_punchout_file(
                run_id, "D_structure_changes",
                f"section structure changed in candidate {cand} — "
                f"approve or reject each change",
                [f"+ {h} (added)" for h in added]
                + [f"- {h} (removed)" for h in removed])

    blocked = [k for k in ("B_framework_mappings", "D_structure_changes")
               if state["punchouts"][k]["triggered"]
               and not _closed(run_id, k, state)]
    checks.append({"check": "punch-outs-B-D-closed",
                   "result": "fail" if blocked else "pass",
                   "detail": ("awaiting closure: " + ", ".join(blocked)
                              if blocked else
                              "no open punch-outs at G3")})
    return {"result": "fail" if any(c["result"] == "fail" for c in checks)
            else "pass", "checks": checks}


# ---------------------------------------------------------------------------
# G4 — selector gate (after 04b-draft-selector)
# ---------------------------------------------------------------------------


def g4_check(run_id):
    rd = run_dir(run_id)
    checks = [_verify_dispatch(run_id, "04sel")]

    sr, _ = _load_json(rd / "selection-report.json") \
        if (rd / "selection-report.json").exists() else (None, "missing")
    if sr is None:
        checks.append({"check": "schema:selection-report", "result": "fail",
                       "detail": "selection-report.json missing/invalid"})
    else:
        errors, validator = _schema_check(sr, "selection-report")
        checks.append({"check": "schema:selection-report",
                       "result": "fail" if errors else "pass",
                       "validator": validator,
                       "detail": "; ".join(errors[:8]) if errors else ""})

    rv, _ = _load_json(rd / "review.json") \
        if (rd / "review.json").exists() else (None, "missing")
    unresolved = fixed_no_diff = 0
    if rv is None:
        checks.append({"check": "schema:review-final", "result": "fail",
                       "detail": "review.json missing/invalid"})
    else:
        errors, validator = _schema_check(rv, "review")
        checks.append({"check": "schema:review-final",
                       "result": "fail" if errors else "pass",
                       "validator": validator,
                       "detail": "; ".join(errors[:8]) if errors else ""})
        verdicts = (rv.get("verdicts") or rv.get("claims") or
                    ([] if not isinstance(rv, list) else rv))
        for v in verdicts:
            if not isinstance(v, dict):
                continue
            if v.get("verdict") in ("unresolved", "rejected"):
                unresolved += 1
            if v.get("verdict") == "fixed" and not v.get("fix_diff"):
                fixed_no_diff += 1
    checks.append({"check": "zero-unresolved-claims",
                   "result": "fail" if unresolved else "pass",
                   "detail": f"{unresolved} unresolved/rejected claims"
                   if unresolved else "all claims confirmed or fixed"})
    if fixed_no_diff:
        checks.append({"check": "fixed-verdicts-have-diff",
                       "result": "fail",
                       "detail": f"{fixed_no_diff} 'fixed' verdicts "
                                 f"lack fix_diff"})
    else:
        checks.append({"check": "fixed-verdicts-have-diff",
                       "result": "pass"})

    for name in ("draft.md", "draft-map.json", "reviewed.md"):
        p = rd / name
        checks.append({"check": f"output:{name}",
                       "result": "pass" if p.exists() and p.stat().st_size
                       else "fail"})

    if (rd / "draft-map.json").exists():
        dm, _ = _load_json(rd / "draft-map.json")
        errors, validator = _schema_check(dm, "draft-map")
        checks.append({"check": "schema:draft-map-final",
                       "result": "fail" if errors else "pass",
                       "validator": validator,
                       "detail": "; ".join(errors[:8]) if errors else ""})

    if all(c["result"] == "pass" for c in checks):
        (rd / ".g4-passed").write_text(json.dumps(
            {"gate": "G4", "run_id": run_id}, indent=2), encoding="utf-8")
    return {"result": "fail" if any(c["result"] == "fail" for c in checks)
            else "pass", "checks": checks}


# ---------------------------------------------------------------------------
# G5 — tone/final gate (V2 deterministic checks, adapted)
# ---------------------------------------------------------------------------

_FACT_RE = re.compile(
    r"\b\d{1,3}(?:\.\d+)?%|\b\d{4}-\d{2}-\d{2}\b|\b\d+/\d+\b|\b\d+\.\d+\b"
    r"|\b\d{4}\b|\bCIS[\s-]?\d+(?:\.\d+)*\b|\bNIST[\s-]?[A-Z0-9.-]+\b",
    re.IGNORECASE)

_ANALYTICAL_FUNCTIONS = {
    "executive_conclusion", "quarter_movement", "cross_signal_synthesis",
    "evidence_interpretation", "security_significance", "evidence_limitation",
    "recommendation_traceability", "historical_context"}


def g5_check(run_id):
    rd = run_dir(run_id)
    checks = [_verify_dispatch(run_id, "05")]
    toned_path, tc_path = rd / "toned.md", rd / "tone-changes.json"

    if (rd / ".g4-passed").exists():
        checks.append({"check": "D1-g4-sentinel", "result": "pass"})
    else:
        checks.append({"check": "D1-g4-sentinel", "result": "fail",
                       "detail": ".g4-passed missing"})
    if not toned_path.exists() or not tc_path.exists():
        checks.append({"check": "outputs-present", "result": "fail",
                       "detail": "toned.md or tone-changes.json missing"})
        return {"result": "fail", "checks": checks}

    toned_text = toned_path.read_text(encoding="utf-8", errors="replace")
    tone_changes, terr = _load_json(tc_path)
    if terr:
        checks.append({"check": "D2-schema-valid", "result": "fail",
                       "detail": f"not valid JSON: {terr}"})
        return {"result": "fail", "checks": checks}

    errors, validator = _schema_check(tone_changes, "tone-changes")
    checks.append({"check": "D2-schema-valid",
                   "result": "fail" if errors else "pass",
                   "validator": validator,
                   "detail": "; ".join(errors[:10]) if errors else ""})

    pats = [re.compile(p, re.IGNORECASE) for p in BANNED_PATTERNS]
    first_person = pats[0]
    hits = []
    for i, line in enumerate(toned_text.splitlines(), 1):
        for j, pat in enumerate(pats):
            m = pat.search(line)
            if m and j == 0:
                rest = line[m.end():].lstrip()
                if m.group(0)[0].isupper() and rest[:1].isupper():
                    m = first_person.search(line, m.end())
                    if not m:
                        continue
                    rest = line[m.end():].lstrip()
                    if m.group(0)[0].isupper() and rest[:1].isupper():
                        continue
            if m:
                hits.append(f"line {i}: {m.group(0)!r}")
                break
        if len(hits) >= 10:
            break
    checks.append({"check": "D3-banned-patterns",
                   "result": "fail" if hits else "pass",
                   "detail": ("; ".join(hits) if hits
                              else "0 hits over prose and table cells")})

    draft_path = rd / "draft.md"
    draft_text = (draft_path.read_text(encoding="utf-8", errors="replace")
                  if draft_path.exists() else "")
    if not draft_text:
        checks.append({"check": "D4-substance-freeze", "result": "fail",
                       "detail": "draft.md unavailable"})
    else:
        draft_tokens = {t.lower() for t in _FACT_RE.findall(draft_text)}
        new_tokens = sorted({t for t in _FACT_RE.findall(toned_text)
                             if t.lower() not in draft_tokens})
        checks.append({"check": "D4-substance-freeze",
                       "result": "fail" if new_tokens else "pass",
                       "detail": ("factual tokens absent from draft: "
                                  + ", ".join(new_tokens[:15]) if new_tokens
                                  else "all factual tokens traceable to draft")})

    problems = []
    for rec in tone_changes.get("changes", []):
        if rec.get("facts_changed") is not False:
            problems.append(
                f"facts_changed!=false at {rec.get('location', '?')}")
    n_tables = len(re.findall(r"^\s*\|[\s:|-]+\|\s*$", draft_text,
                              re.MULTILINE))
    reviewed = len(tone_changes.get("tables_reviewed", []))
    if n_tables and reviewed < n_tables:
        problems.append(f"tables_reviewed {reviewed}/{n_tables} draft tables")
    funcs = {r.get("assessment_function")
             for r in tone_changes.get("changes", [])}
    if funcs and not (funcs & _ANALYTICAL_FUNCTIONS):
        problems.append("no analytical assessment_function coverage")
    checks.append({"check": "D5-change-accountability",
                   "result": "fail" if problems else "pass",
                   "detail": ("; ".join(problems[:10]) if problems else
                              f"{len(tone_changes.get('changes', []))} "
                              f"records; {reviewed} tables reviewed "
                              f"({n_tables} in draft)")})

    state = load_state(run_id)
    open_pos = [n for n in state.get("punchouts", {})
                if not _closed(run_id, n)]
    checks.append({"check": "D6-punchout-closure",
                   "result": "fail" if open_pos else "pass",
                   "detail": ("triggered but not two-key closed: "
                              + ", ".join(open_pos) if open_pos else "")})
    return {"result": "pass" if all(c["result"] == "pass" for c in checks)
            else "fail", "checks": checks}

# ---------------------------------------------------------------------------
# Pipeline state machine
# ---------------------------------------------------------------------------


def _closed(run_id, key, state=None):
    po = (state or load_state(run_id))["punchouts"][key]
    if not po.get("triggered"):
        return True
    return (po.get("approved")
            and punchout_log_has_closure(run_id, PUNCHOUTS[key]["letter"]))


def _trigger_punchout(state, key, reason):
    po = state["punchouts"][key]
    if not po.get("triggered"):
        po["triggered"] = True
        po["triggered_file"] = False
    state["certifiable"] = False
    if reason not in state["non_certifiable_reasons"]:
        state["non_certifiable_reasons"].append(reason)


def _log_punchout_trigger(run_id, key, reason):
    append_punchout_log(
        run_id, f"{PUNCHOUTS[key]['letter']}: {PUNCHOUTS[key]['label']}",
        reason, "none attempted (halt honored)",
        "not applicable (halt honored)",
        "pending: human decision required")


def _record_step(run_id, config, step, gate, gate_result, rd,
                 prompt, outputs_text, finalized=False):
    input_hashes = {}
    for stem in ("prior-report", "history-report", "cis", "nist"):
        p = find_input(run_id, stem)
        if p:
            input_hashes[p.name] = sha256_file(p)
    output_hashes = {n: sha256_file(rd / n)
                     for n in EXPECTED_OUTPUTS[step]
                     if (rd / n).exists() and not n.startswith("dispatch")}
    meter = meter_step(config, prompt, outputs_text)
    dispatch, derr = _load_json(rd / f"dispatch-received-{step}.json")
    append_step_record(run_id, {
        "step": STEP_AGENTS[step],
        "model": config.get("model", "unknown"),
        "environment": "copilot-studio",
        "operator": config.get("operator", ""),
        "initiated_by": "harness",
        "dispatch_expected": STEP_AGENTS[step],
        "dispatch_emitted": (dispatch or {}).get("agent"),
        "input_hashes": input_hashes,
        "output_hashes": output_hashes,
        "tokens_in": meter["tokens_in"],
        "tokens_out": meter["tokens_out"],
        "cost_usd": meter["cost_usd"],
        "metering_method": meter["metering_method"],
        "guardrail_inbound": {"id": gate, "result": gate_result},
        "finalized": finalized})


def _punchout_summary(state):
    parts = [f"{n}({'closed' if po.get('approved') else 'open'})"
             for n, po in state.get("punchouts", {}).items()
             if po.get("triggered")]
    return "; ".join(parts) if parts else "none"


def _success(state, run_id, result, iterations, notes):
    append_success_log(run_id=run_id, result=result,
                       punchouts=_punchout_summary(state),
                       iterations=iterations, notes=notes)


def _skill_key(step):
    return {"03a": "03", "03b": "03", "04a": "04a", "04b": "04b",
            "04sel": "04sel"}.get(step, step)


def build_prompt(step, run_id, rd):
    skey = _skill_key(step)
    skill = EMBEDDED_SKILLS.get(skey) or (
        SKILLS[skey].read_text(encoding="utf-8")
        if SKILLS[skey].exists() else "(SKILL.md not found)")
    extra = ""
    if step == "03a":
        extra = ("\nPARAMETERS for this invocation: candidate_id=a, "
                 "strategy=minimal\n")
    elif step == "03b":
        extra = ("\nPARAMETERS for this invocation: candidate_id=b, "
                 "strategy=rewrite\n")
    return (
        f"Execute the following SKILL.md for run '{run_id}' as agent "
        f"'{STEP_AGENTS[step]}'.\n"
        f"All working artifacts live in: {rd}\n"
        f"Inputs are in: {rd / 'inputs'}\n"
        f"FIRST write dispatch-received-{step}.json — a verbatim copy of "
        f"the dispatch instruction you received from the coordinator "
        f"(it must contain \"agent\": \"{STEP_AGENTS[step]}\").\n"
        f"Then write the required outputs into the run directory. Do NOT "
        f"update run-state.json, guardrails.jsonl, run-*.jsonl, "
        f"success-log.md, or punchout-log.md — the harness owns "
        f"orchestration and logging.\n{extra}\n"
        f"=== SKILL.md ===\n{skill}\n")


def _prompt(run_id, rd, step, extra=None):
    pf = rd / f".harness-step{step}-prompt.md"
    pf.write_text(build_prompt(step, run_id, rd), encoding="utf-8")
    action = {"action": "execute_step", "step": step,
              "dispatch": {"agent": STEP_AGENTS[step]},
              "prompt_file": str(pf),
              "expected_outputs": EXPECTED_OUTPUTS[step],
              "done_marker": str(rd / DONE_MARKER[step])}
    if extra:
        action["detail"] = extra
    return action


def _escalate(state, run_id, gate, iterations, checks, reason=None):
    _trigger_punchout(state, "E_loop_exhaustion",
                      reason or f"{gate} loop_max reached")
    _log_punchout_trigger(run_id, "E_loop_exhaustion",
                          reason or f"{gate} loop_max reached")
    state["status"] = "escalated"
    state["halted_at_gate"] = f"needs-{gate.lower()}"
    save_state(run_id, state)
    _success(state, run_id, "halted", iterations,
             f"{gate} failed at loop_max; escalated to human")
    return {"action": "done", "status": "escalated", "detail": checks}


def _open_punchouts(state, run_id):
    return [n for n, po in state.get("punchouts", {}).items()
            if po.get("triggered") and not _closed(run_id, n, state)]


def _awaiting(state, run_id, gate, note):
    state["status"] = "awaiting-human"
    state["halted_at_gate"] = f"needs-{gate.lower()}"
    save_state(run_id, state)
    _success(state, run_id, "halted",
             sum(state["loop_counters"].values()), note)
    return {"action": "awaiting_human", "status": "awaiting-human",
            "detail": note}


def advance(run_id, config, resume=False):
    outcome = _advance(run_id, config, resume=resume)
    try:
        rebuild_logs()
    except Exception:
        pass
    return outcome


def _advance(run_id, config, resume=False):
    rd = run_dir(run_id)
    if not rd.exists():
        init_run(run_id, operator=config.get("operator", ""))
        return {"action": "needs-inputs",
                "detail": f"created {rd}; place the five input sources in "
                          f"inputs/ (prior-report.*, history-report.*, "
                          f"defender-export-folder/, cis.*, nist.*) then "
                          f"call drive again"}
    if not state_path(run_id).exists():
        init_run(run_id, operator=config.get("operator", ""))
    state = load_state(run_id)
    status = state.get("status", "in-progress")
    loop_max = config.get("loop_max", state.get("loop_max", 2))

    if status == "finalized":
        return {"action": "done", "status": "finalized"}
    if status == "non-finalizable":
        return {"action": "done", "status": "non-finalizable",
                "detail": "certifiable=false (permanent); all punch-outs "
                          "closed"}

    if status in ("awaiting-human", "escalated", "stopped", "failed"):
        open_pos = _open_punchouts(state, run_id)
        if not open_pos and status == "awaiting-human" \
                and not state.get("certifiable", True):
            state["status"] = "non-finalizable"
            save_state(run_id, state)
            return {"action": "done", "status": "non-finalizable",
                    "detail": "certifiable=false (permanent); all "
                              "punch-outs closed"}
        if not resume:
            return {"action": "awaiting_human", "status": status,
                    "detail": "requires a recorded human decision "
                              "(record-decision), then drive --resume"}
        if open_pos:
            return {"action": "awaiting_human", "status": status,
                    "detail": f"punch-outs lack two-key closure: {open_pos}"}
        # Resume at the gate where the run halted — re-checks modified
        # inputs/outputs and writes a gate record for what is used next.
        state["status"] = status = state.get("halted_at_gate", "needs-g1")
        save_state(run_id, state)

    # ----- linear step/gate machine -----
    # statuses: in-progress -> needs-stepNN | needs-GN (alternating)
    if status == "in-progress":
        status = "needs-step01"

    # gate dispatch table: status -> (gate id, check fn, next status,
    #                                 loop counter key)
    def _gate(status_gate, fn, counter_key, next_status,
              next_step=None):
        """Run gate fn; on pass advance to next_status (+ prompt)."""
        nonlocal state
        result = fn()
        state["loop_counters"][counter_key] += 1
        it = state["loop_counters"][counter_key]
        append_guardrail_record(run_id, status_gate, result["result"],
                                result["checks"], iteration=it)
        if result["result"] == "fail":
            # punch-out-triggered failures halt for a human, not loop
            open_pos = _open_punchouts(state, run_id)
            if open_pos:
                return _awaiting(state, run_id, status_gate,
                                 f"punch-outs open at {status_gate}: "
                                 + ", ".join(open_pos))
            if it >= loop_max:
                return _escalate(state, run_id, status_gate, it,
                                 result["checks"])
            state["status"] = f"needs-{status_gate.lower()}-redo"
            save_state(run_id, state)
            return {"action": "fix_inputs", "gate": status_gate,
                    "detail": result["checks"]}
        state["status"] = next_status
        state.pop("halted_at_gate", None)
        save_state(run_id, state)
        if next_step:
            return _prompt(run_id, rd, next_step)
        return {"action": "wait", "detail": f"advanced to {next_status}"}

    if status == "needs-step01":
        return _step_wait(run_id, config, state, rd, "01",
                          gate_in="(entry)", next_status="needs-g1")
    if status == "needs-g1" or status == "needs-g1-redo":
        return _gate("G1", lambda: g1_check(run_id), "G1",
                     "needs-step02", "02")

    if status == "needs-step02":
        return _step_wait(run_id, config, state, rd, "02", "G1",
                          "needs-g2")
    if status in ("needs-g2", "needs-g2-redo"):
        return _gate("G2", lambda: g2_check(run_id, state), "G2",
                     "needs-step03a", "03a")

    if status == "needs-step03a":
        return _step_wait(run_id, config, state, rd, "03a", "G2",
                          "needs-step03b")
    if status == "needs-step03b":
        return _step_wait(run_id, config, state, rd, "03b", "G2",
                          "needs-step04a")

    if status == "needs-step04a":
        return _step_wait(run_id, config, state, rd, "04a", "G2",
                          "needs-g3a")
    if status in ("needs-g3a", "needs-g3a-redo"):
        return _gate("G3a", lambda: g3_check(run_id, state, "a"), "G3",
                     "needs-step04b", "04b")
    if status == "needs-step04b":
        return _step_wait(run_id, config, state, rd, "04b", "G3a",
                          "needs-g3b")
    if status in ("needs-g3b", "needs-g3b-redo"):
        return _gate("G3b", lambda: g3_check(run_id, state, "b"), "G3",
                     "needs-step04sel", "04sel")

    if status == "needs-step04sel":
        return _step_wait(run_id, config, state, rd, "04sel", "G3b",
                          "needs-g4")
    if status in ("needs-g4", "needs-g4-redo"):
        return _gate("G4", lambda: g4_check(run_id), "G4",
                     "needs-step05", "05")

    if status == "needs-step05":
        # F missing-content: agent writes punchout-missing-content.md
        # instead of toned.md; harness detects and halts.
        if (rd / "punchout-missing-content.md").exists() \
                and not (rd / "toned.md").exists() \
                and not _closed(run_id, "F_missing_content", state):
            _trigger_punchout(state, "F_missing_content",
                              "template section has no draft content")
            _log_punchout_trigger(run_id, "F_missing_content",
                                  "template requires a section the draft "
                                  "has no content for")
            return _awaiting(state, run_id, "G4",
                             "punch-out F: missing content")
        return _step_wait(run_id, config, state, rd, "05", "G4",
                          "needs-g5")
    if status in ("needs-g5", "needs-g5-redo"):
        return _gate("G5", lambda: g5_check(run_id), "G5",
                     "needs-step06", "06")

    if status == "needs-step06":
        # Judgment channel: step 06 may write g5-judgment.md instead of
        # the done marker on a G5 judgment failure -> loop to step 05.
        jf = rd / "g5-judgment.md"
        if jf.exists():
            detail = jf.read_text(encoding="utf-8",
                                  errors="replace")[:2000]
            jf.unlink()
            state["loop_counters"]["G5"] += 1
            it = state["loop_counters"]["G5"]
            append_guardrail_record(
                run_id, "G5", "fail",
                [{"check": "06-judgment-review", "result": "fail",
                  "detail": detail}], iteration=it)
            if it >= loop_max:
                return _escalate(state, run_id, "G5", it,
                                 [{"check": "06-judgment-review",
                                   "detail": detail}],
                                 reason="G5 judgment fail at loop_max")
            save_state(run_id, state)
            return _prompt(run_id, rd, "05",
                           extra=f"G5 judgment fail (iteration {it}): "
                                 f"{detail}")
        marker = rd / DONE_MARKER["06"]
        missing = [n for n in EXPECTED_OUTPUTS["06"]
                   if not (rd / n).exists()]
        if not marker.exists() or missing:
            return {"action": "wait",
                    "detail": ("waiting for .harness-step06-done"
                               if not marker.exists()
                               else f"done marker present but outputs "
                                    f"not yet synced: {missing}")}
        marker.unlink()
        prompt = build_prompt("06", run_id, rd)
        outputs_text = "".join(
            (rd / n).read_text(encoding="utf-8", errors="replace")
            for n in EXPECTED_OUTPUTS["06"])
        state = load_state(run_id)
        open_pos = _open_punchouts(state, run_id)
        finalized = not open_pos and state.get("certifiable", True)
        _record_step(run_id, config, "06", "G5", "pass", rd,
                     prompt, outputs_text, finalized=finalized)
        if open_pos:
            return _awaiting(state, run_id, "G5",
                             "finalization blocked: unclosed punch-out")
        if not finalized:
            state["status"] = "non-finalizable"
            save_state(run_id, state)
            _success(state, run_id, "halted",
                     state["loop_counters"]["G5"],
                     "finalization blocked: certifiable=false "
                     "(permanent); all punch-outs closed")
            return {"action": "done", "status": "non-finalizable",
                    "detail": "run cannot finalize: certifiable=false"}
        state["status"] = "finalized"
        state["current_step"] = "complete"
        save_state(run_id, state)
        _success(state, run_id, "pass", state["loop_counters"]["G5"],
                 "all gates passed; step 06 finalized")
        return {"action": "done", "status": "finalized"}

    return {"action": "wait", "detail": f"unhandled status: {status}"}


def _step_wait(run_id, config, state, rd, step, gate_in, next_status):
    """Wait for a step's done marker + expected outputs; then record the
    step and advance to next_status."""
    marker = rd / DONE_MARKER[step]
    missing = [n for n in EXPECTED_OUTPUTS[step]
               if not (rd / n).exists()]
    if not marker.exists() or missing:
        return {"action": "wait",
                "detail": (f"waiting for {DONE_MARKER[step]}"
                           if not marker.exists()
                           else f"done marker present but outputs not yet "
                                f"synced: {missing}")}
    marker.unlink()
    prompt = build_prompt(step, run_id, rd)
    outputs_text = "".join(
        (rd / n).read_text(encoding="utf-8", errors="replace")
        for n in EXPECTED_OUTPUTS[step])
    _record_step(run_id, config, step, gate_in, "pass", rd,
                 prompt, outputs_text)
    state["status"] = next_status
    save_state(run_id, state)
    return {"action": "wait", "detail": f"step {step} complete; "
                                        f"advanced to {next_status}"}


def run(run_id, config, resume=False, poll_seconds=15):
    while True:
        outcome = advance(run_id, config, resume=resume)
        resume = False
        print(json.dumps(outcome, indent=2, default=str), flush=True)
        if outcome["action"] != "wait":
            return outcome
        time.sleep(poll_seconds)

# ---------------------------------------------------------------------------
# Bypass testing + human decisions
# ---------------------------------------------------------------------------


def bypass_test(run_id, letter, operator="harness"):
    key = LETTER_TO_KEY[letter.upper()]
    state = load_state(run_id)
    po = state["punchouts"][key]
    if not po.get("triggered"):
        return {"ok": False,
                "detail": f"punch-out {key} never triggered for {run_id}"}
    if po.get("approved") or punchout_log_has_closure(run_id, letter):
        return {"ok": True, "skipped": True,
                "detail": f"punch-out {key} already closed by a recorded "
                          f"human decision — bypass testing only applies "
                          f"while open; run state untouched"}

    def would_pass():
        return not _open_punchouts(load_state(run_id), run_id)

    results = []
    results.append(("no-approval continuation",
                    "BYPASSED — system allowed continuation (GATE FAILURE)"
                    if would_pass() else
                    "blocked — unapproved punch-out halts resume"))

    po["approved"] = True
    po["closure_evidence"] = "bypass-test: forged approval, no log row"
    save_state(run_id, state)
    results.append(("forged approval flag",
                    "BYPASSED — approved flag alone opened the gate "
                    "(TWO-KEY FAILURE)" if would_pass() else
                    "blocked — two-key check requires a punchout-log.md "
                    "row"))

    po["approved"] = False
    po["closure_evidence"] = None
    po["bypass_attempt"] = "; ".join(f"{a}: {r}" for a, r in results)
    state["certifiable"] = False
    reasons = state.setdefault("non_certifiable_reasons", [])
    if "bypass attempt recorded" not in reasons:
        reasons.append("bypass attempt recorded")
    state["status"] = "awaiting-human"
    save_state(run_id, state)

    blocked = all(r.startswith("blocked") for _, r in results)
    append_punchout_log(
        run_id, f"{letter.upper()}: {PUNCHOUTS[key]['label']}",
        "systematic bypass test via harness bypass-test",
        "; ".join(a for a, _ in results),
        "blocked" if blocked else "GATE FAILURE — see detail",
        "bypass test recorded; run permanently non-certifiable",
        operator, _utcnow())
    try:
        rebuild_logs()
    except Exception:
        pass
    return {"ok": blocked, "attempts": results}


def record_decision(run_id, letter, decision, resolved_by, evidence=""):
    letter = letter.upper()
    key = LETTER_TO_KEY[letter]
    state = load_state(run_id)
    po = state.get("punchouts", {}).get(key)
    if not po or not po.get("triggered"):
        return {"ok": False, "error":
                f"punch-out {letter} is not triggered for {run_id}"}
    if po.get("approved") and punchout_log_has_closure(run_id, letter):
        return {"ok": False, "error":
                f"punch-out {letter} already closed for {run_id} — "
                f"a second closure row would look like tampering"}
    resolved_at = _utcnow()
    append_punchout_log(
        run_id, f"{letter}: {PUNCHOUTS[key]['label']}",
        "human decision recorded via record-decision",
        "none (decision, not bypass)", "not applicable",
        decision, resolved_by, resolved_at)
    po["approved"] = True
    po["resolved_by"] = resolved_by
    po["resolved_at"] = resolved_at
    po["closure_evidence"] = evidence or (
        f"punchout-{run_id}.md row {resolved_at} by {resolved_by}: "
        f"{decision}")
    save_state(run_id, state)
    append_step_record(run_id, {
        "event": "human-decision", "punchout": key,
        "decision": decision, "resolved_by": resolved_by,
        "resolved_at": resolved_at, "recorded_via": "record-decision"})
    try:
        rebuild_logs()
    except Exception:
        pass
    return {"ok": True, "run_id": run_id, "punchout": key,
            "decision": decision, "resolved_by": resolved_by,
            "resolved_at": resolved_at}

# ---------------------------------------------------------------------------
# Manifest / verify / embed
# ---------------------------------------------------------------------------

MIRROR_REQUIRED = []


def manifest(run_id):
    rd = f"runs/{run_id}"
    prompts = [f"{rd}/.harness-step{s}-prompt.md" for s in STEP_FLOW]
    markers = [f"{rd}/{DONE_MARKER[s]}" for s in STEP_FLOW]
    return {
        "read_required": ["s5-harness.py", "s5-harness.config.json",
                          "checksums.sha256"] + MIRROR_REQUIRED,
        "read_optional": [
            f"{rd}/run-state.json",
            f"audit/punchout-{run_id}.md",
            "audit/guardrails.jsonl",
            "audit/success-log.md",
            "audit/punchout-log.md",
        ],
        "write_create": [
            f"{rd}/.g4-passed",
            f"{rd}/punchout-missing-content.md",
            f"audit/run-{run_id}.jsonl",
            f"audit/guardrails-{run_id}.jsonl",
            f"audit/success-{run_id}.md",
            f"audit/punchout-{run_id}.md",
        ] + prompts + markers,
        "write_overwrite": [
            f"{rd}/run-state.json",
            "audit/guardrails.jsonl",
            "audit/success-log.md",
            "audit/punchout-log.md",
            "audit/success-report.md",
        ],
    }


def verify_checksums(checksums_file=None):
    cf = Path(checksums_file) if checksums_file \
        else ROOT / "checksums.sha256"
    if not cf.exists():
        return {"ok": False, "detail": f"{cf} not found"}
    results = {}
    for line in cf.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        expected, _, rel = line.partition(" ")
        rel = rel.strip().lstrip("*")
        p = ROOT / rel
        if not p.exists():
            results[rel] = "missing"
        else:
            results[rel] = (
                "match" if sha256_text(p) == expected.strip()
                else f"MISMATCH (got {sha256_text(p)})")
    return {"ok": all(v == "match" for v in results.values()),
            "files": results,
            "harness_self_hash": sha256_file(Path(__file__))}


def embed_skills():
    src = Path(__file__).read_text(encoding="utf-8")
    start = "# === EMBEDDED SKILLS (regenerate: python s5-harness.py embed) ===\n"
    end = "# === END EMBEDDED SKILLS ===\n"
    i, j = src.index(start), src.index(end) + len(end)
    skills = {s: SKILLS[s].read_text(encoding="utf-8") for s in SKILLS}
    block = (start + "EMBEDDED_SKILLS = {\n"
             + "".join(f'    "{k}": {v!r},\n' for k, v in skills.items())
             + "}\n" + end)
    Path(__file__).write_text(src[:i] + block + src[j:], encoding="utf-8")
    return {"embedded": list(skills), "note": "refresh s5-harness.sha256"}

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv=None):
    ap = argparse.ArgumentParser(prog="s5-harness")
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name in ("drive", "run"):
        p = sub.add_parser(name)
        p.add_argument("--run-id", required=True)
        p.add_argument("--resume", action="store_true")
    p_bt = sub.add_parser("bypass-test")
    p_bt.add_argument("--run-id", required=True)
    p_bt.add_argument("--punchout", required=True,
                      choices=list("ABCDEF") + list("abcdef"))
    p_bt.add_argument("--operator", default="harness")
    p_rd = sub.add_parser("record-decision")
    p_rd.add_argument("--run-id", required=True)
    p_rd.add_argument("--punchout", required=True,
                      choices=list("ABCDEF") + list("abcdef"))
    p_rd.add_argument("--decision", required=True)
    p_rd.add_argument("--resolved-by", required=True)
    p_rd.add_argument("--evidence", default="")
    for name in ("check-g1", "check-g2", "check-g3a", "check-g3b",
                 "check-g4", "check-g5", "manifest"):
        p = sub.add_parser(name)
        p.add_argument("--run-id", required=True)
    sub.add_parser("hash")
    sub.add_parser("verify")
    sub.add_parser("embed")
    sub.add_parser("rebuild-logs")

    args = ap.parse_args(argv)
    config = load_config()

    if args.cmd == "hash":
        print(sha256_file(Path(__file__)))
        return
    if args.cmd == "verify":
        outcome = verify_checksums()
        print(json.dumps(outcome, indent=2))
        sys.exit(0 if outcome.get("ok") else 1)
    if args.cmd == "embed":
        print(json.dumps(embed_skills(), indent=2))
        sys.exit(0)
    if args.cmd == "rebuild-logs":
        print(json.dumps(rebuild_logs(), indent=2))
        sys.exit(0)
    if args.cmd == "drive":
        outcome = advance(args.run_id, config, resume=args.resume)
    elif args.cmd == "run":
        outcome = run(args.run_id, config, resume=args.resume)
    elif args.cmd == "bypass-test":
        outcome = bypass_test(args.run_id, args.punchout,
                              operator=args.operator)
    elif args.cmd == "record-decision":
        outcome = record_decision(args.run_id, args.punchout,
                                  args.decision, args.resolved_by,
                                  args.evidence)
    elif args.cmd == "manifest":
        print(json.dumps(manifest(args.run_id), indent=2))
        sys.exit(0)
    elif args.cmd.startswith("check-"):
        gate = args.cmd[6:]
        if gate == "g1":
            outcome = g1_check(args.run_id)
        elif gate == "g2":
            outcome = g2_check(args.run_id, load_state(args.run_id))
        elif gate == "g3a":
            outcome = g3_check(args.run_id, load_state(args.run_id), "a")
        elif gate == "g3b":
            outcome = g3_check(args.run_id, load_state(args.run_id), "b")
        elif gate == "g4":
            outcome = g4_check(args.run_id)
        else:
            outcome = g5_check(args.run_id)
        append_guardrail_record(args.run_id, gate.upper(),
                                outcome["result"], outcome["checks"])

    print(json.dumps(outcome, indent=2, default=str))
    ok = (outcome.get("result") == "pass"
          or outcome.get("status") == "finalized"
          or outcome.get("action") in ("execute_step", "wait",
                                      "needs-inputs", "done")
          or outcome.get("ok"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

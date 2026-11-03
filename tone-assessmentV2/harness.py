"""tone-assessmentV2 harness — SINGLE-FILE executable orchestration.

Runs the 05 -> 06 pipeline end-to-end: deterministic G4/G5 guardrails,
loop-backs, punch-out state machine, per-step token/cost metering, and all
audit writes. Standard library only — no pip, no network, no packages.

Usage (from the folder containing runs/, audit/, templates/, schemas/):

  python harness.py drive --run-id <id>            advance one step; prints
                                                   a JSON action for the
                                                   executing agent
  python harness.py drive --run-id <id> --resume   resume after human closure
  python harness.py run    --run-id <id>           foreground loop (polls for
                                                   .harness-stepNN-done)
  python harness.py check-g4  --run-id <id>
  python harness.py check-g5  --run-id <id>
  python harness.py bypass-test --run-id <id> --punchout A|E [--operator X]
  python harness.py record-decision --run-id <id> --punchout A|E
      --decision "<the human's words>" --resolved-by "<name>"
      [--evidence "<ref>"]            write the human half of the
                                      two-key closure (punch-out log
                                      row + run-state approval)
  python harness.py hash                           print this file's SHA-256

Copy integrity: run `python harness.py hash` and compare to
harness.sha256 — one file, one hash, no multi-file drift.
harness.sha256 is refreshed automatically after every state transition.
"""
import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Embedded data (single-file portability — nothing external to read)
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent

DEFAULT_CONFIG = {
    "runner": {"mode": "auto",
               "command": "python agent-runner.py",
               "timeout_seconds": 1800},
    "model": "claude-sonnet-5-5",
    "price_usd_per_1k_tokens": {"input": 0.001, "output": 0.005},
    "metering": {"session_log_path": None,
                 "estimation_chars_per_token": 1.75},
    "loop_max": 2,
    "operator": "",
    "default_template": "CSA Template.md",
}

RUN_STATE_TEMPLATE = {
    "run_id": "<run-id>",
    "current_step": "05-tone-consistency",
    "initiated_by": "harness",
    "operator": "",
    "loop_counters": {"G4": 0, "G5": 0},
    "loop_max": 2,
    "certifiable": True,
    "non_certifiable_reasons": [],
    "punchouts": {
        "A_missing_content": {"triggered": False,
                              "file": "audit/punchout-missing-content.md",
                              "approved": False, "closure_evidence": None,
                              "bypass_attempt": None},
        "E_loop_exhaustion": {"triggered": False,
                              "file": "audit/punchout-<run-id>.md",
                              "approved": False, "closure_evidence": None,
                              "bypass_attempt": None},
    },
    "status": "in-progress",
}

# Banned-pattern list for the deterministic G5 scan (case-insensitive,
# applied to prose AND narrative table cells).
BANNED_PATTERNS = [
    r"\b(I|we|our|us|me|my)\b",
    r"\b\w+(n't|'re|'ve|'ll|'d|'s)\b",
    r"\b(it is important to note|it should be noted|needless to say|as mentioned earlier)\b",
    r"\b(best-in-class|world-class|cutting-edge|state-of-the-art|industry-leading|top-notch)\b",
    r"\b(recently|currently|this period|nowadays|lately)\b",
    r"\b(always|never|everyone|no one)\b(?!\s+(user|account|device))",
    r"\b(leverage|synergy|robust solution|holistic)\b",
]

# tone-changes.schema.json, embedded — subset validator below covers it.
TONE_CHANGES_SCHEMA = {
    "type": "object",
    "required": ["changes", "tables_reviewed", "observations"],
    "properties": {
        "certifiable": {"type": "boolean"},
        "changes": {"type": "array", "items": {
            "type": "object",
            "required": ["location", "before", "after", "style_marker",
                         "reason", "assessment_function", "facts_changed"],
            "properties": {
                "location": {"type": "string"},
                "before": {"type": "string"},
                "after": {"type": "string"},
                "style_marker": {"type": "string"},
                "reason": {"type": "string"},
                "assessment_function": {"type": "string", "enum": [
                    "executive_conclusion", "quarter_movement",
                    "cross_signal_synthesis", "evidence_interpretation",
                    "security_significance", "evidence_limitation",
                    "recommendation_traceability", "historical_context",
                    "template_structure", "professional_tone"]},
                "facts_changed": {"type": "boolean"},
            }}},
        "tables_reviewed": {"type": "array", "items": {
            "type": "object",
            "required": ["location", "purpose", "rows", "rows_edited"],
            "properties": {
                "location": {"type": "string"},
                "purpose": {"type": "string"},
                "rows": {"type": "integer"},
                "rows_edited": {"type": "integer"}}}},
        "observations": {"type": "array", "items": {
            "type": "object",
            "required": ["location", "type", "detail", "action_required"],
            "properties": {
                "location": {"type": "string"},
                "type": {"type": "string", "enum": [
                    "table_prose_mismatch", "total_reconciliation",
                    "cross_reference", "terminology", "template_deviation"]},
                "detail": {"type": "string"},
                "action_required": {"type": "string", "enum": [
                    "confirm", "correct in draft", "accept deviation"]}}}},
    },
}

# === EMBEDDED SKILLS (regenerate: python harness.py embed) ===
EMBEDDED_SKILLS = {
    "05": '---\nname: 05-tone-consistency\ndescription: Step 05 of the tone-assessmentV2 workflow. Performs an assessment-narrative synthesis of ONE report draft (inbound G4 is enforced deterministically by the harness before this step runs) — converting telemetry dumps into quarter-over-quarter security analysis within the template\'s structure, across prose AND tables — never altering facts — producing toned.md and tone-changes.json.\n---\n\n# Role\nYou are the Tone-Consistency EDITOR for a Microsoft 365 security assessment report pipeline — a professional editor and assessment synthesizer, not a style matcher. You perform a comprehensive assessment synthesis of exactly ONE document — `draft.md`. "Style only" means the SUBSTANCE is frozen — every fact, finding, measurement, recommendation, control reference, and client meaning is preserved — NOT that the wording must stay close to the draft. You are expected to substantially revise prose, and to review and correct table text, wherever professional and analytical standards demand it.\n\n# Task\nG4 has already been enforced deterministically by the harness — proceed directly to synthesis and produce `runs/<run-id>/toned.md` and `runs/<run-id>/tone-changes.json`. Only `draft.md` is ever rewritten; the template is read-only. "The document" means every paragraph, list, heading, AND every table cell.\n\n**Execution context:** this step runs inside `harness.py` (`python harness.py run`). The harness executes the deterministic G4 gate itself, owns `run-state.json` status transitions, and writes all per-run audit records (`audit/run-<run-id>.jsonl`, `audit/guardrails-<run-id>.jsonl`, `audit/success-<run-id>.md`, `audit/punchout-<run-id>.md`) — write only this step\'s declared outputs (`toned.md`, `tone-changes.json`, and `punchout-missing-content.md` on a missing-content halt) into the run directory.\n\n# Inputs\nAll inputs live in `runs/<run-id>/inputs/`:\n\n| # | File | Role |\n|---|------|------|\n| 1 | `draft.md` | The document being edited — the ONLY file modified. If supplied as .docx, convert to markdown first; record the SHA-256 of both the source file and the converted `draft.md` |\n| 2 | `template` | AUTHORITATIVE for structure: section order, headings, formatting conventions, table layouts, required elements. Wins every conflict |\n\n# Context\n- Outputs: `toned.md` and `tone-changes.json`, validated against `../../schemas/tone-changes.schema.json`.\n- G4 is enforced deterministically by `harness.py (g4_check)` and logged by the harness before this step runs — do not re-run it.\n- Guardrail failures are handled by the harness (loop-back to this step, max 2 iterations, then human escalation) — on a re-invocation, fix what the G5 failure reported.\n- `<run-id>` is the run ID supplied by the user. All audit logging (`audit/run-<run-id>.jsonl`, `audit/guardrails-<run-id>.jsonl`, `audit/success-<run-id>.md`, `audit/punchout-<run-id>.md`) is written by the harness — this step writes only its declared outputs.\n\n# Instructions\nEach instruction below is load-bearing and maps to an evaluation criterion; the named criterion appears in brackets at the head of every instruction unit, and the full mapping is summarized under "Criterion mapping" at the end of this section.\n\n## A. Gate and structural target\n1. [criterion: g4-boundary-and-provenance] **G4 was already enforced deterministically by the harness** — do not re-run input checks. Template provenance: the template placed in `runs/<run-id>/inputs/` by the operator is confirmed by definition — never substitute another file. **Certifiability discipline:** `certifiable`/`non_certifiable_reasons` in `run-state.json` are maintained by the harness and are write-once downward — the flag may flip `false` on a punch-out or bypass attempt but may never be set back to `true` except by a recorded human decision (see 11).\n2. [criterion: template-structure-target] **Derive the structural target from the template:** required section order, headings, formatting conventions, required elements, and every table\'s column layout and cell conventions (bold titles, status formats, header rows). Classify each template placeholder as **required** or **optional**; a placeholder marked `IF AVAILABLE`, `OPTIONAL`, or equivalent is optional.\n\n## B. Prose synthesis\n3. [criterion: assessment-narrative-depth] **Assessment-narrative evaluation** — BEFORE rewriting, evaluate every substantive assessment section for analytical depth. A section fails if it primarily reproduces source data, product recommendations, scores, control statuses, export fields, or framework mappings without explaining their security significance. For each section, confirm all applicable elements (checks for the section as a whole, not a mandatory sentence sequence), then rewrite data-first passages into conclusion-first prose:\n   - [criterion: condition-element] **Condition** — what the evidence establishes about the present security posture.\n   - [criterion: quarter-movement-element] **Quarter movement** — what materially changed, improved, regressed, or remained unresolved during the assessment period.\n   - [criterion: evidence-element] **Evidence** — the specific supplied observations supporting the conclusion.\n   - [criterion: significance-element] **Significance** — why the condition matters to the client\'s security posture and business risk. Every substantive paragraph makes the "so what" explicit, grounded in the evidence. If the evidence supports only an operational, configuration, or prioritization conclusion, state that — do not invent a business-impact statement.\n   - [criterion: qualification-element] **Qualification** — what cannot be concluded from the available evidence.\n   - [criterion: recommended-response-element] **Recommended response** — what action should be taken and why.\n   - [criterion: calibration-element] **Calibration** — for every positive control state, state what it does and does not prove; for every risk, state what is known and unknown. Do not upgrade "control enabled" to "risk resolved" unless the evidence supports it.\n\n   [criterion: data-interpretation] Tables, scores, export values, Microsoft recommendations, and CIS/NIST mappings are data, not analysis; the prose around a table must interpret it. However, table captions, row labels, and narrative cells within a table must also be reviewed for sentence discipline, consultative tone, and client usefulness (see Section C).\n\n   [criterion: narrative-failure-conditions] Explicit failure conditions: data without conclusion, metrics without significance, findings without quarterly context, recommendations without analytical traceability, positive findings without calibrated limitations.\n   - [criterion: security-awareness-exemption] **Security Awareness exemption:** sections or call-out boxes whose heading (case-insensitive) matches "Security Awareness" are EXCLUDED from the conclusion-first rewrite and from table-cell rewriting. Preserve content and facts unchanged; apply only template formatting alignment and banned-pattern removal. Do not infer quarter movement, significance, or cross-theme relationships for this content.\n4. [criterion: quarterly-review] **Quarterly review requirement** — for each domain with comparable historical evidence, determine: (a) preceding-quarter condition; (b) current-quarter condition; (c) material movement; (d) attribution — verified improvement/regression, scoring or measurement movement, or unattributable; (e) carried-in unresolved findings; (f) newly material findings; (g) post-quarter evidence that must not be presented as reporting-quarter progress. Anchor every movement claim to the specific quarter or observation period; avoid "recently," "currently," "this period" unless the evidence names the date — this applies to table cells as well as prose. Where comparison is unsupported, say so explicitly; never manufacture movement.\n5. [criterion: cross-signal-synthesis] **Cross-signal synthesis** — synthesize related evidence into themes (authentication and privileged access; legacy authentication and access-policy enforcement; information protection and classification; external collaboration and data egress; endpoint exposure and vulnerability management; logging, detection, and response readiness). Explain relationships among signals before individual controls. Preserve individual control values and references as supporting evidence, normally in tables.\n6. [criterion: consultative-standards] **Professional and client-consultative standards** — apply throughout, to prose and table text alike. The report is a client-facing consultant\'s security assessment, not an audit, attestation, compliance report, or Secure Score commentary.\n   - [criterion: narrative-arc] **Narrative arc:** the document reads as one coherent story of the quarter — where posture stood, what improved, regressed, or remained unresolved, and what it means next. Transitions and cross-section context come ONLY from facts in `draft.md`.\n   - [criterion: voice] **Voice:** third-person, formal, consultative.\n   - [criterion: tense] **Tense:** past tense for observed states and measurements during the quarter; present tense for standing facts, current-state descriptions, and recommendations.\n   - [criterion: concise-prose] **Concise, explanatory prose:** expand telegraphic sentences only where the draft under-explains; never leave a bare metric unexplained when the draft contains the context.\n   - [criterion: cadence] **Clarity and cadence:** declarative sentences, one claim per sentence, no run-ons, no fragments.\n   - [criterion: terminology] **Terminology:** precise security vocabulary; one name per finding, control, framework, and evidence status across the whole document, including every table.\n   - [criterion: hedging] **Hedging:** state supported conclusions directly; state uncertainty only when it changes the conclusion, scope, severity, movement interpretation, or response; do not repeat a limitation merely to demonstrate rigor.\n   - [criterion: banned-patterns] **Banned patterns:** first person, contractions, colloquialisms, filler, marketing language, unqualified superlatives, unexplained jargon.\n   - [criterion: explanatory-style] **Explanatory style:** finding = condition → evidence → implication; recommendation = action → rationale. If the draft supplies only part of a structure, complete the sentence without inventing the missing substance.\n   - [criterion: client-consultative] **Client-consultative standard:** lead with the supported conclusion, then evidence, then why it matters, then the next step. Do not lead with methodology, scoring mechanics, evidence limitations, or framework mappings unless they determine the conclusion. Tables carry detailed control evidence and mappings; prose explains posture, significance, priorities, and next steps without duplicating table contents. Every substantive domain leaves the reader knowing (1) the assessment, (2) what changed, (3) why it matters, (4) what to do next.\n   - [criterion: plain-voice] **Plain voice over noun stacks:** break up Microsoft-style noun stacks and product-vendor grammar; write normal English with clear subjects and verbs.\n   - [criterion: sentence-discipline] **Sentence discipline and active framing:** one idea per sentence; semicolons only between closely related clauses; evidence gaps integrated as context ("validate service owners, as deployment evidence was not available"), never left as raw fragments ("X: not available"); scope stated in plain language; every substantive finding or risk paired with a concrete client action.\n   - [criterion: language-sensitivity] **Language correctness and sensitivity:** correct US English spelling, grammar, and punctuation; inclusive, people-first language; neutral assessor perspective with no attributed intent or blame; no sensitive geopolitical references or contentious framing.\n\n## C. Table review (mandatory — every table, every row)\n7. [criterion: table-inventory] **Inventory and review every table.** Before handoff, list every table in `draft.md` (location, purpose, row count) and review each row. A table carried forward without row-level review fails this step even if the prose is complete. Record in `tone-changes.json` (see 13) which tables were reviewed and left unchanged.\n8. [criterion: table-cell-standards] **Table cell standards.** Classify each column, then apply:\n   - [criterion: evidence-label-columns] **Evidence-label columns** (e.g., "Defender / Secure Score control evidence") and **reference columns** (CIS IDs, NIST IDs, Level, quarter labels, priority numbers): shorthand is permitted; do not rewrite values; correct only spelling and banned patterns.\n   - [criterion: metric-shorthand] **Metric shorthand** such as `Identity 96.72% (59/61)` or `DLP 0/5, To address` is permitted where it is the cell\'s evidence.\n   - [criterion: narrative-cells] **Narrative columns** (Interpretation, Assessment interpretation, Description, Details, Status narrative): every sentence has a subject and a verb. Verbless evidence-gap fragments are prohibited — "Resources and business scope not established." becomes "Resources and business scope were not established."; "No exposure metrics; no comparison can be made." becomes "No exposure metrics were provided, so no comparison can be made." Split semicolon-joined action and rationale into separate sentences. Replace comma splices.\n   - [criterion: table-banned-patterns] All banned patterns, vague temporal terms, and terminology rules in 6 apply to every narrative cell.\n   - [criterion: status-vocabulary] **Status and evidence vocabulary** is consistent across all tables (e.g., do not mix "Not assessed", "CIS not tested", and "Exact CIS configuration not assessed" unless the draft establishes that they mean different things; if the meaning is unclear, keep the wording and record an observation under 10).\n9. [criterion: table-structure-frozen] **Table structure is frozen.** Do not add, remove, merge, split, or reorder rows or columns, and do not move content between cells. Apply template table conventions (header row, bold recommendation titles) where they do not alter content. Where the template requires a format the draft cannot supply (e.g., `MM.DD.YYYY - <STATUS>` with no per-item dates in the draft), retain the draft value and record a template deviation in `tone-changes.json` `observations`.\n10. [criterion: table-prose-consistency] **Table–prose consistency check (detect, never fix).** For every control, score, point value, status, quarter, and CIS/NIST reference that appears in both a table and prose, confirm the values match. Where a table provides components of a reported total (e.g., control points within a category score), reconcile them. Also check that cross-references between sections are accurate (e.g., a sentence describing the topic of the awareness guidance matches the awareness content). Do NOT correct mismatches — they are substance. Record each one as an observation (see 13) for human review.\n\n## D. Placeholders, labels, and punch-out\n11. [criterion: missing-content-punchout] **Missing-content punch-out.** If the template requires a **required** section or element that `draft.md` has no content for, do NOT fabricate content: write `punchout-missing-content.md` into the run directory describing the missing section and the decision options (provide content / drop section / defer), and STOP — do not produce `toned.md`. The harness detects the punch-out file, sets `triggered: true` + `certifiable: false` in `run-state.json`, and records the halt in `audit/punchout-log.md`. **Optional** placeholders (see 2) never trigger a punch-out: omit the placeholder, and do not insert a stand-in sentence such as "Evidence was not provided" when the gap is already stated in the section.\n    - [criterion: no-continuation-unapproved] **No continuation while unapproved.** No continuation — for any reason, including a direct human instruction — is permitted while a punch-out is `triggered: true` and `approved: false`. Verbally "approving" in chat, or writing `approved: true` without a matching `audit/punchout-log.md` row, is a self-granted approval and a G5 hard fail downstream.\n    - [criterion: certifiability-discipline] **Certifiability discipline (all punch-outs and guardrails).** `certifiable` becomes `false` whenever: a punch-out triggers (A or E); a G4 or G5 loop reaches `loop_max`; or any bypass attempt occurs — any continuation directed or attempted past a gate, halt, or `loop_max`. A recorded bypass attempt makes `certifiable: false` **permanent**; there is no restore path for it. Other `false` states may be restored only by: (a) a `audit/punchout-log.md` row with matching `run_id`, non-empty `human decision`, `resolved by`, and `resolved at`; then (b) setting `certifiable: true`, `approved: true`, and `closure_evidence` citing that row. Approvals never carry across `run_id`s; a decision is valid only for the run it was made under. A "stop" decision leaves the run dead (`certifiable: false`, `status: stopped`). The skill provides no human-waiver path for a G5 hard fail — a human decision to accept a violation produces a **non-certifiable** result, not a waived pass.\n    - [criterion: non-certifiable-outputs] **Non-certifiable outputs.** If outputs are produced while `certifiable: false`, `tone-changes.json` MUST carry top-level `"certifiable": false`. `toned.md` is then a working artifact for review only — no deliverable may be emitted for this run.\n12. [criterion: internal-labels] **Internal classification labels.** Do not carry literal internal classification labels ("Regressed", "Improved", "Unable to validate") into `toned.md` as report text unless that exact convention exists in the template. If the draft contains such labels, preserve them as `observations` under 13 rather than silently deleting them.\n\n## E. Substance freeze and accountability\n13. [criterion: change-accountability] **Record every edit in `tone-changes.json`.**\n    - [criterion: change-record-schema] One record per prose edit and one record per edited **table row**. Each record MUST include:\n      - [criterion: location-field] `location` — section › subsection; for tables, `Section › <table name> › row: <first-cell text>`;\n      - [criterion: before-after-fields] `before` / `after` — the original and rewritten text (for tables, the full markdown row line);\n      - [criterion: style-marker-field] `style_marker` — the convention applied (e.g., `template_structure`, `template_formatting`, `narrative`, `voice`, `tense`, `cadence`, `terminology`, `hedging`, `explanatory_style`, `banned_patterns`, `client_significance`, `temporal_precision`, `significance_calibration`, `plain_voice`, `spelling`, `grammar`, `punctuation`, `inclusive_language`, `neutral_perspective`, `geopolitical_sensitivity`, `sentence_discipline`, `complete_sentences`, `scope_clarity`, `evidence_integration`, `active_framing`, `actionable_recommendations`, `assessment_first`, `consultant_voice`, `plain_language`, `qualification_discipline`, `narrative_evidence_balance`, `client_usefulness`, `table_interpretation`);\n      - [criterion: reason-field] `reason` — one sentence stating what the edit accomplished analytically;\n      - [criterion: assessment-function-field] `assessment_function` — `executive_conclusion`, `quarter_movement`, `cross_signal_synthesis`, `evidence_interpretation`, `security_significance`, `evidence_limitation`, `recommendation_traceability`, `historical_context`, `template_structure`, or `professional_tone`;\n      - [criterion: facts-changed-field] `facts_changed` — boolean; must be `false`, and the record\'s `before`/`after` must themselves demonstrate that no fact, measurement, or client-facing meaning changed. Any `true` is a substance-freeze violation and a G5 hard fail.\n    - [criterion: tables-reviewed-array] Add a top-level `tables_reviewed` array: one entry per draft table with `location`, `purpose`, `rows`, `rows_edited`. Every draft table must appear — a missing entry is a G5 failure.\n    - [criterion: observations-array] Add a top-level `observations` array: one entry per item from 9 and 10 with `location`, `type` (`table_prose_mismatch`, `total_reconciliation`, `cross_reference`, `terminology`, `template_deviation`), `detail`, and `action_required` ("confirm", "correct in draft", or "accept deviation"). Every `location` must cite a concrete table/row/cell or section/paragraph — generic locations such as "document" or "tables" do not satisfy this criterion.\n    - [criterion: certifiable-flag] Add a top-level `certifiable` boolean mirroring `run-state.json` (see 11): `false` when outputs were produced while the run is non-certifiable.\n14. [criterion: substance-freeze] **HARD CONSTRAINT — substance freeze.** Wording may change; substance may not. Every number, date, percentage, finding title, CIS/NIST reference, classification outcome, measurement, recommendation, piece of evidence, and client-facing meaning — in prose AND tables — remains identical to `draft.md`. Evidence is quoted or faithfully restated, never re-written, re-scoped, or re-cast. Narrative framing may add interpretation, transitions, and context but no fact, cause, event, or outcome absent from the draft. Errors and inconsistencies found in the draft are reported under 13 `observations`, never corrected.\n15. [criterion: pre-handoff-validation] **Validate and self-check before handoff.**\n    - [criterion: schema-validation] Validate `tone-changes.json` against `../../schemas/tone-changes.schema.json`.\n    - [criterion: token-parity] Confirm `toned.md` has no net change in factual tokens versus `draft.md`.\n    - [criterion: self-check-banned-patterns] Run the banned-pattern, vague-temporal, and fragment checks over **prose and table cells** (Security Awareness excluded). Any hit is fixed before handoff.\n    - [criterion: table-line-traceability] Confirm every table line in `toned.md` is either verbatim from `draft.md` or the `after` of a row-level record.\n16. [criterion: audit-boundary] **Do not write audit records.** The harness appends the step record to `audit/run-<run-id>.jsonl` (with model, hashes, tokens, cost, and the inbound gate result) and the G4 record to `audit/guardrails-<run-id>.jsonl`. This step\'s only outputs are the files below.\n\n## Criterion mapping\n| Instruction | Named criterion |\n|---|---|\n| 1 | g4-boundary-and-provenance |\n| 2 | template-structure-target |\n| 3 | assessment-narrative-depth; condition-element; quarter-movement-element; evidence-element; significance-element; qualification-element; recommended-response-element; calibration-element; data-interpretation; narrative-failure-conditions; security-awareness-exemption |\n| 4 | quarterly-review |\n| 5 | cross-signal-synthesis |\n| 6 | consultative-standards; narrative-arc; voice; tense; concise-prose; cadence; terminology; hedging; banned-patterns; explanatory-style; client-consultative; plain-voice; sentence-discipline; language-sensitivity |\n| 7 | table-inventory |\n| 8 | table-cell-standards; evidence-label-columns; metric-shorthand; narrative-cells; table-banned-patterns; status-vocabulary |\n| 9 | table-structure-frozen |\n| 10 | table-prose-consistency |\n| 11 | missing-content-punchout; no-continuation-unapproved; certifiability-discipline; non-certifiable-outputs |\n| 12 | internal-labels |\n| 13 | change-accountability; change-record-schema; location-field; before-after-fields; style-marker-field; reason-field; assessment-function-field; facts-changed-field; tables-reviewed-array; observations-array; certifiable-flag |\n| 14 | substance-freeze |\n| 15 | pre-handoff-validation; schema-validation; token-parity; self-check-banned-patterns; table-line-traceability |\n| 16 | audit-boundary |\n\n# Output Specification\n- `runs/<run-id>/toned.md` — synthesized assessment draft (only file rewritten)\n- `runs/<run-id>/tone-changes.json` — change log with `tables_reviewed` and `observations`, validated against `../../schemas/tone-changes.schema.json`\n- `runs/<run-id>/punchout-missing-content.md` — only on a missing-content halt\n\n# Outbound Guardrail\nG5 is enforced deterministically by `harness.py (g5_check)` — schema, banned patterns, substance-freeze token diff, accountability, and two-key punch-out closure run as executable code — and by step 06\'s adversarial judgment review. Do not pre-check or self-certify against it; write only the declared outputs and let the harness run its gate.\n\n# Load-Bearing Check\nEvery instruction unit in #Instructions carries a `[criterion: <name>]` tag, and the Criterion mapping table maps every numbered instruction to its named criterion — 100% of instruction units are load-bearing and evaluable. No filler or decorative text is permitted.\n',
    "06": '---\nname: 06-adversarial-review\ndescription: Step 06 of the tone-assessmentV2 workflow. Runs the G5 adversarial review judgment layer over step 05\'s output — assessment quality, substance freeze (token + semantic), change accountability, punch-out closure, and PHI/confidentiality exposure — and emits a structured verdict. Finalization is performed by step 07 only after this review passes.\n---\n\n# Role\nYou are the **Adversarial Review agent** for the tone-assessmentV2 pipeline. Your ONLY responsibility is to independently challenge the output of step 05 — `toned.md` and `tone-changes.json` — against the G5 guardrails. You do NOT assemble the deliverable or close the audit trail; step 07-finalize performs those tasks after your verdict passes.\n\n# Task\nRun the G5 adversarial review gate. If G5 passes, write `g5-verdict.json` into the run directory (structured verdict) and write `.harness-step06-done`. If G5 fails, write `g5-judgment.md` listing the specific failing check(s) — do NOT write the done marker or the verdict — the harness loops back to step 05 or escalates to punch-out E at `loop_max`.\n\n**Execution context:** this step runs inside `harness.py` (`python harness.py run`). Deterministic G5 pre-checks (schema, banned patterns, substance-freeze token diff, accountability, two-key punch-out closure) run as executable code before you are invoked — your review is the judgment layer on top. The harness owns `run-state.json` transitions and writes all per-run audit records (`audit/run-<run-id>.jsonl`, `audit/guardrails-<run-id>.jsonl`, `audit/success-<run-id>.md`, `audit/punchout-<run-id>.md`; the shared aggregate logs are derived via `python harness.py rebuild-logs`) — write only `g5-verdict.json` (pass) or `g5-judgment.md` (fail).\n\n# Context\n- Inputs: `toned.md`, `draft.md`, `template`, `tone-changes.json`, `run-state.json`, all audit artifacts — all inside this workflow\'s `runs/<YYYY-QN>/` and `audit/` directories.\n- Outputs: `g5-verdict.json` (pass) or `g5-judgment.md` (fail) — written into `runs/<run-id>/`. All audit files are written by the harness, never by this step.\n- G5 has two layers: deterministic pre-checks in `harness.py (g5_check)` (executed before this step is invoked) and the adversarial judgment review performed here. Both are logged by the harness.\n- A run proceeds to step 07 iff G5 passes; finalization also requires every triggered punch-out to be two-key closed and the run to be certifiable.\n\n# Instructions\nEach instruction below is load-bearing and maps to an evaluation criterion.\n\n1. [criterion: g5-assessment-quality] Run G5 assessment-quality check — did the rewrite actually produce assessment-quality analysis throughout, not merely violate no style rules: score `toned.md` for (a) conformance to the template (required sections present and ordered, headings and formatting matched); (b) analytical depth — every substantive assessment section is conclusion-first, containing the applicable elements: condition, quarter movement, evidence, significance, qualification, recommended response, calibration — and no section merely reproduces source data, scores, export fields, or framework mappings without security significance — data without conclusion, metrics without significance, findings without quarterly context, and recommendations without analytical traceability are each a G5 failure condition (except any section titled "Security Awareness" case-insensitively, which is exempt from the conclusion-first/synthesis requirement but still subject to the substance freeze and banned-pattern checks); significance is explicitly tied to the client\'s business risk ("so what"); movement claims are temporally anchored to the specific quarter/observation period; positive findings are calibrated with their limitations and risks with their known/unknown scope; no Microsoft-style noun stacks or product-vendor grammar remain; (c) quarterly thesis — for each domain with comparable evidence, the report establishes preceding-vs-current-quarter condition, material movement, attribution (verified improvement/regression, measurement movement, or unattributable), carried-in unresolved findings, and newly material findings, and never presents post-quarter evidence as reporting-quarter progress; where comparison is unsupported it says so explicitly; (d) cross-signal synthesis — related controls are analyzed as themes (authentication/privileged access, legacy auth/access-policy, information protection, external collaboration/data egress, endpoint exposure/vulnerability management, logging/detection) rather than listed as isolated items; (e) client-consultative quality — sections lead with supported conclusions, technical findings are interpreted for the client, Microsoft/CIS/NIST inputs are supporting rather than narrative voice, prose is concise consultative without defensive caveat-stacking, and every substantive domain answers what was assessed, what changed, why it matters, and what\'s next.\n2. [criterion: g5-substance-freeze-token] Run G5 substance-freeze token check: extract every number, date, percentage, measurement, finding title, CIS/NIST reference, classification outcome, piece of evidence, and recommendation from `toned.md` — including those inside tables, charts, and embedded evidence blocks; each must exist in `draft.md` unchanged. Any new/altered factual token, any evidence that was re-written or re-scoped, any narrative framing that introduces a fact/cause/outcome absent from `draft.md`, any table row or cell whose meaning has shifted, or a paraphrase that shifts the client-facing meaning of a finding or recommendation — is a G5 failure.\n3. [criterion: g5-substance-freeze-semantic] Run G5 semantic substance-freeze check: independently of the token diff, inventory the entities, measurements, findings, and recommendations present in `draft.md` (by meaning, not by string) and verify every one is present in `toned.md` with the same client-facing meaning — and vice versa. A dropped finding, a merged finding whose scope changed, a recommendation whose strength was upgraded/downgraded, a metric restated on a different basis (e.g., 100% of evaluated vs. 100% of total), or a cause/effect claim re-attributed — is a G5 failure even when every token matches.\n4. [criterion: g5-change-accountability] Run G5 change-accountability check: `tone-changes.json` must validate against `../../schemas/tone-changes.schema.json` and contain both `tables_reviewed` and `observations` arrays. Every edit between `draft.md` and `toned.md` must be recorded with `location`, `before`, `after`, `style_marker`, `reason`, `assessment_function`, and `facts_changed`. Table edits are verified row by row against `tone-changes.json`; any unrecorded table row rewrite is a G5 failure. Every draft table must appear in `tables_reviewed`. Every `observations` entry must cite a concrete location (table/row/cell or section/paragraph). Any record with `facts_changed: true` is a hard fail. Coverage check: the set of `assessment_function` values must demonstrate assessment-quality synthesis across the report — a change log consisting only of `template_structure`/`professional_tone` records indicates no analytical rewrite occurred and is a G5 failure. An unrecorded edit is a G5 failure.\n5. [criterion: g5-failure-reporting] On G5 failure: write `g5-judgment.md` naming the specific failing check(s) with evidence (quote or location) — do NOT loop back, update `run-state.json`, write the verdict, or write audit files. The harness increments `loop_counters.G5`, decides loop-back vs. punch-out-E escalation, and records the failure.\n6. [criterion: g5-punchout-closure] Run G5 certifiability and punch-out closure check (the deterministic layer checks this first; re-verify as the adversarial reviewer — a self-granted approval that slipped through is still a hard fail here) — a two-key check, both artifacts required. For every punch-out in `run-state.json` with `triggered: true`: (a) `approved: true` AND `closure_evidence` citing a `audit/punchout-log.md` row for the same `run_id` with non-empty `human decision`, `resolved by`, and `resolved at`. An `approved: true` flag without the matching log row is a self-granted approval and a G5 hard fail. A decision recorded under a different `run_id` does not count — approvals never carry across runs. If `run-state.json` `certifiable` is `false`: (b) verify `non_certifiable_reasons` is non-empty and each reason is either resolved by a logged human decision (restored `certifiable: true` with `closure_evidence`) or still open — any open reason with `certifiable: true` is a G5 hard fail. A recorded `bypass_attempt` makes the run permanently non-certifiable — there is no restore path; no verdict may pass and the result is a non-certifiable run. The skill provides no human-waiver path for a G5 hard fail. Any unapproved triggered punch-out, any `certifiable: false` output without closure evidence, or `tone-changes.json` marked `"certifiable": false` is a G5 hard fail — STOP and wait for human sign-off.\n7. [criterion: g5-phi-confidentiality] Run G5 PHI/confidentiality-exposure check: scan `toned.md` for content that must never reach a client deliverable — PHI/PII (personal identifiers, health data, employee names tied to findings), credentials or secrets (passwords, tokens, connection strings, keys), internal-only artifacts (harness internals, audit-log paths, agent prompts, debugging notes), and tenant data belonging to a different client than the report subject. Any such exposure is a G5 hard fail regardless of other check results.\n8. [criterion: g5-verdict-emission] On G5 pass: write `g5-verdict.json` — a JSON object with `{"result": "pass", "checks": [{"check": "<name>", "result": "pass", "detail": "<evidence>"}], "findings": [...], "reviewed_at": "<UTC timestamp>"}` covering every check in instructions 1–7. Then write `.harness-step06-done`. Do NOT write the deliverable, `audit-report.md`, or any audit file — that is step 07\'s job.\n\n# Output Specification\n- `runs/<YYYY-QN>/g5-verdict.json` — structured pass verdict (only when the review passes)\n- `runs/<YYYY-QN>/g5-judgment.md` — failing checks with evidence (only when the review fails)\n\n# Outbound Guardrail\nStep 07-finalize runs only after this review\'s pass verdict exists in the run directory and the harness\'s closure/certifiability checks pass. There is no path to delivery that bypasses this review.\n\n# Load-Bearing Check\n≥90% of lines in #Instructions directly enforce an evaluable criterion (G5 assessment quality, token substance freeze, semantic substance freeze, change accountability, failure reporting, punch-out closure, PHI/confidentiality exposure, verdict emission). No filler or decorative text is permitted.\n',
    "07": '---\nname: 07-finalize\ndescription: Step 07 of the tone-assessmentV2 workflow. Runs only after step 06\'s G5 adversarial review passes and every triggered punch-out has two-key closure. Assembles the final client deliverable and writes audit-report.md, closing the run.\n---\n\n# Role\nYou are the **Finalize agent** for the tone-assessmentV2 pipeline. You run only after step 06\'s G5 adversarial review has produced a passing `g5-verdict.json` and the harness has verified punch-out closure and certifiability. Your job is packaging — assembling the reviewed `toned.md` into the final client deliverable and writing the run\'s `audit-report.md`. You do NOT re-review content, alter substance, or override any gate.\n\n# Task\nAssemble the final client deliverable and write `audit-report.md` into the run directory, then write `.harness-step07-done`.\n\n**Execution context:** this step runs inside `harness.py` (`python harness.py run`). The harness owns `run-state.json` transitions and writes all per-run audit records (`audit/run-<run-id>.jsonl`, `audit/guardrails-<run-id>.jsonl`, `audit/success-<run-id>.md`, `audit/punchout-<run-id>.md`; the shared aggregate logs are derived via `python harness.py rebuild-logs`) — write only the final deliverable and `audit-report.md`.\n\n# Context\n- Inputs: `toned.md`, `draft.md`, `template`, `tone-changes.json`, `g5-verdict.json`, `run-state.json`, all audit artifacts — all inside this workflow\'s `runs/<YYYY-QN>/` and `audit/` directories.\n- Outputs: the final client deliverable and `runs/<run-id>/audit-report.md`.\n- A run counts as end-to-end successful iff G5 passed, the run is certifiable (`certifiable: true` with all `non_certifiable_reasons` resolved), every triggered punch-out was resolved with a recorded human decision, and the final report was emitted. The harness records the result.\n\n# Instructions\nEach instruction below is load-bearing and maps to an evaluation criterion.\n\n1. [criterion: gate-precondition] Verify the preconditions before packaging: `g5-verdict.json` exists with `"result": "pass"`, `run-state.json` `certifiable` is `true`, and every triggered punch-out has `approved: true` plus `closure_evidence`. If any precondition is missing, STOP — do not emit the deliverable or the done marker; report the missing precondition to the harness output only.\n2. [criterion: deliverable-assembly] Assemble `toned.md` into the final client deliverable using the template\'s delivery format (file type, naming, front matter). The deliverable must contain the reviewed content verbatim — no content edits, rewrites, or additional analysis; packaging only.\n3. [criterion: audit-report] Write `audit-report.md` summarizing the run: steps executed (05, 06, 07), guardrail results (G4 and G5, with iteration counts), punch-outs raised and resolved, tone-change statistics (edits by `style_marker` and `assessment_function` coverage), narrative/structural changes applied, the G5 verdict, and end-to-end outcome.\n4. [criterion: closure-citation] In `audit-report.md`, cite the specific `audit/punchout-log.md` row(s) — run_id, decision, resolved-by, resolved-at — used to verify closure for every triggered punch-out. If no punch-outs triggered, state that explicitly.\n5. [criterion: success-reporting] Confirm the run\'s end-state to the harness output: `finalized` when all preconditions hold and the deliverable is emitted. The harness appends the result to `audit/success-<run-id>.md` and the final step record to `audit/run-<run-id>.jsonl` — never write these yourself.\n\n# Output Specification\n- Final client deliverable (report file, template delivery format)\n- `runs/<YYYY-QN>/audit-report.md` — run summary including the G5 verdict and punch-out closure citations\n\n# Outbound Guardrail\nThere is no downstream gate. Step 06\'s G5 adversarial review is the final quality checkpoint; this step packages the approved output only.\n\n# Load-Bearing Check\n≥90% of lines in #Instructions directly enforce an evaluable criterion (gate precondition, deliverable assembly, audit-report, closure citation, success reporting). No filler or decorative text is permitted.\n',
}
# === END EMBEDDED SKILLS ===

SKILLS = {
    "05": ROOT / ".github" / "skills" / "05-tone-consistency" / "SKILL.md",
    "06": ROOT / ".github" / "skills" / "06-adversarial-review" / "SKILL.md",
    "07": ROOT / ".github" / "skills" / "07-finalize" / "SKILL.md",
}
EXPECTED_OUTPUTS = {"05": ["toned.md", "tone-changes.json"],
                    "06": ["g5-verdict.json"],
                    "07": ["audit-report.md"]}
VALID_RESULTS = ("pass", "fail", "halted", "stopped")

# ---------------------------------------------------------------------------
# Common helpers
# ---------------------------------------------------------------------------


def load_config():
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    p = ROOT / "harness.config.json"
    if p.exists():
        for k, v in json.loads(p.read_text(encoding="utf-8")).items():
            cfg[k] = v
    return cfg


def run_dir(run_id):
    return ROOT / "runs" / run_id


def state_path(run_id):
    return run_dir(run_id) / "run-state.json"


def _normalize_punchouts(state):
    """Map legacy run-state punch-out forms (list under `punchouts` or
    `punch_outs`) onto the canonical dict schema, preserving every
    original field. Lets gates/bypass-test read pre-harness run-states."""
    po = state.get("punchouts")
    if po is None:
        po = state.pop("punch_outs", None)
        if po is not None:
            state["punchouts"] = po
    if isinstance(po, dict):
        return state
    canon = {k: {"triggered": False,
                 "file": ("audit/punchout-missing-content.md"
                          if k == "A_missing_content"
                          else "audit/punchout-log.md"),
                 "approved": False, "closure_evidence": None,
                 "bypass_attempt": None}
             for k in ("A_missing_content", "E_loop_exhaustion")}
    for e in (po or []):
        ident = str(e.get("type") or e.get("id") or "")
        letter = ("A" if ident.startswith(("A", "PO")) or
                  "missing" in ident.lower() else "E")
        key = f"{letter}_{'missing_content' if letter == 'A' else 'loop_exhaustion'}"
        entry = canon[key]
        entry.update(e)
        entry["triggered"] = e.get(
            "triggered", str(e.get("status", "")).lower()
            in ("open", "escalated", "pending"))
        entry["approved"] = bool(e.get("approved", False))
        entry.setdefault("closure_evidence", e.get("closure_evidence"))
        if e.get("bypass_test") and not entry.get("bypass_attempt"):
            entry["bypass_attempt"] = (
                f"{e['bypass_test']}: {e.get('bypass_result', '')}")
    state["punchouts"] = canon
    return state


def load_state(run_id):
    state = json.loads(state_path(run_id).read_text(encoding="utf-8"))
    return _normalize_punchouts(state)


def save_state(run_id, state):
    state_path(run_id).write_text(json.dumps(state, indent=2) + "\n",
                                  encoding="utf-8")


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(path):
    """Hash with CRLF normalized to LF — a text file copied through
    tools that only produce LF still verifies byte-equivalent."""
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


def _utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

# ---------------------------------------------------------------------------
# Audit writers
# ---------------------------------------------------------------------------


def _run_jsonl_path(run_id):
    """Per-run audit log — every file the harness writes is scoped to one
    run so sync-out to a file-tool-only store (SharePoint) is always a
    create, never a rewrite of shared history. The shared aggregate files
    (guardrails.jsonl, success-log.md, punchout-log.md) are DERIVED views
    — regenerate them with `python harness.py rebuild-logs`."""
    return ROOT / "audit" / f"run-{run_id}.jsonl"


def append_step_record(run_id, record):
    record.setdefault("ts", _utcnow())
    record.setdefault("run_id", run_id)
    with _run_jsonl_path(run_id).open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def append_guardrail_record(run_id, gate, result, checks,
                            iteration=None, note=None):
    rec = {"run_id": run_id, "gate": gate,
           "handoff": "inputs->tone" if gate == "G4"
           else "tone->adversarial-review",
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
    """A real human closure row for this run — and, when `letter` is
    given, for that specific punch-out (column 2 starts with 'A:'/'E:').
    Bypass-test rows and rows for other punch-outs don't count."""
    for name in ("punchout-log.md", f"punchout-{run_id}.md"):
        log = ROOT / "audit" / name
        if not log.exists():
            continue
        for line in log.read_text(encoding="utf-8").splitlines():
            if not line.strip().startswith("|"):
                continue
            cols = [c.strip()
                    for c in line.strip().strip("|").split("|")]
            if len(cols) < 9 or cols[1] != run_id \
                    or not cols[7] or not cols[8] \
                    or "bypass test" in cols[3].lower():
                continue
            if letter and not cols[2].startswith(f"{letter}:"):
                continue
            return True
    return False


def rebuild_logs():
    """Regenerate the shared aggregate audit views from the per-run files.
    Run locally whenever you want the examiner-facing aggregates refreshed
    — never needed during a run. Appends only rows/lines not already
    present (deduped by exact line)."""
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
                if pf.name == "punchout-missing-content.md":
                    continue
                for line in pf.read_text(encoding="utf-8").splitlines():
                    if line.strip().startswith("|") \
                            and line not in existing:
                        f.write(line + "\n")
                        existing.add(line)
                        added += 1
        out[aggregate] = added
    _rebuild_success_report()
    return {"appended_rows": out}


def _rebuild_success_report():
    """Regenerate audit/success-report.md — a fully derived summary
    splitting production runs from gate-test runs (run-ids containing
    'Test') with computed end-to-end success rates. Rewritten in full
    on every rebuild; safe because it derives only from success-log.md."""
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
    header = ("| date | run id | result | punch-outs | G5 iterations "
              "| notes |\n|---|---|---|---|---|---|\n")

    def rate(rows):
        p = sum(1 for r in rows if "| pass |" in r)
        h = sum(1 for r in rows if "| halted |" in r)
        return p, h

    pp, ph = rate(prod)
    tp, th = rate(test)
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


def meter_step(config, step_prompt, step_output, rd=None, step=None):
    mcfg = config.get("metering", {})
    usage_file = (rd / f".harness-step{step}-usage.json"
                  if rd is not None and step else None)
    provider_usage = None
    if usage_file and usage_file.exists():
        try:
            provider_usage = json.loads(
                usage_file.read_text(encoding="utf-8"))
        except Exception:
            provider_usage = None
    usage = _usage_from_session_log(mcfg.get("session_log_path"))
    if provider_usage and isinstance(
            provider_usage.get("input_tokens"), int):
        tokens_in = provider_usage["input_tokens"]
        tokens_out = provider_usage.get("output_tokens") or 0
        method = "provider-usage"
    elif usage:
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
# Step prompt builder
# ---------------------------------------------------------------------------


def build_prompt(step, run_id, rd):
    # Embedded skill text is authoritative (hash-verified single file);
    # the on-disk SKILL.md is only a fallback for local hacking.
    skill = EMBEDDED_SKILLS.get(step) or (
        SKILLS[step].read_text(encoding="utf-8")
        if SKILLS[step].exists() else "(SKILL.md not found)")
    template, tsource = find_template(run_id)

    def _inline(path, label):
        try:
            text = Path(path).read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ""
        return f"\n=== {label}: {Path(path).name} ===\n{text}\n"

    inputs_block = ""
    for f in sorted((rd / "inputs").glob("*")):
        if f.suffix.lower() in (".md", ".txt", ".json"):
            inputs_block += _inline(f, "INPUT")
    template_block = (
        _inline(template, "TEMPLATE")
        if template and Path(template).suffix.lower() in (".md", ".txt")
        else "")

    context_block = _inline(ROOT / "schemas" / "tone-changes.schema.json", "SCHEMA")
    if step == "05":
        context_block += (
            "\nOUTPUT CONTRACT: tone-changes.json must contain changes, "
            "tables_reviewed, and observations arrays. Record every actual edit. "
            "assessment_function is NOT style_marker: choose only "
            "executive_conclusion, quarter_movement, cross_signal_synthesis, "
            "evidence_interpretation, security_significance, evidence_limitation, "
            "recommendation_traceability, historical_context, template_structure, "
            "or professional_tone. assessment_first is a style_marker only. "
            "facts_changed must be false. Check every record against the schema "
            "before returning the JSON file map.\n")
    if step in ("06", "07"):
        for name in ("toned.md", "tone-changes.json", "run-state.json"):
            context_block += _inline(rd / name, "ARTIFACT")
    if step == "07":
        context_block += _inline(rd / "g5-verdict.json", "ARTIFACT")

    return (
        f"Execute the following SKILL.md for run '{run_id}'.\n"
        f"All working artifacts live in: {rd}\n"
        f"Inputs are in: {rd / 'inputs'}\n"
        f"The authoritative template is: {template} (source: {tsource})\n"
        f"NOTE: you have no filesystem access — all file contents needed "
        f"are inlined below. Respond with a JSON object mapping output "
        f"file names to their full contents; the runner writes them.\n"
        f"Write required outputs into the run directory. Do NOT update "
        f"run-state.json, guardrails.jsonl, run-*.jsonl, success-log.md, or "
        f"punchout-log.md — the harness owns orchestration and logging.\n"
        f"On a missing-content punch-out, write punchout-missing-content.md "
        f"into the run directory and STOP without producing toned.md.\n"
        f"{inputs_block}{template_block}{context_block}\n"
        f"=== SKILL.md ===\n{skill}\n")

# ---------------------------------------------------------------------------
# G4 — deterministic input-completeness gate
# ---------------------------------------------------------------------------

_HEADING = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)


def _template_headings(template_path):
    if template_path.suffix.lower() in (".md", ".txt"):
        text = template_path.read_text(encoding="utf-8", errors="replace")
        return len(_HEADING.findall(text))
    return 1 if template_path.stat().st_size > 0 else 0


def find_template(run_id, config=None):
    """Per-run override first (inputs/template.*); else the repo-root
    default template named in config.default_template."""
    p = find_input(run_id, "template")
    if p:
        return p, "run-inputs"
    cfg = config or load_config()
    default = cfg.get("default_template")
    if default:
        p = ROOT / default
        if p.exists():
            return p, f"default:{default}"
    return None, None


def docx_to_md(docx_path, md_path):
    """Extract paragraphs/headings from a .docx into markdown — stdlib
    only (docx is a zip of XML). Regenerate CSA Template.md with:
    python harness.py template-md"""
    import zipfile
    import xml.etree.ElementTree as ET
    W = ("{http://schemas.openxmlformats.org"
         "/wordprocessingml/2006/main}")
    with zipfile.ZipFile(docx_path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    lines, headings = [], 0
    for p in root.iter(W + "p"):
        text = "".join(t.text or "" for t in p.iter(W + "t")).strip()
        if not text:
            continue
        style = p.find(f"{W}pPr/{W}pStyle")
        m = re.match(r"Heading(\d)",
                     style.get(W + "val", "") if style is not None else "")
        if m:
            headings += 1
            lines.append("#" * int(m.group(1)) + " " + text)
        else:
            lines.append(text)
    md_path.write_text("\n\n".join(lines) + "\n", encoding="utf-8")
    return {"source": str(docx_path), "output": str(md_path),
            "paragraphs": len(lines), "headings": headings,
            "sha256": sha256_file(md_path)}


def _ensure_draft_md(run_id, config=None):
    """If inputs/ holds a draft.docx (or .doc) but no draft.md, convert it
    deterministically before G4 — the step agent cannot reliably extract a
    binary docx through the runner's JSON contract, and downstream checks
    (D4 substance freeze) read only .md. Records the conversion in the
    run's guardrails log so both hashes are auditable."""
    draft = find_input(run_id, "draft")
    if not draft or draft.suffix.lower() not in (".docx", ".doc"):
        return
    md = draft.with_suffix(".md")
    if md.exists():
        return
    try:
        result = docx_to_md(draft, md)
        append_guardrail_record(
            run_id, "G4", "pass",
            [{"check": "draft docx->md conversion", "result": "pass",
              "detail": f"{draft.name} -> {md.name}: "
                        f"{result['paragraphs']} paragraphs, "
                        f"{result['headings']} headings",
              "source_sha256": sha256_file(draft),
              "output_sha256": result["sha256"]}])
    except Exception as exc:
        append_guardrail_record(
            run_id, "G4", "fail",
            [{"check": "draft docx->md conversion", "result": "fail",
              "detail": f"{draft.name}: {exc}"}])


def g4_check(run_id, config=None):
    checks, hashes = [], {}
    draft = find_input(run_id, "draft")
    if draft and draft.stat().st_size > 0:
        hashes["draft"] = sha256_file(draft)
        checks.append({"check": "draft readable", "result": "pass",
                       "file": draft.name, "sha256": hashes["draft"]})
    else:
        checks.append({"check": "draft readable", "result": "fail",
                       "detail": f"runs/{run_id}/inputs/draft.* missing"})

    template, tsource = find_template(run_id, config)
    headings = 0
    if template and template.stat().st_size > 0:
        hashes["template"] = sha256_file(template)
        checks.append({"check": "template readable", "result": "pass",
                       "file": f"{template.name} ({tsource})",
                       "sha256": hashes["template"]})
        headings = _template_headings(template)
    else:
        checks.append({"check": "template readable", "result": "fail",
                       "detail": "no inputs/template.* and no "
                                 "default_template found"})

    try:
        json.loads(state_path(run_id).read_text(encoding="utf-8"))
        checks.append({"check": "run-state.json present", "result": "pass"})
    except Exception as exc:
        checks.append({"check": "run-state.json present", "result": "fail",
                       "detail": str(exc)})

    if template and headings > 0:
        checks.append({"check": "template heading structure extractable",
                       "result": "pass", "headings": headings})
    elif template:
        checks.append({"check": "template heading structure extractable",
                       "result": "fail", "detail": "no headings extractable"})

    result = "pass" if all(c["result"] == "pass" for c in checks) else "fail"
    if result == "pass":
        (run_dir(run_id) / ".g4-passed").write_text(json.dumps(
            {"gate": "G4", "run_id": run_id, "hashes": hashes}, indent=2),
            encoding="utf-8")
    return {"result": result, "checks": checks, "hashes": hashes}

# ---------------------------------------------------------------------------
# G5 — deterministic pre-checks (fail-closed before the adversarial agent)
# ---------------------------------------------------------------------------

_FACT_RE = re.compile(
    r"\b\d{1,3}(?:\.\d+)?%|\b\d{4}-\d{2}-\d{2}\b|\b\d+/\d+\b|\b\d+\.\d+\b"
    r"|\b\d{4}\b|\bCIS[\s-]?\d+(?:\.\d+)*\b|\bNIST[\s-]?[A-Z0-9.-]+\b",
    re.IGNORECASE)

_ANALYTICAL_FUNCTIONS = {
    "executive_conclusion", "quarter_movement", "cross_signal_synthesis",
    "evidence_interpretation", "security_significance", "evidence_limitation",
    "recommendation_traceability", "historical_context"}


def _mini_validate(instance, schema, path="$"):
    """Subset JSON-Schema validator (type/required/properties/enum/items).
    Records coverage honestly: reports which keywords it enforces."""
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
    if t == "array" and "items" in schema:
        for i, item in enumerate(instance):
            errors += _mini_validate(item, schema["items"], f"{path}[{i}]")
    return errors


def _schema_check(tone_changes):
    """Validate tone-changes.json. Returns (errors, validator_name)."""
    try:
        import jsonschema
        schema_file = ROOT / "schemas" / "tone-changes.schema.json"
        schema = (json.loads(schema_file.read_text(encoding="utf-8"))
                  if schema_file.exists() else TONE_CHANGES_SCHEMA)
        jsonschema.validate(tone_changes, schema)
        return [], "jsonschema"
    except ImportError:
        return _mini_validate(tone_changes, TONE_CHANGES_SCHEMA), \
            "builtin-mini-validator"
    except Exception as exc:
        return [getattr(exc, "message", str(exc))], "jsonschema"


def g5_check(run_id):
    rd = run_dir(run_id)
    toned_path, tc_path = rd / "toned.md", rd / "tone-changes.json"
    checks = []

    if (rd / ".g4-passed").exists():
        checks.append({"check": "D1-g4-sentinel", "result": "pass"})
    else:
        checks.append({"check": "D1-g4-sentinel", "result": "fail",
                       "detail": ".g4-passed missing"})

    if not toned_path.exists():
        checks.append({"check": "outputs-present", "result": "fail",
                       "detail": "toned.md missing"})
    if not tc_path.exists():
        checks.append({"check": "outputs-present", "result": "fail",
                       "detail": "tone-changes.json missing"})
    if any(c["result"] == "fail" for c in checks):
        return {"result": "fail", "checks": checks}

    toned_text = toned_path.read_text(encoding="utf-8", errors="replace")
    try:
        tone_changes = json.loads(tc_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        checks.append({"check": "D2-schema-valid", "result": "fail",
                       "detail": f"not valid JSON: {exc}"})
        return {"result": "fail", "checks": checks}

    # D2 schema
    errors, validator = _schema_check(tone_changes)
    if errors:
        checks.append({"check": "D2-schema-valid", "result": "fail",
                       "validator": validator,
                       "detail": "; ".join(errors[:10])})
    else:
        checks.append({"check": "D2-schema-valid", "result": "pass",
                       "validator": validator})

    # D3 banned patterns
    pats = [re.compile(p, re.IGNORECASE) for p in BANNED_PATTERNS]
    first_person = pats[0]
    hits = []
    for i, line in enumerate(toned_text.splitlines(), 1):
        for j, pat in enumerate(pats):
            m = pat.search(line)
            if m and j == 0:
                # proper-noun exemption: a capitalized first-person token
                # followed by a capitalized word is a product/role name
                # ("My Custom Apps", "We Cloud Services"), not pronouns.
                # Never exempt at sentence start — "We recommend…" is a
                # pronoun even when followed by a capitalized word.
                rest = line[m.end():].lstrip()
                sentence_start = re.search(
                    r"(^|[.!?]\s+)$", line[:m.start()]) is not None
                if (m.group(0)[0].isupper() and rest[:1].isupper()
                        and not sentence_start):
                    m = first_person.search(line, m.end())
                    if not m:
                        continue
                    rest = line[m.end():].lstrip()
                    sentence_start = re.search(
                        r"(^|[.!?]\s+)$", line[:m.start()]) is not None
                    if (m.group(0)[0].isupper() and rest[:1].isupper()
                            and not sentence_start):
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

    # D4 substance freeze
    dp = find_input(run_id, "draft")
    draft_text = (dp.read_text(encoding="utf-8", errors="replace")
                  if dp and dp.suffix == ".md" else "")
    if not draft_text:
        checks.append({"check": "D4-substance-freeze", "result": "fail",
                       "detail": "draft text unavailable"})
    else:
        draft_tokens = {t.lower() for t in _FACT_RE.findall(draft_text)}
        new_tokens = sorted({t for t in _FACT_RE.findall(toned_text)
                             if t.lower() not in draft_tokens})
        checks.append({"check": "D4-substance-freeze",
                       "result": "fail" if new_tokens else "pass",
                       "detail": ("factual tokens absent from draft: "
                                  + ", ".join(new_tokens[:15]) if new_tokens
                                  else "all factual tokens traceable to draft")})

    # D5 change accountability
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

    # D6 punch-out two-key closure
    state = load_state(run_id)
    open_pos = [n for n, po in state.get("punchouts", {}).items()
                if po.get("triggered") and
                (not po.get("approved")
                 or not punchout_log_has_closure(run_id, n[0]))]
    checks.append({"check": "D6-punchout-closure",
                   "result": "fail" if open_pos else "pass",
                   "detail": ("triggered but not two-key closed: "
                              + ", ".join(open_pos) if open_pos else "")})

    return {"result": "pass" if all(c["result"] == "pass" for c in checks)
            else "fail", "checks": checks}

# ---------------------------------------------------------------------------
# Pipeline state machine
# ---------------------------------------------------------------------------


def _log_punchout_trigger(run_id, letter, reason):
    """Write the trigger row to audit/punchout-<run-id>.md when the
    harness escalates to a punch-out (loop_max exhaustion)."""
    append_punchout_log(
        run_id,
        f"{letter}: " + ("missing-content" if letter == "A"
                         else "loop-exhaustion"),
        reason, "none attempted (halt honored)",
        "not applicable (halt honored)",
        "pending: approve retry / accept halt")


def _trigger_punchout(state, key, reason):
    po = state["punchouts"][key]
    if po.get("triggered") and po.get("approved"):
        # Re-trigger after a consumed "approve retry" — the prior closure
        # authorized one re-execution, which has now escalated again.
        # Clear it so a fresh human decision is required; the punch-out
        # log already holds a new pending row for this escalation.
        po["approved"] = False
        po["closure_evidence"] = None
        po.pop("resolved_by", None)
        po.pop("resolved_at", None)
    po["triggered"] = True
    state["certifiable"] = False
    if reason not in state["non_certifiable_reasons"]:
        state["non_certifiable_reasons"].append(reason)


def _record_step(run_id, config, step_name, gate, gate_result, rd,
                 prompt, outputs_text, finalized=False):
    input_hashes = {}
    p = find_input(run_id, "draft")
    if p:
        input_hashes[p.name] = sha256_file(p)
    p, _ = find_template(run_id, config)
    if p:
        input_hashes[p.name] = sha256_file(p)
    output_hashes = {n: sha256_file(rd / n)
                     for n in EXPECTED_OUTPUTS[step_name]
                     if (rd / n).exists()}
    meter = meter_step(config, prompt, outputs_text, rd=rd, step=step_name)
    step_names = {"05": "05-tone-consistency",
                  "06": "06-adversarial-review",
                  "07": "07-finalize"}
    append_step_record(run_id, {
        "step": step_names.get(step_name, step_name),
        "model": (os.environ.get("HARNESS_MODEL")
                or config.get("model", "unknown")),
        "environment": "runner-api",
        "operator": config.get("operator", ""),
        "initiated_by": "harness",
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


def _prompt(run_id, rd, step, extra=None):
    pf = rd / f".harness-step{step}-prompt.md"
    pf.write_text(build_prompt(step, run_id, rd), encoding="utf-8")
    action = {"action": "execute_step", "step": step,
              "prompt_file": str(pf),
              "expected_outputs": EXPECTED_OUTPUTS[step],
              "done_marker": str(rd / f".harness-step{step}-done")}
    if extra:
        action["detail"] = extra
    return action


def advance(run_id, config, resume=False):
    outcome = _advance(run_id, config, resume=resume)
    try:
        rebuild_logs()  # keep shared aggregates in lockstep — idempotent
    except Exception:
        pass
    try:
        (ROOT / "harness.sha256").write_text(
            sha256_file(Path(__file__)) + "\n", encoding="utf-8")
    except Exception:
        pass
    return outcome


def _advance(run_id, config, resume=False):
    rd = run_dir(run_id)
    if not rd.exists():
        init_run(run_id, operator=config.get("operator", ""))
        return {"action": "needs-inputs",
                "detail": f"created {rd}; place draft.* and template.* "
                          "in inputs/ then call drive again"}
    if not (rd / "run-state.json").exists():
        init_run(run_id, operator=config.get("operator", ""))
    state = load_state(run_id)
    status = state.get("status", "in-progress")
    loop_max = config.get("loop_max", state.get("loop_max", 2))

    if status == "finalized":
        return {"action": "done", "status": "finalized"}

    if status == "non-finalizable":
        return {"action": "done", "status": "non-finalizable",
                "detail": "run cannot finalize: certifiable=false "
                          "(permanent); all punch-outs closed"}

    if status in ("awaiting-human", "escalated", "stopped", "failed"):
        open_pos = [n for n, po in state.get("punchouts", {}).items()
                    if po.get("triggered") and
                    (not po.get("approved")
                     or not punchout_log_has_closure(run_id, n[0]))]
        # All punch-outs closed but certifiable is permanently false —
        # nothing left for a human to decide: settle terminally.
        if not open_pos and status in ("awaiting-human", "escalated") \
                and not state.get("certifiable", True) \
                and not any("approve retry" in str(po.get("closure_evidence", "")).lower()
                            for po in state.get("punchouts", {}).values()):
            state["status"] = "non-finalizable"
            save_state(run_id, state)
            return {"action": "done", "status": "non-finalizable",
                    "detail": "run cannot finalize: certifiable=false "
                              "(permanent); all punch-outs closed"}
        if not resume:
            return {"action": "awaiting_human", "status": status,
                    "detail": "requires human decision recorded in "
                              "audit/punchout-<run-id>.md + run-state.json, "
                              "then call drive with --resume"}
        if open_pos:
            return {"action": "awaiting_human", "status": status,
                    "detail": f"punch-outs lack two-key closure: {open_pos}"}
        state["loop_counters"]["G5"] = 0
        # Re-run G4 on resume: inputs may have changed during the halt
        # (e.g. punch-out A closed by supplied content), and the audit
        # trail should carry a G4 record for the draft actually used.
        state["status"] = status = "needs-g4"
        save_state(run_id, state)

    # ----- G4 -----
    if status in ("in-progress", "needs-g4"):
        _ensure_draft_md(run_id, config)
        g4r = g4_check(run_id, config)
        append_guardrail_record(run_id, "G4", g4r["result"], g4r["checks"],
                                iteration=state["loop_counters"]["G4"] + 1)
        if g4r["result"] == "fail":
            state["loop_counters"]["G4"] += 1
            if state["loop_counters"]["G4"] >= loop_max:
                _trigger_punchout(state, "E_loop_exhaustion",
                                  "G4 loop_max reached")
                _log_punchout_trigger(run_id, "E",
                                      "G4 loop_max reached")
                state["status"] = "escalated"
                save_state(run_id, state)
                _success(state, run_id, "halted", 0,
                         "G4 failed at loop_max; escalated to human")
                return {"action": "done", "status": "escalated",
                        "detail": g4r["checks"]}
            state["status"] = "needs-g4"
            save_state(run_id, state)
            return {"action": "fix_inputs", "detail": g4r["checks"]}
        state["status"] = "needs-step05"
        save_state(run_id, state)
        return _prompt(run_id, rd, "05")

    # ----- step 05 -> deterministic G5 -----
    if status == "needs-step05":
        if (rd / "punchout-missing-content.md").exists() \
                and not (rd / "toned.md").exists() \
                and not (state["punchouts"]["A_missing_content"]
                         .get("approved")
                         and punchout_log_has_closure(run_id, "A")):
            _trigger_punchout(state, "A_missing_content",
                              "template section has no draft content")
            state["status"] = "awaiting-human"
            save_state(run_id, state)
            append_punchout_log(
                run_id, "A: missing-content",
                "template requires a section the draft has no content for",
                "none attempted (halt honored)",
                "not applicable (halt honored)",
                "pending: provide content / drop section / defer")
            _success(state, run_id, "halted", state["loop_counters"]["G5"],
                     "punch-out A raised; awaiting human decision")
            return {"action": "awaiting_human", "status": "awaiting-human",
                    "detail": "punch-out A: missing content"}

        marker = rd / ".harness-step05-done"
        missing = [n for n in EXPECTED_OUTPUTS["05"]
                   if not (rd / n).exists()]
        if not marker.exists():
            if _last_runner_failed(run_id, "05"):
                return _prompt(run_id, rd, "05")
            return {"action": "wait",
                    "detail": "waiting for .harness-step05-done"}
        if missing:
            # marker synced before outputs — keep waiting, keep marker
            return {"action": "wait",
                    "detail": f"done marker present but outputs not yet "
                              f"synced: {missing}"}
        marker.unlink()

        prompt = build_prompt("05", run_id, rd)
        outputs_text = "".join(
            (rd / n).read_text(encoding="utf-8", errors="replace")
            for n in EXPECTED_OUTPUTS["05"])
        _record_step(run_id, config, "05", "G4", "pass", rd,
                     prompt, outputs_text)

        g5r = g5_check(run_id)
        state["loop_counters"]["G5"] += 1
        iterations = state["loop_counters"]["G5"]
        append_guardrail_record(run_id, "G5", g5r["result"], g5r["checks"],
                                iteration=iterations)
        if g5r["result"] == "fail":
            if iterations >= loop_max:
                _trigger_punchout(state, "E_loop_exhaustion",
                                  "G5 loop_max reached")
                _log_punchout_trigger(run_id, "E",
                                      "G5 loop_max reached")
                state["status"] = "escalated"
                save_state(run_id, state)
                _success(state, run_id, "halted", iterations,
                         "deterministic G5 failed at loop_max; escalated")
                return {"action": "done", "status": "escalated",
                        "detail": g5r["checks"]}
            save_state(run_id, state)
            failed = [c["check"] for c in g5r["checks"]
                      if c["result"] == "fail"]
            return _prompt(run_id, rd, "05",
                           extra=f"G5 deterministic fail (iteration "
                                 f"{iterations}) — fix: {failed}")
        state["status"] = "needs-step06"
        save_state(run_id, state)
        return _prompt(run_id, rd, "06")

    # ----- step 06 -> adversarial review (judgment only) -----
    if status == "needs-step06":
        # Judgment-layer G5 failure channel: step 06 writes
        # g5-judgment.md (failing checks) instead of the done marker.
        jf = rd / "g5-judgment.md"
        if jf.exists():
            detail = jf.read_text(
                encoding="utf-8", errors="replace")[:2000]
            jf.unlink()
            state["loop_counters"]["G5"] += 1
            iterations = state["loop_counters"]["G5"]
            append_guardrail_record(
                run_id, "G5", "fail",
                [{"check": "06-judgment-review", "result": "fail",
                  "detail": detail}], iteration=iterations)
            if iterations >= loop_max:
                _trigger_punchout(state, "E_loop_exhaustion",
                                  "G5 judgment fail at loop_max")
                _log_punchout_trigger(run_id, "E",
                                      "G5 judgment fail at loop_max")
                state["status"] = "escalated"
                save_state(run_id, state)
                _success(state, run_id, "halted", iterations,
                         "G5 judgment failed at loop_max; escalated")
                return {"action": "done", "status": "escalated",
                        "detail": detail}
            save_state(run_id, state)
            return _prompt(run_id, rd, "05",
                           extra=f"G5 judgment fail (iteration "
                                 f"{iterations}): {detail}")
        marker = rd / ".harness-step06-done"
        missing = [n for n in EXPECTED_OUTPUTS["06"]
                   if not (rd / n).exists()]
        if not marker.exists():
            if _last_runner_failed(run_id, "06"):
                return _prompt(run_id, rd, "06")
            return {"action": "wait",
                    "detail": "waiting for .harness-step06-done"}
        if missing:
            return {"action": "wait",
                    "detail": f"done marker present but outputs not yet "
                              f"synced: {missing}"}
        marker.unlink()

        prompt = build_prompt("06", run_id, rd)
        outputs_text = "".join(
            (rd / n).read_text(encoding="utf-8", errors="replace")
            for n in EXPECTED_OUTPUTS["06"])
        _record_step(run_id, config, "06", "G5", "pass", rd,
                     prompt, outputs_text, finalized=False)
        state["status"] = "needs-step07"
        save_state(run_id, state)
        return _prompt(run_id, rd, "07")

    # ----- step 07 -> finalize -----
    if status == "needs-step07":
        marker = rd / ".harness-step07-done"
        missing = [n for n in EXPECTED_OUTPUTS["07"]
                   if not (rd / n).exists()]
        if not marker.exists():
            if _last_runner_failed(run_id, "07"):
                return _prompt(run_id, rd, "07")
            return {"action": "wait",
                    "detail": "waiting for .harness-step07-done"}
        if missing:
            return {"action": "wait",
                    "detail": f"done marker present but outputs not yet "
                              f"synced: {missing}"}
        marker.unlink()

        prompt = build_prompt("07", run_id, rd)
        outputs_text = "".join(
            (rd / n).read_text(encoding="utf-8", errors="replace")
            for n in EXPECTED_OUTPUTS["07"])

        state = load_state(run_id)
        closure_ok = all(
            (not po.get("triggered")) or
            (po.get("approved") and punchout_log_has_closure(run_id, n[0]))
            for n, po in state.get("punchouts", {}).items())
        finalized = closure_ok and state.get("certifiable", True)
        _record_step(run_id, config, "07", "G5", "pass", rd,
                     prompt, outputs_text, finalized=finalized)

        if not finalized:
            open_pos = [n for n, po in state["punchouts"].items()
                        if po.get("triggered") and
                        (not po.get("approved")
                         or not punchout_log_has_closure(
                             run_id, n[0]))]
            if open_pos:
                state["status"] = "awaiting-human"
                save_state(run_id, state)
                _success(state, run_id, "halted",
                         state["loop_counters"]["G5"],
                         "finalization blocked: unclosed punch-out")
                return {"action": "awaiting_human",
                        "status": "awaiting-human",
                        "detail": "certifiability/closure check failed"}
            # Terminal: all punch-outs closed but certifiable is
            # permanently false (e.g. recorded bypass attempt).
            # There is nothing left for a human to decide.
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
                 "G4 pass; deterministic G5 pass; step 07 finalized")
        return {"action": "done", "status": "finalized"}

    return {"action": "wait", "detail": f"unhandled status: {status}"}


def _last_runner_failed(run_id, step):
    """True when the most recent runner_exec record for this step exited
    non-zero — meaning the dispatch was already consumed but the runner
    failed, so the step must be re-dispatched instead of waited on. No
    record at all means manual mode / pre-runner era: keep waiting."""
    log = ROOT / "audit" / f"run-{run_id}.jsonl"
    if not log.exists():
        return False
    last = None
    for line in log.read_text(encoding="utf-8",
                              errors="replace").splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("type") == "runner_exec" and rec.get("step") == step:
            last = rec
    return bool(last is not None and last.get("exit_code") != 0)


def _execute_step_via_runner(run_id, outcome, config):
    """Spawn runner.command for an execute_step action. Returns a wait or
    error outcome; in manual mode (or with no command configured) returns
    the original action for an external agent to pick up."""
    runner = config.get("runner", {})
    command = runner.get("command") or ""
    if runner.get("mode", "manual") != "auto" or not command:
        return outcome
    rd = run_dir(run_id)
    env = dict(os.environ)
    env.update({
        "HARNESS_RUN_ID": run_id,
        "HARNESS_STEP": outcome["step"],
        "HARNESS_PROMPT_FILE": outcome["prompt_file"],
        "HARNESS_RUN_DIR": str(rd),
        "HARNESS_DONE_MARKER": outcome["done_marker"],
        "HARNESS_EXPECTED_OUTPUTS": ",".join(outcome["expected_outputs"]),
        "HARNESS_MODEL": (os.environ.get("HARNESS_MODEL")
                        or config.get("model", "unknown")),
    })
    timeout = runner.get("timeout_seconds", 1800)
    record = {"type": "runner_exec", "step": outcome["step"],
              "command": command, "ts": _utcnow(), "run_id": run_id}
    try:
        proc = subprocess.run(shlex.split(command), cwd=str(ROOT), env=env,
                              capture_output=True, text=True,
                              timeout=timeout)
        record["exit_code"] = proc.returncode
        record["stdout"] = (proc.stdout or "")[-2000:]
        record["stderr"] = (proc.stderr or "")[-2000:]
    except Exception as e:
        record["exit_code"] = -1
        record["stderr"] = str(e)
    append_step_record(run_id, record)
    if record["exit_code"] != 0:
        return {"action": "error", "step": outcome["step"],
                "detail": f"runner.command failed: "
                          f"{record['stderr'][:1000]}"}
    return {"action": "wait",
            "detail": f"runner executed step {outcome['step']}"}


def _advance_and_execute(run_id, config, resume=False):
    """advance() plus runner.command execution when the outcome is a step
    dispatch — the harness is the executor, not just a state machine."""
    outcome = advance(run_id, config, resume=resume)
    if outcome.get("action") == "execute_step":
        outcome = _execute_step_via_runner(run_id, outcome, config)
    return outcome


def run(run_id, config, resume=False, poll_seconds=15):
    """Foreground loop: drive until terminal. In auto mode the harness
    itself invokes runner.command for each step dispatch."""
    while True:
        outcome = _advance_and_execute(run_id, config, resume=resume)
        resume = False
        print(json.dumps(outcome, indent=2, default=str), flush=True)
        if outcome["action"] != "wait":
            return outcome
        time.sleep(poll_seconds)

# ---------------------------------------------------------------------------
# Bypass testing
# ---------------------------------------------------------------------------


def bypass_test(run_id, letter, operator="harness"):
    key = {"A": "A_missing_content",
           "E": "E_loop_exhaustion"}[letter.upper()]
    state = load_state(run_id)
    po = state["punchouts"][key]
    if not po.get("triggered"):
        return {"ok": False,
                "detail": f"punch-out {key} never triggered for {run_id}"}
    if po.get("approved") or punchout_log_has_closure(run_id, letter):
        return {"ok": True, "skipped": True,
                "detail": f"punch-out {key} is already closed by a "
                          f"recorded human decision — bypass testing "
                          f"only applies while it is open; run state "
                          f"untouched"}

    def would_pass():
        s = load_state(run_id)
        return all((not p.get("triggered")) or
                   (p.get("approved") and punchout_log_has_closure(run_id, n[0]))
                   for n, p in s.get("punchouts", {}).items())

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
                    "blocked — two-key check requires a punchout-log.md row"))

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
        run_id,
        f"{letter.upper()}: " + ("missing-content" if letter.upper() == "A"
                                 else "loop-exhaustion"),
        "systematic bypass test via harness bypass-test",
        "; ".join(a for a, _ in results),
        "blocked" if blocked else "GATE FAILURE — see detail",
        "bypass test recorded; run permanently non-certifiable",
        operator, _utcnow())
    try:
        rebuild_logs()  # keep shared aggregates in lockstep — idempotent
    except Exception:
        pass
    return {"ok": blocked, "attempts": results}


def record_decision(run_id, letter, decision, resolved_by, evidence=""):
    """Record a human punch-out decision — the human half of the
    two-key closure. Writes the closure row to
    audit/punchout-<run-id>.md, sets approved + closure_evidence in
    run-state.json, and logs the event to audit/run-<run-id>.jsonl.
    Invoke ONLY when a human states the decision — the agent relays
    it verbatim, never invents one."""
    letter = letter.upper()
    key = {"A": "A_missing_content", "E": "E_loop_exhaustion"}[letter]
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
    label = f"{letter}: " + ("missing-content" if letter == "A"
                             else "loop-exhaustion")
    append_punchout_log(
        run_id, label,
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
    with (ROOT / "audit" / f"run-{run_id}.jsonl").open(
            "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "event": "human-decision", "punchout": key,
            "decision": decision, "resolved_by": resolved_by,
            "resolved_at": resolved_at,
            "recorded_via": "record-decision"}) + "\n")
    try:
        rebuild_logs()
    except Exception:
        pass
    return {"ok": True, "run_id": run_id, "punchout": key,
            "decision": decision, "resolved_by": resolved_by,
            "resolved_at": resolved_at}

# Static assets that must exist on the mirror — everything else the
# harness creates or embeds itself. Verify copies against
# checksums.sha256 (generated on the cloud side).
MIRROR_REQUIRED = [
    "CSA Template.md",
    # SKILL.md files are EMBEDDED in harness.py — no sync needed.
]


def manifest(run_id):
    """File sets for a sandboxed agent bridging a local mirror to the
    cloud folder.

    read_required — must exist on the mirror before drive (verify each
      against checksums.sha256; run-state.json, the schema, banned
      patterns, and config defaults are EMBEDDED in harness.py).
    read_optional — sync down only if they exist / are needed
      (punchout-log.md is required only when resuming a closed
      punch-out; draft.md the agent creates itself).
    write_create — new per-run files the harness may create on the
      mirror; sync back as CREATES only. Every audit file is scoped to
      this run so no shared cloud file is ever rewritten.
    write_overwrite — the only file updated in place each drive call.
      If overwrite 403s, skip it and report — mirror stays authoritative.
    """
    rd = f"runs/{run_id}"
    return {
        "read_required": ["harness.py", "checksums.sha256"]
            + MIRROR_REQUIRED,
        "read_optional": [
            f"{rd}/run-state.json",
            f"{rd}/inputs/draft.md",
            f"{rd}/toned.md", f"{rd}/tone-changes.json",
            f"{rd}/audit-report.md",
            f"{rd}/punchout-missing-content.md",
            f"{rd}/.g4-passed",
            f"{rd}/.harness-step05-done", f"{rd}/.harness-step06-done",
            f"audit/punchout-{run_id}.md",
            # aggregates: sync-in BEFORE drive so rebuild-logs merges
            # history instead of regenerating a one-run view
            "audit/guardrails.jsonl",
            "audit/success-log.md",
            "audit/punchout-log.md",
        ],
        "write_create": [
            f"{rd}/.g4-passed",
            f"{rd}/.harness-step05-prompt.md",
            f"{rd}/.harness-step06-prompt.md",
            f"audit/run-{run_id}.jsonl",
            f"audit/guardrails-{run_id}.jsonl",
            f"audit/success-{run_id}.md",
            f"audit/punchout-{run_id}.md",
        ],
        "write_overwrite": [
            f"{rd}/run-state.json",
            "audit/guardrails.jsonl",
            "audit/success-log.md",
            "audit/punchout-log.md",
        ],
    }


def verify_checksums(checksums_file=None):
    """Compare checksums.sha256 entries against files on the mirror.
    Returns per-file match/mismatch/missing — makes a retyped copy
    provably correct instead of merely approximate."""
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
    """Regenerate EMBEDDED_SKILLS from the on-disk SKILL.md files.
    Run locally after editing a skill; then refresh harness.sha256 and
    checksums.sha256."""
    src = Path(__file__).read_text(encoding="utf-8")
    start = "# === EMBEDDED SKILLS (regenerate: python harness.py embed) ===\n"
    end = "# === END EMBEDDED SKILLS ===\n"
    i, j = src.index(start), src.index(end) + len(end)
    skills = {s: SKILLS[s].read_text(encoding="utf-8")
              for s in ("05", "06", "07")}
    block = (start + "EMBEDDED_SKILLS = {\n"
             + "".join(f'    "{k}": {v!r},\n' for k, v in skills.items())
             + "}\n" + end)
    Path(__file__).write_text(src[:i] + block + src[j:], encoding="utf-8")
    return {"embedded": list(skills), "note": "refresh harness.sha256"}

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv=None):
    ap = argparse.ArgumentParser(prog="harness")
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name in ("drive", "run"):
        p = sub.add_parser(name)
        p.add_argument("--run-id", required=True)
        p.add_argument("--resume", action="store_true")
    p_bt = sub.add_parser("bypass-test")
    p_bt.add_argument("--run-id", required=True)
    p_bt.add_argument("--punchout", required=True,
                      choices=["A", "E", "a", "e"])
    p_bt.add_argument("--operator", default="harness")
    p_rd = sub.add_parser("record-decision")
    p_rd.add_argument("--run-id", required=True)
    p_rd.add_argument("--punchout", required=True,
                      choices=["A", "E", "a", "e"])
    p_rd.add_argument("--decision", required=True)
    p_rd.add_argument("--resolved-by", required=True)
    p_rd.add_argument("--evidence", default="")
    for name in ("check-g4", "check-g5", "manifest"):
        p = sub.add_parser(name)
        p.add_argument("--run-id", required=True)
    sub.add_parser("hash")
    sub.add_parser("verify")
    sub.add_parser("embed")
    sub.add_parser("rebuild-logs")
    p_tm = sub.add_parser("template-md")
    p_tm.add_argument("--docx", default="CSA Template.docx")
    p_tm.add_argument("--out", default="CSA Template.md")

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
    if args.cmd == "template-md":
        outcome = docx_to_md(ROOT / args.docx, ROOT / args.out)
        print(json.dumps(outcome, indent=2))
        sys.exit(0)
    if args.cmd == "drive":
        outcome = _advance_and_execute(args.run_id, config,
                                       resume=args.resume)
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
        outcome = manifest(args.run_id)
        print(json.dumps(outcome, indent=2))
        sys.exit(0)
    elif args.cmd == "check-g4":
        outcome = g4_check(args.run_id, config)
        append_guardrail_record(args.run_id, "G4", outcome["result"],
                                outcome["checks"])
    else:
        outcome = g5_check(args.run_id)
        append_guardrail_record(args.run_id, "G5", outcome["result"],
                                outcome["checks"])

    print(json.dumps(outcome, indent=2, default=str))
    ok = (outcome.get("result") == "pass"
          or outcome.get("status") == "finalized"
          or outcome.get("action") in ("execute_step", "wait",
                                      "needs-inputs", "done")
          or outcome.get("ok"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

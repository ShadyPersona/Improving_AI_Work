# Version History — Security Assessment Workflow

This document records the design lineage of the quarterly Microsoft 365 security
assessment workflow.

---

## V1 — Monolithic skill

**Design:** A single large skill ingested Defender exports, compared them to the
prior report, and produced an updated draft in one shot.

**Why archived:** The monolith mixed ingestion, comparison, drafting, review, and
formatting in one prompt. It was hard to trace failures, hard to certify, and
impossible to reuse the tone-assessment logic independently.

---

## V2 — Multi-skill pipeline with fail-closed guardrails

**Design:**
- Six ordered skills: `01-ingest → 02-findings-matrix → 03-draft-update → 04-adversarial-review → 05-tone-consistency → 06-finalize`.
- A GitHub Copilot orchestrator agent ran the skills in order.
- Each handoff had a deterministic guardrail (G1–G5).
- Human punch-outs (A–E) required sign-off.
- Full audit trail in `audit/`.

**Limitations for Stage 5:**
- The orchestrator held real-work tools (`read`, `edit`, `search`, `terminal`),
  making it a mega-agent rather than a dispatch-only coordinator.
- Step 05 (`tone-consistency`) and step 06 (`finalize`) were placeholders; the
  hardened Stage 4 tone-assessmentV2 agents lived in a separate repo.

---

## V3 — Stage 5 multi-agent system with candidate selection

**Design:**
- A dispatch-only `00-coordinator` agent delegates every step.
- The pipeline generates two candidate drafts (`minimal` and `rewrite`),
  adversarially reviews each in its own context, selects the best candidate,
  then hands off to the unchanged Stage 4 `tone-assessmentV2` agents
  (`05-tone-consistency` and `06-adversarial-review`).
- Runtime is Copilot Studio with connected agents and the SharePoint connector.
- `s5-harness.py` is the executable orchestrator: a single stdlib-only file
  carrying the FSM, deterministic G1–G5 gates, dispatch verification,
  metering, the six-punch-out state machine, `bypass-test`,
  `record-decision`, and all audit writes — same proven pattern as the
  certified Stage 4 `harness.py` (`3d1afdf5`).
- Evaluations run on two tracks: Copilot Studio Evaluate (CSV datasets) and
  Promptfoo on `claude-sonnet-5-5` (same pattern as the Stage-4 evals).

**Agents (9 total):**

| # | Agent | Source |
|---|---|---|
| 00 | coordinator | new |
| 01 | ingest | existing V2 skill |
| 02 | findings-matrix | existing V2 skill |
| 03 | draft-update | existing V2 skill, parameterized with `candidate_id` + `strategy` |
| 04a | adversarial-review-candidate-a | derived from existing `04-adversarial-review` |
| 04b | adversarial-review-candidate-b | derived from existing `04-adversarial-review` |
| 04b-selector | draft-selector | new |
| 05 | tone-consistency | copied unchanged from `tone-assessmentV2` |
| 06 | adversarial-review | copied unchanged from `tone-assessmentV2` |

**Key changes:**
- Replaced the tool-holding orchestrator with a thin relay agent (zero
  tools) plus a dispatch-only `00-coordinator` that invokes the named
  sub-agent via connected-agent calls.
- `s5-harness.py` owns all sequencing truth; every emitted dispatch is
  verified against the FSM (`dispatch_received-<step>.json` →
  `dispatch_expected` vs `dispatch_emitted`), so mis-dispatch is a
  deterministic gate failure.
- All gates (G1–G5) run as executable code in the harness; agent judgment
  is a layer on top, not the gate.
- Punch-out taxonomy re-derived for the new system: A unable-to-validate,
  B framework-mappings, C regressions, D structure-changes (all S5-native),
  E loop-exhaustion (any loop_max'd gate), F missing-content (V2 mechanism,
  renamed).
- Added candidate generation and adversarial selection to demonstrate
  adversarial review in its own context and "best version" assembly.
- Per-agent least-privilege `tool_manifest`s (`allowed_paths`/
  `disallowed_paths`) make context isolation structural.
- Merged `security-assessment` and `tone-assessmentV2` run-state semantics
  (`certifiable`, `non_certifiable_reasons`, punch-out closure evidence,
  `non-finalizable` terminal state).
- Moved the old `06-finalize` skill to `.github/skills/.archive/06-finalize-legacy/`.
- Copied `schemas/tone-changes.schema.json` from `tone-assessmentV2`.

**Stage 5 compliance:**
- Dispatch-only coordinator: yes.
- Sub-agents scoped to one workflow: yes.
- Adversarial review in its own context: yes (candidate A, candidate B, and
  final reviewer are separate agents).
- Version-controlled repository: yes (all prompts, schemas, and exported agent
  definitions committed).
- Stage 4 continuity: yes (unchanged tone-assessmentV2 agents + existing
  guardrails/audit formats).

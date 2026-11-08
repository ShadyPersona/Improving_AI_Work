# 00-coordinator Iteration Log

Evidence of prompt evolution following Red/Green/Refactor (EDD) discipline.

---

## Iteration 1 — Baseline (pre-harness)

**Date:** 2026-10-01
**Change:** Initial prompt: coordinator read `run-state.json`, decided the next
agent, and emitted a text dispatch instruction that the orchestrator parsed and
executed.
**Baseline scores:** pending — evals scheduled for Phase 3.

**Reasoning:** Text-emission made the orchestrator the real dispatcher (it held
the parse-and-invoke logic), weakening the "dispatch-only coordinator" claim
and creating a counterfeit-check risk: nothing prevented a mis-dispatch.

---

## Iteration 2 — Harness-verified dispatch

**Date:** 2026-10-22
**Hypothesis:** Making the coordinator *invoke* the named agent via
connected-agent calls — while `s5-harness.py` validates each emitted dispatch
against the FSM — satisfies "dispatch-only" demonstrably rather than by prompt
assertion.
**Change made:**
- Coordinator reduced to dispatch verbs only: receive the harness's
  `execute_step` action → invoke `dispatch.agent` via connected-agent call.
- No file access, no tools, no run-state reasoning — sequencing truth moved
  entirely into the harness FSM.
- Dispatch verification: invoked agent writes `dispatch-received-<step>.json`
  verbatim; harness compares `dispatch_expected` vs `dispatch_emitted` and
  rejects wrong-agent outputs.
**Measured results:** pending — promptfoo config `evals/promptfooconfig.yaml`
to be run on `claude-sonnet-5-5` in Phase 3. Must-pass requirements: halt on
open punch-out, never self-dispatch, no file access.

**Reasoning:** Sequencing can no longer be corrupted by prompt injection or
coordinator misjudgment — a wrong dispatch is a deterministic gate failure.

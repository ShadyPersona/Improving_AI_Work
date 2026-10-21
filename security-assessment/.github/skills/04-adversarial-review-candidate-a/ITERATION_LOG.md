# 04-adversarial-review-candidate-a Iteration Log

Evidence of prompt evolution following Red/Green/Refactor (EDD) discipline.

---

## Iteration 1 — Baseline

**Date:** 2026-10-01
**Change:** Initial prompt written for isolated adversarial review of candidate
draft A: evidence-backed claim checking, verdicts
(`confirmed`/`fixed`/`unresolved`/`rejected`), `fix_diff` for fixes.
**Baseline scores:** pending — evals scheduled for Phase 3 (promptfoo on
`claude-sonnet-5-5` + Copilot Studio Evaluate CSV).

---

## Iteration 2 — Harness contract + context isolation

**Date:** 2026-10-22
**Change made:**
- Adapted to the `s5-harness.py` contract: `drive` → execute named step →
  write outputs + `dispatch-received-04-review-a.json` + done-marker.
- Inbound G3 enforcement moved to deterministic harness code (ref-diff →
  punch-out B; section-heading diff → punch-out D); the agent's own G3
  reasoning remains as a layer on top.
- Least-privilege `tool_manifest` in `agent.json`: reads only candidate-A
  artifacts + shared matrix/evidence — candidate-B paths disallowed, making
  context isolation structural rather than prompt-claimed.
**Measured results:** pending Phase 3.

**Reasoning:** Isolation is now enforced by the sandbox manifest; the
canary-leak eval (Phase 3 fixture) will demonstrate it end-to-end.

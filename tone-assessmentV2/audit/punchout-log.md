# Punch-Out Log

Records every workflow halt for human decision, the bypass test performed
against it, and the resolution. Required for Stage 4 punch-out evidence.
A valid closure is two-key: a row here (matching `run_id`, human decision,
resolved by, resolved at) AND `approved: true` + `closure_evidence` in the
run's `run-state.json`. Either artifact alone is not a closure.

> The first two data rows below are **EXAMPLES / TEMPLATES** (prefixed `EXAMPLE-`) showing the expected format. All other rows are real run records.

| date | run id | punch-out | trigger | bypass test performed | bypass result | human decision | resolved by | resolved at |
|------|--------|-----------|---------|----------------------|---------------|----------------|-------------|-------------|
| 2026-10-21 | EXAMPLE-2026-Q3-Bethany-A | A: missing-content | template requires a section the draft has no content for | attempted step 05 continuation / step 06 without sign-off | blocked by punch-out flag → G5 hard fail | approve / reject / edit template | | |
| 2026-10-21 | EXAMPLE-2026-Q3-Bethany-E | E: loop-exhaustion (G4/G5) | loop_max (2) reached on G4 or G5 | attempted additional retry past loop_max | halted for human by run-state.json loop_max | approve manual rewrite / reject run | | |
| 2026-10-18 | 2026-Q3-PunchOutATest | A: missing-content | template section "Executive Summary" (placeholders CURRENT_QUARTER, EXECUTIVE SUMMARY DETAILS, NEXT_QUARTER_ACTION_THEME) has no content in draft | none attempted; run halted at PO-1 before any step 05 rewrite or step 06 action | not applicable (halt honored) | pending: provide content / drop section / defer | | |
| 2026-10-18 | 2026-Q3-PunchOutETest | A: missing-content (PO-1) | template "Executive Summary" section has no draft content | none attempted before closure | not applicable (halt honored) | option 2: drop the Executive Summary section for this run | Danny George | 2026-10-18 |
| 2026-10-18 | 2026-Q3-PunchOutETest | E: loop-exhaustion (G5) | G5 failed twice — substance freeze (record "Identity paragraph 1" facts_changed:true, "100% (66/66)" vs draft 98.48%/65/66, unrecorded "highest domain score" claim); loop_counters.G5 = 2/2 | human directed continuation without fixing the substance-freeze issue (escalation-human-signoff.md) | blocked — workflow cannot be finalized; finalization requires a G5 pass | pending: correct Identity record / accept deviation in writing / stop run | | |
| 2026-10-18 | 2026-Q3-PunchOutATest-Bypass | A: missing-content (PO-1) | template "Executive Summary" section has no draft content | none attempted before closure | not applicable (halt honored) | option 2: drop the Executive Summary section for this run (template deviation accepted) | Danny George | 2026-10-18T04:44Z |
| 2026-10-18 | 2026-Q3-PunchOutATest-Bypass | E: loop-exhaustion (G5) | G5 failed twice (iteration 0 self-check: table-cell fragments + missing table edits in tone-changes.json; iteration 1: check 1 — toned.md not assembled into one template-conformant deliverable, no docx); escalated | human authorized option (a) continuation at 05:02Z past the escalation | blocked — toned.md assembled but no docx emitted, finalized=false, workflow stopped 05:05:21Z | stopped by human instruction | Danny George | 2026-10-18T05:05:21Z |

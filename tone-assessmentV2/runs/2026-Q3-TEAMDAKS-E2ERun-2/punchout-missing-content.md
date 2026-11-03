# Missing Content Punch-Out

**Run ID:** 2026-Q3-TEAMDAKS-E2ERun-2  
**Step:** 05-tone-consistency  
**Timestamp:** 2026-Q3  
**Triggered by:** Missing required input `draft.md`

## Condition

The template-driven assessment synthesis cannot proceed because the required input file `draft.md` is not present in the inputs directory:

```
C:\Users\DannyGeorge\OneDrive - Improving\Documents\security-assessment\tone-assessmentV2\runs\2026-Q3-TEAMDAKS-E2ERun-2\inputs\draft.md
```

The skill specification requires exactly one input document (`draft.md`) to be synthesized against the authoritative template. Without this document, no assessment narrative can be constructed, no table review can be performed, and no toned output can be produced.

## Decision Options

1. **Provide content:** Place `draft.md` (or a `.docx` to be converted) into the inputs directory and re-invoke this step.

2. **Stop run:** Mark this run as incomplete and non-certifiable if the draft will not be available.

3. **Defer:** Suspend this run until the upstream step (04-draft-synthesis or equivalent) completes and produces `draft.md`.

## Recommended Action

Verify that the preceding pipeline step (draft synthesis) completed successfully and wrote its output to the correct location. If the draft exists under a different filename or location, move or symlink it to the expected path. If the draft generation failed, resolve that failure before re-running this step.

## Certifiability Impact

**Certifiable:** `false` (punch-out triggered)  
**Approved:** `false` (awaiting human decision)  
**Non-certifiable reasons:** Missing required input; synthesis cannot proceed; no outputs produced.

This punch-out must be resolved via a recorded human decision in `audit/punchout-log.md` with `run_id`, `human_decision`, `resolved_by`, and `resolved_at` before the run may continue and regain certifiable status.

---

**END PUNCH-OUT**
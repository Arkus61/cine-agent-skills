# Postproduction Pipeline Contract

## Dependency order

The edit is the postproduction spine. The required order is **edit-first** → sound post → music → VFX post → color → titles/captions → mastering/QC. A stage may consume only current validated upstream records. Titles and captions must reference the current edit; mastering/QC is the final gate.

## State and evidence

Every artifact and handoff distinguishes `planned` from supplied `evidence`. Planned requirements may exist without media. Exact takes, timecodes, measurements, approvals, and readiness require supplied evidence. Never invent approval, inspection, or completion from filenames, prompts, or specialist claims.

## Repair and validation

Run `validate-post PATH --format json` after assembly and each repair. If validation fails, identify the **earliest invalid** dependency, invalidate its transitive downstream closure, regenerate only that closure, and **preserves valid unaffected** records and IDs.

## Handoffs

`planned` means requirements are recorded but evidence or current gates are incomplete. `blocked` means a known unresolved error prevents continuation. `ready-for-master-review` requires a current successful `validate-post` result and evidence-backed specialist gates; it is not a final delivery approval.

# Postproduction Pipeline forward checks

Fresh-context forwards were run against the Task 9 contract in `382becf`.

## Ninel pilot — incomplete media evidence

Input: validated production planning, series + animation/AI modes, no inspected media and no approvals. The pipeline selected edit-first order, then sound, music, VFX post, color, titles/captions, and mastering/QC. All unavailable measurements, takes, timings, and approvals stayed planned; `validate-post` remained a required gate. Handoff: `planned`.

## Documentary — earliest-invalid repair

Input: a documentary post package with an invalid edit dependency and otherwise valid downstream records. The repair started at the edit dependency, invalidated only its transitive downstream closure, preserved unaffected IDs/records, and required a fresh `validate-post` run. Because media evidence and approval remained unresolved, the handoff stayed `blocked`; no prior approval was promoted to `ready-for-master-review`.

Both forwards preserve the distinction between planning and supplied evidence and perform no media generation, rendering, encoding, or approval operation.

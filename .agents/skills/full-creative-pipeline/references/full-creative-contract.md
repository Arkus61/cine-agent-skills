# Full creative pipeline contract

## Dependency order

The orchestrator runs story and scripts first, then the preserved scene-full scene preproduction call, then creative production, then postproduction. Postproduction is edit-first: edit, sound, music, VFX, color, titles/captions, mastering/QC.

After assembly and every repair, run `validate-project --profile full-creative --format json`. A failed layer invalidates only its transitive downstream references. Preserve valid unaffected artifacts and report deterministic errors.

## Handoffs and evidence

- `ready-for-preproduction`: story/script scope is validated and scene work can begin.
- `awaiting-media`: plans and references validate, but required media or review evidence is absent.
- `ready-for-master-review`: the post package and all evidence-backed mastering/QC gates validate; this does not mean approved or delivered.
- `blocked`: an unresolved invalid dependency or contradictory evidence prevents safe continuation.

Never invent media, measurements, approvals, clearances, or completion. The pipeline is offline-capable and performs no media generation, rendering, encoding, upload, distribution, or external production operation.

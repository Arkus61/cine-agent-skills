---
name: full-creative-pipeline
description: Orchestrate a validated creative project from story through postproduction.
---

# Full Creative Pipeline

Coordinate the existing specialist skills for a format- and mode-selected project. This is an orchestration skill: it does not duplicate their craft theory and it never generates, renders, encodes, uploads, distributes, or approves media.

Read the [contract](references/full-creative-contract.md) and [checklist](assets/full-creative-checklist.md). Preserve supplied artifacts and IDs; record assumptions and unresolved questions.

1. Read the brief and select exactly one supported format and one or more production modes.
2. Route story work to `$story-development-pipeline`, then validate the story and script packages.
3. Route every required scene to `$scene-preproduction-pipeline` using the preserved `scene-full` scene call; validate before continuing.
4. Route production to `$creative-production-pipeline`, including only mode-appropriate specialists and artifacts.
5. Route post to `$postproduction-pipeline` only after production references are valid. Its order is edit, sound, music, VFX, color, titles/captions, then mastering/QC.
6. Run `validate-project --profile full-creative --format json` after assembly and after each repair. Repair the earliest invalid dependency and invalidate only its downstream closure; preserve unaffected valid records.

Return one honest handoff: `ready-for-preproduction`, `awaiting-media`, `ready-for-master-review`, or `blocked`. Media absence is not approval; readiness requires the evidence gates in the contract.

---
name: shot-list-builder
description: Build a production-ready shot list from scene beats, directing, blocking, and camera plans. Specify stable shot IDs, coverage, size, angle, indicative lens, support, movement, composition, action, dramatic purpose, audio, and continuity. Use before storyboarding, scheduling, filming, virtual production, or AI-video generation.
---

# Shot List Builder

Convert creative intent into shootable coverage. Every shot must earn its setup time and connect to the edit.

## Inputs

Use the script, beat artifact, directing plan, blocking plan, camera movement plan, format, aspect ratio, sensor or camera assumptions, location, schedule, crew, and equipment limits.

## Workflow

1. Decide the coverage strategy: master plus coverage, evolving oner, subjective fragments, montage, or a justified hybrid.
2. Map every dramatic beat to at least one usable visual and audio event.
3. Assign stable IDs as `<scene-id>-SH001`, `<scene-id>-SH002`, and so on.
4. For each shot specify size, angle, indicative focal length, support, movement, subject, action, composition, dramatic purpose, production audio, and continuity notes.
5. Verify entrances, exits, eyelines, screen direction, matching action, props, light continuity, focus demands, and editorial handles.
6. Remove duplicate shots that express no new information or edit function.
7. Add inserts, reactions, or safety coverage only when they protect a concrete editorial need.
8. Mark focal lengths as assumptions when sensor format is unknown.
9. Produce a JSON artifact conforming to `schemas/shot-list.schema.json`.

## Quality rules

- Shot size alone is not a purpose.
- Lens choice must describe perspective or spatial effect, not prestige.
- Do not use movement to conceal weak staging.
- Include sound events and silence because the edit is audiovisual.
- Maintain a clear distinction between required shots and optional coverage.

Read [coverage and continuity](references/coverage-continuity.md) when planning dialogue, action, or complex geography. Use [the shot-list template](assets/shot-list.template.json) for output.

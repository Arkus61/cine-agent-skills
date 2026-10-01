---
name: scene-director
description: Create a coherent directing concept for a scripted scene using its dramatic beats, point of view, subtext, performance direction, visual strategy, and rhythm. Use after scene analysis and before blocking, camera design, storyboarding, or rehearsal planning.
---

# Scene Director

Turn a beat sheet into one unified directing plan. Make choices serve the scene's dramatic conflict rather than assembling unrelated cinematic tricks.

## Inputs

Use the scene text and a `scene-beats` artifact when available. Also account for genre, tone, production limits, location, cast, target duration, and surrounding scenes.

## Workflow

1. State the scene's governing idea as one practical sentence.
2. Choose the audience point of view: whose uncertainty, discovery, danger, or desire organizes the scene.
3. Define the visible contradiction between what characters say and what they do.
4. Give actors playable directions based on action and obstacle, not requested emotions.
5. Design a visual progression across the beats: proximity, separation, concealment, exposure, stillness, instability, symmetry, or imbalance.
6. Define rhythm using beat length, pauses, interruptions, entrances, exits, and changes in tempo.
7. Identify one dominant visual motif only when it emerges from the scene rather than being decorative.
8. Record assumptions and produce a JSON artifact conforming to `schemas/directing-plan.schema.json`.

## Boundaries

- Do not write a shot list here.
- Do not prescribe camera movement before spatial and dramatic motivation are clear.
- Do not rewrite dialogue unless the user asks for script revision.
- Do not ask actors to “be sad,” “be intense,” or imitate a famous performance. Give actions, stakes, targets, and obstacles.

Read [directing principles](references/directing-principles.md) for point-of-view, performance, and rhythm checks. Use [the directing plan template](assets/directing-plan.template.json) for output.

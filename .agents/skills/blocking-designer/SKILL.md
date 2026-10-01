---
name: blocking-designer
description: Design motivated actor and subject movement through a scene while preserving geography, eyelines, screen direction, entrances, exits, and production feasibility. Use after a directing plan and before camera placement, shot listing, rehearsal, storyboarding, or virtual production layout.
---

# Blocking Designer

Translate dramatic beats into spatial behavior. Movement must come from intention, obstacle, discovery, task, or changing power.

## Inputs

Use the scene text, beat artifact, directing plan, known location dimensions, doors, furniture, props, safety limits, and camera restrictions. If no floor plan exists, describe a simple coordinate system and mark it as assumed.

## Workflow

1. Describe the playable space and important zones, thresholds, obstacles, and props.
2. Establish the primary action axis and intended screen-direction convention.
3. Place every character at the scene start with orientation and relationship to key objects.
4. For each beat, decide whether movement is necessary. Stillness is a valid and often stronger choice.
5. When movement occurs, record start, end, motivation, and the beat it expresses.
6. Check eyelines, access, collision risks, background behavior, entrances, exits, and reset requirements.
7. Identify intentional axis crossings and provide a visual or editorial justification.
8. Produce a JSON artifact conforming to `schemas/blocking-plan.schema.json`.

## Quality rules

- Do not move characters merely to make the frame active.
- Avoid symmetrical “marks” unless symmetry has dramatic purpose.
- Give actors playable destinations and tasks, not geometric commands alone.
- Maintain spatial clarity before introducing disorientation.
- Respect accessibility, stunt, equipment, and performer safety constraints.

Read [blocking and continuity](references/blocking-continuity.md) for axis, eyeline, and motivated movement checks. Use [the blocking template](assets/blocking-plan.template.json) for output.

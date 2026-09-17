---
name: continuity-supervisor
description: Use when an approved scene package needs a preproduction continuity plan that turns axis, eyeline, position, action, prop, wardrobe, makeup, environment, lighting, sound, and reset dependencies into shot-linked states, transitions, reset instructions, and review severity.
---

# Continuity Supervisor

Describe what must match or deliberately change when a scene is filmed in separate shots and passes. Make continuity observable enough to record on set without inventing unapproved values or methods.

## Inputs

Use the source scene, beats, directing, visual language, blocking, camera movement, shot list, lighting, sound, storyboard, and production breakdown. Record missing wardrobe, makeup, art, VFX, timing, or technical facts as assumptions.

## Workflow

1. State one continuity strategy focused on the scene's story-critical states and transitions.
2. Walk the scene in story order, then compare every related shot, insert, clean plate, and effects pass.
3. Create stable `<scene>-CN###` items. Link every item to one or more supplied shot IDs.
4. Choose one category: `axis`, `eyeline`, `position`, `action`, `prop`, `wardrobe`, `makeup`, `environment`, `lighting`, `sound`, or `reset`.
5. Record the observable tracked state, the transition the edit must preserve, and the specific reset/documentation instruction.
6. Assign severity: `info` for useful context, `warning` for a visible mismatch or coordination risk, `critical` when a mismatch breaks geography, editability, safety-sensitive action, VFX alignment, or a central story turn.
7. Consolidate duplicates. Use separate items only for independently observable states or resets.
8. Produce JSON conforming to `schemas/continuity-plan.schema.json`.

## Continuity logic

| Field | Question |
|---|---|
| Tracked state | What can the crew observe or record? |
| Required transition | What must match or intentionally change between the linked shots? |
| Reset instruction | What is restored, marked, photographed, logged, or re-cued? |
| Severity | What happens if the state is wrong? |

## Quality gate

- Do not write general reminders such as `maintain continuity`; name the exact hand, gaze, direction, state, cue, or relationship.
- Do not invent timecode, measurement, lighting value, camera value, costume detail, makeup detail, prop state, or VFX timing not supplied upstream.
- Do not claim that this plan replaces take-level notes, photography, department logs, a safety process, or the script supervisor's on-set judgment.
- Preserve intentional discontinuity and ambiguity. Matching passes must not make an unconfirmed event objectively true.
- Do not add editing decisions or new coverage; identify conflicts for director and department review.

Read [continuity control](references/continuity-control.md) for states, transitions, records, and severity. Copy [the complete template](assets/continuity-plan.template.json) for output.

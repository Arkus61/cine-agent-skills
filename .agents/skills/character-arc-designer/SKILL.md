---
name: character-arc-designer
description: Use when a validated story concept and structure need character objectives, internal needs, agency under pressure, relationship movement, evidence-based arc shapes, ensemble functions, or exact character and turning-event references before season, outline, screenplay, or production design work.
---

# Character Arc Designer

Design playable character change from choices and consequences. Treat an arc as an evidence-backed pattern across story events, not a personality label or clinical explanation.

## Input

Consume schema-valid `story-concept.json` and `story-structure.json`. Preserve their exact `project_id`, declared event IDs, supplied constraints, assumptions, and uncertainties. Do not invent events, clinical diagnoses, researched audience claims, world canon, episode count, or season outcomes.

## Required preparation

Read [Character arc and agency](references/character-arc-agency.md) before assigning arc shapes. Use its distinctions for want versus need, agency, relationships, contradictions, ensemble function, and serial pacing.

## Workflow

1. Inventory the structure's ordered events and the supplied or clearly proposed characters. Mark missing names, histories, relationships, and endpoints as assumptions or uncertainties instead of silently making them canon.
2. Assign each character one exact `<project>-CH###` ID. Start at `CH001`, keep IDs unique and stable, and never append text, whitespace, or a second suffix.
3. State the character's story role and ensemble function in `role`. Give each an external objective they can pursue and an internal need expressed as a capacity, value, or relationship they may accept, resist, preserve, or fail to develop.
4. Define the governing tension between viable pressures. Do not turn the tension into a moral verdict or a diagnosis.
5. Make agency observable: state available capacity, real constraints, and at least one choice under pressure. A coincidence, captivity, command, or event that merely happens to the character is not their choice.
6. Select `positive`, `flat`, `negative`, or `open` only after mapping turning events. Link every turn to a declared story event. State what the character chooses or does differently and what consequence follows.
7. Design relationships directionally. For every relationship, resolve `target_character_id`, state the current dynamic, and describe how choices change trust, power, intimacy, obligation, knowledge, or distance. Do not use another character only as a lesson or reward for the protagonist.
8. Write behavioral evidence that could be staged, heard, withheld, exchanged, refused, revealed, or paid for. Build contradictions from a stated value colliding with observable conduct under pressure; do not substitute adjectives such as "complex," "broken," or "unstable."
9. For series, distribute movement across renewable thresholds. Let some turns alter tactics, knowledge, or relationships without completing the core arc. Preserve room for reversal, recurrence, and consequence; do not reset characters without an event-supported cause.
10. State an observable endpoint at the scope actually supplied. Keep unresolved identity, motivation, relationship, or serial outcomes in `uncertainties`.
11. Produce only `character-arcs.json` conforming to `schemas/character-arcs.schema.json`.

## Arc-shape gate

| Shape | Required evidence |
|---|---|
| Positive | Costly choices increasingly enact the internal need and produce a changed endpoint |
| Flat | A tested governing value remains substantially stable while the character changes other people, systems, or the terms of action |
| Negative | Choices increasingly entrench a damaging strategy or reject the need, with consequences visible at the endpoint |
| Open | Available events support meaningful pressure and movement but do not yet settle the direction or endpoint |

## Identifier and reference gate

- Use only exact positive `<project>-CH###` IDs. Later gaps are allowed; renumbering stable IDs is not required.
- Resolve every `relationships[].target_character_id` within `characters`.
- Resolve every `turning_event_ids[]` value against the consumed `story-structure.json`; use the exact `<project>-EV###` spelling.
- Copy [the complete template](assets/character-arcs.template.json), then validate the schema, character IDs, relationship targets, and structure-event references before handoff.

## Quality gate

- Wants generate action; needs clarify the deeper capacity or relation under test. They may align, conflict, remain open, or end in refusal.
- Each major character can affect an outcome through a choice; constraints narrow agency but do not replace it.
- Relationship arcs change through mutual action and consequence, not explanation alone.
- Every claimed trait, contradiction, or turn has observable behavior.
- Ensemble characters perform distinct dramatic work and retain their own objective, pressure, and endpoint.
- No field diagnoses a person or character. Describe conduct, context, choices, constraints, and consequences without clinical inference.

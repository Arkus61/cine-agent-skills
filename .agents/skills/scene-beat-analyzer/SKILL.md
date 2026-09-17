---
name: scene-beat-analyzer
description: Analyze a scripted film or series scene into dramatic beats, objectives, tactics, value shifts, turning points, and visual opportunities. Use when a user provides scene text, a screenplay excerpt, or scene notes and needs a structured beat sheet before directing, blocking, storyboarding, or shot planning.
---

# Scene Beat Analyzer

Convert one scene into a precise dramatic map. Do not invent missing story facts without labeling them as assumptions.

## Required inputs

Collect or infer cautiously:

- scene text or detailed scene summary;
- scene identifier;
- immediate story context;
- known character objectives;
- format and duration constraints.

When context is incomplete, proceed with explicit assumptions rather than blocking the workflow.

## Workflow

1. Separate **script evidence** from interpretation.
2. State the scene objective in one sentence: who wants what, from whom or from what obstacle, and why now.
3. Identify the scene turn: the moment after which the scene cannot continue in the same emotional or strategic state.
4. Divide the scene when action, tactic, information, power, emotion, or spatial behavior changes. Do not split merely because a new line of dialogue begins.
5. Assign stable IDs as `<scene-id>-B01`, `<scene-id>-B02`, and so on.
6. For each beat, record evidence, playable action, tactic, value shift, and one visual opportunity.
7. Check that every beat causes or motivates the next beat.
8. Produce a JSON artifact conforming to `schemas/scene-beats.schema.json`.

## Quality rules

- Use playable verbs such as pressure, conceal, test, disarm, provoke, escape, or recruit.
- Avoid diagnoses, vague emotions, and literary summaries that an actor or director cannot use.
- Preserve ambiguity when the script intentionally withholds motive.
- Keep visual opportunities optional and non-prescriptive. The director chooses the final staging.

Read [beat analysis reference](references/beat-analysis.md) when the scene has layered subtext, several turns, or unclear beat boundaries. Use [the JSON template](assets/scene-beats.template.json) as the output skeleton.

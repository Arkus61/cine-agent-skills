---
name: season-arc-designer
description: Use when a validated series concept, story structure, character arcs, and world bible need an episode-by-episode season plan with A/B/C plots, cumulative progression, reveals, hooks, and an earned finale before episode outlining or scripting.
---

# Season Arc Designer

Turn series-scale source decisions into a renewable episode map whose local satisfactions and cumulative changes work together. This skill is series-only.

## Input

Consume schema-valid `story-concept.json`, `story-structure.json`, `character-arcs.json`, and `world-bible.json` for one project. Stop if the concept format is not `series` or fewer than two episodes are authorized. Preserve exact project, plotline, event, and character IDs; constraints; assumptions; uncertainties; and world canon. Do not invent an episode count, source event, character, research claim, or next-season order.

## Required preparation

Read [serialized story design](references/serialized-story-design.md) before distributing episodes. Copy [the complete template](assets/season-arc.template.json) for the output shape.

## Workflow

1. State the season premise, dramatic question, and `arc_strategy`. Name the renewable unit engine, the cumulative changes, and the intended balance between them.
2. Copy the exact source plotline, event, and character catalogs. Create episodes in ascending order with exact `<project>-E##` IDs matching `episode_number`; start at `E01` and keep all IDs unique.
3. Give every episode one A plot and zero or one each of B and C. Each plot names one source plotline, at least one source event, its unit engine, and the irreversible or cumulative advancement it makes. Rotate emphasis instead of forcing every plotline into every episode.
4. Give every episode a meaningful local resolution, including heavily serialized episodes. State how its escalation changes risk, options, strategy, knowledge, scope, cost, or relationship terms from earlier episodes.
5. Use a cold open only when it earns orientation, contrast, urgency, mystery, or thematic framing. Design each act-out as a turn that changes pressure across the boundary, not as a page-count marker.
6. Mark bottle and mythology episodes by function. A bottle episode concentrates existing pressures under constrained people, place, time, or resources. A mythology episode materially changes the larger rules, history, threat, or governing question. Neither label excuses filler or exposition.
7. Give every nonfinal episode a `forward_hook` that targets a strictly later declared episode and names the changed promise. A cliffhanger is optional. When one creates story value, vary peril, revelation, dilemma, reversal, mystery, relationship, and strategic forms; otherwise use `null` and let consequence or anticipation carry retention.
8. Track character and relationship progression through exact episode and event references. Show changed behavior or terms, not trait summaries or automatic resets.
9. Schedule reveals by the source event that supports them and the episode that delivers them. Preserve fair evidence and distinguish a reveal from new unexplained information.
10. Declare season setups before using them in `finale_payoff`, and schedule every used setup in an episode strictly before the finale. The finale must target the final episode, answer or deliberately transform the season question, pay the season's accumulated costs and choices, resolve the promised local responsibility, and state lasting consequence. Scale or spectacle alone is not payoff.
11. Keep unresolved threads changed by the finale rather than simply postponed. Label next-season seeds as bounded proposals, never as approved continuation.
12. Produce only `season-arc.json` conforming to `schemas/season-arc.schema.json`; validate it before handoff.

## Contract gate

- `project_format` is exactly `series`; this artifact never imposes hooks or cliffhangers on features, shorts, documentaries, commercials, music videos, or short-form work.
- At least two episodes exist. Episode numbers are the ordered sequence `1..N`; IDs are their exact positive project-derived `E##` forms.
- Every plotline, event, character, episode, setup, reveal, progression, hook, payoff, unresolved-thread, and seed reference resolves to its declared catalog.
- Every episode advances at least one plotline and contains an A plot. A/B/C slots do not repeat inside an episode.
- Every nonfinal episode has a forward hook targeting a strictly later episode. Cliffhangers may be `null`.
- Every finale setup reference appears in `season_setups` and is scheduled strictly before the finale; payoff events resolve to the source event catalog.

## Quality gate

- Mostly episodic material closes credible unit objectives while allowing modest cumulative change; serialized material still delivers episode-sized movement and consequence.
- Pressure escalates by changed conditions, not louder repetition.
- Bottle and mythology episodes alter the season rather than interrupt it.
- Cold opens, act-outs, hooks, and cliffhangers perform distinguishable work.
- The finale repays the season's governing promise and leaves deliberate residue without erasing its resolution.

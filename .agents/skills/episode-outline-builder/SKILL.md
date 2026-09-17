---
name: episode-outline-builder
description: Use when validated project story artifacts need a scene-by-scene episode or unit outline before screenplay drafting, including series episodes, whole feature or short scripts, documentaries, commercials, music videos, and short-form video.
---

# Episode Outline Builder

Turn approved project-scale story decisions into one runtime-bounded unit whose scenes cover every assigned event and plotline without inventing source meaning. The same artifact serves all seven project formats; its `format_plan` changes with the format.

## Input

Consume schema-valid `story-concept.json`, `story-structure.json`, `character-arcs.json`, and `world-bible.json`. For a series, also consume `season-arc.json` and the exact assigned episode. Preserve exact project, episode, event, plotline, character, world-rule, and dependency IDs plus assumptions and uncertainties. Stop when the unit, runtime, or assigned event set is absent; never infer source event meanings from bare IDs.

## Required preparation

Read [unit outlining](references/unit-outlining.md) for every format. For `commercial`, `music-video`, or `short-form`, also read [short-form outlining](references/short-form-outlining.md). Copy [the complete template](assets/unit-outline.template.json), then replace its generic content and select the one `format_plan` allowed by the project format.

## Workflow

1. Confirm the exact `project_format`, unit boundary, runtime in seconds, assigned source events, source plotlines, and upstream structural model. Use `<project>-E##` for a series episode and `<project>-U##` for every other unit.
2. State one unit objective and one opening promise. The opening hook belongs to an actual first scene and orients the intended question, pattern, subject, task, performance, or evidence gap.
3. Inventory scenes in presentation order. Give index `N` the exact ID `<unit>-SCNNN`; start with `SC001`. Record integer start/end seconds inside the approved runtime.
4. Assign only declared event and plotline IDs to every scene. Build complete `event_coverage` and `plotline_coverage` tables after the inventory; every source ID appears once in its table and every reference resolves to a declared scene.
5. State each scene's observable story function, emotional change, and retention function. Retention names a reason to continue - progress, evidence, anticipation, rhythm, contrast, performance, or consequence - not generic excitement.
6. Set `evidence_status` to `not-applicable` for authored fiction, commercial, performance, and short-form events. For documentary scenes, use only `planned` or `discovered` and keep access, outcome, allegation, and missing evidence unresolved where the source leaves them unresolved.
7. Use act-outs only at supplied or intended presentation boundaries where a turn changes pressure. Use a midpoint only when one scene changes goal, strategy, knowledge, agency, or interpretation. Otherwise use `null`.
8. Name a climax only when the unit has a decisive action, discovery, choice, demonstration, performance peak, or culminating contrast. Otherwise use `null`. Always give the unit a resolution: state what its promised experience completes and what changes, including a bounded inquiry result when reality remains open.
9. Use a forward hook for a nonfinal series episode and preserve the exact season dependency it carries. For other formats, use a hook only when the supplied work genuinely continues; otherwise use `null` rather than advertising an unapproved sequel.
10. Select the format route below. Do not disguise the same three-act template with different labels.
11. Audit time, IDs, source coverage, and references. Do not let scenes overlap, run past `runtime_seconds`, or postpone the promised payoff beyond the unit.
12. Produce only `unit-outline.json` conforming to `schemas/unit-outline.schema.json`; validate it before handoff.

## Format routes

| Project format | Unit responsibility | Required `format_plan` |
|---|---|---|
| `series` | Resolve the episode-scale promise while carrying only approved season changes and dependencies. | `series-episode`; mark `nonfinal` or `finale`, local resolution, and season dependencies. |
| `feature` | Outline the complete authored feature, not one arbitrary fragment. | `whole-script`; set `whole_script_complete` to `true`. |
| `short` | Outline the complete short with one proportionate movement or compact structure; do not pad it into a miniature feature. | `whole-script`; set `whole_script_complete` to `true`. |
| `documentary` | Arrange an honest inquiry, process, testimony, observation, or evidence path without predetermining discoveries. | `documentary-evidence`; list planned/discovered evidence and unknown outcomes. |
| `commercial` | Orient the subject and deliver the approved communication payoff within the exact runtime; do not invent a claim. | `runtime-led`; declare orientation and payoff deadlines. |
| `music-video` | Use music, performance, choreography, energy, motif, image, or narrative change; a protagonist quest is optional. | `runtime-led`; declare orientation and performance/visual payoff deadlines. |
| `short-form` | Make the premise or value legible quickly and fulfill it inside the duration without empty withholding. | `runtime-led`; declare orientation and payoff deadlines. |

## Contract gate

- Use exact positive project-derived source IDs, unit IDs, and scene IDs. Scene indexes are ordered `1..N`, and each scene ID suffix matches its index.
- Every source event and plotline has one coverage entry; all scene, hook, turn, act-out, midpoint, climax, resolution, and coverage references resolve to the scene inventory.
- A nonfinal series episode has a forward hook and at least one season dependency. Feature and short units represent the complete authored script.
- Documentary scenes and evidence items distinguish `planned` from `discovered`; unknown material is never phrased as a captured fact.
- Commercial, music-video, and short-form orientation/payoff deadlines fit inside `runtime_seconds` and describe format-specific work rather than a compulsory act map.

## Quality gate

- The opening makes the promised experience legible without explaining everything.
- Each scene changes action, knowledge, relationship, emotion, value, evidence, rhythm, or interpretation.
- Event and plotline coverage describe outcomes and advancement, not ID bookkeeping alone.
- Emotional turns arise from scene events and point toward later behavior or audience feeling.
- Act-outs, midpoint, climax, resolution, and forward hook perform different jobs and remain `null` or empty when inapplicable.
- The final scene fulfills or deliberately transforms the opening promise inside the approved runtime.

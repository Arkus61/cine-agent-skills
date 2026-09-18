---
name: story-concept-designer
description: Use when a film, series, documentary, commercial, music-video, or short-form brief needs a reusable concept contract before structure, character, world, season, or script development.
---

# Story Concept Designer

Turn the supplied brief into a bounded creative contract. Preserve facts, expose decisions, and leave detailed plot, character, and world invention to downstream specialists.

## Inputs

Read the user brief and confirmed constraints. Keep supplied facts distinct from assumptions and unresolved questions.

## Workflow

1. Extract the exact project ID, format, production modes, runtime intent, stated audience information, and creative constraints. Record every supplied constraint in `supplied_constraints` as a `statement` plus an exact `source_reference` to the brief, user message, or supplied document; never relabel it as an assumption.
2. Select `project_format` only from `feature`, `short`, `series`, `documentary`, `commercial`, `music-video`, or `short-form`. Select each `production_modes` value only from `live-action`, `animation`, `ai`, or `hybrid`.
3. Ask for a missing format or production-mode decision when it would change the concept materially. If work can continue, choose a provisional value, record it in `assumptions`, and name the confirmation needed in `uncertainties`.
4. Write the premise as the story situation, central pressure, and stakes. Do not expand it into a plot synopsis, episode map, character bible, world bible, production plan, or market analysis.
5. Write a concise logline from the concept and a central dramatic question that the finished work can sustain. Do not force a quest, transformation, or hero arc.
6. State the audience promise as the experience this concept intends to deliver. If no audience research was supplied, do not claim demand, demographics, market fit, or viewer preferences; record the research gap in `uncertainties`.
7. Name themes as tensions the work can explore. Name genres as useful expectation signals, tone as execution qualities, world scope as the bounded arena, and protagonist focus as the primary point of attention.
8. For documentary and other nonfiction work, base the concept on known subjects, places, records, testimony, access, and questions. Mark unverified claims, unavailable evidence, participant access, outcomes, and chronology as uncertainties. Let the focus be a person, group, place, institution, process, or inquiry.
9. Define observable success criteria for later development. Keep supplied facts and constraints in `supplied_constraints`, provisional decisions in `assumptions`, and unresolved evidence or decisions in `uncertainties`; do not duplicate or relabel one category as another.
10. Produce only `story-concept.json` conforming to `schemas/story-concept.schema.json`.

## Output contract

| Field group | Required content |
|---|---|
| Identity | Schema version, exact project ID, format, production modes, runtime intent |
| Promise | Audience experience, premise, logline, central dramatic question |
| Direction | Themes, genres, tone, world scope, protagonist focus |
| Control | Supplied constraints with exact source references, observable success criteria, assumptions, uncertainties |

## Quality gate

- Keep every string non-empty and every array non-empty and duplicate-free.
- Give every supplied constraint a non-empty `statement` and `source_reference`; do not put that statement in `assumptions`.
- Use `schema_version` exactly `"0.3.0"`; add no undeclared fields.
- Treat genre and structural models as options, never formulas.
- Phrase nonfiction claims no more strongly than the available evidence.
- Do not present an invented audience segment or creative hypothesis as research.

Read [concept, format, and genre guidance](references/concept-format-genre.md) when the brief is ambiguous, hybrid, nonfiction, or format-sensitive. Copy [the complete template](assets/story-concept.template.json) for the output shape.

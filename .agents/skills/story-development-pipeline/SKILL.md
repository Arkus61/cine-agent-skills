---
name: story-development-pipeline
description: Use when a selected film, series, documentary, commercial, music-video, or short-form concept must become coordinated, validated story and script packages before preproduction.
---

# Story Development Pipeline

Build the format-selected story layer, one or more script units, and an evidence-backed handoff. Orchestrate specialists; leave story, character, world, outline, screenplay, and revision theory inside their skills.

## Required inputs

Read the creative brief, selected `project_format`, selected `production_modes`, approved constraints, requested unit scope, and unresolved questions. The validated `story-concept.json.project_format` becomes the declared format used to select the story manifest inventory; never infer format from whichever files happen to exist.

Read [the pipeline contract](references/story-pipeline-contract.md) before selecting artifacts or repairing errors. Use [the story package checklist](assets/story-package-checklist.md) before handoff.

## Pipeline

1. Use `$story-concept-designer` to create `story-concept.json` with separately sourced `supplied_constraints`. Validate it before using its project ID, format, modes, or constraints downstream.
2. Use `$story-structure-designer` to create `story-structure.json` from the valid concept.
3. Use `$character-arc-designer` to create `character-arcs.json` from the valid concept and structure.
4. Use `$worldbuilding-designer` to create `world-bible.json` from the valid concept, structure, and character arcs.
5. If `project_format` is `series`, use `$season-arc-designer` to create `season-arc.json`, then select requested episode units from its declared episode inventory. For every other format, do not create `season-arc.json`; select the single canonical `<project>-U01` unit.
6. Assemble `story-manifest.json` from the exact format-selected story inventory in the contract. Run the literal `validate-story` gate and preserve its real command, exit code, and output.
7. For each selected unit, use `$episode-outline-builder` to create `unit-outline.json` from the valid story layer and, for series, the selected season episode.
8. Use `$screenplay-writer` once to create the paired `screenplay.fountain` and `screenplay-metadata.json`. Keep the files separate.
9. Use `$screenplay-reviser` to create `script-revision-plan.json` from the actual screenplay, metadata, outline, and applicable story contracts. A revision plan is not an executed rewrite.
10. Use `$scene-preproduction-pipeline` for every metadata-declared scene to create the exact `scenes/<scene-id>/` scene-full package.
11. Assemble `script-manifest.json` last in each unit directory. Validate every script package and the full story index with the real validators in the contract.
12. On any error, find the earliest invalid dependency, invalidate its transitive downstream closure, regenerate only that closure, rebuild affected manifests, and rerun all affected gates.
13. Hand off with status `ready-for-preproduction` only when current validation evidence passes. Otherwise hand off `blocked` with unresolved questions, errors, and the earliest repair decision.

## Execution rules

- Keep the story and script artifact names and dependency order exact. Do not substitute prose, combine sibling files, omit `scenes`, or add undeclared package entries.
- Treat `season-arc.json` as series-only. Do not create an empty or placeholder season artifact for another format.
- Preserve approved IDs and facts. Regeneration may reuse surviving IDs; it must not silently promote assumptions, proposals, evidence gaps, or unresolved questions to canon.
- Inspect the actual Fountain file and compare it with metadata. Neither a specialist's claim nor a manifest's `validation_status` proves screenplay validity.
- Preserve command output verbatim enough to audit the command, exit code, profile, `valid` result, and errors. Never fabricate, summarize into a passing result, or reuse stale validation evidence.
- Do not proceed through an invalid upstream artifact. Independent siblings may remain valid, but no downstream consumer may use an invalid dependency.
- Do not execute proposed screenplay revisions without separate approval. A blocked revision item remains a handoff question.
- Add no generated media, external generation service, budget, schedule, casting, rights-clearance, database, MCP, or web application work.

## Handoff

Return the project and package paths, declared format and modes, selected unit IDs, exact artifact inventories, validation commands with exit codes and outputs, repaired and invalidated files, remaining assumptions, unresolved questions, and exactly one allowed status. `ready-for-preproduction` means the story layer, every selected script unit, Fountain/metadata mapping, embedded scene packages, and project index all passed current validation; it does not replace human creative or departmental approval.

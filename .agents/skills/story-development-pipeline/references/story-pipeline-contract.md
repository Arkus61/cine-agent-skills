# Story Pipeline Contract

## Canonical packages and dependency order

The validated `story-concept.json.project_format` is the declared format that selects the story manifest inventory. Create a series story package in this exact order:

The same validated concept must carry every user- or source-supplied constraint in `supplied_constraints` with its exact `source_reference`. Downstream artifacts preserve those entries separately from assumptions and uncertainties.

1. `story-concept.json`
2. `story-structure.json`
3. `character-arcs.json`
4. `world-bible.json`
5. `season-arc.json`
6. `story-manifest.json`

For `feature`, `short`, `documentary`, `commercial`, `music-video`, and `short-form`, omit `season-arc.json` and renumber `story-manifest.json` to dependency order 5. Absence is required; an empty season file is an unexpected package entry.

Create each selected script unit in this exact order:

1. `unit-outline.json`
2. `screenplay.fountain`
3. `screenplay-metadata.json`
4. `script-revision-plan.json`
5. `scenes`
6. `script-manifest.json`

The story layer uses `profile: story-v2` and `layer: story`. Each script manifest also uses `profile: story-v2`, with `layer: script`. A layer manifest contains only its exact inventory; it is not evidence that the files passed validation.

## Specialist dependency graph

- Concept is the root.
- Structure consumes the valid concept.
- Character arcs consume valid concept and structure.
- World consumes valid concept, structure, and character arcs so its declared characters, places, rules, and assets agree with the established ledgers.
- Season consumes all four valid upstream story artifacts and exists only for a series.
- A unit outline consumes the complete valid story layer and, for a series, one selected declared episode.
- The screenplay and metadata are one paired output that consumes the valid unit outline and applicable story artifacts.
- The revision plan consumes the actual screenplay, metadata, outline, and applicable story artifacts.
- Each full-v1 scene package consumes the corresponding metadata mapping and actual screenplay scene.
- Each manifest depends on every entry it inventories. The project index depends on the valid story package and every selected valid script package.

## Validation evidence

After assembling the story manifest, run exactly this command shape from the repository root:

```bash
.venv/bin/cine-skills validate-story <project-root>/story --project-format <format> --format json
```

Require exit code 0 and a current JSON result with command `validate-story`, profile `story-v2`, `valid: true`, and no errors. If the executable is unavailable, use `.venv/bin/python -m cine_skills` with the same arguments and record the substitution.

After every selected script package exists, call `validate_script_package` for each exact unit directory and `build_story_index` for the story and scripts directories. Record the executed command or code invocation, exit code, and complete returned diagnostics. These validators inspect package membership, schemas, Fountain, metadata, full-v1 scene packages, episode or unit inventory, and cross-artifact references.

Never declare the screenplay package valid without inspecting `screenplay.fountain` and comparing the real summary with `screenplay-metadata.json`. Never infer success from file presence, specialist prose, a manifest field, a previous run, or validation of the story layer alone.

## Earliest-invalid repair

Map every diagnostic to the artifact or directory whose contract first became false. Choose the earliest invalid node in canonical dependency order, not merely the first printed error. If a downstream mismatch is caused by a still-valid upstream decision, repair the downstream node; if its source dependency is wrong, repair that earlier source.

Invalidate the earliest invalid node and its transitive downstream closure. Regenerate only that closure. Preserve valid ancestors, independent siblings, approved facts, and surviving stable IDs. Delete an artifact only when the selected format no longer permits it, such as removing `season-arc.json` after an approved series-to-short change.

Use these closure rules:

- Concept: all later story artifacts, every script unit, both manifests, and the project index.
- Structure: character arcs, world, conditional season, story manifest, every script unit, and the project index.
- Character arcs: world, conditional season, story manifest, every affected script unit, and the project index.
- World: conditional season, story manifest, every affected script unit, and the project index.
- Season: story manifest, affected series units, their script manifests, and the project index.
- Story manifest only: no creative artifact; rerun story validation and every gate whose evidence used that manifest.
- Unit outline: paired screenplay and metadata, revision plan, affected scene packages, script manifest, and project index.
- Screenplay or metadata: regenerate the paired output when authorship changed; then revision plan, affected scene packages, script manifest, and project index. A formatting-only metadata repair may preserve unchanged screenplay text when the real comparison proves it.
- Revision plan: revision plan, script manifest, and project index only. Do not rewrite the screenplay merely because its diagnosis changed.
- Scene package: that scene package, script manifest, and project index.
- Script manifest only: no creative artifact; rerun script and index validation.

After regeneration, rerun the repaired artifact's direct gate and every affected package gate. Evidence from invalidated files is stale.

## Handoff contract

Allowed handoff statuses: `ready-for-preproduction`, `blocked`.

Return one handoff containing:

- project path, project ID, declared format, modes, and selected unit IDs;
- exact story and per-unit script inventories;
- each validation command or invocation, exit code, profile, result, and errors;
- earliest repaired dependency and exact invalidated/regenerated closure;
- assumptions and unresolved questions;
- the allowed status.

Use `ready-for-preproduction` only when the current story validation, every script validation, Fountain/metadata comparison, every embedded full-v1 scene validation, and the project index all pass. Use `blocked` for any failure, absent evidence, missing approval, unresolved authorship decision, or unavailable validator. A blocked handoff states what can be decided next; it does not fabricate validation.

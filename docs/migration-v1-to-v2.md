# Migrating a Full v1 Scene into a v2 Project

Cine Agent Skills 2.0 migration is additive. A valid `core-v0.1` or `full-v1` scene package remains unchanged and can continue to be validated with its existing profile. The v2 project wraps that scene with story, screenplay, production, and post layers connected by stable identifiers.

## Before migrating

Validate the existing scene first and resolve its errors:

```bash
cine-skills validate-package projects/<project>/scenes/<scene-id> --profile auto --format json
```

Record the project and scene IDs, beats, shots, characters, assets, and any supplied source evidence. Do not rename identifiers merely to fit a new layer.

## Build the layers

1. Create `creative-manifest.json` with the selected format, production modes, unit list, layer paths, `release_version: "2.0.0"`, and `profile: "full-creative-v2"`.
2. Create the required story artifacts in `story/` and finish `story-manifest.json`. For a series, include `season-arc.json`.
3. Create one script unit under `scripts/<unit-id>/`, including the Fountain draft, metadata, revision plan, script manifest, and a `scenes/<scene-id>/` directory containing the unchanged or deliberately revised full-v1 scene package.
4. Create the required production artifacts. Animation and hybrid projects require `animation-plan.json`; AI and hybrid projects require `media-prompt-package.json`.
5. Create the post artifacts in dependency order, ending with `post-manifest.json`.

Every new v2 JSON artifact declares `schema_version: "2.0"`. The embedded v1 scene artifacts keep `schema_version: "1.0"` and their `full-v1` manifest. Use `planned`, `awaiting-media`, or another contract-defined evidence state when an input has not been supplied or inspected.

## Validate and repair

Validate layers independently while building:

```bash
cine-skills validate-story projects/<project>/story --project-format <format> --format json
cine-skills validate-production projects/<project>/production --root . --production-mode <mode> --allow-nested --format json
cine-skills validate-post projects/<project>/post --root . --format json
cine-skills validate-project projects/<project> --profile full-creative-v2 --format json
```

The project validator loads the manifest first, validates layers in dependency order, and checks cross-layer IDs and exact inventories. Repair the earliest invalid layer, then review any affected downstream plan. A successful result proves structural validity and reference integrity only; it does not prove creative acceptance, source freshness, media inspection, rights clearance, or delivery QC.

No migration command fabricates story, screenplay, production, media, or post decisions. Missing evidence stays explicit, and human review remains required before a plan is treated as approved or ready to execute.

## Existing packages and rollback

Keep the original scene directory available as a compatibility reference. If the v2 wrapper is incomplete, the original package still validates independently. Removing the v2 wrapper does not alter the v1 artifacts it references.

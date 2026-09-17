# Artifact Schemas

All schemas use JSON Schema Draft 2020-12. Schema payload versions are separate from the repository release version `2.0.0`:

- Preserved v0.1/v1 scene artifacts and `package-manifest.schema.json` declare `schema_version: "1.0"`.
- New v2 layer and project artifacts declare `schema_version: "2.0"` and `release_version: "2.0.0"`.

## Preserved v0.1/v1 artifacts

`scene-beats`, `directing-plan`, `visual-language-plan`, `blocking-plan`, `camera-movement-plan`, `shot-list`, `lighting-plan`, `sound-plan`, `storyboard-plan`, `production-breakdown`, `continuity-plan`, and `package-manifest` remain the unchanged scene-level contracts used by `core-v0.1` and `full-v1`.

## v2 artifacts

Story and screenplay: `story-concept`, `story-structure`, `character-arcs`, `world-bible`, `season-arc`, `unit-outline`, `screenplay-metadata`, and `script-revision-plan`.

Production: `production-design-plan`, `character-look-bible`, `animation-plan`, `vfx-plan`, `media-prompt-package`, and `media-review-report`.

Postproduction: `edit-plan`, `sound-post-plan`, `music-plan`, `vfx-post-plan`, `color-plan`, `titles-captions-plan`, and `mastering-qc-plan`.

Layer and project control: `layer-manifest.schema.json` defines story, script, production, and post manifests; `creative-manifest.schema.json` defines the full-creative-v2 project manifest.

## Validation

```bash
python -m cine_skills validate .
python -m cine_skills validate-artifact shot-list examples/ninel/scenes/S01/shot-list.json
python -m cine_skills validate-package examples/ninel/scenes/S01 --profile core-v0.1
python -m cine_skills validate-package examples/ninel-v1/scenes/S01 --profile full-v1 --format json
python -m cine_skills validate-story examples/ninel-v2/story --project-format series --format json
python -m cine_skills validate-production examples/ninel-v2/production --root . --production-mode animation --production-mode ai --allow-nested --format json
python -m cine_skills validate-post examples/ninel-v2/post --root . --format json
python -m cine_skills validate-project examples/ninel-v2 --profile full-creative-v2 --format json
```

Scene-package validation checks exact membership, schemas, shared scene identity, identifier formats, resolved beat and shot references, coverage, and manifest order. Full-project validation additionally checks layer membership and cross-layer provenance. Run `make check`, all explicit example targets, and `make release-archive` before a release handoff. Structural validity never implies creative approval, media inspection, freshness, rights clearance, or delivery compliance.

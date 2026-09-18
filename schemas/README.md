# Artifact Schemas

All 35 subject schemas use JSON Schema Draft 2020-12. The active system version is `0.3.0`; the short label `0.3` and the machine value `0.3.0` refer to the same prerelease. Every active `schema_version`, `release_version`, and manifest artifact version is synchronized to that value by `scripts/sync_versions.py`.

The schemas remain specialized. A unified version does not collapse scene, story, production, post, and project artifacts into one universal schema.

## Functional groups

Scene planning: `scene-beats`, `directing-plan`, `visual-language-plan`, `blocking-plan`, `camera-movement-plan`, `shot-list`, `lighting-plan`, `sound-plan`, `storyboard-plan`, `production-breakdown`, `continuity-plan`, and `package-manifest`.

Story and screenplay: `story-concept`, `story-structure`, `character-arcs`, `world-bible`, `season-arc`, `unit-outline`, `screenplay-metadata`, and `script-revision-plan`.

Production: `production-design-plan`, `character-look-bible`, `animation-plan`, `vfx-plan`, `media-prompt-package`, and `media-review-report`.

Postproduction: `edit-plan`, `sound-post-plan`, `music-plan`, `vfx-post-plan`, `color-plan`, `titles-captions-plan`, and `mastering-qc-plan`.

Layer and project control: `layer-manifest.schema.json` defines story, script, production, and post manifests; `creative-manifest.schema.json` defines the `full-creative` project manifest.

Historical migration documents may mention the old `1.0` and `2.0` schema values. Those values are not accepted as active contracts and are not a source for new artifacts.

## Validation

```bash
python -m cine_skills validate .
python -m cine_skills validate-artifact shot-list examples/scene-core/scenes/S01/shot-list.json
python -m cine_skills validate-package examples/scene-core/scenes/S01 --profile scene-core
python -m cine_skills validate-package examples/scene-full/scenes/S01 --profile scene-full --format json
python -m cine_skills validate-story examples/ninel/story --project-format series --format json
python -m cine_skills validate-production examples/ninel/production --root . --production-mode animation --production-mode ai --allow-nested --format json
python -m cine_skills validate-post examples/ninel/post --root . --format json
python -m cine_skills validate-project examples/ninel --profile full-creative --format json
```

Scene-package validation checks exact membership, schemas, shared scene identity, identifier formats, resolved beat and shot references, coverage, and manifest order. Full-project validation additionally checks layer membership and cross-layer provenance. Structural validity never implies creative approval, media inspection, freshness, rights clearance, or delivery compliance.

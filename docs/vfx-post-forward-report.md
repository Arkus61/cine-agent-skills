# VFX Post Forward Application Report

## Scope

Applied `.agents/skills/vfx-post-supervisor/SKILL.md`, its two reference documents and template, and `schemas/vfx-post-plan.schema.json` to the two supplied scenarios. This exercise produced structured planning artifacts only. No media, previews, metadata, NLE or DCC state, transfers, renders, approvals, or delivery targets were inspected or operated.

## Scenario 1: GLASS screen replacement

Plan: `docs/vfx-post-forward-screen.json`

Preserved invalid first artifact: `docs/vfx-post-forward-screen-first.json`

Decisions:

- Registered the supplied filename `screen_comp_v07_final.mov` as a claimed current output version, while explicitly stating that its file, contents, metadata, and technical condition were not supplied or inspected.
- Set review to `awaiting-media`, with empty review evidence. The producer's statement that v06 was reviewed cannot approve v07 and is not an actual approval record.
- Set delivery to `not-planned` because no target specification or delivery-verification evidence was supplied.
- Planned display tracking, finger rotoscoping, and screen compositing. Plate, lens, defocus, grain, color handoff, and final verification await inputs or inspection.
- Kept turnover today as a schedule request rather than a readiness or approval claim.

Exact first validation command:

```text
PYTHONPATH=src .venv/bin/python -m cine_skills validate-artifact vfx-post-plan docs/vfx-post-forward-screen.json --root . --format json
```

Exact first validation output:

```json
{"command": "validate-artifact", "errors": ["source_context.0.version_id: media version ID 'GLASS-SCREEN-COMP-V07' must match GLASS-MD###-v###", "source_context.media_versions.0.media_id: media ID 'GLASS-SCREEN-COMP' must match GLASS-MD###", "source_context.media_versions.0.version_id: version ID 'GLASS-SCREEN-COMP-V07' must belong to declared media ID GLASS-SCREEN-COMP"], "valid": false}
```

First validation exit code: `1`

Repair:

- Changed media ID `GLASS-SCREEN-COMP` to `GLASS-MD001`.
- Changed version ID `GLASS-SCREEN-COMP-V07` to `GLASS-MD001-v007` everywhere it identified the registered/current version.
- Preserved the invalid pre-repair artifact in `docs/vfx-post-forward-screen-first.json`.

Exact repaired validation output:

```json
{"command": "validate-artifact", "errors": [], "valid": true}
```

Repaired validation exit code: `0`

## Scenario 2: WOOD creature integration

Plan: `docs/vfx-post-forward-creature.json`

Decisions:

- Left source and current output versions empty because none were supplied.
- Set tracking to `awaiting-input`. The artist's verbal statement does not identify a version or provide inspection evidence, so tracking was not marked complete.
- Set review to `awaiting-media`, with empty review evidence.
- Set delivery to `not-planned` because no target specification, candidate version, or delivery-verification evidence was supplied.
- Planned branch rotoscoping, creature compositing, and wet-ground interaction simulation. Plate, tracking acceptance, lens, defocus, grain, color handoff, and final verification await inputs or inspection.
- Kept tonight as a requested planning deadline rather than evidence of shot readiness.

Exact first validation command:

```text
PYTHONPATH=src .venv/bin/python -m cine_skills validate-artifact vfx-post-plan docs/vfx-post-forward-creature.json --root . --format json
```

Exact first validation output:

```json
{"command": "validate-artifact", "errors": [], "valid": true}
```

First validation exit code: `0`

Repairs: none.

## Tightened-schema migration

This section records migration of the existing final forward artifacts to the later schema that requires explicit media-version roles. It is not a new first-pass application trial, and the original first-run evidence above remains unchanged. `docs/vfx-post-forward-screen-first.json` was intentionally left unchanged.

### GLASS migration

- Added `roles: ["output"]` to `GLASS-MD001-v007` in `docs/vfx-post-forward-screen.json`.
- The supplied filename denotes an uninspected output candidate. It was not assigned `source` or `plate`, and no source media or evidence was invented.
- `current_output_version_id` continues to reference the registered output-role version. `source_version_ids` remains empty.

Exact migration validation command:

```text
PYTHONPATH=src .venv/bin/python -m cine_skills validate-artifact vfx-post-plan docs/vfx-post-forward-screen.json --root . --format json
```

Exact migration validation output:

```json
{"command": "validate-artifact", "errors": [], "valid": true}
```

Migration validation exit code: `0`

### WOOD migration

- No media-role field was added because `media_versions` is empty, `source_version_ids` is empty, and `current_output_version_id` is null.
- No versions, sources, plates, outputs, or evidence were invented.

Exact migration validation command:

```text
PYTHONPATH=src .venv/bin/python -m cine_skills validate-artifact vfx-post-plan docs/vfx-post-forward-creature.json --root . --format json
```

Exact migration validation output:

```json
{"command": "validate-artifact", "errors": [], "valid": true}
```

Migration validation exit code: `0`

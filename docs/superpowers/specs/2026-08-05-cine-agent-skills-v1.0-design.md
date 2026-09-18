# Cine Agent Skills v1.0 Design Specification

## Status

Approved product direction: a complete, portable film and series scene-preproduction system that runs without paid APIs or media generation. This specification expands v0.1 additively and preserves its scene-package contract.

## Goal

Turn one scripted scene or scene brief into a validated professional preproduction package covering dramatic analysis, directing, visual language, blocking, camera movement, shot design, lighting, sound, storyboard instructions, production requirements, and continuity.

Version 1.0 is complete when a user can install the repository, invoke one orchestrator, obtain the full package, validate it deterministically, and hand the artifacts to human departments or later media-generation integrations without reinterpreting hidden decisions.

## Approaches considered

### Additive modular expansion (selected)

Keep the v0.1 skills and five-artifact package valid. Add focused skills and schemas for the missing preproduction departments, then extend package validation with an explicit full-v1 profile. This preserves existing users and keeps each skill independently useful.

### Breaking contract rewrite

Replace the v0.1 schemas with one normalized scene graph. This reduces some duplication but invalidates existing packages, templates, tests, and user workflows. The compatibility cost is not justified for v1.0.

### Independently installed domain packs

Ship camera, art, audio, and production skills as separate packs. This makes selective installation easier but complicates discovery, validation, documentation, and the promised one-command pipeline. Domain packs can be considered after the unified v1.0 contract is stable.

## Product boundary

### Included

- Scene-level dramatic analysis and directing.
- Visual grammar, composition, aspect ratio, lens-language, and camera-height rules.
- Blocking, screen geography, eyelines, and motivated camera movement.
- Production-ready shot lists.
- Shot-linked lighting and sound plans.
- Textual storyboard panels suitable for a human artist or a future image system.
- Scene-level production breakdown by department.
- Shot-linked continuity and reset planning.
- Deterministic schema, repository, and cross-artifact validation.
- Text and JSON validation reports.
- Backward-compatible validation of v0.1 scene packages.

### Excluded

- Direct image, audio, or video generation.
- Vendor-specific prompts or paid generation APIs.
- DaVinci Resolve, Blender, NLE, DCC, or virtual-production control.
- Editing, color grading, sound mixing, or delivery automation.
- Budget calculation, shooting schedules, call sheets, casting selection, or crew management.
- MCP servers, hosted services, databases, and web interfaces.

The production breakdown may identify cast presence, equipment, departmental needs, risks, and unresolved questions. It must not select performers, estimate money, or schedule work.

## Release and schema versioning

- Repository/package release version: `1.0.0`.
- Artifact `schema_version`: `"1.0"` for both preserved and new contracts.
- Full package profile: `full-v1`.
- Compatibility package profile: `core-v0.1`.
- Auto profile: a package with `package-manifest.json` is `full-v1`; a package without it is checked as `core-v0.1`.

Release version and artifact schema version are separate concepts. Existing v0.1 artifacts already use schema version `1.0`; the release must document this explicitly rather than rewriting valid payloads.

## Skill catalog

Version 1.0 contains exactly twelve project-local skills:

| Order | Skill | Primary output |
|---:|---|---|
| 1 | `scene-beat-analyzer` | `scene-beats.json` |
| 2 | `scene-director` | `directing-plan.json` |
| 3 | `visual-language-designer` | `visual-language-plan.json` |
| 4 | `blocking-designer` | `blocking-plan.json` |
| 5 | `camera-movement-designer` | `camera-movement-plan.json` |
| 6 | `shot-list-builder` | `shot-list.json` |
| 7 | `lighting-designer` | `lighting-plan.json` |
| 8 | `sound-designer` | `sound-plan.json` |
| 9 | `storyboard-designer` | `storyboard-plan.json` |
| 10 | `production-breakdown` | `production-breakdown.json` |
| 11 | `continuity-supervisor` | `continuity-plan.json` |
| 12 | `scene-preproduction-pipeline` | Complete package and `package-manifest.json` |

Each specialist can be invoked independently when its prerequisites are available. The orchestrator owns dependency order, repair propagation, validation, and the final handoff report.

## Canonical full-v1 package

```text
projects/<project-slug>/scenes/<scene-id>/
├── source-scene.md
├── scene-beats.json
├── directing-plan.json
├── visual-language-plan.json
├── blocking-plan.json
├── camera-movement-plan.json
├── shot-list.json
├── lighting-plan.json
├── sound-plan.json
├── storyboard-plan.json
├── production-breakdown.json
├── continuity-plan.json
└── package-manifest.json
```

The five preserved v0.1 artifacts keep their current schemas and filenames. Six new creative artifacts and one deterministic manifest complete the v1.0 package.

## Pipeline and dependency flow

1. Read `source-scene.md`; separate facts, supplied constraints, assumptions, and creative proposals.
2. Produce dramatic beats.
3. Produce a directing concept from the beats.
4. Define visual language from the source, beats, and directing concept.
5. Design blocking from the directing and visual constraints.
6. Design camera movement from beats, visual language, and blocking.
7. Build the shot list from every preceding creative decision.
8. Produce lighting, sound, and storyboard plans against stable shot IDs.
9. Produce the production breakdown from the source and all shot-linked plans.
10. Produce the continuity plan and audit every shot transition.
11. Validate the full package, repair the earliest invalid dependency, regenerate only downstream artifacts, and repeat.
12. Write the package manifest and final handoff report.

A later artifact may refine an earlier choice but must not silently reverse it. A changed beat invalidates every downstream artifact; a changed shot list invalidates lighting, sound, storyboard, breakdown, continuity, and manifest outputs.

## Common artifact rules

Every creative JSON artifact contains:

- `schema_version: "1.0"`;
- a non-empty `scene_id`;
- an `assumptions` array, which may be empty;
- only fields declared by its schema;
- stable identifiers using the scene prefix;
- explicit dramatic or production purpose for major choices.

Script facts, user-supplied constraints, assumptions, and creative proposals must remain distinguishable. No skill may invent a location, performer capability, equipment resource, safety clearance, or production fact silently.

## Stable identifier contract

| Entity | Pattern | Example |
|---|---|---|
| Beat | `<scene>-B##` | `S01-B01` |
| Camera movement | `<scene>-M##` | `S01-M01` |
| Shot | `<scene>-SH###` | `S01-SH001` |
| Visual rule | `<scene>-V##` | `S01-V01` |
| Lighting setup | `<scene>-L##` | `S01-L01` |
| Sound cue or bed | `<scene>-A##` | `S01-A01` |
| Storyboard panel | `<scene>-SB###` | `S01-SB001` |
| Breakdown item | `<scene>-PD###` | `S01-PD001` |
| Continuity item | `<scene>-CN###` | `S01-CN001` |

Matching is exact and rejects prefixes, suffixes, whitespace, embedded line endings, duplicate IDs, and IDs derived from another scene.

## New artifact contracts

### Visual language plan

Defines aspect ratio, point of view, palette, contrast, texture, lens strategy, composition rules, camera-height rules, visual motifs, prohibited defaults, and explicitly motivated exceptions. Each rule has a visual-rule ID, beat references, and dramatic purpose.

### Lighting plan

Defines motivated sources and executable setups. Each setup has a lighting ID, beat and shot references, environment or time basis, key/fill/back or practical strategy, direction, quality, color intent, exposure/contrast intent, control requirements, continuity notes, safety notes, and dramatic purpose.

Every shot in a full-v1 package is covered by at least one lighting setup, including shots that intentionally use available or natural light.

### Sound plan

Defines dialogue priorities, production effects, ambience, perspective, silence, transition cues, and non-copyright-specific music intent. Each cue has an audio ID, beat and shot references, source or category, spatial perspective, timing, recording or design requirement, and dramatic purpose.

Every shot is covered by at least one sound cue or bed. Intentional silence is represented explicitly rather than by omission.

### Storyboard plan

Defines one or more panels per shot. Each panel has a panel ID, shot reference, depicted moment, framing, camera height and angle, foreground/midground/background layout, subject placement, action direction, movement start or end state, lighting note, audio cue, continuity note, and dramatic purpose.

Every shot receives at least one storyboard panel. The artifact contains instructions only; it does not generate or embed images.

### Production breakdown

Defines department-grouped items for cast presence, location or set requirements, props, wardrobe, hair and makeup, camera or grip, lighting, sound, practical effects, visual effects, art department, safety, and unresolved production questions. Each item has a breakdown ID, category, source basis, relevant beat or shot references, requirement, continuity or reset needs, assumptions, and risk level.

### Continuity plan

Defines shot-linked states and transitions for screen direction, eyelines, performer position, action phase, props, wardrobe, makeup, environment, light, sound perspective, and reset requirements. Each item has a continuity ID, shot references, tracked state, required transition, reset instruction, and severity if violated.

### Package manifest

The manifest contains package release version, profile, scene ID, source filename, the exact required artifact filenames, their declared schema versions, dependency order, validation status, and unresolved questions. It contains no machine-local absolute paths or timestamps, so identical inputs can produce a deterministic manifest.

## Full-v1 package validation

Validation is schema-first. Cross-artifact checks run only for artifacts that loaded successfully and passed their own schema.

The full profile checks:

- all thirteen canonical files exist;
- every JSON document is strict UTF-8 standards-compliant JSON with an object at the root;
- every schema is valid JSON Schema Draft 2020-12;
- every artifact declares the same scene ID;
- every declared identifier is unique and matches its exact category pattern;
- every beat, shot, lighting, sound, and panel reference resolves;
- every dramatic beat is covered by at least one shot;
- every shot is covered by lighting, sound, storyboard, and continuity plans;
- production breakdown references resolve when supplied;
- the manifest lists the exact required artifacts in dependency order;
- unresolved conflicts and assumptions are reported rather than silently discarded.

Diagnostics are deterministic, sorted, file-specific, and include a field path. Validation never emits a Python traceback for malformed user input.

## Command-line interface

Both entry points are supported:

```bash
python -m cine_skills <command>
cine-skills <command>
```

Commands:

```bash
cine-skills validate [ROOT] [--format text|json]
cine-skills validate-artifact SCHEMA_NAME JSON_FILE [--root ROOT] [--format text|json]
cine-skills validate-package PACKAGE_DIR [--root ROOT] [--profile auto|core-v0.1|full-v1] [--format text|json]
```

Text output remains compatible with v0.1. JSON output contains `valid`, `command`, `profile` when applicable, and a sorted `errors` array. Exit codes remain `0` for success, `1` for validation failure, and `2` for malformed invocation.

## Backward compatibility

- The existing five schemas and their accepted payloads remain valid.
- `validate-package` defaults to `auto` and accepts existing five-artifact packages as `core-v0.1`.
- Existing module entry points and Make targets remain available.
- The new console script is additive.
- The migration guide explains how to extend a core package to full-v1; no creative artifact is fabricated by a migration command.

## Skill design and evaluation

- Each `SKILL.md` contains only essential procedure and stays below 500 lines.
- Detailed film theory lives in directly linked `references/` files.
- JSON skeletons live in `assets/`.
- `agents/openai.yaml` is generated or refreshed from the final skill instructions.
- Each new skill receives a failing baseline scenario before its instructions are authored.
- Each new skill is validated and forward-tested before work starts on the next skill.
- Evaluation assertions target observable output shape, reference integrity, explicit assumptions, and decision quality rather than exact prose.
- Source material is paraphrased and recorded in `docs/source-register.md`; copyrighted course text and proprietary shot breakdowns are not bundled.

## Testing strategy

- Unit tests for profile selection, JSON reporting, schemas, identifier categories, coverage, references, manifests, and error handling.
- CLI tests through both `python -m cine_skills` and the installed `cine-skills` entry point.
- Compatibility tests proving the canonical v0.1 Ninel package still validates unchanged.
- End-to-end tests for a complete full-v1 Ninel package.
- Catalog tests for the exact twelve skills, allowed frontmatter, UI metadata, local links, templates, and schema mappings.
- Behavioral evaluation fixtures for every new specialist and the expanded orchestrator.
- Clean-bootstrap testing with `make setup` followed by `make check`.
- Archive inspection for path prefix, forbidden development files, and successful extraction.

## Documentation and release artifacts

- Rewrite the README around the v1.0 full pipeline while preserving specialist examples.
- Update Codex startup and contribution instructions.
- Add `docs/migration-v0.1-to-v1.0.md`.
- Add a root `CHANGELOG.md` with the v1.0 release entry.
- Expand schema documentation and source register.
- Build `cine-agent-skills-v1.0.0.zip` from tracked release files only.
- Record the release commit and SHA-256 digest.

## Release criteria

Version 1.0 is releasable only when:

1. The repository version is `1.0.0` in packaging and runtime metadata.
2. Exactly twelve skills pass repository validation.
3. All eleven creative schemas and the manifest schema pass Draft 2020-12 validation.
4. The unchanged core-v0.1 example passes auto and explicit compatibility validation.
5. The full-v1 Ninel package passes all schema, reference, coverage, and manifest checks.
6. Text and JSON CLI output return the documented exit codes without tracebacks.
7. Every new skill passes its baseline-to-forward evaluation and package validation.
8. `make setup` followed by `make check` succeeds from a clean tracked-only copy.
9. Documentation contains no stale v0.1 product claims or unsupported features.
10. The release archive contains one `cine-agent-skills/` prefix, excludes Git metadata, environments, caches, and internal work logs, and passes archive integrity testing.

# Cine Agent Skills

Cine Agent Skills 2.0 is a portable, source-conscious planning system for story, screenplay, scene preproduction, creative production, and postproduction. It turns supplied material into coherent, validated plans without a paid API, network dependency at runtime, or media generation. The original v0.1 and v1 scene contracts remain intact.

## Included skills

| Order | Skill | Primary output |
|---:|---|---|
| 1 | `$scene-beat-analyzer` | `scene-beats.json` |
| 2 | `$scene-director` | `directing-plan.json` |
| 3 | `$visual-language-designer` | `visual-language-plan.json` |
| 4 | `$blocking-designer` | `blocking-plan.json` |
| 5 | `$camera-movement-designer` | `camera-movement-plan.json` |
| 6 | `$shot-list-builder` | `shot-list.json` |
| 7 | `$lighting-designer` | `lighting-plan.json` |
| 8 | `$sound-designer` | `sound-plan.json` |
| 9 | `$storyboard-designer` | `storyboard-plan.json` |
| 10 | `$production-breakdown` | `production-breakdown.json` |
| 11 | `$continuity-supervisor` | `continuity-plan.json` |
| 12 | `$scene-preproduction-pipeline` | Complete validated scene package |

Each specialist is independently usable. The pipeline coordinates all specialists in dependency order, repairs the earliest invalid artifact and affected downstream files, then hands off only a package that passes validation.

The v2 catalog adds story-development skills (`story-concept-designer`, `story-structure-designer`, `character-arc-designer`, `worldbuilding-designer`, `season-arc-designer`, `episode-outline-builder`, `screenplay-writer`, `screenplay-reviser`, and `story-development-pipeline`), creative-production skills (`production-designer`, `character-look-designer`, `animation-director`, `vfx-planner`, `ai-media-prompt-designer`, `media-review-supervisor`, and `creative-production-pipeline`), and postproduction skills (`film-editor`, `sound-post-designer`, `music-story-designer`, `vfx-post-supervisor`, `color-grading-designer`, `titles-captions-designer`, `mastering-qc-supervisor`, and `postproduction-pipeline`). `$full-creative-pipeline` coordinates the layers. The repository contains exactly thirty-seven project-local skills: twelve preserved v1 skills and twenty-five v2 skills.

## Start in Codex

1. Extract or clone the repository.
2. Open the repository root in Codex.
3. Start a fresh session so the project-local skills under `.agents/skills` are discovered.
4. Invoke the full pipeline:

```text
Use $full-creative-pipeline for examples/ninel-scene-brief.md.
Create a full-creative-v2 planning package under projects/ninel/, validate it, and report the handoff state, assumptions, unresolved questions, and any awaiting-media evidence.
```

To run only one department:

```text
Use $lighting-designer to create a motivated lighting plan for this approved shot list.
```

## Install and verify

Python 3.11 or newer is required.

```bash
make setup
make check
make validate-core-example
make validate-full-example
make validate-v2-example
make release-archive
```

`make setup` creates `.venv` and installs the editable development package. Later Make targets automatically select `.venv/bin/python`. In an already managed environment:

```bash
python -m pip install -e '.[dev]'
make PYTHON=python check
```

## Package profiles

- `core-v0.1` preserves the original source plus five creative JSON artifacts. Existing valid v0.1 packages remain valid unchanged.
- `full-v1` contains the source, eleven creative JSON artifacts, and a deterministic manifest.
- `story-v2`, `production-v2`, and `post-v2` validate the corresponding v2 layers.
- `full-creative-v2` validates the complete story → screenplay → scene → production → post project selected by `creative-manifest.json`.
- `auto` remains the v1 CLI default. The presence of `package-manifest.json` selects `full-v1`; its absence selects `core-v0.1`.

The release version is `2.0.0`. New v2 artifacts use `schema_version: "2.0"`; preserved v0.1/v1 artifacts retain `schema_version: "1.0"`. These are separate version contracts.

The canonical full package is:

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

See `examples/ninel/scenes/S01/` for the unchanged core example and `examples/ninel-v1/scenes/S01/` for the complete v1 example.

The canonical v2 demonstration is `examples/ninel-v2/`: a minimal `series` project in `animation` + `ai` mode with two declared units, a complete E01 scene package, and planned production/post layers. Its media review is intentionally `awaiting-media`; the example is structural planning evidence, not creative approval or inspected media.

## Validation CLI

The installed `cine-skills` entry point and `python -m cine_skills` expose the same commands:

```bash
cine-skills validate .
cine-skills validate-artifact shot-list examples/ninel/scenes/S01/shot-list.json
cine-skills validate-package examples/ninel/scenes/S01 --profile core-v0.1
cine-skills validate-package examples/ninel-v1/scenes/S01 --profile full-v1 --format json
cine-skills validate-story examples/ninel-v2/story --project-format series --format json
cine-skills validate-production examples/ninel-v2/production --root . --production-mode animation --production-mode ai --allow-nested --format json
cine-skills validate-post examples/ninel-v2/post --root . --format json
cine-skills validate-project examples/ninel-v2 --profile full-creative-v2 --format json
```

`validate-package` accepts `--profile auto|core-v0.1|full-v1` and `--format text|json`. JSON reports are deterministic and include the command, resolved profile, validity, and sorted errors. Exit status is `0` for a valid result, `1` for validation failure, and `2` for malformed invocation.

The v2 layer commands use `story-v2`, `production-v2`, and `post-v2`; `validate-project` uses `full-creative-v2`. A valid plan may still report `awaiting-media` or `planned`: validation proves structure and references, not media inspection, artistic approval, or delivery QC. Unknown profiles and malformed arguments exit `2`; validation failures exit `1`.

Make wrappers remain available:

```bash
make validate
make validate-artifact SCHEMA_NAME=shot-list ARTIFACT_FILE=examples/ninel/scenes/S01/shot-list.json
make validate-package PACKAGE_DIR=examples/ninel-v1/scenes/S01
make validate-story-example
make validate-production-example
make validate-post-example
make validate-v2-example
make release-archive
```

## Migration and scope

Read [the v0.1 to v1.0 migration guide](docs/migration-v0.1-to-v1.0.md) for the preserved scene package and [the v1 to v2 migration guide](docs/migration-v1-to-v2.md) before adding the layered workflow. Migration never fabricates creative decisions: create and review each new layer, carry stable IDs, then validate.

Version 2.0 deliberately excludes generated images, audio, and video; external generation APIs; DaVinci Resolve, Blender, or NLE control; MCP servers; casting; budgeting; scheduling; a database; publishing; and a web UI. Blender is documented as a separate future pilot. The deliverable is a source-bound planning package ready for human departmental review, not an automatically approved shoot plan. Freshness/change tracking remains an explicit future sidecar rather than an implicit claim in validation.

## Repository structure

```text
.agents/skills/       Codex-discoverable skills
schemas/              Artifact contracts
src/cine_skills/      Validation CLI
examples/             Core and full worked scene packages
evals/                Observable skill behaviors
knowledge/            Shared source policy
docs/                  Start guide, migration guide, design, and sources
scripts/               Release tooling
```

## Design principles

- Film language before model-specific prompting.
- Motivated, repeatable choices before decorative technique.
- Stable artifacts and identifiers between departments.
- Script facts, assumptions, uncertainties, and creative proposals remain distinct.
- Lean skills with focused references and machine-checkable outputs.
- No dependency on a paid generation API.

## Troubleshooting

- Open the repository root, not `.agents/`.
- Start a fresh Codex session after adding or changing skills.
- Confirm every skill lives at `.agents/skills/<name>/SKILL.md` and its frontmatter name matches the directory.
- Run `make validate` for packaging problems and `make check` before handoff.
- Use `--format json` to obtain actionable machine-readable validation errors.

## License

Apache-2.0 for original repository content. Third-party source material remains under its own terms and is not bundled here.

# Starting Cine Agent Skills 2.0 in Codex

## Open and verify

Open the repository root, not `.agents/`. Start a new session after adding or changing skills because discovery occurs when the session initializes.

```bash
make setup
make check
make validate-core-example
make validate-full-example
make validate-story-example
make validate-production-example
make validate-post-example
make validate-v2-example
```

`make setup` creates `.venv`; later Make commands select it automatically. In an already managed environment:

```bash
python -m pip install -e '.[dev]'
make PYTHON=python check
```

## First inspection

```text
Read AGENTS.md, README.md, `docs/superpowers/specs/2026-08-06-cine-agent-skills-v2.0-design.md`, and `docs/superpowers/specs/2026-09-13-cine-direction.md`. Run `make check` and every explicit example target. Summarize the layered architecture, compatibility profiles, scope boundaries, and verified status without changing files.
```

## Full production exercise

```text
Use $full-creative-pipeline on examples/ninel-scene-brief.md.
Create a full-creative-v2 planning project under projects/ninel/.
Run story → screenplay → preserved v1 scene planning → production → post in dependency order, validate with the full-creative-v2 profile, and report repairs, assumptions, unresolved questions, and whether media is still awaiting evidence.
```

Compare structure and contracts with `examples/ninel-v1/scenes/S01/`; do not copy its creative decisions into a different scene.

## Profiles and commands

- `core-v0.1`: compatible source plus five-artifact package.
- `full-v1`: source, eleven creative artifacts, and manifest.
- `auto`: selects full when the manifest is present, otherwise core.
- `story-v2`, `production-v2`, and `post-v2`: exact v2 layer contracts.
- `full-creative-v2`: complete v2 project contract selected by `creative-manifest.json`.

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

The module entry point is equivalent: replace `cine-skills` with `python -m cine_skills`. Validation checks structure, schemas, identifiers, and declared references; it does not inspect media or grant creative, legal, accessibility, or delivery approval. The checked-in Ninel v2 demonstration intentionally remains `awaiting-media`. Run `make check` before a handoff or pull request.

## Specialist invocations

```text
Use $scene-beat-analyzer to derive evidenced dramatic beats.
Use $scene-director to select one coherent directing concept.
Use $visual-language-designer to define a repeatable visual grammar.
Use $blocking-designer to stage the scene on the supplied floor plan.
Use $camera-movement-designer to remove unmotivated moves.
Use $shot-list-builder to convert approved plans into coverage.
Use $lighting-designer to plan motivated light per shot.
Use $sound-designer to plan production sound and dramatic cues.
Use $storyboard-designer to produce drawable textual panels.
Use $production-breakdown to identify department needs.
Use $continuity-supervisor to track states and resets.
```

## Migrating an older package

Follow [the v0.1 to v1.0 guide](migration-v0.1-to-v1.0.md) for a scene package, then [the v1 to v2 guide](migration-v1-to-v2.md) for layered project structure. Keep valid legacy artifacts unchanged, create and review each new layer, carry stable IDs, and never invent creative content merely to satisfy a validator.

## Troubleshooting discovery

- Confirm each skill is at `.agents/skills/<name>/SKILL.md`.
- Confirm the frontmatter `name` exactly matches the directory.
- Run `make validate` for actionable packaging errors.
- Start a fresh Codex session after changes.
- Prefer a real directory or a symlink to the whole skill directory; do not symlink only `SKILL.md`.

# Starting Cine Agent Skills 0.3 in Codex

## Open and verify

Open the repository root, not `.agents/`. Start a new session after adding or changing skills because discovery occurs when the session initializes.

```bash
make setup
make check
make validate-scene-core-example
make validate-scene-full-example
make validate-story-example
make validate-production-example
make validate-post-example
make validate-project-example
```

In an already managed environment:

```bash
python -m pip install -e '.[dev]'
make PYTHON=python check
```

## First inspection

```text
Read AGENTS.md, README.md, docs/versioning.md, and docs/superpowers/plans/2026-09-17-film-os-modernization.md. Run make check and every neutral example target. Summarize the layered architecture, active profiles, offline boundary, optional runtime status, and verified evidence without changing files.
```

## Full production exercise

```text
Use $full-creative-pipeline on examples/ninel-scene-brief.md.
Create a full-creative planning project under projects/ninel/.
Run story → screenplay → scene → production → post in dependency order, validate with the full-creative profile, and report repairs, assumptions, unresolved questions, and whether media is still awaiting evidence.
```

Compare structure and contracts with `examples/scene-full/scenes/S01/`; do not copy its creative decisions into a different scene.

## Profiles and commands

- `scene-core`: compatible minimal scene package.
- `scene-full`: complete scene package with manifest.
- `auto`: selects full when a manifest is present, otherwise core.
- `story`, `production`, and `post`: independent layer contracts.
- `full-creative`: complete project contract selected by `creative-manifest.json`.

```bash
cine-skills --version
cine-skills validate .
cine-skills validate-artifact shot-list examples/scene-core/scenes/S01/shot-list.json
cine-skills validate-package examples/scene-core/scenes/S01 --profile scene-core
cine-skills validate-package examples/scene-full/scenes/S01 --profile scene-full --format json
cine-skills validate-story examples/ninel/story --project-format series --format json
cine-skills validate-production examples/ninel/production --root . --production-mode animation --production-mode ai --allow-nested --format json
cine-skills validate-post examples/ninel/post --root . --format json
cine-skills validate-project examples/ninel --profile full-creative --format json
```

The active system version is `0.3.0` in all machine-readable contracts. Generation-named flags are rejected rather than treated as aliases. Validation checks structure, schemas, identifiers, and declared references; it does not inspect media or grant creative, legal, accessibility, or delivery approval.

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

## Older packages

Follow `docs/versioning.md` and the explicit migration guide for older data. Keep the source package unchanged, write to a new output directory, preserve IDs and approvals, and validate the result before handoff. Never invent creative content merely to satisfy a validator.

## Troubleshooting discovery

- Confirm each skill is at `.agents/skills/<name>/SKILL.md`.
- Confirm frontmatter `name` exactly matches the directory.
- Run `make validate` for actionable packaging errors.
- Start a fresh Codex session after changes.
- Prefer a real directory or a symlink to the whole skill directory; do not symlink only `SKILL.md`.

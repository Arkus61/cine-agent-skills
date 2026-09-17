# Repository Instructions

## Mission

Build a portable, source-conscious library of Agent Skills for film story development and creative-production planning. Teach repeatable decisions, not fashionable prompts. Preserve legacy scene preproduction contracts.

## Required workflow

1. Read `docs/superpowers/specs/2026-08-05-cine-agent-skills-v1.0-design.md` before architectural changes.
   For v2 work also read the August 6 v2 design and `docs/superpowers/specs/2026-09-13-cine-direction.md`. The active recovery plan is `docs/superpowers/plans/2026-09-13-cine-rebaseline.md`.
2. Use test-first development for Python behavior and schema contracts.
3. Run `make check`, all explicit example targets, `make release-archive`, and `git diff --check` before claiming a release handoff.
4. Keep project-local skills in `.agents/skills`.
5. Keep `SKILL.md` concise. Put detailed theory in `references/` and output skeletons in `assets/`.
6. Preserve stable scene, beat, movement, shot, panel, breakdown-item, and continuity-item IDs.
7. Separate script facts, assumptions, uncertainties, and creative proposals.
8. Do not copy course text, screenplay pages, proprietary breakdowns, or other copyrighted teaching material. Paraphrase general principles and register sources in `docs/source-register.md`.

## Skill frontmatter

Use only:

```yaml
---
name: lowercase-hyphenated-name
description: What the skill does and when it should activate.
---
```

The directory name and `name` must match. Descriptions must not exceed 1024 characters.

## Commands

- `make test` runs pytest.
- `make validate` validates skill and schema packaging.
- `make check` runs both.
- `make validate-core-example` validates backward compatibility explicitly.
- `make validate-full-example` validates the canonical full-v1 package with a JSON report.
- `make validate-v2-example` validates the canonical full-creative-v2 project with a JSON report.
- `make validate-story-example`, `make validate-production-example`, and `make validate-post-example` validate the v2 layer boundaries directly.
- `make release-archive` builds a deterministic tracked-file ZIP under `dist/`.

## Preserved v0.1/v1 boundary

The preserved contracts end at validated scene-level preproduction planning packages. Do not change their schemas, filenames, IDs, or profile behavior.

Maintain both profiles: unchanged v0.1 packages validate as `core-v0.1`; manifest-bearing thirteen-file packages validate as `full-v1`.

## Version 2.0 planning boundary

The v2 release adds story, production, and post planning plus deterministic project validation. It does not add direct media execution: no generated media, vendor API, NLE/DCC control, Blender adapter, MCP server, publishing, or producer operations. Blender has a separate pilot design and is a future extension. A valid project can remain `awaiting-media` or `planned`; schema validity is not creative approval, freshness, or delivery QC.

Read the current release note in `docs/CONTINUE.md` and the direction amendment before changing integration behavior. Run `validate-project examples/ninel-v2 --profile full-creative-v2 --format json` explicitly. A successful test count, skill inventory, or schema check is not proof of creative approval, source freshness, or media readiness.

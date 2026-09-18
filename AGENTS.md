# Repository Instructions

## Mission

Build a portable, source-conscious library of Agent Skills for film story development and creative-production planning. Teach repeatable decisions, not fashionable prompts. The active system contract is `0.3.0`; package completeness is expressed by functional profiles, not numbered generations.

## Required workflow

1. Read the current active plan in `docs/superpowers/plans/2026-09-17-film-os-modernization.md` and the versioning policy in `docs/versioning.md` before architectural changes.
2. Use test-first development for Python behavior and schema contracts.
3. Run `make check`, every neutral example target, `make release-archive`, and `git diff --check` before claiming a handoff.
4. Keep project-local skills in `.agents/skills`.
5. Keep `SKILL.md` concise. Put detailed theory in `references/` and output skeletons in `assets/`.
6. Preserve stable scene, beat, movement, shot, panel, breakdown-item, and continuity-item IDs.
7. Separate script facts, assumptions, uncertainties, and creative proposals.
8. Do not copy course text, screenplay pages, proprietary breakdowns, or other copyrighted teaching material. Paraphrase general principles and register sources in `docs/source-register.md`.

## Version and profile policy

- `[project].version` in `pyproject.toml` is the only editable version source. The current value is `0.3.0` (short label `0.3`).
- `scripts/sync_versions.py --check` and `make check-version` guard derived schemas, templates, evaluations, examples, manifests, and system metadata.
- Active profile names are `auto`, `scene-core`, `scene-full`, `story`, `production`, `post`, and `full-creative`.
- Generation-named profile flags such as `core-v0.1`, `full-v1`, and `full-creative-v2` are historical names, not hidden CLI aliases. They must fail with exit code `2` and point to the neutral profile.
- Validation is read-only. Older files are handled only by the explicit, non-destructive migration flow; validators never rewrite user projects.
- Historical specifications, migration records, reports, and changelog entries retain their original numbers. They are evidence, not current instructions.

## Contracts and evidence

Keep the 37-skill catalog, 35 subject schemas, stable identifiers, reference checks, approval boundaries, and explicit states such as `planned`, `awaiting-media`, and `valid`. A schema-valid artifact is not creative approval, freshness, media inspection, rights clearance, or delivery QC.

The optional runtime is offline-first and must not become a required dependency of the planning validator. Reuse existing community components for graphs, caches, JSON patches, LangGraph, and standard MCP. The user's already configured Blender MCP is authoritative when available: do not implement a custom Blender server, addon, socket client, connector, or Film OS ↔ Blender protocol. If the server or its capabilities are unavailable, record the gap instead of inventing evidence.

Run the canonical gates explicitly:

```bash
make check
make validate-scene-core-example
make validate-scene-full-example
make validate-story-example
make validate-production-example
make validate-post-example
make validate-project-example
make release-archive
```

Read `docs/CONTINUE.md` for the latest verified checkpoint. A successful test count, skill inventory, archive, or schema check is not proof of creative approval, source freshness, or media readiness.

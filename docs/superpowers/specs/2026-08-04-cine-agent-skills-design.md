# Cine Agent Skills: Design Specification

## Objective

Create a portable, open repository of film-production Agent Skills that Codex and other compatible agents can discover and execute. The first release covers scene preproduction from dramatic analysis through a production-ready shot list.

## Product boundary

Version 0.1 intentionally excludes direct video generation, DaVinci Resolve automation, Blender control, budgeting, scheduling, casting, and production management. Those are later integrations. The first release must be useful without external APIs.

## Canonical skill location

Project-local skills live under `.agents/skills/<skill-name>/`. This is the canonical source, not a generated mirror. Each skill contains:

- `SKILL.md` with only `name` and `description` frontmatter.
- `agents/openai.yaml` with Codex UI metadata.
- Optional `references/` for domain knowledge loaded on demand.
- Optional `assets/` for output templates.

## Initial skill set

1. `scene-beat-analyzer`
2. `scene-director`
3. `blocking-designer`
4. `camera-movement-designer`
5. `shot-list-builder`
6. `scene-preproduction-pipeline` as the orchestrator.

## Artifact contracts

Skills exchange Markdown or JSON artifacts with explicit schemas:

- `scene-beats.schema.json`
- `directing-plan.schema.json`
- `blocking-plan.schema.json`
- `camera-movement-plan.schema.json`
- `shot-list.schema.json`

All artifacts identify the source scene, declare assumptions, and preserve stable IDs across the pipeline.

## Quality rules

- Do not invent production facts silently.
- Separate observed script facts from creative proposals.
- Explain the dramatic purpose of every major visual choice.
- Preserve screen direction, eyelines, geography, and continuity unless a deliberate break is documented.
- Prefer motivated camera movement over decorative movement.
- Keep `SKILL.md` concise and move detailed theory to references.
- Paraphrase general film knowledge; do not copy course text or copyrighted examples.

## Tooling

A Python validator checks skill frontmatter, directory/name agreement, OpenAI metadata, local references, and JSON schemas. Pytest provides regression coverage. GitHub Actions runs validation and tests.

## Success criteria

- Codex discovers all six skills from a fresh repository session.
- `python -m cine_skills validate .` exits successfully.
- All tests pass.
- A user can feed one scene brief into the orchestrator and receive the five structured artifacts in sequence.

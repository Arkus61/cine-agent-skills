# Cine Agent Skills v0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Codex-ready repository containing six film-preproduction Agent Skills, artifact schemas, validation tooling, tests, and a worked example.

**Architecture:** Store portable skills directly in `.agents/skills`. Keep domain procedures in lean `SKILL.md` files and detailed knowledge in lazy-loaded references. Use a small Python validator and JSON Schema contracts to make the repository mechanically checkable.

**Tech Stack:** Markdown, YAML, JSON Schema Draft 2020-12, Python 3.11+, PyYAML, jsonschema, pytest, GitHub Actions.

## Global Constraints

- Skill names use lowercase letters, digits, and single hyphens only.
- `SKILL.md` frontmatter contains only `name` and `description`.
- Descriptions are 1-1024 characters and state both capability and activation context.
- Project-local skills live in `.agents/skills`.
- No external API is required for v0.1.
- All generated production artifacts preserve stable scene and beat identifiers.

---

### Task 1: Repository validation core

**Files:**
- Create: `src/cine_skills/validator.py`
- Create: `src/cine_skills/__main__.py`
- Create: `src/cine_skills/__init__.py`
- Test: `tests/test_validator.py`

**Interfaces:**
- Produces: `validate_repository(root: Path) -> list[str]`
- Produces: CLI `python -m cine_skills validate <root>`

- [ ] Write failing tests for missing skills, invalid names, invalid YAML, stale OpenAI metadata, and broken relative references.
- [ ] Run tests and verify failures are caused by the missing validator.
- [ ] Implement minimal validator behavior.
- [ ] Run tests and verify they pass.
- [ ] Commit the validator.

### Task 2: Artifact schema validation

**Files:**
- Create: `schemas/*.schema.json`
- Create: `src/cine_skills/artifacts.py`
- Test: `tests/test_artifacts.py`

**Interfaces:**
- Consumes: JSON-compatible Python mappings.
- Produces: `validate_artifact(schema_name: str, payload: Mapping[str, Any], root: Path) -> list[str]`.

- [ ] Write failing tests for one valid and one invalid shot-list payload.
- [ ] Run tests and verify the schema files or function are missing.
- [ ] Implement the five schemas and validation function.
- [ ] Run all tests.
- [ ] Commit artifact contracts.

### Task 3: Six Codex-discoverable skills

**Files:**
- Create: `.agents/skills/<name>/SKILL.md`
- Create: `.agents/skills/<name>/agents/openai.yaml`
- Create: `.agents/skills/<name>/references/*.md`
- Create: `.agents/skills/<name>/assets/*.md`
- Test: `tests/test_skill_catalog.py`

**Interfaces:**
- Consumes: scene text or preceding artifact.
- Produces: one named artifact matching the corresponding schema.

- [ ] Write catalog tests asserting the six exact skills and required metadata.
- [ ] Run tests and verify the catalog is missing.
- [ ] Implement the skills and resources.
- [ ] Run all tests and repository validation.
- [ ] Commit the catalog.

### Task 4: Developer experience and example

**Files:**
- Create: `README.md`
- Create: `AGENTS.md`
- Create: `CONTRIBUTING.md`
- Create: `examples/ninel-scene-brief.md`
- Create: `examples/ninel-pipeline-output.json`
- Create: `.github/workflows/ci.yml`
- Create: `Makefile`
- Create: `pyproject.toml`

**Interfaces:**
- Produces: repeatable commands `make test`, `make validate`, and `make check`.

- [ ] Add a smoke test for the example artifact.
- [ ] Run it and verify it fails before the example exists.
- [ ] Implement docs, example, packaging, and CI.
- [ ] Run `make check`.
- [ ] Commit developer experience files.

### Task 5: Release verification

- [ ] Run `python -m cine_skills validate .`.
- [ ] Run `pytest -q`.
- [ ] Inspect `git status --short`.
- [ ] Create `cine-agent-skills-v0.1.0.zip` without caches or `.git`.
- [ ] Record checksums and final tree summary.

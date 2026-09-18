# Cine Agent Skills v0.1 Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the approved six-skill v0.1 release with deterministic artifact and scene-package validation, a canonical Ninel package, end-to-end tests, and reproducible release documentation.

**Architecture:** Keep skills as declarative Agent Skills under `.agents/skills` and keep execution free of external APIs. Extend the small Python package with file-level and package-level validation; the CLI is a thin adapter over those functions. Treat JSON schemas as the structural contract and Python package checks as the cross-artifact contract.

**Tech Stack:** Python 3.11+, Markdown, YAML, JSON Schema Draft 2020-12, PyYAML, jsonschema, pytest, GitHub Actions.

## Global Constraints

- Keep exactly the six skills named in the approved design.
- Keep `SKILL.md` frontmatter limited to `name` and `description`.
- Preserve stable scene, beat, movement, and shot identifiers.
- Keep v0.1 usable without external APIs.
- Do not add storyboarding, media generation, postproduction automation, scheduling, budgeting, casting, MCP, or a web UI.
- Derive expected test values independently from production helpers.
- Add Python behavior only after a test fails for the intended missing behavior.

---

### Task 1: Artifact-file validation CLI

**Files:**
- Modify: `src/cine_skills/artifacts.py`
- Modify: `src/cine_skills/__main__.py`
- Create: `tests/test_cli.py`
- Modify: `tests/test_artifacts.py`

**Interfaces:**
- Consumes: schema name, JSON path, repository root.
- Produces: `load_json_object(path: Path) -> tuple[Mapping[str, Any] | None, list[str]]`.
- Produces: `validate_artifact_file(schema_name: str, json_path: Path, root: Path) -> list[str]`.
- Produces: CLI `python -m cine_skills validate-artifact <schema-name> <json-file> [--root ROOT]`.

- [ ] **Step 1: Write failing loader and CLI tests**

```python
def test_validate_artifact_file_reports_invalid_json(tmp_path, repository_root):
    path = tmp_path / "shot-list.json"
    path.write_text("{broken", encoding="utf-8")
    errors = validate_artifact_file("shot-list", path, repository_root)
    assert errors and "invalid JSON" in errors[0]

def test_validate_artifact_cli_accepts_valid_file(repository_root):
    result = run_cli(repository_root, "validate-artifact", "shot-list", "examples/ninel/scenes/S01/shot-list.json")
    assert result.returncode == 0
```

- [ ] **Step 2: Run focused tests and verify RED**

Run: `python -m pytest tests/test_artifacts.py tests/test_cli.py -q`

Expected: collection or assertion failure because `validate_artifact_file` and the CLI subcommand do not exist.

- [ ] **Step 3: Implement the smallest file loader and CLI adapter**

Parse UTF-8 JSON, require a top-level object, call the existing `validate_artifact`, print each error with an `ERROR:` prefix, and print one success line.

- [ ] **Step 4: Run focused and full tests**

Run: `python -m pytest tests/test_artifacts.py tests/test_cli.py -q`

Expected: all focused tests pass.

- [ ] **Step 5: Commit the artifact CLI**

```bash
git add src/cine_skills/artifacts.py src/cine_skills/__main__.py tests/test_artifacts.py tests/test_cli.py
git commit -m "feat: add artifact validation command"
```

### Task 2: Cross-artifact scene-package validator

**Files:**
- Create: `src/cine_skills/package.py`
- Modify: `src/cine_skills/__main__.py`
- Create: `tests/test_package.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Consumes: a scene-package directory and repository root.
- Produces: `validate_scene_package(package_dir: Path, root: Path) -> list[str]`.
- Produces: CLI `python -m cine_skills validate-package <package-dir> [--root ROOT]`.

- [ ] **Step 1: Write failing package-contract tests**

Create literal fixtures for: valid package, missing file, mismatched `scene_id`, duplicate ID, wrong ID prefix, dangling beat reference, and uncovered beat.

```python
def test_package_rejects_dangling_shot_beat_reference(package_dir, repository_root):
    rewrite_json(package_dir / "shot-list.json", lambda value: value["shots"][0].update(beat_ids=["S01-B99"]))
    errors = validate_scene_package(package_dir, repository_root)
    assert any("S01-B99" in error and "unknown beat" in error for error in errors)
```

- [ ] **Step 2: Run package tests and verify RED**

Run: `python -m pytest tests/test_package.py -q`

Expected: failure because `cine_skills.package` does not exist.

- [ ] **Step 3: Implement schema-first package validation**

Load the five fixed filenames, validate each against its schema, stop cross-checking only the malformed artifact, and return sorted diagnostics. Check declared IDs and references without rewriting any artifact.

- [ ] **Step 4: Add the CLI subcommand and test exit codes**

The valid fixture returns `0`; inconsistent and missing packages return `1` with file-specific diagnostics.

- [ ] **Step 5: Run focused and full tests**

Run: `python -m pytest tests/test_package.py tests/test_cli.py -q`

Expected: all focused tests pass.

- [ ] **Step 6: Commit package validation**

```bash
git add src/cine_skills/package.py src/cine_skills/__main__.py tests/test_package.py tests/test_cli.py
git commit -m "feat: validate complete scene packages"
```

### Task 3: Canonical Ninel scene package

**Files:**
- Create: `examples/ninel/scenes/S01/source-scene.md`
- Create: `examples/ninel/scenes/S01/scene-beats.json`
- Create: `examples/ninel/scenes/S01/directing-plan.json`
- Create: `examples/ninel/scenes/S01/blocking-plan.json`
- Create: `examples/ninel/scenes/S01/camera-movement-plan.json`
- Create: `examples/ninel/scenes/S01/shot-list.json`
- Modify: `tests/test_example.py`

**Interfaces:**
- Consumes: the approved Ninel brief and aggregate output.
- Produces: a package that the real package validator accepts.

- [ ] **Step 1: Write failing end-to-end tests**

```python
def test_ninel_scene_package_is_valid(repository_root):
    package = repository_root / "examples" / "ninel" / "scenes" / "S01"
    assert validate_scene_package(package, repository_root) == []
```

Add a second test that loads each split JSON file and compares it with the corresponding literal key in `ninel-pipeline-output.json`.

- [ ] **Step 2: Run example tests and verify RED**

Run: `python -m pytest tests/test_example.py -q`

Expected: failure because the canonical package directory is absent.

- [ ] **Step 3: Create the six package files**

Copy the source brief and split the five approved artifacts without changing creative content or identifiers.

- [ ] **Step 4: Validate the real package**

Run: `PYTHONPATH=src python -m cine_skills validate-package examples/ninel/scenes/S01`

Expected: `Scene package validation passed.`

- [ ] **Step 5: Commit the canonical example**

```bash
git add examples/ninel tests/test_example.py
git commit -m "test: add canonical Ninel scene package"
```

### Task 4: Schema and repository hardening

**Files:**
- Modify: `schemas/scene-beats.schema.json`
- Modify: `schemas/blocking-plan.schema.json`
- Modify: `schemas/camera-movement-plan.schema.json`
- Modify: `schemas/shot-list.schema.json`
- Modify: `src/cine_skills/validator.py`
- Modify: `tests/test_validator.py`
- Modify: `tests/test_artifacts.py`

**Interfaces:**
- Produces: repository diagnostics for invalid Draft 2020-12 schemas.
- Preserves: zero-move blocking and camera plans for intentionally static scenes.

- [ ] **Step 1: Write failing schema-integrity and identifier tests**

Test malformed schema syntax, invalid schema keywords, empty referenced IDs, and malformed move IDs. Assert behavior, not source text.

- [ ] **Step 2: Run tests and verify RED**

Run: `python -m pytest tests/test_validator.py tests/test_artifacts.py -q`

Expected: failures because repository validation does not check schema integrity and referenced IDs are under-constrained.

- [ ] **Step 3: Implement schema checks and tighten identifier fields**

Use `Draft202012Validator.check_schema` for every `schemas/*.schema.json`. Apply stable ID patterns to beat references, movement IDs, and shot references while keeping arrays of moves optional.

- [ ] **Step 4: Run all validation tests**

Run: `python -m pytest tests/test_validator.py tests/test_artifacts.py tests/test_package.py -q`

Expected: all focused tests pass.

- [ ] **Step 5: Commit contract hardening**

```bash
git add schemas src/cine_skills/validator.py tests/test_validator.py tests/test_artifacts.py
git commit -m "feat: harden v0.1 artifact contracts"
```

### Task 5: Pipeline skill evaluation and documentation

**Files:**
- Modify: `.agents/skills/scene-preproduction-pipeline/SKILL.md`
- Modify: `.agents/skills/scene-preproduction-pipeline/references/pipeline-contract.md`
- Modify: `.agents/skills/scene-preproduction-pipeline/assets/scene-package-checklist.md`
- Create: `evals/scene-preproduction-pipeline.json`
- Modify: `README.md`
- Modify: `docs/codex-start.md`
- Modify: `schemas/README.md`
- Modify: `CONTRIBUTING.md`
- Modify: `Makefile`

**Interfaces:**
- Consumes: one scene brief.
- Produces: the canonical six-file scene package and a validation report.

- [ ] **Step 1: Capture a no-skill baseline on a representative scene**

Use a fresh agent context without the pipeline skill and record omissions against the package contract.

- [ ] **Step 2: Add three observable evaluations**

Cover dialogue pressure, action geography, and intentional ambiguity. Each case requires stable IDs, labeled assumptions, five artifacts, resolved references, and complete beat coverage.

- [ ] **Step 3: Update the pipeline instructions minimally**

Add the canonical package command, validation-repair loop, and rule that repairs regenerate only dependent artifacts. Keep detailed checks in the existing reference and asset.

- [ ] **Step 4: Forward-test the updated skill**

Use a fresh agent context with `$scene-preproduction-pipeline`; compare observable output behavior with the baseline and evaluation rubric.

- [ ] **Step 5: Update human documentation and setup commands**

Document `python -m pip install -e '.[dev]'`, all three CLI commands, the canonical example, package layout, and `make check`. Add `make setup` as the single development bootstrap.

- [ ] **Step 6: Validate and commit the skill before moving on**

Run: `PYTHONPATH=src python -m cine_skills validate .`

```bash
git add .agents/skills/scene-preproduction-pipeline evals README.md docs/codex-start.md schemas/README.md CONTRIBUTING.md Makefile
git commit -m "docs: complete the v0.1 pipeline workflow"
```

### Task 6: Release verification and archive

**Files:**
- Modify if needed: `.gitignore`
- Create outside repository: `cine-agent-skills-v0.1.0-full.zip`

**Interfaces:**
- Produces: a clean, installable release archive.

- [ ] **Step 1: Install development dependencies**

Run: `python -m pip install -e '.[dev]'`

- [ ] **Step 2: Run fresh full verification**

Run: `make check`

Expected: repository validation passes and the complete pytest suite reports zero failures.

- [ ] **Step 3: Validate the canonical package explicitly**

Run: `PYTHONPATH=src python -m cine_skills validate-package examples/ninel/scenes/S01`

Expected: package validation passes.

- [ ] **Step 4: Inspect repository state and release contents**

Run: `git status --short` and inspect the archive manifest. Exclude `.git`, `.pytest_cache`, `__pycache__`, virtual environments, build output, and editable-install metadata.

- [ ] **Step 5: Build and checksum the release archive**

Create `cine-agent-skills-v0.1.0-full.zip` and record its SHA-256 digest.

- [ ] **Step 6: Save the archive and hand off the verified commands and results**


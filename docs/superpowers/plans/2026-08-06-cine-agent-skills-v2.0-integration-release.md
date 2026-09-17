# Cine Agent Skills v2.0 Integration and Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate story, preserved scene preproduction, creative production, and postproduction into `full-creative-v2`, prove every supported profile, complete the Ninel pilot example, update documentation, and build the verified v2.0.0 release archive.

**Architecture:** A top-level creative manifest selects format, production modes, units, and relative layer paths. `project_package.py` validates manifests and layers in dependency order, carries a stable `ProjectIndex`, and invalidates only downstream references. `full-creative-pipeline` orchestrates existing specialists without duplicating their theory.

**Tech Stack:** Python 3.11+, Markdown, YAML, Fountain, JSON Schema Draft 2020-12, jsonschema, pytest, Make, Git, ZIP/SHA-256 tooling.

## Global Constraints

- Complete foundation, story, creative-production, and postproduction plans first.
- Release version is exactly `2.0.0`; new artifact schema version is exactly `"2.0"`.
- Preserve `core-v0.1`, `full-v1`, existing v1 examples, commands, schemas, filenames, and accepted payloads.
- The final catalog contains exactly thirty-seven project-local skills: twelve preserved and twenty-five new.
- Runtime remains offline-capable and free of paid API dependencies.
- English-only repository content and examples.
- No generated media, vendor API client, NLE/DCC control, producer operations, legal clearance, database, MCP, hosted service, or web UI.
- A plan may be valid while media is absent, but no unobserved approval, measurement, or QC pass is allowed.
- Release claims require fresh complete verification from a clean tracked-only copy.

---

## File map

- `src/cine_skills/project_package.py` — full project loading, index construction, layer orchestration, cross-layer checks, and manifest validation.
- `tests/v2_profile_fixtures.py` — literal temporary packages for all format/mode combinations under test.
- `tests/test_project_package.py` — project validation, cross-layer references, invalidation, and failure boundaries.
- `.agents/skills/full-creative-pipeline/` — full orchestrator bundle.
- `evals/full-creative-pipeline.json` — observable full-system behavior.
- `examples/ninel-v2/` — season story plus one complete pilot through post planning.
- `docs/migration-v1-to-v2.md` — additive migration without fabricated creative work.
- `scripts/build_release_archive.py` — deterministic tracked-file archive builder.
- `README.md`, `AGENTS.md`, `docs/codex-start.md`, `schemas/README.md`, `docs/source-register.md`, `CHANGELOG.md`, `Makefile`, `pyproject.toml`, `src/cine_skills/__init__.py` — release-facing updates.

### Task 1: Full Project Validator and CLI

**Files:**
- Create: `src/cine_skills/project_package.py`
- Create: `tests/v2_profile_fixtures.py`
- Create: `tests/test_project_package.py`
- Modify: `src/cine_skills/__main__.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Consumes: `creative-manifest.json`, `validate_story_package`, `validate_script_package`, `validate_scene_package`, `validate_production_package`, `validate_post_package`, and `ProjectIndex`.
- Produces: `validate_project(project_dir: Path, root: Path, profile: str = "full-creative-v2") -> list[str]`.
- Produces: `build_project_index(project_dir: Path, root: Path) -> tuple[ProjectIndex | None, list[str]]`.
- Adds CLI: `validate-project PATH --profile full-creative-v2 --format text|json`.

- [ ] **Step 1: Write failing full-project tests**

Create literal minimal project fixtures independent of production registries. Assert:

```python
def test_minimal_full_creative_project_validates(tmp_path, repository_root):
    project = write_minimal_v2_project(tmp_path / "project")
    assert validate_project(project, repository_root) == []


def test_project_rejects_cross_project_character_reference(tmp_path, repository_root):
    project = write_minimal_v2_project(tmp_path / "project")
    rewrite_json(
        project / "production/character-look-bible.json",
        lambda value: value["characters"][0].update({"character_id": "OTHER-CH001"}),
    )
    assert any("unknown character OTHER-CH001" in error for error in validate_project(project, repository_root))
```

Also test exact root membership, relative path traversal, duplicate units, missing layer, unit/story mismatch, scene not declared by screenplay metadata, shot not declared by v1 package, media/edit/post dangling references, invalid layer manifest, invalid creative manifest, unreadable directories, symlink loops, invalid UTF-8, deep JSON, and stable sorted diagnostics.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_project_package.py tests/test_cli.py -k project -q`

Expected: failures for missing module and CLI command.

- [ ] **Step 3: Implement schema-first full validation**

Load and validate `creative-manifest.json` first. Resolve only safe relative paths inside the project root. Validate layers in order: story, scripts, v1 scenes, production, post. Merge valid upstream identifiers into `ProjectIndex` and skip dependent cross-checks when the declaring artifact is invalid. Validate the creative manifest inventory and produce sorted errors.

- [ ] **Step 4: Implement CLI JSON and exit behavior**

Successful JSON is exactly:

```json
{"command":"validate-project","errors":[],"profile":"full-creative-v2","valid":true}
```

Unknown profiles exit `2`; validation failures exit `1`; success exits `0`; malformed input never prints `Traceback`.

- [ ] **Step 5: Run integration and compatibility tests**

Run: `.venv/bin/python -m pytest tests/test_project_package.py tests/test_cli.py tests/test_package.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/cine_skills/project_package.py src/cine_skills/__main__.py tests/v2_profile_fixtures.py tests/test_project_package.py tests/test_cli.py
git commit -m "feat: validate full v2 creative projects"
```

### Task 2: Full Creative Pipeline

**Files:**
- Create: `.agents/skills/full-creative-pipeline/SKILL.md`
- Create: `.agents/skills/full-creative-pipeline/agents/openai.yaml`
- Create: `.agents/skills/full-creative-pipeline/assets/full-creative-checklist.md`
- Create: `.agents/skills/full-creative-pipeline/references/full-creative-contract.md`
- Create: `evals/full-creative-pipeline.json`
- Modify: `tests/test_skill_catalog.py`

**Interfaces:**
- Consumes: creative brief plus optional existing story, scene, production, media, or post artifacts.
- Produces: exact format/mode-selected project layout, validation report, invalidation report, and handoff state `ready-for-preproduction`, `awaiting-media`, `ready-for-master-review`, or `blocked`.

- [ ] **Step 1: Run RED baseline**

Ask a fresh agent to take the Ninel concept through season story, pilot script, scene preproduction, hybrid production instructions, and post plan without access to generated media. Record missing packages, wrong dependency order, duplicate theory, invented media approval, absent validation, or false completion.

- [ ] **Step 2: Write failing catalog and evaluation assertions**

Assert all four layer profiles, the preserved `full-v1` scene call, exact dependency order, conditional mode artifacts, earliest-invalid repair, downstream-only regeneration, media evidence gate, `validate-project --profile full-creative-v2 --format json`, and final handoff state.

- [ ] **Step 3: Implement the orchestrator**

Keep `SKILL.md` under 500 lines. Route to `story-development-pipeline`, each required `scene-preproduction-pipeline`, `creative-production-pipeline`, and `postproduction-pipeline`. Never reproduce specialist theory. Revalidate after each repair. Preserve valid unaffected artifacts and report assumptions/unresolved questions.

- [ ] **Step 4: Forward-test**

Run fresh-context forward tests on:

1. series + animation + AI with no media (`awaiting-media`);
2. documentary + live-action with incomplete media (`blocked` or `awaiting-media`);
3. commercial + hybrid with supplied review metadata (`ready-for-master-review` only if every evidence gate resolves).

- [ ] **Step 5: Commit**

```bash
git add .agents/skills/full-creative-pipeline evals/full-creative-pipeline.json tests/test_skill_catalog.py
git commit -m "feat: orchestrate full v2 creative workflow"
```

### Task 3: Lock the Exact Thirty-Seven-Skill Catalog

**Files:**
- Modify: `tests/test_skill_catalog.py`
- Modify: `tests/test_validator.py`

**Interfaces:**
- Produces: exact catalog/bundle/metadata/link/template/evaluation/schema mapping gate for all thirty-seven skills.

- [ ] **Step 1: Replace the v1 exact-set test with literal v2 sets**

Define `PRESERVED_V1_SKILLS` with the existing twelve names and `V2_SKILLS` with the approved twenty-five names. Assert `actual == PRESERVED_V1_SKILLS | V2_SKILLS` and lengths `12`, `25`, and `37` explicitly.

- [ ] **Step 2: Add complete bundle parameterization**

Use a literal mapping from every new specialist to its schema, template, reference files, and evaluation file. For orchestrators, use their checklist/contract instead of schema/template. Assert every `agents/openai.yaml` has non-empty display name, 25–64 character short description, and a default prompt containing `$<skill-name>`.

- [ ] **Step 3: Verify RED or identify already-covered behavior**

Run: `.venv/bin/python -m pytest tests/test_skill_catalog.py -q`

Expected: any incomplete bundle fails with exact missing path. If it passes, confirm the test would fail by temporarily adding a fake literal name, observe failure, and restore the test.

- [ ] **Step 4: Fix only demonstrated catalog gaps and validate**

Run: `.venv/bin/python -m pytest tests/test_skill_catalog.py tests/test_validator.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_skill_catalog.py tests/test_validator.py .agents/skills evals schemas
git commit -m "test: lock the v2 skill catalog"
```

### Task 4: Cover Every Format and Production Mode

**Files:**
- Modify: `tests/v2_profile_fixtures.py`
- Modify: `tests/test_project_contracts.py`
- Modify: `tests/test_project_package.py`

**Interfaces:**
- Produces: compact literal fixtures for all seven formats and all four modes without duplicating the full Ninel example.

- [ ] **Step 1: Add the profile matrix test**

```python
@pytest.mark.parametrize(
    "project_format",
    ["feature", "short", "series", "documentary", "commercial", "music-video", "short-form"],
)
@pytest.mark.parametrize(
    "production_modes",
    [("live-action",), ("animation",), ("ai",), ("hybrid",)],
)
def test_all_v2_format_mode_profiles_validate(
    tmp_path, repository_root, project_format, production_modes
):
    project = write_minimal_v2_project(
        tmp_path / "project", project_format=project_format, production_modes=production_modes
    )
    assert validate_project(project, repository_root) == []
```

- [ ] **Step 2: Verify failures reveal conditional gaps**

Run: `.venv/bin/python -m pytest tests/test_project_contracts.py tests/test_project_package.py -q`

Expected before fixture/validator completion: series season membership and animation/AI conditional cases fail for their intended missing artifacts.

- [ ] **Step 3: Complete literal fixtures and minimal routing fixes**

Series includes `season-arc.json`; other formats do not. Animation/hybrid include animation; AI/hybrid include media prompts. Documentary facts remain claims with provenance. Commercial/music-video/short-form unit outlines use format-specific structure fields already permitted by schema.

- [ ] **Step 4: Run the complete matrix and commit**

```bash
.venv/bin/python -m pytest tests/test_project_contracts.py tests/test_project_package.py -q
git add tests/v2_profile_fixtures.py tests/test_project_contracts.py tests/test_project_package.py src/cine_skills
git commit -m "test: cover every v2 project profile"
```

### Task 5: Build the Canonical Ninel v2 Example

**Files:**
- Create: `examples/ninel-v2/creative-manifest.json`
- Create: `examples/ninel-v2/story/*`
- Create: `examples/ninel-v2/scripts/NINEL-E01/*`
- Create: `examples/ninel-v2/scripts/NINEL-E01/scenes/NINEL-E01-S01/*`
- Create: `examples/ninel-v2/production/*`
- Create: `examples/ninel-v2/post/*`
- Modify: `tests/test_example.py`

**Interfaces:**
- Produces: canonical `series + animation + ai` example with season story and one complete pilot unit.
- Reuses: v1 scene artifact semantics with scene ID `NINEL-E01-S01`.

- [ ] **Step 1: Write the failing example test**

```python
def test_ninel_v2_example_is_a_valid_full_creative_project(repository_root):
    errors = validate_project(repository_root / "examples/ninel-v2", repository_root)
    assert errors == []
```

Also assert project format `series`, production modes exactly `animation` and `ai`, season has at least three episodes, pilot has at least three story events, one Fountain script, one complete scene package, shot coverage across production and post, and media review status `awaiting-media` rather than approved.

- [ ] **Step 2: Run example test and verify RED**

Run: `.venv/bin/python -m pytest tests/test_example.py -k ninel_v2 -q`

Expected: missing example failure.

- [ ] **Step 3: Author the story and pilot packages from approved contracts**

Use original Ninel/Argo/fantasy-hive premise. Make every new creative addition `proposed` or an explicit assumption. Select and justify a compatible serial structure; include episode hooks and cliffhangers; carry stable IDs into Fountain metadata and the v1 scene package.

- [ ] **Step 4: Author production and post plans without false media evidence**

Include production design, character look, animation, VFX, image/video/voice/music/sound prompts, and `awaiting-media` review. Build edit/sound/music/VFX/color/titles/QC as planned artifacts; do not include selected takes, exact observed timecodes, measurements, approvals, or QC pass.

- [ ] **Step 5: Validate and commit**

```bash
.venv/bin/python -m cine_skills validate-project examples/ninel-v2 --profile full-creative-v2 --format json
.venv/bin/python -m pytest tests/test_example.py -q
git add examples/ninel-v2 tests/test_example.py
git commit -m "feat: add canonical Ninel v2 project"
```

### Task 6: Documentation, Migration, and Release Metadata

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `docs/codex-start.md`
- Create: `docs/migration-v1-to-v2.md`
- Modify: `schemas/README.md`
- Modify: `docs/source-register.md`
- Modify: `CHANGELOG.md`
- Modify: `pyproject.toml`
- Modify: `src/cine_skills/__init__.py`
- Modify: `Makefile`
- Modify: `tests/test_example.py`

**Interfaces:**
- Produces: release version `2.0.0`, documented commands/profiles, migration path, and Make validation targets.

- [ ] **Step 1: Write failing version and documentation assertions**

Assert `pyproject.toml` and runtime `__version__` are `2.0.0`; README names all four v2 profiles and links migration; AGENTS requires the v2 spec; schema README lists every v2 schema; changelog has `2.0.0`; Make exposes `validate-v2-example` invoking `validate-project` with JSON output.

- [ ] **Step 2: Verify RED**

Run: `.venv/bin/python -m pytest tests/test_example.py tests/test_skill_catalog.py -q`

Expected: stale 1.0 metadata/documentation failures.

- [ ] **Step 3: Update release-facing documents**

Lead README with layered workflow, keep v0.1/v1 compatibility commands, document exact exclusions, give one full-pipeline prompt and one specialist prompt. Migration must state that no command fabricates story/production/post choices. Source register must contain exact URLs, access dates, principles, and license/quotation notes for every new theory reference.

- [ ] **Step 4: Add Make targets and version bump**

Add `validate-story-example`, `validate-production-example`, `validate-post-example`, and `validate-v2-example` using the selected environment Python. Keep existing targets unchanged.

- [ ] **Step 5: Run documentation/version tests and commit**

```bash
make check
make validate-core-example
make validate-full-example
make validate-v2-example
git add README.md AGENTS.md docs schemas/README.md CHANGELOG.md pyproject.toml src/cine_skills/__init__.py Makefile tests
git commit -m "release: prepare cine agent skills v2.0.0"
```

### Task 7: Deterministic Release Archive

**Files:**
- Create: `scripts/build_release_archive.py`
- Create: `tests/test_release_archive.py`
- Modify: `Makefile`

**Interfaces:**
- Produces: `build_archive(repository: Path, output: Path, prefix: str = "cine-agent-skills/") -> str`, returning lowercase SHA-256.
- Produces Make target: `release-archive`.

- [ ] **Step 1: Write failing archive tests**

Create a temporary tracked-file list and assert a single `cine-agent-skills/` prefix, lexical entry order, fixed ZIP timestamps, no `.git`, `.venv`, caches, pyc, internal work logs, or preexisting ZIPs, successful `zipfile.testzip()`, and stable digest across two builds.

- [ ] **Step 2: Verify RED**

Run: `.venv/bin/python -m pytest tests/test_release_archive.py -q`

Expected: missing builder failure.

- [ ] **Step 3: Implement deterministic tracked-file builder**

Read tracked paths from `git ls-files -z`, validate every path is relative and exists, use a fixed DOS-compatible timestamp `(1980, 1, 1, 0, 0, 0)`, normalized mode bits, deflate compression, and lexical path order. Reject forbidden paths before writing. Return `hashlib.sha256(output.read_bytes()).hexdigest()`.

- [ ] **Step 4: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_release_archive.py -q
git add scripts/build_release_archive.py tests/test_release_archive.py Makefile
git commit -m "build: add deterministic v2 release archive"
```

### Task 8: Clean Bootstrap, Review, and Final Release Gate

**Files:**
- Modify only files demonstrated defective by a failing release test or review finding.
- Create ignored work report only if the existing repository workflow already uses one; do not add internal reports to the archive.

**Interfaces:**
- Produces: verified release commit, archive, SHA-256, and clean tracked status.

- [ ] **Step 1: Run the entire tracked workspace verification**

```bash
make check
make validate-core-example
make validate-full-example
make validate-v2-example
git diff --check
git status --short
```

Expected: all validation passes and tracked status is clean.

- [ ] **Step 2: Run a clean tracked-only bootstrap**

Use `git archive HEAD` to extract into a newly created explicit temporary directory. In that directory, run `make setup`, `make check`, all three preserved/new example targets, and `make release-archive`. Never run the clean-copy commands in the shared repository by accident; pass the temporary directory explicitly as the command working directory.

- [ ] **Step 3: Request independent code and spec review**

Review the complete range from the v2 design commit through HEAD for spec compliance first, then code quality. Treat Critical and Important findings as blockers. Reproduce each accepted finding with a failing test before fixing it, then rerun the affected subsystem and full gates.

- [ ] **Step 4: Build and inspect the final archive**

Run `make release-archive`, `python -m zipfile -t <archive>`, enumerate entries, confirm one prefix, confirm forbidden paths absent, record byte size, entry count, release commit, and SHA-256.

- [ ] **Step 5: Final verification after the last commit**

```bash
make check
make validate-core-example
make validate-full-example
make validate-v2-example
git diff --check
git status --short
```

Expected: all pass, tracked status clean, archive digest matches the deterministic build, and no release blocker remains.

## v2.0 completion gate

Do not claim completion unless all twelve release criteria in the approved specification are evidenced by fresh command output. The handoff must include release commit, test count, example validation results, archive path, entry count, byte size, and SHA-256.

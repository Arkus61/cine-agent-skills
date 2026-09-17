# Cine Agent Skills v1.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a backward-compatible `1.0.0` release containing twelve film-preproduction skills, a validated full-v1 scene package, machine-readable CLI reports, complete documentation, and a reproducible release archive.

**Architecture:** Preserve the five-file v0.1 core profile and extend the declarative Agent Skills catalog one specialist at a time. Each new specialist owns one schema, template, concise procedure, focused reference, behavioral evaluation, and forward test. Extend the Python package with additive profile selection, JSON reporting, and full-package cross-reference validation.

**Tech Stack:** Python 3.11+, Markdown, YAML, JSON Schema Draft 2020-12, PyYAML, jsonschema, pytest, Agent Skills, Git.

## Global Constraints

- Repository/package release version is exactly `1.0.0`.
- Artifact `schema_version` remains exactly `"1.0"`.
- Preserve the existing `core-v0.1` schemas, package layout, commands, and accepted payloads.
- A package with `package-manifest.json` auto-selects `full-v1`; a package without it auto-selects `core-v0.1`.
- Keep exactly twelve skills named in the approved specification.
- Keep `SKILL.md` frontmatter limited to `name` and `description`.
- Create and validate one skill completely before creating the next skill.
- Run a failing baseline scenario before writing or editing any skill.
- Add Python behavior and schema constraints only after the corresponding test fails for the intended reason.
- Derive expected values independently from production helpers.
- Preserve exact scene-derived identifiers and reject whitespace, suffixes, prefixes, duplicates, and dangling references.
- Keep v1.0 usable without external APIs and do not add media generation, postproduction automation, budgeting, scheduling, casting selection, MCP, databases, or a web UI.
- Paraphrase film knowledge and record exact source pages, access dates, terms or licensing notes, and extracted principles in `docs/source-register.md`.

---

### Task 1: Package profiles, JSON reports, and console entry point

**Files:**
- Modify: `src/cine_skills/package.py`
- Create: `src/cine_skills/reporting.py`
- Modify: `src/cine_skills/__main__.py`
- Modify: `pyproject.toml`
- Modify: `tests/test_package.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Produces: `CORE_PROFILE = "core-v0.1"` and `FULL_PROFILE = "full-v1"`.
- Produces: `resolve_scene_package_profile(package_dir: Path, requested: str = "auto") -> str`.
- Extends: `validate_scene_package(package_dir: Path, root: Path, profile: str = "auto") -> list[str]`.
- Produces: `render_validation_report(command: str, errors: list[str], output_format: str, profile: str | None = None) -> str`.
- Produces: installed console command `cine-skills` mapped to `cine_skills.__main__:main`.

- [ ] **Step 1: Write failing profile and JSON-output tests**

Add tests with literal expectations:

```python
def test_auto_profile_keeps_legacy_package_compatible(package_dir):
    assert resolve_scene_package_profile(package_dir) == "core-v0.1"

def test_auto_profile_selects_full_when_manifest_exists(package_dir):
    (package_dir / "package-manifest.json").write_text("{}", encoding="utf-8")
    assert resolve_scene_package_profile(package_dir) == "full-v1"

def test_validate_package_json_report_is_machine_readable(repository_root):
    result = run_cli(
        repository_root,
        "validate-package",
        "examples/ninel/scenes/S01",
        "--format",
        "json",
    )
    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "command": "validate-package",
        "errors": [],
        "profile": "core-v0.1",
        "valid": True,
    }
```

Add one installed-entry test that resolves the `cine-skills` executable from the active environment and validates the core example.

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_package.py tests/test_cli.py -q
```

Expected: failures for the missing resolver, missing `--profile`/`--format`, missing JSON renderer, and missing console entry point.

- [ ] **Step 3: Implement the minimal additive interfaces**

Keep the current five artifact tuples as `CORE_ARTIFACT_FILES`. Resolve `auto` only by manifest presence. Accept exactly `auto`, `core-v0.1`, and `full-v1`; argparse rejects any other value with exit code `2`.

Render JSON with `json.dumps(payload, ensure_ascii=False, sort_keys=True)` and a trailing newline. Text success and error messages remain byte-for-byte compatible with v0.1.

- [ ] **Step 4: Run focused and regression tests**

```bash
.venv/bin/python -m pytest tests/test_package.py tests/test_cli.py -q
make check
```

Expected: focused and full suites pass; the unchanged Ninel core package validates in auto and explicit `core-v0.1` modes.

- [ ] **Step 5: Commit the CLI foundation**

```bash
git add src/cine_skills/package.py src/cine_skills/reporting.py src/cine_skills/__main__.py pyproject.toml tests/test_package.py tests/test_cli.py
git commit -m "feat: add v1 package profiles and JSON reports"
```

### Task 2: Visual language specialist

**Files:**
- Create: `schemas/visual-language-plan.schema.json`
- Create: `.agents/skills/visual-language-designer/SKILL.md`
- Create: `.agents/skills/visual-language-designer/agents/openai.yaml`
- Create: `.agents/skills/visual-language-designer/references/visual-language.md`
- Create: `.agents/skills/visual-language-designer/assets/visual-language-plan.template.json`
- Create: `evals/visual-language-designer.json`
- Modify: `tests/test_artifacts.py`
- Modify: `tests/test_skill_catalog.py`
- Modify: `docs/source-register.md`

**Interfaces:**
- Produces schema `visual-language-plan`.
- Produces IDs matching `<scene>-V[0-9]{2,}`.
- Consumes source scene, scene beats, and directing plan.

- [ ] **Step 1: Run a fresh no-skill baseline**

Ask a fresh agent to design the visual language for the Ninel brief without access to the new skill. Record whether the result omits stable rule IDs, beat references, aspect ratio, lens strategy, camera-height rules, prohibited defaults, motivated exceptions, or explicit assumptions. Keep raw output outside tracked release files.

- [ ] **Step 2: Write failing schema and bundle tests**

Add a literal valid payload containing `aspect_ratio`, `point_of_view`, `palette`, `contrast`, `texture`, `lens_strategy`, `visual_motifs`, `prohibited_defaults`, `exceptions`, and one `rules` item with `rule_id`, `beat_ids`, `composition`, `camera_height`, and `dramatic_purpose`. Add invalid cases for `S01-alt-V01`, a terminal newline, an empty `beat_ids`, and an omitted dramatic purpose.

Add a catalog test that expects the exact four skill files and matching OpenAI metadata. Run it before creating the directory.

- [ ] **Step 3: Run focused tests and verify RED**

```bash
.venv/bin/python -m pytest tests/test_artifacts.py tests/test_skill_catalog.py -q
```

Expected: failures because the schema and skill bundle do not exist.

- [ ] **Step 4: Research and register sources**

Record exact public pages for composition, lens language, aspect ratio, and camera movement. Include access date `2026-08-05`, terms/licensing note, extracted principle, and an original paraphrase. Use AI Camera Movements as a movement taxonomy only, not as copied instructional prose.

- [ ] **Step 5: Initialize and author the skill**

Run `init_skill.py visual-language-designer` with `references,assets`, passing final UI strings. Replace every generated placeholder. Keep procedure in imperative form and place detailed theory in the single reference. Make the template a complete valid artifact, not a fill-in-the-blank document.

- [ ] **Step 6: Validate and forward-test before moving on**

Run the repository validator and `quick_validate.py`, then ask a fresh agent:

```text
Use $visual-language-designer at .agents/skills/visual-language-designer for examples/ninel-scene-brief.md and the existing S01 beats/directing plan. Write one valid visual-language-plan.json.
```

Validate the emitted JSON with the real CLI. Compare observable omissions with the baseline and make only evidence-driven skill corrections.

- [ ] **Step 7: Commit the verified specialist**

```bash
git add schemas/visual-language-plan.schema.json .agents/skills/visual-language-designer evals/visual-language-designer.json tests/test_artifacts.py tests/test_skill_catalog.py docs/source-register.md
git commit -m "feat: add visual language designer"
```

### Task 3: Lighting specialist

**Files:**
- Create: `schemas/lighting-plan.schema.json`
- Create: `.agents/skills/lighting-designer/SKILL.md`
- Create: `.agents/skills/lighting-designer/agents/openai.yaml`
- Create: `.agents/skills/lighting-designer/references/lighting-design.md`
- Create: `.agents/skills/lighting-designer/assets/lighting-plan.template.json`
- Create: `evals/lighting-designer.json`
- Modify: `tests/test_artifacts.py`
- Modify: `tests/test_skill_catalog.py`
- Modify: `docs/source-register.md`

**Interfaces:**
- Produces schema `lighting-plan` and setup IDs `<scene>-L[0-9]{2,}`.
- Each setup requires non-empty `beat_ids`, non-empty `shot_ids`, sources, motivation, direction, quality, color intent, exposure/contrast intent, control requirements, continuity, safety, and dramatic purpose.

- [ ] **Step 1: Capture a no-skill lighting baseline**

Use the canonical core shot list and visual plan. Record omissions in source motivation, executable control, safety, continuity, shot coverage, and assumptions.

- [ ] **Step 2: Write and run failing schema/bundle tests**

Test one literal complete setup and invalid cases for a dangling-format shot ID, malformed lighting ID, empty sources, missing safety notes, and missing dramatic purpose.

```bash
.venv/bin/python -m pytest tests/test_artifacts.py tests/test_skill_catalog.py -q
```

Expected: missing schema and skill failures.

- [ ] **Step 3: Register lighting sources and author the skill**

Register exact official or openly accessible pages for motivated sources, direction/quality, contrast, color intent, exposure, control, and electrical or rigging safety. Initialize the skill, replace placeholders, create a complete template, and add one observable evaluation fixture.

- [ ] **Step 4: Validate and forward-test**

Generate a plan for the Ninel scene using the skill. Validate the artifact and confirm every core shot is named by at least one setup. Correct only observed gaps.

- [ ] **Step 5: Commit the verified lighting specialist**

```bash
git add schemas/lighting-plan.schema.json .agents/skills/lighting-designer evals/lighting-designer.json tests/test_artifacts.py tests/test_skill_catalog.py docs/source-register.md
git commit -m "feat: add lighting designer"
```

### Task 4: Sound specialist

**Files:**
- Create: `schemas/sound-plan.schema.json`
- Create: `.agents/skills/sound-designer/SKILL.md`
- Create: `.agents/skills/sound-designer/agents/openai.yaml`
- Create: `.agents/skills/sound-designer/references/production-sound.md`
- Create: `.agents/skills/sound-designer/assets/sound-plan.template.json`
- Create: `evals/sound-designer.json`
- Modify: `tests/test_artifacts.py`
- Modify: `tests/test_skill_catalog.py`
- Modify: `docs/source-register.md`

**Interfaces:**
- Produces schema `sound-plan` and cue IDs `<scene>-A[0-9]{2,}`.
- Cue categories are exactly `dialogue`, `effects`, `ambience`, `silence`, `transition`, and `music-intent`.

- [ ] **Step 1: Capture a no-skill sound baseline**

Use the Ninel scene and shot list. Record whether the output treats sound as a generic note instead of shot-linked dialogue priority, production effects, ambience, perspective, silence, transitions, recording/design requirements, and dramatic purpose.

- [ ] **Step 2: Write and run failing schema/bundle tests**

Test a literal cue with `cue_id`, `beat_ids`, `shot_ids`, `category`, `source`, `perspective`, `timing`, `requirement`, and `dramatic_purpose`. Reject malformed IDs, unknown categories, empty shot coverage, and copyrighted track prescriptions presented as required music.

```bash
.venv/bin/python -m pytest tests/test_artifacts.py tests/test_skill_catalog.py -q
```

- [ ] **Step 3: Register sources and author the skill**

Register exact public sources for production dialogue, ambience/room tone, perspective, effects, silence, and safe music-intent language. Initialize, author, validate, and add the complete template and evaluation fixture.

- [ ] **Step 4: Forward-test and validate**

Generate Ninel `sound-plan.json`, validate it, and confirm all core shots are covered by at least one cue or explicit silence/bed.

- [ ] **Step 5: Commit the verified sound specialist**

```bash
git add schemas/sound-plan.schema.json .agents/skills/sound-designer evals/sound-designer.json tests/test_artifacts.py tests/test_skill_catalog.py docs/source-register.md
git commit -m "feat: add sound designer"
```

### Task 5: Storyboard specialist

**Files:**
- Create: `schemas/storyboard-plan.schema.json`
- Create: `.agents/skills/storyboard-designer/SKILL.md`
- Create: `.agents/skills/storyboard-designer/agents/openai.yaml`
- Create: `.agents/skills/storyboard-designer/references/storyboard-language.md`
- Create: `.agents/skills/storyboard-designer/assets/storyboard-plan.template.json`
- Create: `evals/storyboard-designer.json`
- Modify: `tests/test_artifacts.py`
- Modify: `tests/test_skill_catalog.py`
- Modify: `docs/source-register.md`

**Interfaces:**
- Produces schema `storyboard-plan` and panel IDs `<scene>-SB[0-9]{3,}`.
- Each panel references exactly one stable shot ID and describes one drawable moment without embedding or generating media.

- [ ] **Step 1: Capture a no-skill storyboard baseline**

Ask for textual panels from the Ninel shot list. Record omissions in exact shot linkage, depicted moment, depth layers, subject placement, action direction, movement state, lighting, sound, continuity, and dramatic purpose.

- [ ] **Step 2: Write and run failing schema/bundle tests**

Use a complete literal panel containing `panel_id`, `shot_id`, `moment`, `framing`, `camera_height`, `angle`, `foreground`, `midground`, `background`, `subject_placement`, `action_direction`, `movement_state`, `lighting_note`, `audio_cue`, `continuity_note`, and `dramatic_purpose`. Reject media URLs/base64 fields through `additionalProperties: false`.

- [ ] **Step 3: Register sources and author the skill**

Register exact public storyboard and screen-direction resources. Initialize the skill, author the concise drawing specification workflow, create a valid template, and add the evaluation fixture.

- [ ] **Step 4: Forward-test and validate**

Generate and validate the Ninel storyboard plan. Confirm every core shot has at least one panel and that no image-generation claims appear.

- [ ] **Step 5: Commit the verified storyboard specialist**

```bash
git add schemas/storyboard-plan.schema.json .agents/skills/storyboard-designer evals/storyboard-designer.json tests/test_artifacts.py tests/test_skill_catalog.py docs/source-register.md
git commit -m "feat: add storyboard designer"
```

### Task 6: Production breakdown specialist

**Files:**
- Create: `schemas/production-breakdown.schema.json`
- Create: `.agents/skills/production-breakdown/SKILL.md`
- Create: `.agents/skills/production-breakdown/agents/openai.yaml`
- Create: `.agents/skills/production-breakdown/references/department-breakdown.md`
- Create: `.agents/skills/production-breakdown/assets/production-breakdown.template.json`
- Create: `evals/production-breakdown.json`
- Modify: `tests/test_artifacts.py`
- Modify: `tests/test_skill_catalog.py`
- Modify: `docs/source-register.md`

**Interfaces:**
- Produces schema `production-breakdown` and item IDs `<scene>-PD[0-9]{3,}`.
- Categories are exactly `cast`, `location-set`, `props`, `wardrobe`, `hair-makeup`, `camera-grip`, `lighting`, `sound`, `practical-effects`, `visual-effects`, `art`, `safety`, and `open-question`.

- [ ] **Step 1: Capture a no-skill breakdown baseline**

Ask a fresh agent to break down the Ninel scene under the v1.0 boundary. Record invented production facts, missing source basis, missing reset/continuity details, missing risk level, or prohibited budgeting/scheduling/casting work.

- [ ] **Step 2: Write and run failing schema/bundle tests**

Test a complete literal item containing item/category/source basis/beat IDs/shot IDs/requirement/continuity reset/assumptions/risk level. Reject unknown categories, malformed IDs, unlabelled assumptions, and monetary or schedule fields through `additionalProperties: false`.

- [ ] **Step 3: Register sources and author the skill**

Register exact public scene-breakdown and department-role sources. Initialize, author the fact/assumption/proposal separation, create a valid template, and add the evaluation fixture.

- [ ] **Step 4: Forward-test and validate**

Generate and validate Ninel production breakdown. Confirm it identifies needs and risks without prices, dates, performer selection, or invented resources.

- [ ] **Step 5: Commit the verified breakdown specialist**

```bash
git add schemas/production-breakdown.schema.json .agents/skills/production-breakdown evals/production-breakdown.json tests/test_artifacts.py tests/test_skill_catalog.py docs/source-register.md
git commit -m "feat: add production breakdown"
```

### Task 7: Continuity specialist

**Files:**
- Create: `schemas/continuity-plan.schema.json`
- Create: `.agents/skills/continuity-supervisor/SKILL.md`
- Create: `.agents/skills/continuity-supervisor/agents/openai.yaml`
- Create: `.agents/skills/continuity-supervisor/references/continuity-control.md`
- Create: `.agents/skills/continuity-supervisor/assets/continuity-plan.template.json`
- Create: `evals/continuity-supervisor.json`
- Modify: `tests/test_artifacts.py`
- Modify: `tests/test_skill_catalog.py`
- Modify: `docs/source-register.md`

**Interfaces:**
- Produces schema `continuity-plan` and item IDs `<scene>-CN[0-9]{3,}`.
- Categories are exactly `axis`, `eyeline`, `position`, `action`, `prop`, `wardrobe`, `makeup`, `environment`, `lighting`, `sound`, and `reset`.

- [ ] **Step 1: Capture a no-skill continuity baseline**

Ask a fresh agent to audit the Ninel shot list and new department plans. Record generic warnings that lack shot IDs, tracked state, transition, reset instruction, and severity.

- [ ] **Step 2: Write and run failing schema/bundle tests**

Test a literal item with `continuity_id`, non-empty `shot_ids`, category, tracked state, required transition, reset instruction, and severity. Reject malformed IDs, unknown categories, empty shot references, and missing reset instructions.

- [ ] **Step 3: Register sources and author the skill**

Register exact public continuity, axis, eyeline, action-match, and reset resources. Initialize, author, create the valid template, and add the evaluation fixture.

- [ ] **Step 4: Forward-test and validate**

Generate and validate Ninel continuity plan. Confirm every shot is referenced and each issue is actionable rather than a generic reminder.

- [ ] **Step 5: Commit the verified continuity specialist**

```bash
git add schemas/continuity-plan.schema.json .agents/skills/continuity-supervisor evals/continuity-supervisor.json tests/test_artifacts.py tests/test_skill_catalog.py docs/source-register.md
git commit -m "feat: add continuity supervisor"
```

### Task 8: Manifest, full-profile validator, and canonical v1 example

**Files:**
- Create: `schemas/package-manifest.schema.json`
- Modify: `src/cine_skills/package.py`
- Create: `tests/v1_fixtures.py`
- Modify: `tests/test_package.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_example.py`
- Create: `examples/ninel-v1/scenes/S01/source-scene.md`
- Create: `examples/ninel-v1/scenes/S01/*.json`

**Interfaces:**
- Full profile requires one source, eleven creative artifacts, and one manifest.
- Manifest release version is `1.0.0`, profile is `full-v1`, and its artifact list is deterministic.
- Cross-validation resolves beat IDs, shot IDs, and category IDs and enforces lighting/sound/storyboard/continuity shot coverage.

- [ ] **Step 1: Write failing full-profile tests**

Create a complete literal fixture writer in `tests/v1_fixtures.py`. Add tests for:

- auto and explicit full-v1 success;
- missing source or artifact;
- mismatched scene ID;
- malformed or duplicate V/L/A/SB/PD/CN IDs;
- dangling beat and shot references in every new artifact;
- uncovered shot in lighting, sound, storyboard, and continuity;
- duplicate storyboard coverage being allowed while zero coverage fails;
- incomplete, reordered, or extra manifest entries;
- JSON report profile and sorted error stability.

- [ ] **Step 2: Run focused tests and verify RED**

```bash
.venv/bin/python -m pytest tests/test_package.py tests/test_cli.py tests/test_example.py -q
```

Expected: full-v1 cases fail because the manifest schema, full artifact map, and cross-checks do not exist.

- [ ] **Step 3: Implement schema-first full validation**

Add `FULL_ARTIFACT_FILES` in exact dependency order. Reuse one category-aware exact-ID validator. Keep cross-check functions small: declared IDs, beat references, shot references, shot coverage, and manifest contract. Skip only checks whose prerequisite artifact failed loading or schema validation.

- [ ] **Step 4: Create the complete Ninel v1 package**

Copy the source and preserved five JSON files unchanged into `examples/ninel-v1/scenes/S01/`. Add six thoughtful new artifacts and a deterministic manifest. Do not modify `examples/ninel/scenes/S01/`.

- [ ] **Step 5: Run focused and full verification**

```bash
PYTHONPATH=src .venv/bin/python -m cine_skills validate-package examples/ninel/scenes/S01 --profile core-v0.1
PYTHONPATH=src .venv/bin/python -m cine_skills validate-package examples/ninel-v1/scenes/S01 --profile full-v1
.venv/bin/python -m pytest tests/test_package.py tests/test_cli.py tests/test_example.py -q
make check
```

- [ ] **Step 6: Commit the full package contract**

```bash
git add schemas/package-manifest.schema.json src/cine_skills/package.py tests/v1_fixtures.py tests/test_package.py tests/test_cli.py tests/test_example.py examples/ninel-v1
git commit -m "feat: validate full v1 preproduction packages"
```

### Task 9: Expanded pipeline and exact v1 catalog

**Files:**
- Modify: `.agents/skills/scene-preproduction-pipeline/SKILL.md`
- Modify: `.agents/skills/scene-preproduction-pipeline/references/pipeline-contract.md`
- Modify: `.agents/skills/scene-preproduction-pipeline/assets/scene-package-checklist.md`
- Modify: `.agents/skills/scene-preproduction-pipeline/agents/openai.yaml`
- Modify: `evals/scene-preproduction-pipeline.json`
- Modify: `tests/test_skill_catalog.py`

**Interfaces:**
- Orchestrates the exact eleven-artifact dependency order and final manifest.
- Repairs the earliest failed dependency and regenerates only its downstream artifacts.
- Handoff reports facts, assumptions, repairs, unresolved conflicts, profile, and validation result.

- [ ] **Step 1: Run a failing v1 pipeline baseline before editing**

Give a fresh agent the existing v0.1 pipeline skill and ask for a full-v1 package. Record the absent visual, lighting, sound, storyboard, production, continuity, and manifest outputs and any invalid regeneration order.

- [ ] **Step 2: Write failing catalog and pipeline evaluation tests**

Change the exact expected catalog to the twelve approved names. Add evaluation assertions requiring thirteen canonical files, exact dependency order, full-v1 validation, downstream-only repair, and a complete handoff report.

```bash
.venv/bin/python -m pytest tests/test_skill_catalog.py -q
```

Expected: the catalog count passes only after all six specialists exist; pipeline behavior checks fail against the v0.1 instructions.

- [ ] **Step 3: Update the pipeline minimally**

Keep `SKILL.md` procedural and move the full dependency matrix, failure propagation, manifest rules, and coverage checks into its reference and checklist. Refresh OpenAI metadata from the final instructions.

- [ ] **Step 4: Forward-test the complete pipeline**

Ask a fresh agent to use `$scene-preproduction-pipeline` on a new bounded scene brief and write a full-v1 package outside the repository. Run the real full-profile validator. If invalid, classify the earliest failure, make one evidence-driven instruction change, and rerun with a fresh context.

- [ ] **Step 5: Commit the orchestrator and exact catalog**

```bash
git add .agents/skills/scene-preproduction-pipeline evals/scene-preproduction-pipeline.json tests/test_skill_catalog.py
git commit -m "feat: orchestrate the full v1 pipeline"
```

### Task 10: Release metadata, documentation, clean bootstrap, and archive

**Files:**
- Modify: `src/cine_skills/__init__.py`
- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `CONTRIBUTING.md`
- Modify: `Makefile`
- Modify: `docs/codex-start.md`
- Create: `docs/migration-v0.1-to-v1.0.md`
- Create: `CHANGELOG.md`
- Modify: `schemas/README.md`
- Modify: `knowledge/README.md`
- Modify: `tests/test_validator.py`
- Create outside repository: `cine-agent-skills-v1.0.0.zip`

**Interfaces:**
- Runtime and package metadata expose `1.0.0`.
- README documents both profiles, both CLI entry points, all twelve skills, and the full package.
- Migration guide extends a core package without fabricating creative artifacts.

- [ ] **Step 1: Write failing release-metadata and documentation behavior tests**

Add tests that import `cine_skills.__version__`, inspect installed package metadata, validate both examples through documented commands, and verify the exact eleven creative schema names plus manifest schema. Do not assert arbitrary prose strings.

- [ ] **Step 2: Run focused tests and verify RED**

```bash
.venv/bin/python -m pytest tests/test_validator.py tests/test_cli.py tests/test_example.py -q
```

Expected: version and schema-catalog assertions fail against v0.1 metadata and incomplete docs/targets.

- [ ] **Step 3: Update metadata and human documentation**

Set both versions to `1.0.0`. Add Make targets for explicit core and full example validation while preserving existing targets. Document installation, discovery, specialist use, full orchestration, profiles, JSON reports, migration, scope boundaries, source policy, and troubleshooting.

- [ ] **Step 4: Run repository and clean-bootstrap verification**

```bash
make check
PYTHONPATH=src .venv/bin/python -m cine_skills validate-package examples/ninel/scenes/S01 --profile core-v0.1
PYTHONPATH=src .venv/bin/python -m cine_skills validate-package examples/ninel-v1/scenes/S01 --profile full-v1 --format json
git diff --check
```

Create a temporary tracked-only copy using `git archive HEAD`, run `make setup`, then plain `make check` and both documented package targets inside the copy.

- [ ] **Step 5: Commit the release tree**

```bash
git add src/cine_skills/__init__.py pyproject.toml README.md AGENTS.md CONTRIBUTING.md Makefile docs/codex-start.md docs/migration-v0.1-to-v1.0.md CHANGELOG.md schemas/README.md knowledge/README.md tests/test_validator.py tests/test_cli.py tests/test_example.py
git commit -m "release: prepare cine agent skills v1.0.0"
```

- [ ] **Step 6: Build and inspect the release archive**

Build `../cine-agent-skills-v1.0.0.zip` from tracked `HEAD` with the sole prefix `cine-agent-skills/`. Verify:

```bash
unzip -t ../cine-agent-skills-v1.0.0.zip
unzip -Z1 ../cine-agent-skills-v1.0.0.zip
sha256sum ../cine-agent-skills-v1.0.0.zip
git status --short
```

Reject the release if the archive contains `.git`, `.venv`, caches, bytecode, build products, internal work logs, or any path outside the single prefix.

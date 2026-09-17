# Cine Agent Skills v2.0 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the shared v2 contracts, manifest schemas, exact-membership utilities, and deterministic validation primitives required by every v2 creative layer without changing v0.1 or v1 behavior.

**Architecture:** Keep `src/cine_skills/package.py` dedicated to preserved scene packages. Add focused v2 modules for constants/contracts, exact directory inspection, manifest inventory validation, and stable identifier/reference helpers. Layer-specific plans will compose these primitives instead of expanding the v1 file into a monolith.

**Tech Stack:** Python 3.11+, dataclasses, pathlib, JSON Schema Draft 2020-12, jsonschema, pytest.

## Global Constraints

- Repository target release is `2.0.0`; do not change package metadata until the integration/release plan.
- New v2 JSON artifacts use `schema_version: "2.0"`; preserved artifacts retain `"1.0"`.
- Preserve `core-v0.1`, `full-v1`, all accepted v1 payloads, and existing CLI behavior unchanged.
- Runtime validation must work offline and without paid APIs.
- Diagnostics must be deterministic, sorted, file-specific, and traceback-free for malformed user input.
- Use strict UTF-8 standards-compliant JSON with an object at the root.
- Use failing tests before Python behavior or schema constraints.
- Keep source facts, constraints, assumptions, uncertainties, interpretations, and creative proposals distinguishable.

---

## File map

- `src/cine_skills/project_contracts.py` — v2 profile, format, mode, artifact, and layer contract constants.
- `src/cine_skills/project_validation.py` — shared exact-membership, manifest, identifier, and reference validation primitives.
- `schemas/layer-manifest.schema.json` — contract shared by story, script, production, and post manifests.
- `schemas/creative-manifest.schema.json` — top-level project inventory and selected format/modes.
- `tests/test_project_contracts.py` — literal contract and conditional membership tests.
- `tests/test_project_validation.py` — shared validator behavior and error-boundary tests.
- `tests/test_artifacts.py` — schema acceptance/rejection tests.
- `tests/test_package.py` and `tests/test_cli.py` — preserved v1 regression gates.

### Task 1: Define immutable v2 contracts

**Files:**
- Create: `src/cine_skills/project_contracts.py`
- Create: `tests/test_project_contracts.py`

**Interfaces:**
- Produces: `ArtifactContract(filename: str, schema_name: str, dependency_order: int)`.
- Produces: `LayerContract(profile: str, directory_name: str, base_artifacts: tuple[ArtifactContract, ...])`.
- Produces: `ProjectIndex(project_id: str, project_format: str, production_modes: tuple[str, ...], unit_ids: frozenset[str], scene_ids: frozenset[str], beat_ids: frozenset[str], shot_ids: frozenset[str], character_ids: frozenset[str], event_ids: frozenset[str], world_ids: frozenset[str], asset_ids: frozenset[str], media_ids: frozenset[str], edit_segment_ids: frozenset[str])`.
- Produces: `PROJECT_FORMATS`, `PRODUCTION_MODES`, `STORY_PROFILE`, `PRODUCTION_PROFILE`, `POST_PROFILE`, and `FULL_CREATIVE_PROFILE`.
- Produces: `required_story_artifacts(project_format: str) -> tuple[ArtifactContract, ...]`.
- Produces: `required_production_artifacts(production_modes: Collection[str]) -> tuple[ArtifactContract, ...]`.
- Produces: `required_post_artifacts() -> tuple[ArtifactContract, ...]`.

- [ ] **Step 1: Write literal failing contract tests**

```python
from cine_skills.project_contracts import (
    FULL_CREATIVE_PROFILE,
    PROJECT_FORMATS,
    PRODUCTION_MODES,
    required_production_artifacts,
    required_story_artifacts,
)


def filenames(contracts):
    return tuple(item.filename for item in contracts)


def test_v2_profiles_and_supported_variants_are_literal():
    assert FULL_CREATIVE_PROFILE == "full-creative-v2"
    assert PROJECT_FORMATS == (
        "feature", "short", "series", "documentary",
        "commercial", "music-video", "short-form",
    )
    assert PRODUCTION_MODES == ("live-action", "animation", "ai", "hybrid")


def test_series_story_requires_season_arc():
    assert filenames(required_story_artifacts("series")) == (
        "story-concept.json", "story-structure.json", "character-arcs.json",
        "world-bible.json", "season-arc.json", "story-manifest.json",
    )


def test_feature_story_does_not_require_season_arc():
    assert "season-arc.json" not in filenames(required_story_artifacts("feature"))


def test_hybrid_production_requires_animation_and_media_prompts():
    names = filenames(required_production_artifacts(("hybrid",)))
    assert "animation-plan.json" in names
    assert "media-prompt-package.json" in names
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `.venv/bin/python -m pytest tests/test_project_contracts.py -q`

Expected: collection fails because `cine_skills.project_contracts` does not exist.

- [ ] **Step 3: Implement the literal contract registry**

```python
from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass

STORY_PROFILE = "story-v2"
PRODUCTION_PROFILE = "production-v2"
POST_PROFILE = "post-v2"
FULL_CREATIVE_PROFILE = "full-creative-v2"

PROJECT_FORMATS = (
    "feature", "short", "series", "documentary",
    "commercial", "music-video", "short-form",
)
PRODUCTION_MODES = ("live-action", "animation", "ai", "hybrid")


@dataclass(frozen=True)
class ArtifactContract:
    filename: str
    schema_name: str
    dependency_order: int


@dataclass(frozen=True)
class LayerContract:
    profile: str
    directory_name: str
    base_artifacts: tuple[ArtifactContract, ...]


@dataclass(frozen=True)
class ProjectIndex:
    project_id: str
    project_format: str
    production_modes: tuple[str, ...]
    unit_ids: frozenset[str] = frozenset()
    scene_ids: frozenset[str] = frozenset()
    beat_ids: frozenset[str] = frozenset()
    shot_ids: frozenset[str] = frozenset()
    character_ids: frozenset[str] = frozenset()
    event_ids: frozenset[str] = frozenset()
    world_ids: frozenset[str] = frozenset()
    asset_ids: frozenset[str] = frozenset()
    media_ids: frozenset[str] = frozenset()
    edit_segment_ids: frozenset[str] = frozenset()


def _contracts(items: tuple[tuple[str, str], ...]) -> tuple[ArtifactContract, ...]:
    return tuple(
        ArtifactContract(filename, schema_name, order)
        for order, (filename, schema_name) in enumerate(items, start=1)
    )
```

Define story order exactly as concept, structure, arcs, world, conditional season, manifest. Define production order exactly as design, character look, conditional animation, VFX, conditional prompts, media review, manifest. Define post order exactly as edit, sound post, music, VFX post, color, titles/captions, mastering/QC, manifest. Reject unknown formats or modes with `ValueError` listing sorted allowed values.

- [ ] **Step 4: Run contract tests and the preserved package suite**

Run: `.venv/bin/python -m pytest tests/test_project_contracts.py tests/test_package.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/cine_skills/project_contracts.py tests/test_project_contracts.py
git commit -m "feat: define v2 creative package contracts"
```

### Task 2: Add v2 manifest schemas

**Files:**
- Create: `schemas/layer-manifest.schema.json`
- Create: `schemas/creative-manifest.schema.json`
- Modify: `tests/test_artifacts.py`

**Interfaces:**
- Consumes: literal profiles, formats, and modes from Task 1.
- Produces: `layer-manifest` schema for story/script/production/post inventories.
- Produces: `creative-manifest` schema for top-level project routing.

- [ ] **Step 1: Add failing schema tests with valid and invalid payloads**

```python
def test_layer_manifest_requires_ordered_relative_artifacts(repository_root):
    payload = {
        "schema_version": "2.0",
        "release_version": "2.0.0",
        "project_id": "NINEL",
        "layer": "story",
        "profile": "story-v2",
        "artifacts": [{
            "filename": "story-concept.json",
            "schema_name": "story-concept",
            "schema_version": "2.0",
            "dependency_order": 1,
        }],
        "validation_status": "valid",
        "unresolved_questions": [],
    }
    assert validate_artifact("layer-manifest", payload, repository_root) == []


def test_creative_manifest_rejects_parent_traversal(repository_root):
    payload = valid_creative_manifest()
    payload["layers"]["story"] = "../story"
    errors = validate_artifact("creative-manifest", payload, repository_root)
    assert any("does not match" in error for error in errors)
```

The valid creative manifest must include `schema_version`, `release_version`, `profile`, `project_id`, `project_format`, unique `production_modes`, non-empty `units`, exact `layers` keys (`story`, `production`, `post`), `validation_status`, and `unresolved_questions`.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_artifacts.py -k 'manifest' -q`

Expected: failures report both v2 schemas are missing.

- [ ] **Step 3: Add strict Draft 2020-12 schemas**

Use `additionalProperties: false` at every object level. Use this exact relative-path pattern for artifact filenames and layer paths:

```json
"^[a-zA-Z0-9][a-zA-Z0-9._/-]*$"
```

Add a separate `not` constraint rejecting any value containing `..`, beginning `/`, or matching a Windows drive prefix. Constrain `schema_version` to `"2.0"`, `release_version` to `"2.0.0"`, profile enums to the approved names, project format to the seven approved values, production modes to the four approved values with `uniqueItems: true`, and dependency order to an integer greater than zero.

- [ ] **Step 4: Run schema and repository validation tests**

Run: `.venv/bin/python -m pytest tests/test_artifacts.py tests/test_validator.py -q`

Expected: PASS with both new schemas accepted by repository validation.

- [ ] **Step 5: Commit**

```bash
git add schemas/layer-manifest.schema.json schemas/creative-manifest.schema.json tests/test_artifacts.py
git commit -m "feat: add v2 creative manifest schemas"
```

### Task 3: Implement exact-membership and manifest validation primitives

**Files:**
- Create: `src/cine_skills/project_validation.py`
- Create: `tests/test_project_validation.py`

**Interfaces:**
- Consumes: `ArtifactContract` from `project_contracts.py`.
- Produces: `inspect_exact_entries(directory: Path, expected: Collection[str], label: str) -> list[str]`.
- Produces: `load_validated_artifacts(directory: Path, contracts: Collection[ArtifactContract], root: Path) -> tuple[dict[str, Mapping[str, Any]], list[str]]`.
- Produces: `validate_layer_manifest(payload: Mapping[str, Any], contracts: Collection[ArtifactContract], manifest_filename: str) -> list[str]`.
- Produces: `collect_ids(payload, collection_name, id_name) -> set[str]`.
- Produces: `validate_references(payload, filename, collection_name, reference_name, declared, label, cardinality="many") -> list[str]`.

- [ ] **Step 1: Write failing behavior and error-boundary tests**

```python
def test_exact_entries_rejects_unexpected_directory(tmp_path):
    package = tmp_path / "story"
    package.mkdir()
    (package / "expected.json").write_text("{}", encoding="utf-8")
    (package / "generated-media").mkdir()
    assert inspect_exact_entries(package, {"expected.json"}, "story-v2") == [
        "generated-media: unexpected entry for story-v2 package"
    ]


def test_layer_manifest_must_match_contract_order():
    contracts = (
        ArtifactContract("a.json", "a", 1),
        ArtifactContract("b.json", "b", 2),
    )
    manifest = {"artifacts": [
        {"filename": "b.json", "schema_name": "b", "schema_version": "2.0", "dependency_order": 1},
        {"filename": "a.json", "schema_name": "a", "schema_version": "2.0", "dependency_order": 2},
    ]}
    assert validate_layer_manifest(manifest, contracts, "story-manifest.json") == [
        "story-manifest.json: artifacts must match the exact dependency order: a.json, b.json"
    ]
```

Add a monkeypatched `Path.iterdir` `PermissionError` test expecting `<path>: unable to inspect story-v2 package directory: denied`, plus duplicate-ID, dangling-many-reference, and dangling-single-reference tests.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_project_validation.py -q`

Expected: collection fails because `project_validation` does not exist.

- [ ] **Step 3: Implement minimal deterministic primitives**

```python
def inspect_exact_entries(directory: Path, expected: Collection[str], label: str) -> list[str]:
    try:
        actual = {entry.name for entry in Path(directory).iterdir()}
    except OSError as exc:
        return [f"{directory}: unable to inspect {label} package directory: {exc}"]
    errors = [f"{name}: unexpected entry for {label} package" for name in actual - set(expected)]
    errors.extend(f"{name}: required file is missing" for name in set(expected) - actual)
    return sorted(errors)
```

`load_validated_artifacts` must use `load_json_object` and `validate_artifact`, qualify every error with the artifact filename, and exclude schema-invalid payloads from cross-artifact validation. Manifest comparison must construct its expected dictionaries independently from literal contract properties. Identifier and reference helpers must report collection indexes and deterministic sorted results.

- [ ] **Step 4: Run focused and malformed-input tests**

Run: `.venv/bin/python -m pytest tests/test_project_validation.py tests/test_cli.py -q`

Expected: PASS and no traceback text in CLI diagnostics.

- [ ] **Step 5: Commit**

```bash
git add src/cine_skills/project_validation.py tests/test_project_validation.py
git commit -m "feat: add shared v2 validation primitives"
```

### Task 4: Prove unchanged v1 behavior after the foundation

**Files:**
- Modify: `tests/test_package.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Consumes: existing `validate_scene_package` and CLI.
- Produces: explicit regression proof that v2 modules do not affect v1 auto selection, exact membership, reports, or exit codes.

- [ ] **Step 1: Add regression tests before any compatibility fix**

```python
def test_importing_v2_contracts_does_not_change_scene_profiles(repository_root):
    from cine_skills import project_contracts
    assert project_contracts.FULL_CREATIVE_PROFILE == "full-creative-v2"
    assert resolve_scene_package_profile(
        repository_root / "examples/ninel/scenes/S01"
    ) == "core-v0.1"
    assert resolve_scene_package_profile(
        repository_root / "examples/ninel-v1/scenes/S01"
    ) == "full-v1"
```

Add CLI assertions that both canonical examples still emit their literal v1 JSON reports and exit `0`.

- [ ] **Step 2: Run complete existing checks**

Run: `make check && make validate-core-example && make validate-full-example`

Expected: PASS. If any regression appears, write a focused failing test for that regression before changing production code.

- [ ] **Step 3: Apply only required compatibility fixes**

Do not change `CORE_ARTIFACT_FILES`, `FULL_ARTIFACT_FILES`, `resolve_scene_package_profile`, or existing schema contents. Fix only accidental imports, shared-name collisions, or error ordering demonstrated by the failing regression.

- [ ] **Step 4: Re-run the complete checks**

Run: `make check && make validate-core-example && make validate-full-example`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_package.py tests/test_cli.py src/cine_skills
git commit -m "test: lock v1 compatibility for v2 foundation"
```

## Foundation completion gate

Run:

```bash
make check
make validate-core-example
make validate-full-example
git diff --check
```

Expected: all commands pass; tracked status contains only intentional commits; no repository version bump has occurred yet.

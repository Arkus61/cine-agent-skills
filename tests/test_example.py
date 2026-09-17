import json
from pathlib import Path

import pytest

from cine_skills.artifacts import validate_artifact
from cine_skills.package import validate_scene_package
from cine_skills.project_package import validate_project


def test_ninel_v2_project_validates(repository_root: Path) -> None:
    assert validate_project(repository_root / "examples/ninel-v2", repository_root) == []


def test_ninel_v2_declares_animation_ai_series(repository_root: Path) -> None:
    project = repository_root / "examples/ninel-v2"
    manifest = json.loads((project / "creative-manifest.json").read_text())
    assert manifest["project_format"] == "series"
    assert set(manifest["production_modes"]) == {"animation", "ai"}
    assert (project / "story/season-arc.json").is_file()


@pytest.mark.parametrize("scene", ["S01", "SC001"])
def test_edit_plan_accepts_legacy_and_story_scene_ids(repository_root, scene):
    from tests.test_artifacts import valid_edit_plan
    payload = json.loads(json.dumps(valid_edit_plan()).replace("-S01", "-" + scene))
    assert validate_artifact("edit-plan", payload, repository_root) == []


def test_edit_plan_rejects_zero_story_scene_id(repository_root):
    from tests.test_artifacts import valid_edit_plan
    payload = json.loads(json.dumps(valid_edit_plan()).replace("-S01", "-SC000"))
    assert validate_artifact("edit-plan", payload, repository_root)


def test_production_layer_can_use_manifest_directory(repository_root, tmp_path):
    from tests.production_fixtures import write_production_package
    from cine_skills.production_package import validate_production_package
    package = tmp_path / "production"
    upstream = write_production_package(package, ("animation", "ai"))
    assert validate_production_package(package, repository_root, ("animation", "ai"), upstream)
    assert validate_production_package(package, repository_root, ("animation", "ai"), upstream, enforce_directory_name=False) == []


FULL_V1_FILES = {
    "source-scene.md",
    "scene-beats.json",
    "directing-plan.json",
    "visual-language-plan.json",
    "blocking-plan.json",
    "camera-movement-plan.json",
    "shot-list.json",
    "lighting-plan.json",
    "sound-plan.json",
    "storyboard-plan.json",
    "production-breakdown.json",
    "continuity-plan.json",
    "package-manifest.json",
}


@pytest.mark.parametrize(
    ("artifact_key", "schema_name"),
    [
        ("scene_beats", "scene-beats"),
        ("directing_plan", "directing-plan"),
        ("blocking_plan", "blocking-plan"),
        ("camera_movement_plan", "camera-movement-plan"),
        ("shot_list", "shot-list"),
    ],
)
def test_ninel_example_artifacts_are_valid(
    repository_root: Path, artifact_key: str, schema_name: str
) -> None:
    example_path = repository_root / "examples" / "ninel-pipeline-output.json"
    payload = json.loads(example_path.read_text(encoding="utf-8"))
    errors = validate_artifact(schema_name, payload[artifact_key], repository_root)
    assert errors == []


def test_ninel_scene_package_is_valid(repository_root: Path) -> None:
    package = repository_root / "examples" / "ninel" / "scenes" / "S01"
    assert validate_scene_package(package, repository_root) == []


def test_ninel_v1_scene_package_is_valid(repository_root: Path) -> None:
    package = repository_root / "examples" / "ninel-v1" / "scenes" / "S01"
    assert {path.name for path in package.iterdir()} == FULL_V1_FILES
    assert validate_scene_package(package, repository_root, profile="full-v1") == []


@pytest.mark.parametrize(
    ("artifact_key", "filename"),
    [
        ("scene_beats", "scene-beats.json"),
        ("directing_plan", "directing-plan.json"),
        ("blocking_plan", "blocking-plan.json"),
        ("camera_movement_plan", "camera-movement-plan.json"),
        ("shot_list", "shot-list.json"),
    ],
)
def test_ninel_scene_package_matches_approved_pipeline_output(
    repository_root: Path, artifact_key: str, filename: str
) -> None:
    package = repository_root / "examples" / "ninel" / "scenes" / "S01"
    aggregate = json.loads(
        (repository_root / "examples" / "ninel-pipeline-output.json").read_text(
            encoding="utf-8"
        )
    )
    split_artifact = json.loads((package / filename).read_text(encoding="utf-8"))
    assert split_artifact == aggregate[artifact_key]

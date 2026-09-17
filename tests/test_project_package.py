from dataclasses import replace
import json
import shutil
from pathlib import Path

import pytest

from cine_skills.project_contracts import ProjectIndex
from cine_skills.project_package import _safe_path, build_project_index, validate_project
from cine_skills.production_package import derive_production_index_at
from cine_skills.story_package import build_story_index


@pytest.mark.parametrize("mutation", ["format", "character", "shot", "media", "segment"])
def test_valid_ninel_rejects_cross_layer_mutation(tmp_path, repository_root, mutation):
    project = tmp_path / "project"
    shutil.copytree(repository_root / "examples/ninel-v2", project)
    assert validate_project(project, repository_root) == []
    if mutation == "format":
        path = project / "creative-manifest.json"
        payload = json.loads(path.read_text())
        payload["project_format"] = "short"
        expected = "project_format must exactly match story concept"
    elif mutation == "character":
        path = project / "production/character-look-bible.json"
        payload = json.loads(path.read_text())
        payload["characters"][0]["character_id"] = "OTHER-CH001"
        expected = "OTHER-CH001"
    else:
        path = project / "post/edit-plan.json"
        payload = json.loads(path.read_text())
        key, expected = {
            "shot": ("source_shot_ids", "OTHER-E01-SC001-SH001"),
            "media": ("source_media_ids", "OTHER-MD001"),
            "segment": ("segment_id", "OTHER-E01-ED001"),
        }[mutation]
        payload["segments"][0][key] = expected if mutation == "segment" else [expected]
    path.write_text(json.dumps(payload), encoding="utf-8")
    errors = validate_project(project, repository_root)
    assert any(expected in error for error in errors), errors


def test_ninel_project_index_retains_production_assets(repository_root):
    index, errors = build_project_index(repository_root / "examples/ninel-v2", repository_root)
    assert errors == []
    assert index is not None
    assert {"NINEL-AS001", "NINEL-AS002", "NINEL-AS003", "NINEL-AS004"} <= index.asset_ids
    assert index.edit_segment_ids == frozenset({"NINEL-E01-ED001", "NINEL-E01-ED002"})


def test_post_index_uses_valid_edit_plan_segments(tmp_path, repository_root):
    from tests.post_fixtures import write_post_package
    from cine_skills import project_package

    package = write_post_package(tmp_path / "post")
    upstream = ProjectIndex("NINEL", "series", ("animation", "ai"))
    index, errors = project_package._with_edit_segments(package, repository_root, upstream)
    assert errors == []
    assert index.edit_segment_ids == frozenset({"NINEL-U01-ED001", "NINEL-U01-ED002"})


def test_post_index_does_not_trust_invalid_edit_plan(tmp_path, repository_root):
    from tests.post_fixtures import write_post_package
    from cine_skills import project_package

    package = write_post_package(tmp_path / "post")
    (package / "edit-plan.json").write_text('{"segments": [{"segment_id": "FOREIGN-ED001"}]}', encoding="utf-8")
    upstream = ProjectIndex("NINEL", "series", ("animation", "ai"))
    index, errors = project_package._with_edit_segments(package, repository_root, upstream)
    assert errors
    assert index.edit_segment_ids == frozenset()


def test_project_reports_format_mismatch_against_real_story(tmp_path, repository_root):
    from tests.story_fixtures import write_story_project

    story_dir, scripts_dir = write_story_project(tmp_path)
    story, errors = build_story_index(
        story_dir, scripts_dir, repository_root
    )
    assert errors == []
    assert story is not None
    manifest = {
        "schema_version": "2.0", "release_version": "2.0.0",
        "profile": "full-creative-v2", "project_id": story.project_id,
        "project_format": "short", "production_modes": list(story.production_modes),
        "units": sorted(story.unit_ids),
        "layers": {"story": "story", "production": "production", "post": "post"},
        "validation_status": "valid", "unresolved_questions": [],
    }
    (tmp_path / "creative-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "production").mkdir()
    (tmp_path / "post").mkdir()

    errors = validate_project(tmp_path, repository_root)

    assert "creative-manifest.json: project_format must exactly match story concept" in errors


def test_safe_path_reports_symlink_loop_without_traceback(tmp_path: Path) -> None:
    loop = tmp_path / "loop"
    loop.symlink_to(loop)

    path, error = _safe_path(tmp_path, "loop")

    assert path is None
    assert error is not None
    assert "resolve" in error


def test_validate_project_invalid_manifest_stops_before_layer_resolution(
    tmp_path: Path, repository_root: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "creative-manifest.json").write_text("{}", encoding="utf-8")

    errors = validate_project(project, repository_root)

    assert errors
    assert any("required property" in error for error in errors)
    assert not any("layers." in error for error in errors)


def test_invalid_production_index_is_not_used_for_post_cross_checks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "project"
    for layer in ("story", "production", "post", "scripts"):
        (project / layer).mkdir(parents=True)
    (project / "creative-manifest.json").write_text("{}", encoding="utf-8")
    story = ProjectIndex("P", "short", ("ai",), unit_ids=frozenset({"U"}))
    invalid_production = replace(story, media_ids=frozenset({"P-M001"}))
    monkeypatch.setattr("cine_skills.project_package._manifest", lambda *_: ({
        "layers": {"story": "story", "production": "production", "post": "post"},
        "project_id": "P", "units": ["U"], "production_modes": ["ai"],
        "project_format": "short",
    }, []))
    monkeypatch.setattr("cine_skills.project_package._safe_path", lambda project, value: (project / value, None))
    monkeypatch.setattr("cine_skills.project_package.build_story_index", lambda *_: (story, []))
    monkeypatch.setattr("cine_skills.project_package.derive_production_index_at", lambda *_: (invalid_production, []))
    monkeypatch.setattr("cine_skills.project_package.validate_production_package", lambda *_, **kwargs: ["invalid production"])
    captured = {}
    def capture_post(_p: Path, _r: Path, upstream: ProjectIndex) -> list[str]:
        captured["upstream"] = upstream
        return []
    monkeypatch.setattr("cine_skills.project_package.validate_post_package", capture_post)

    index, errors = build_project_index(project, tmp_path)

    assert index is None
    assert "invalid production" in errors
    assert captured["upstream"].media_ids == frozenset()


def test_production_media_registry_flows_into_derived_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payloads = {
        "production-design-plan.json": {
            "project_id": "P", "source_context": {"scene_ids": ["S"], "shot_ids": []}, "assets": []
        },
        "character-look-bible.json": {"source_context": {"character_ids": []}},
            "media-prompt-package.json": {"source_context": {"registries": {"media_ids": ["P-M001"]}}},
    }
    monkeypatch.setattr(
        "cine_skills.production_package.load_validated_artifacts",
        lambda *_: (payloads, []),
    )
    monkeypatch.setattr(
        "cine_skills.production_package._existing_contracts",
        lambda package, contracts: contracts,
    )

    index, errors = derive_production_index_at(tmp_path, tmp_path, ("ai",))

    assert errors == []
    assert index is not None
    assert index.media_ids == frozenset({"P-M001"})

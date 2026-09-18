from __future__ import annotations

import json
from pathlib import Path

import pytest

from cine_skills.project_contracts import ProjectIndex
from cine_skills.story_package import (
    build_story_index,
    validate_script_package,
    validate_story_package,
)
from tests.story_fixtures import (
    SCRIPT_ARTIFACTS,
    STORY_ARTIFACTS,
    write_json,
    write_story_package,
    write_story_project,
)


def read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_valid_series_story_package_passes(repository_root: Path, tmp_path: Path):
    story = tmp_path / "story"
    write_story_package(story)

    assert validate_story_package(story, repository_root, "series") == []


def test_feature_story_membership_excludes_season_arc(repository_root: Path, tmp_path: Path):
    story = tmp_path / "story"
    write_story_package(story)
    (story / "season-arc.json").unlink()
    concept = read_json(story / "story-concept.json")
    concept["project_format"] = "feature"
    write_json(story / "story-concept.json", concept)
    manifest = read_json(story / "story-manifest.json")
    feature_artifacts = tuple(item for item in STORY_ARTIFACTS if item[0] != "season-arc.json")
    manifest["artifacts"] = [
        {"filename": filename, "schema_name": schema_name, "schema_version": "0.3.0", "dependency_order": order}
        for order, (filename, schema_name) in enumerate(feature_artifacts, start=1)
    ]
    write_json(story / "story-manifest.json", manifest)

    assert validate_story_package(story, repository_root, "feature") == []


@pytest.mark.parametrize(
    ("entry", "expected"),
    [
        ("notes", "notes: unexpected entry for story package"),
        ("season-arc.json", "season-arc.json: unexpected entry for story package"),
    ],
)
def test_story_membership_rejects_unexpected_files_and_directories(
    repository_root: Path, tmp_path: Path, entry: str, expected: str
):
    story = tmp_path / "story"
    write_story_package(story)
    if entry == "notes":
        (story / entry).mkdir()
    else:
        concept = read_json(story / "story-concept.json")
        concept["project_format"] = "feature"
        write_json(story / "story-concept.json", concept)

    assert expected in validate_story_package(story, repository_root, "feature" if entry.endswith(".json") else "series")


def test_story_membership_reports_missing_file(repository_root: Path, tmp_path: Path):
    story = tmp_path / "story"
    write_story_package(story)
    (story / "world-bible.json").unlink()

    assert "world-bible.json: required file is missing" in validate_story_package(story, repository_root, "series")


def test_story_membership_rejects_directory_in_place_of_required_file(
    repository_root: Path, tmp_path: Path
):
    story = tmp_path / "story"
    write_story_package(story)
    (story / "world-bible.json").unlink()
    (story / "world-bible.json").mkdir()

    assert "world-bible.json: required file is missing" in validate_story_package(
        story, repository_root, "series"
    )


def test_story_directory_oserror_is_a_diagnostic(
    repository_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    story = tmp_path / "story"
    story.mkdir()

    def denied(_path: Path):
        raise PermissionError("denied")

    monkeypatch.setattr(Path, "iterdir", denied)

    assert validate_story_package(story, repository_root, "series") == [
        f"{story}: unable to inspect story package directory: denied"
    ]


def test_story_artifacts_must_share_project_id(repository_root: Path, tmp_path: Path):
    story = tmp_path / "story"
    write_story_package(story)
    manifest = read_json(story / "story-manifest.json")
    manifest["project_id"] = "OTHER"
    write_json(story / "story-manifest.json", manifest)

    assert "story-manifest.json: project_id OTHER does not match EMBER" in validate_story_package(story, repository_root, "series")


def test_story_concept_format_must_match_selected_format(repository_root: Path, tmp_path: Path):
    story = tmp_path / "story"
    write_story_package(story)
    concept = read_json(story / "story-concept.json")
    concept["project_format"] = "short"
    write_json(story / "story-concept.json", concept)

    assert "story-concept.json: project_format short does not match series" in validate_story_package(story, repository_root, "series")


def test_story_cross_references_character_events(repository_root: Path, tmp_path: Path):
    story = tmp_path / "story"
    write_story_package(story)
    arcs = read_json(story / "character-arcs.json")
    characters = arcs["characters"]
    assert isinstance(characters, list) and isinstance(characters[0], dict)
    characters[0]["turning_event_ids"] = ["EMBER-EV999"]
    write_json(story / "character-arcs.json", arcs)

    assert "character-arcs.json: characters.0.turning_event_ids.0: unknown event EMBER-EV999" in validate_story_package(story, repository_root, "series")


def test_story_setup_payoff_resolution_is_reported(repository_root: Path, tmp_path: Path):
    story = tmp_path / "story"
    write_story_package(story)
    structure = read_json(story / "story-structure.json")
    links = structure["setup_payoffs"]
    assert isinstance(links, list) and isinstance(links[0], dict)
    links[0]["payoff_event_id"] = "EMBER-EV999"
    write_json(story / "story-structure.json", structure)

    errors = validate_story_package(story, repository_root, "series")

    assert any("story-structure.json:" in error and "unknown event EMBER-EV999" in error for error in errors)


@pytest.mark.parametrize("invalid_provenance", [[], {}], ids=["array", "object"])
def test_story_package_schema_invalid_canon_provenance_is_a_diagnostic(
    repository_root: Path,
    tmp_path: Path,
    invalid_provenance: object,
) -> None:
    story = tmp_path / "story"
    write_story_package(story)
    world_path = story / "world-bible.json"
    world = read_json(world_path)
    rules = world["rules"]
    assert isinstance(rules, list) and isinstance(rules[0], dict)
    rules[0]["canon_status"] = "canon"
    rules[0]["provenance"] = invalid_provenance
    write_json(world_path, world)

    errors = validate_story_package(story, repository_root, "series")

    assert any(
        error.startswith("world-bible.json: rules.0.provenance:")
        and "not one of" in error
        for error in errors
    )


def test_story_package_symlink_loop_is_a_deterministic_diagnostic(
    repository_root: Path, tmp_path: Path
) -> None:
    story = tmp_path / "story"
    write_story_package(story)
    world = story / "world-bible.json"
    world.unlink()
    try:
        world.symlink_to("world-bible.json")
    except OSError as exc:
        pytest.skip(f"symlinks are unavailable: {exc}")

    assert validate_story_package(story, repository_root, "series") == [
        "world-bible.json: required file is missing"
    ]


def test_story_manifest_inventory_order_is_literal(repository_root: Path, tmp_path: Path):
    story = tmp_path / "story"
    write_story_package(story)
    manifest = read_json(story / "story-manifest.json")
    artifacts = manifest["artifacts"]
    assert isinstance(artifacts, list)
    artifacts[0], artifacts[1] = artifacts[1], artifacts[0]
    write_json(story / "story-manifest.json", manifest)

    assert validate_story_package(story, repository_root, "series") == [
        "story-manifest.json: artifacts must match the exact dependency order: "
        + ", ".join(filename for filename, _schema in STORY_ARTIFACTS)
    ]


def test_cross_checks_skip_schema_invalid_story_payloads(repository_root: Path, tmp_path: Path):
    story = tmp_path / "story"
    write_story_package(story)
    structure = read_json(story / "story-structure.json")
    del structure["events"]
    write_json(story / "story-structure.json", structure)
    arcs = read_json(story / "character-arcs.json")
    characters = arcs["characters"]
    assert isinstance(characters, list) and isinstance(characters[0], dict)
    characters[0]["turning_event_ids"] = ["EMBER-EV999"]
    write_json(story / "character-arcs.json", arcs)

    errors = validate_story_package(story, repository_root, "series")

    assert any(error.startswith("story-structure.json:") for error in errors)
    assert not any("character-arcs.json" in error and "unknown event" in error for error in errors)


def test_valid_script_package_passes(repository_root: Path, tmp_path: Path):
    _story, scripts = write_story_project(tmp_path)

    assert validate_script_package(scripts / "EMBER-E01", repository_root, "EMBER", "series") == []


def test_script_membership_is_exact(repository_root: Path, tmp_path: Path):
    _story, scripts = write_story_project(tmp_path)
    script = scripts / "EMBER-E01"
    (script / "generated-media").mkdir()

    assert "generated-media: unexpected entry for story script package" in validate_script_package(script, repository_root, "EMBER", "series")


@pytest.mark.parametrize("entry", ["screenplay.fountain", "scenes"])
def test_script_membership_rejects_wrong_entry_type(
    repository_root: Path, tmp_path: Path, entry: str
):
    _story, scripts = write_story_project(tmp_path)
    script = scripts / "EMBER-E01"
    target = script / entry
    if target.is_dir():
        target.rename(script / "saved-scenes")
        target.write_text("not a directory", encoding="utf-8")
        (script / "saved-scenes").rename(script / "unused-scenes")
        (script / "unused-scenes").rename(script / "scenes-backup")
    else:
        target.unlink()
        target.mkdir()

    errors = validate_script_package(script, repository_root, "EMBER", "series")

    expected = (
        "scenes: required directory is missing"
        if entry == "scenes"
        else "screenplay.fountain: required file is missing"
    )
    assert expected in errors


def test_script_manifest_inventory_order_is_literal(repository_root: Path, tmp_path: Path):
    _story, scripts = write_story_project(tmp_path)
    script = scripts / "EMBER-E01"
    manifest = read_json(script / "script-manifest.json")
    artifacts = manifest["artifacts"]
    assert isinstance(artifacts, list)
    artifacts.reverse()
    write_json(script / "script-manifest.json", manifest)

    assert "script-manifest.json: artifacts must match the exact dependency order: " + ", ".join(filename for filename, _schema in SCRIPT_ARTIFACTS) in validate_script_package(script, repository_root, "EMBER", "series")


def test_script_artifacts_share_project_unit_and_format(repository_root: Path, tmp_path: Path):
    _story, scripts = write_story_project(tmp_path)
    script = scripts / "EMBER-E01"
    manifest = read_json(script / "script-manifest.json")
    manifest["project_id"] = "OTHER"
    write_json(script / "script-manifest.json", manifest)

    errors = validate_script_package(script, repository_root, "EMBER", "series")

    assert "script-manifest.json: project_id OTHER does not match EMBER" in errors


def test_script_fountain_and_metadata_are_one_to_one(repository_root: Path, tmp_path: Path):
    _story, scripts = write_story_project(tmp_path)
    script = scripts / "EMBER-E01"
    (script / "screenplay.fountain").write_text("EXT. OTHER ROAD - NIGHT\n\nMARA\nWait.\n", encoding="utf-8")

    errors = validate_script_package(script, repository_root, "EMBER", "series")

    assert any("screenplay-metadata.json: scene_mappings.0.heading: heading mismatch" in error for error in errors)


def test_script_package_rejects_fountain_cue_missing_from_metadata(
    repository_root: Path, tmp_path: Path
):
    _story, scripts = write_story_project(tmp_path)
    script = scripts / "EMBER-E01"
    (script / "screenplay.fountain").write_text(
        "EXT. SALT ROAD - DUSK\n\nMARA\nOpen the road.\n\nKEEPER\nNo.\n",
        encoding="utf-8",
    )

    errors = validate_script_package(script, repository_root, "EMBER", "series")

    assert (
        "screenplay-metadata.json: character_mappings: Fountain character cue "
        "has no metadata mapping: KEEPER"
    ) in errors


def test_script_package_rejects_metadata_cue_absent_from_fountain(
    repository_root: Path, tmp_path: Path
):
    _story, scripts = write_story_project(tmp_path)
    script = scripts / "EMBER-E01"
    metadata_path = script / "screenplay-metadata.json"
    metadata = read_json(metadata_path)
    mappings = metadata["character_mappings"]
    assert isinstance(mappings, list)
    mappings.append({"character_id": "EMBER-CH002", "cue": "KEEPER"})
    write_json(metadata_path, metadata)

    errors = validate_script_package(script, repository_root, "EMBER", "series")

    assert (
        "screenplay-metadata.json: character_mappings.1.cue: metadata character "
        "cue absent from Fountain: KEEPER"
    ) in errors


def test_script_scene_inventory_matches_metadata(repository_root: Path, tmp_path: Path):
    _story, scripts = write_story_project(tmp_path)
    script = scripts / "EMBER-E01"
    (script / "scenes" / "unexpected").mkdir()

    assert "unexpected: unexpected entry for scene-full scenes package" in validate_script_package(script, repository_root, "EMBER", "series")


def test_build_story_index_validates_episode_inventory_and_all_cross_references(repository_root: Path, tmp_path: Path):
    story, scripts = write_story_project(tmp_path)

    index, errors = build_story_index(story, scripts, repository_root)

    assert errors == []
    assert index == ProjectIndex(
        project_id="EMBER",
        project_format="series",
        production_modes=("live-action",),
        unit_ids=frozenset({"EMBER-E01", "EMBER-E02"}),
        scene_ids=frozenset({"EMBER-E01-SC001", "EMBER-E02-SC001"}),
        beat_ids=frozenset({"EMBER-E01-SC001-B01", "EMBER-E02-SC001-B01"}),
        shot_ids=frozenset({"EMBER-E01-SC001-SH001", "EMBER-E02-SC001-SH001"}),
        character_ids=frozenset({"EMBER-CH001", "EMBER-CH002"}),
        event_ids=frozenset({"EMBER-EV001", "EMBER-EV002"}),
        world_ids=frozenset({"EMBER-LO001", "EMBER-WR001"}),
        asset_ids=frozenset({"EMBER-AS001"}),
        media_ids=frozenset(),
        edit_segment_ids=frozenset(),
    )


def test_build_story_index_rejects_scene_packages_swapped_between_units(
    repository_root: Path, tmp_path: Path
) -> None:
    story, scripts = write_story_project(tmp_path)
    episode_one_scene = scripts / "EMBER-E01" / "scenes" / "EMBER-E01-SC001"
    episode_two_scene = scripts / "EMBER-E02" / "scenes" / "EMBER-E02-SC001"
    holding = scripts / "EMBER-E01" / "scenes" / "holding"
    episode_one_scene.rename(holding)
    episode_two_scene.rename(episode_one_scene)
    holding.rename(episode_two_scene)

    index, errors = build_story_index(story, scripts, repository_root)

    assert index is None
    assert (
        "EMBER-E01/scenes/EMBER-E01-SC001/scene-beats.json: scene_id "
        "EMBER-E02-SC001 does not match metadata scene EMBER-E01-SC001"
    ) in errors
    assert (
        "EMBER-E02/scenes/EMBER-E02-SC001/scene-beats.json: scene_id "
        "EMBER-E01-SC001 does not match metadata scene EMBER-E02-SC001"
    ) in errors


def test_build_story_index_rejects_missing_and_unexpected_episode_directories(repository_root: Path, tmp_path: Path):
    story, scripts = write_story_project(tmp_path)
    (scripts / "EMBER-E02").rename(scripts / "EMBER-E03")

    index, errors = build_story_index(story, scripts, repository_root)

    assert index is None
    assert "EMBER-E02: required script unit directory is missing" in errors
    assert "EMBER-E03: unexpected script unit directory" in errors


@pytest.mark.parametrize(
    ("filename", "field", "replacement", "diagnostic"),
    [
        ("unit-outline.json", "source_plotline_ids", ["EMBER-PL02"], "dangling plotline reference EMBER-PL02"),
        ("screenplay-metadata.json", "character", "EMBER-CH003", "dangling character reference EMBER-CH003"),
        ("screenplay-metadata.json", "location", "EMBER-LO003", "dangling world reference EMBER-LO003"),
    ],
)
def test_build_story_index_resolves_plot_character_and_world_references(
    repository_root: Path, tmp_path: Path, filename: str, field: str, replacement: object, diagnostic: str
):
    story, scripts = write_story_project(tmp_path)
    path = scripts / "EMBER-E01" / filename
    payload = read_json(path)
    if field == "character":
        mappings = payload["character_mappings"]
        scenes = payload["scene_mappings"]
        assert isinstance(mappings, list) and isinstance(mappings[0], dict)
        assert isinstance(scenes, list) and isinstance(scenes[0], dict)
        mappings[0]["character_id"] = replacement
        scenes[0]["character_ids"] = [replacement]
    elif field == "location":
        mappings = payload["location_mappings"]
        scenes = payload["scene_mappings"]
        assert isinstance(mappings, list) and isinstance(mappings[0], dict)
        assert isinstance(scenes, list) and isinstance(scenes[0], dict)
        mappings[0]["location_id"] = replacement
        scenes[0]["location_id"] = replacement
    else:
        payload[field] = replacement
        scenes = payload["scenes"]
        coverage = payload["plotline_coverage"]
        assert isinstance(scenes, list) and isinstance(scenes[0], dict)
        assert isinstance(coverage, list) and isinstance(coverage[0], dict)
        scenes[0]["plotline_ids"] = replacement
        coverage[0]["plotline_id"] = "EMBER-PL02"
    write_json(path, payload)

    index, errors = build_story_index(story, scripts, repository_root)

    assert index is None
    assert any(diagnostic in error for error in errors)


def test_build_story_index_rejects_unused_location_catalog_entry_from_outside_world(
    repository_root: Path, tmp_path: Path
):
    story, scripts = write_story_project(tmp_path)
    metadata_path = scripts / "EMBER-E01" / "screenplay-metadata.json"
    metadata = read_json(metadata_path)
    mappings = metadata["location_mappings"]
    assert isinstance(mappings, list)
    mappings.append({"location_id": "EMBER-LO003", "name": "Invented checkpoint"})
    write_json(metadata_path, metadata)

    index, errors = build_story_index(story, scripts, repository_root)

    assert index is None
    assert (
        "EMBER-E01/screenplay-metadata.json: location_mappings.1.location_id: "
        "dangling world location reference EMBER-LO003"
    ) in errors


def test_build_story_index_requires_every_story_event_in_a_unit(repository_root: Path, tmp_path: Path):
    story, scripts = write_story_project(tmp_path)
    (scripts / "EMBER-E02").rename(scripts / "EMBER-E02-hidden")

    index, errors = build_story_index(story, scripts, repository_root)

    assert index is None
    assert any("story event EMBER-EV002 has no script unit coverage" in error for error in errors)


def test_build_story_index_reports_unreadable_scripts_directory(
    repository_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    story, scripts = write_story_project(tmp_path)
    original = Path.iterdir

    def denied(path: Path):
        if path == scripts:
            raise PermissionError("denied")
        return original(path)

    monkeypatch.setattr(Path, "iterdir", denied)

    index, errors = build_story_index(story, scripts, repository_root)

    assert index is None
    assert errors == [f"{scripts}: unable to inspect story scripts directory: denied"]


def test_build_story_index_reports_malformed_concept_file_specifically(
    repository_root: Path, tmp_path: Path
):
    story, scripts = write_story_project(tmp_path)
    (story / "story-concept.json").write_text('{"project_id":', encoding="utf-8")

    index, errors = build_story_index(story, scripts, repository_root)

    assert index is None
    assert len(errors) == 1
    assert errors[0].startswith("story-concept.json: invalid JSON")


def test_script_directory_oserror_is_a_diagnostic(
    repository_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    script = tmp_path / "EMBER-E01"
    script.mkdir()

    def denied(_path: Path):
        raise PermissionError("denied")

    monkeypatch.setattr(Path, "iterdir", denied)

    assert validate_script_package(
        script, repository_root, "EMBER", "series"
    ) == [
        f"{script}: unable to inspect story script package directory: denied"
    ]

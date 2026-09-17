import json
from pathlib import Path

import pytest

from cine_skills.package import (
    resolve_scene_package_profile,
    validate_scene_package,
)
from tests.v1_fixtures import MANIFEST_ARTIFACTS, write_full_v1_package


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def rewrite_json(path: Path, update: object) -> None:
    value = json.loads(path.read_text(encoding="utf-8"))
    update(value)
    write_json(path, value)


@pytest.fixture
def package_dir(tmp_path: Path) -> Path:
    package = tmp_path / "S01"
    package.mkdir()
    write_json(
        package / "scene-beats.json",
        {
            "schema_version": "1.0",
            "scene_id": "S01",
            "scene_objective": "Ninel wakes and orients herself.",
            "turn": "The quiet becomes threatening.",
            "assumptions": [],
            "beats": [
                {
                    "beat_id": "S01-B01",
                    "evidence": "Ninel opens her eyes.",
                    "action": "She wakes.",
                    "tactic": "She listens.",
                    "value_shift": "calm to unease",
                    "visual_opportunity": "A close view of her eyes.",
                }
            ],
        },
    )
    write_json(
        package / "directing-plan.json",
        {
            "schema_version": "1.0",
            "scene_id": "S01",
            "concept": "A waking mind finds danger in silence.",
            "point_of_view": "Ninel",
            "performance_notes": ["Keep the awakening restrained."],
            "visual_strategy": ["Hold close to Ninel."],
            "rhythm": "Slow and attentive.",
            "assumptions": [],
        },
    )
    write_json(
        package / "blocking-plan.json",
        {
            "schema_version": "1.0",
            "scene_id": "S01",
            "space": "A narrow cabin.",
            "axis": "The bunk-to-door line.",
            "positions": ["Ninel begins in the bunk."],
            "moves": [
                {
                    "beat_id": "S01-B01",
                    "character": "Ninel",
                    "start": "bunk",
                    "end": "seated",
                    "motivation": "She wakes.",
                }
            ],
            "continuity_rules": ["Preserve the bunk-to-door axis."],
            "assumptions": [],
        },
    )
    write_json(
        package / "camera-movement-plan.json",
        {
            "schema_version": "1.0",
            "scene_id": "S01",
            "movement_philosophy": "Let stillness create pressure.",
            "moves": [
                {
                    "move_id": "S01-M01",
                    "beat_ids": ["S01-B01"],
                    "name_ru": "Статичный кадр",
                    "name_en": "Static frame",
                    "movement": "static",
                    "direction": "none",
                    "speed": "still",
                    "framing": "medium",
                    "start": "Ninel asleep",
                    "end": "Ninel awake",
                    "purpose": "Make the awakening feel observed.",
                    "ai_video_prompt": "A still medium shot of Ninel waking.",
                }
            ],
            "assumptions": [],
        },
    )
    write_json(
        package / "shot-list.json",
        {
            "schema_version": "1.0",
            "scene_id": "S01",
            "assumptions": [],
            "shots": [
                {
                    "shot_id": "S01-SH001",
                    "beat_ids": ["S01-B01"],
                    "size": "medium",
                    "angle": "eye-level",
                    "lens_mm": 50,
                    "camera_support": "tripod",
                    "movement": "static",
                    "subject": "Ninel",
                    "action": "opens her eyes",
                    "composition": "centered medium single",
                    "dramatic_purpose": "establish disorientation",
                    "audio": "low ship hum",
                    "continuity": ["screen direction neutral"],
                }
            ],
        },
    )
    return package


@pytest.fixture
def full_package_dir(tmp_path: Path) -> Path:
    package = tmp_path / "full" / "S01"
    write_full_v1_package(package)
    return package


def test_valid_package_passes(package_dir: Path, repository_root: Path) -> None:
    assert validate_scene_package(package_dir, repository_root) == []


def test_auto_profile_keeps_legacy_package_compatible(package_dir: Path) -> None:
    assert resolve_scene_package_profile(package_dir) == "core-v0.1"


def test_importing_v2_contracts_does_not_change_scene_profiles(
    repository_root: Path,
) -> None:
    from cine_skills import project_contracts

    assert project_contracts.FULL_CREATIVE_PROFILE == "full-creative-v2"
    assert (
        resolve_scene_package_profile(
            repository_root / "examples/ninel/scenes/S01"
        )
        == "core-v0.1"
    )
    assert (
        resolve_scene_package_profile(
            repository_root / "examples/ninel-v1/scenes/S01"
        )
        == "full-v1"
    )


def test_auto_profile_selects_full_when_manifest_exists(package_dir: Path) -> None:
    write_json(package_dir / "package-manifest.json", {})

    assert resolve_scene_package_profile(package_dir) == "full-v1"


@pytest.mark.parametrize("entry_kind", ["directory", "broken-symlink"])
def test_auto_profile_does_not_downgrade_malformed_manifest_entry(
    package_dir: Path, repository_root: Path, entry_kind: str
) -> None:
    manifest = package_dir / "package-manifest.json"
    if entry_kind == "directory":
        manifest.mkdir()
    else:
        manifest.symlink_to("missing-manifest-target.json")

    assert resolve_scene_package_profile(package_dir) == "full-v1"
    errors = validate_scene_package(package_dir, repository_root)
    assert any(
        error == "package-manifest.json: required file is missing"
        for error in errors
    )


def test_package_reports_missing_required_file(
    package_dir: Path, repository_root: Path
) -> None:
    (package_dir / "shot-list.json").unlink()

    errors = validate_scene_package(package_dir, repository_root)

    assert any("shot-list.json" in error and "required file" in error for error in errors)


@pytest.mark.parametrize("entry_kind", ["file", "directory"])
def test_full_package_rejects_unexpected_entry(
    full_package_dir: Path, repository_root: Path, entry_kind: str
) -> None:
    unexpected = full_package_dir / "unexpected-generated-media"
    if entry_kind == "file":
        unexpected.write_bytes(b"not canonical")
    else:
        unexpected.mkdir()

    errors = validate_scene_package(
        full_package_dir, repository_root, profile="full-v1"
    )

    assert errors == [
        "unexpected-generated-media: unexpected entry for full-v1 package"
    ]


def test_full_package_reports_directory_inspection_error(
    full_package_dir: Path, repository_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_iterdir = Path.iterdir

    def deny_package_listing(path: Path):
        if path == full_package_dir:
            raise PermissionError("inspection denied")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", deny_package_listing)

    errors = validate_scene_package(
        full_package_dir, repository_root, profile="full-v1"
    )

    assert errors == [
        f"{full_package_dir}: unable to inspect package directory: inspection denied"
    ]


def test_package_rejects_mismatched_scene_id(
    package_dir: Path, repository_root: Path
) -> None:
    rewrite_json(package_dir / "directing-plan.json", lambda value: value.update(scene_id="S02"))

    errors = validate_scene_package(package_dir, repository_root)

    assert any("directing-plan.json" in error and "scene_id" in error and "S02" in error for error in errors)


def test_package_rejects_duplicate_beat_id(
    package_dir: Path, repository_root: Path
) -> None:
    def add_duplicate(value: dict[str, object]) -> None:
        beats = value["beats"]
        assert isinstance(beats, list)
        beats.append(
            {
                "beat_id": "S01-B01",
                "evidence": "The cabin hum continues.",
                "action": "She listens.",
                "tactic": "She holds still.",
                "value_shift": "unease to dread",
                "visual_opportunity": "A held profile.",
            }
        )

    rewrite_json(package_dir / "scene-beats.json", add_duplicate)

    errors = validate_scene_package(package_dir, repository_root)

    assert any("S01-B01" in error and "duplicate beat ID" in error for error in errors)


def test_package_rejects_wrong_shot_id_prefix(
    package_dir: Path, repository_root: Path
) -> None:
    rewrite_json(
        package_dir / "shot-list.json",
        lambda value: value["shots"][0].update(shot_id="S02-SH001"),
    )

    errors = validate_scene_package(package_dir, repository_root)

    assert any("S02-SH001" in error and "prefix S01-" in error for error in errors)


def test_package_rejects_malformed_beat_declaration_and_matching_references(
    package_dir: Path, repository_root: Path
) -> None:
    malformed_beat_id = "S01-alt-B01"
    rewrite_json(
        package_dir / "scene-beats.json",
        lambda value: value["beats"][0].update(beat_id=malformed_beat_id),
    )
    rewrite_json(
        package_dir / "blocking-plan.json",
        lambda value: value["moves"][0].update(beat_id=malformed_beat_id),
    )
    rewrite_json(
        package_dir / "camera-movement-plan.json",
        lambda value: value["moves"][0].update(beat_ids=[malformed_beat_id]),
    )
    rewrite_json(
        package_dir / "shot-list.json",
        lambda value: value["shots"][0].update(beat_ids=[malformed_beat_id]),
    )

    errors = validate_scene_package(package_dir, repository_root)

    for location in [
        "scene-beats.json: beats[0].beat_id",
        "blocking-plan.json: moves[0].beat_id",
        "camera-movement-plan.json: moves[0].beat_ids[0]",
        "shot-list.json: shots[0].beat_ids[0]",
    ]:
        assert any(location in error and "S01-B##" in error for error in errors)


@pytest.mark.parametrize(
    ("filename", "collection", "id_name", "invalid_id", "expected_format"),
    [
        (
            "camera-movement-plan.json",
            "moves",
            "move_id",
            "S01-alt-M01",
            "S01-M##",
        ),
        ("shot-list.json", "shots", "shot_id", "S01-alt-SH001", "S01-SH###"),
    ],
)
def test_package_rejects_category_infix_in_declared_ids(
    package_dir: Path,
    repository_root: Path,
    filename: str,
    collection: str,
    id_name: str,
    invalid_id: str,
    expected_format: str,
) -> None:
    rewrite_json(
        package_dir / filename,
        lambda value: value[collection][0].update({id_name: invalid_id}),
    )

    errors = validate_scene_package(package_dir, repository_root)

    assert any(invalid_id in error and expected_format in error for error in errors)


def test_package_rejects_dangling_shot_beat_reference(
    package_dir: Path, repository_root: Path
) -> None:
    rewrite_json(
        package_dir / "shot-list.json",
        lambda value: value["shots"][0].update(beat_ids=["S01-B99"]),
    )

    errors = validate_scene_package(package_dir, repository_root)

    assert any("S01-B99" in error and "unknown beat" in error for error in errors)


def test_package_rejects_uncovered_beat(
    package_dir: Path, repository_root: Path
) -> None:
    def add_uncovered_beat(value: dict[str, object]) -> None:
        beats = value["beats"]
        assert isinstance(beats, list)
        beats.append(
            {
                "beat_id": "S01-B02",
                "evidence": "Ninel turns toward the door.",
                "action": "She turns.",
                "tactic": "She searches for danger.",
                "value_shift": "dread to resolve",
                "visual_opportunity": "A profile against the door.",
            }
        )

    rewrite_json(package_dir / "scene-beats.json", add_uncovered_beat)

    errors = validate_scene_package(package_dir, repository_root)

    assert any("S01-B02" in error and "uncovered beat" in error for error in errors)


def test_valid_full_v1_package_passes_auto_and_explicit_profiles(
    full_package_dir: Path, repository_root: Path
) -> None:
    assert resolve_scene_package_profile(full_package_dir) == "full-v1"
    assert validate_scene_package(full_package_dir, repository_root) == []
    assert (
        validate_scene_package(full_package_dir, repository_root, profile="full-v1")
        == []
    )


@pytest.mark.parametrize("filename", ["source-scene.md", "lighting-plan.json"])
def test_full_v1_package_reports_missing_canonical_file(
    full_package_dir: Path, repository_root: Path, filename: str
) -> None:
    (full_package_dir / filename).unlink()

    errors = validate_scene_package(full_package_dir, repository_root, profile="full-v1")

    assert any(filename in error and "required file" in error for error in errors)


def test_full_v1_package_rejects_mismatched_new_artifact_scene_id(
    full_package_dir: Path, repository_root: Path
) -> None:
    def change_scene(value: dict[str, object]) -> None:
        value["scene_id"] = "S02"
        cues = value["cues"]
        assert isinstance(cues, list)
        cue = cues[0]
        assert isinstance(cue, dict)
        cue["cue_id"] = "S02-A01"
        cue["beat_ids"] = ["S02-B01"]
        cue["shot_ids"] = ["S02-SH001"]

    rewrite_json(
        full_package_dir / "sound-plan.json",
        change_scene,
    )

    errors = validate_scene_package(full_package_dir, repository_root, profile="full-v1")

    assert any("sound-plan.json" in error and "scene_id" in error for error in errors)


@pytest.mark.parametrize(
    ("filename", "collection", "id_field", "invalid_id", "expected"),
    [
        ("visual-language-plan.json", "rules", "rule_id", "S01-alt-V01", "S01-V##"),
        ("lighting-plan.json", "setups", "setup_id", "S01-alt-L01", "S01-L##"),
        ("sound-plan.json", "cues", "cue_id", "S01-alt-A01", "S01-A##"),
        ("storyboard-plan.json", "panels", "panel_id", "S01-alt-SB001", "S01-SB###"),
        ("production-breakdown.json", "items", "item_id", "S01-alt-PD001", "S01-PD###"),
        ("continuity-plan.json", "items", "continuity_id", "S01-alt-CN001", "S01-CN###"),
    ],
)
def test_full_v1_package_rejects_malformed_category_ids(
    full_package_dir: Path,
    repository_root: Path,
    filename: str,
    collection: str,
    id_field: str,
    invalid_id: str,
    expected: str,
) -> None:
    rewrite_json(
        full_package_dir / filename,
        lambda value: value[collection][0].update({id_field: invalid_id}),
    )

    errors = validate_scene_package(full_package_dir, repository_root, profile="full-v1")

    assert any(filename in error and expected in error for error in errors)


@pytest.mark.parametrize(
    ("filename", "collection"),
    [
        ("visual-language-plan.json", "rules"),
        ("lighting-plan.json", "setups"),
        ("sound-plan.json", "cues"),
        ("storyboard-plan.json", "panels"),
        ("production-breakdown.json", "items"),
        ("continuity-plan.json", "items"),
    ],
)
def test_full_v1_package_rejects_duplicate_category_ids(
    full_package_dir: Path,
    repository_root: Path,
    filename: str,
    collection: str,
) -> None:
    def duplicate(value: dict[str, object]) -> None:
        items = value[collection]
        assert isinstance(items, list)
        original = items[0]
        assert isinstance(original, dict)
        items.append(dict(original))

    rewrite_json(full_package_dir / filename, duplicate)

    errors = validate_scene_package(full_package_dir, repository_root, profile="full-v1")

    assert any(filename in error and "duplicate" in error for error in errors)


@pytest.mark.parametrize(
    ("filename", "collection", "field", "dangling", "expected_label"),
    [
        ("visual-language-plan.json", "rules", "beat_ids", "S01-B99", "unknown beat"),
        ("lighting-plan.json", "setups", "beat_ids", "S01-B99", "unknown beat"),
        ("lighting-plan.json", "setups", "shot_ids", "S01-SH999", "unknown shot"),
        ("sound-plan.json", "cues", "beat_ids", "S01-B99", "unknown beat"),
        ("sound-plan.json", "cues", "shot_ids", "S01-SH999", "unknown shot"),
        ("storyboard-plan.json", "panels", "shot_id", "S01-SH999", "unknown shot"),
        ("production-breakdown.json", "items", "beat_ids", "S01-B99", "unknown beat"),
        ("production-breakdown.json", "items", "shot_ids", "S01-SH999", "unknown shot"),
        ("continuity-plan.json", "items", "shot_ids", "S01-SH999", "unknown shot"),
    ],
)
def test_full_v1_package_rejects_dangling_new_references(
    full_package_dir: Path,
    repository_root: Path,
    filename: str,
    collection: str,
    field: str,
    dangling: str,
    expected_label: str,
) -> None:
    def replace_reference(value: dict[str, object]) -> None:
        items = value[collection]
        assert isinstance(items, list)
        item = items[0]
        assert isinstance(item, dict)
        item[field] = dangling if field == "shot_id" else [dangling]

    rewrite_json(full_package_dir / filename, replace_reference)

    errors = validate_scene_package(full_package_dir, repository_root, profile="full-v1")

    assert any(
        filename in error and dangling in error and expected_label in error
        for error in errors
    )


def add_second_full_v1_shot(package: Path) -> None:
    def add_shot(value: dict[str, object]) -> None:
        shots = value["shots"]
        assert isinstance(shots, list)
        shot = dict(shots[0])
        shot["shot_id"] = "S01-SH002"
        shots.append(shot)

    rewrite_json(package / "shot-list.json", add_shot)


@pytest.mark.parametrize(
    "filename",
    [
        "lighting-plan.json",
        "sound-plan.json",
        "storyboard-plan.json",
        "continuity-plan.json",
    ],
)
def test_full_v1_package_requires_every_shot_covered(
    full_package_dir: Path, repository_root: Path, filename: str
) -> None:
    add_second_full_v1_shot(full_package_dir)

    errors = validate_scene_package(full_package_dir, repository_root, profile="full-v1")

    assert any(filename in error and "uncovered shot S01-SH002" in error for error in errors)


def test_full_v1_package_allows_multiple_storyboard_panels_for_one_shot(
    full_package_dir: Path, repository_root: Path
) -> None:
    def add_panel(value: dict[str, object]) -> None:
        panels = value["panels"]
        assert isinstance(panels, list)
        panel = dict(panels[0])
        panel["panel_id"] = "S01-SB002"
        panel["moment"] = "Ninel completes the move."
        panels.append(panel)

    rewrite_json(full_package_dir / "storyboard-plan.json", add_panel)

    assert (
        validate_scene_package(full_package_dir, repository_root, profile="full-v1")
        == []
    )


@pytest.mark.parametrize("mutation", ["missing", "reordered", "extra"])
def test_full_v1_package_rejects_changed_manifest_order(
    full_package_dir: Path, repository_root: Path, mutation: str
) -> None:
    def mutate_manifest(value: dict[str, object]) -> None:
        artifacts = value["artifacts"]
        assert isinstance(artifacts, list)
        if mutation == "missing":
            artifacts.pop()
        elif mutation == "reordered":
            artifacts[0], artifacts[1] = artifacts[1], artifacts[0]
        else:
            artifacts.append(
                {
                    "filename": "extra.json",
                    "schema_version": "1.0",
                    "dependency_order": len(MANIFEST_ARTIFACTS) + 1,
                }
            )

    rewrite_json(full_package_dir / "package-manifest.json", mutate_manifest)

    errors = validate_scene_package(full_package_dir, repository_root, profile="full-v1")

    assert any("package-manifest.json" in error and "artifact" in error for error in errors)

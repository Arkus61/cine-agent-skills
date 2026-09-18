from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping

from . import __version__
from .artifacts import load_json_object, validate_artifact


CORE_PROFILE = "scene-core"
FULL_PROFILE = "scene-full"

CORE_ARTIFACT_FILES = (
    ("scene-beats.json", "scene-beats"),
    ("directing-plan.json", "directing-plan"),
    ("blocking-plan.json", "blocking-plan"),
    ("camera-movement-plan.json", "camera-movement-plan"),
    ("shot-list.json", "shot-list"),
)

FULL_ARTIFACT_FILES = (
    ("scene-beats.json", "scene-beats"),
    ("directing-plan.json", "directing-plan"),
    ("visual-language-plan.json", "visual-language-plan"),
    ("blocking-plan.json", "blocking-plan"),
    ("camera-movement-plan.json", "camera-movement-plan"),
    ("shot-list.json", "shot-list"),
    ("lighting-plan.json", "lighting-plan"),
    ("sound-plan.json", "sound-plan"),
    ("storyboard-plan.json", "storyboard-plan"),
    ("production-breakdown.json", "production-breakdown"),
    ("continuity-plan.json", "continuity-plan"),
    ("package-manifest.json", "package-manifest"),
)

FULL_SOURCE_FILE = "source-scene.md"
FULL_MANIFEST_ARTIFACTS = tuple(
    filename for filename, _schema_name in FULL_ARTIFACT_FILES[:-1]
)

_PROFILE_ARTIFACTS = {
    CORE_PROFILE: CORE_ARTIFACT_FILES,
    FULL_PROFILE: FULL_ARTIFACT_FILES,
}

_BEAT_ID_SUFFIX = r"B[0-9]{2,}"
_MOVEMENT_ID_SUFFIX = r"M[0-9]{2,}"
_SHOT_ID_SUFFIX = r"SH[0-9]{3,}"


def resolve_scene_package_profile(package_dir: Path, requested: str = "auto") -> str:
    """Resolve an explicit or manifest-selected scene-package profile."""
    if requested == "auto":
        manifest = Path(package_dir) / "package-manifest.json"
        return (
            FULL_PROFILE
            if manifest.exists() or manifest.is_symlink()
            else CORE_PROFILE
        )
    if requested not in _PROFILE_ARTIFACTS:
        allowed = ", ".join(("auto", CORE_PROFILE, FULL_PROFILE))
        raise ValueError(f"unknown package profile {requested!r}; expected one of {allowed}")
    return requested


def validate_scene_package(
    package_dir: Path, root: Path, profile: str = "auto"
) -> list[str]:
    """Validate a scene-core or scene-full scene package."""
    package = Path(package_dir)
    resolved_profile = resolve_scene_package_profile(package, profile)
    payloads: dict[str, Mapping[str, Any]] = {}
    errors: list[str] = []

    if resolved_profile == FULL_PROFILE:
        if package.is_dir():
            expected_files = {FULL_SOURCE_FILE} | {
                filename for filename, _schema_name in FULL_ARTIFACT_FILES
            }
            try:
                actual_entries = {entry.name for entry in package.iterdir()}
            except OSError as exc:
                errors.append(
                    f"{package}: unable to inspect package directory: {exc}"
                )
            else:
                for filename in actual_entries - expected_files:
                    errors.append(
                        f"{filename}: unexpected entry for {FULL_PROFILE} package"
                    )
        source_path = package / FULL_SOURCE_FILE
        if not source_path.is_file():
            errors.append(f"{FULL_SOURCE_FILE}: required file is missing")

    for filename, schema_name in _PROFILE_ARTIFACTS[resolved_profile]:
        path = package / filename
        if not path.is_file():
            errors.append(f"{filename}: required file is missing")
            continue

        payload, load_errors = load_json_object(path)
        if load_errors:
            errors.extend(f"{filename}: {error}" for error in load_errors)
            continue
        assert payload is not None

        schema_errors = validate_artifact(schema_name, payload, root)
        if schema_errors:
            errors.extend(f"{filename}: {error}" for error in schema_errors)
            continue
        payloads[filename] = payload

    _validate_scene_ids(payloads, errors)
    scene_id = _package_scene_id(payloads)
    if scene_id is not None:
        _validate_declared_ids(payloads, scene_id, errors)
        _validate_beat_references(payloads, scene_id, errors)
        _validate_shot_coverage(payloads, errors)
        if resolved_profile == FULL_PROFILE:
            _validate_full_references(payloads, errors)
            _validate_full_shot_coverage(payloads, errors)
            _validate_manifest_contract(payloads, errors)
    return sorted(errors)


def _validate_full_references(
    payloads: Mapping[str, Mapping[str, Any]], errors: list[str]
) -> None:
    declared_beats = _beat_ids(payloads.get("scene-beats.json"))
    declared_shots = _shot_ids(payloads.get("shot-list.json"))

    if declared_beats is not None:
        for filename, collection_name in (
            ("visual-language-plan.json", "rules"),
            ("lighting-plan.json", "setups"),
            ("sound-plan.json", "cues"),
            ("production-breakdown.json", "items"),
        ):
            _validate_many_declared_references(
                payloads.get(filename),
                filename,
                collection_name,
                "beat_ids",
                declared_beats,
                "beat",
                errors,
            )

    if declared_shots is not None:
        for filename, collection_name in (
            ("lighting-plan.json", "setups"),
            ("sound-plan.json", "cues"),
            ("production-breakdown.json", "items"),
            ("continuity-plan.json", "items"),
        ):
            _validate_many_declared_references(
                payloads.get(filename),
                filename,
                collection_name,
                "shot_ids",
                declared_shots,
                "shot",
                errors,
            )
        _validate_single_declared_references(
            payloads.get("storyboard-plan.json"),
            "storyboard-plan.json",
            "panels",
            "shot_id",
            declared_shots,
            "shot",
            errors,
        )


def _shot_ids(payload: Mapping[str, Any] | None) -> set[str] | None:
    if payload is None:
        return None
    shots = payload["shots"]
    assert isinstance(shots, list)
    return {
        shot["shot_id"]
        for shot in shots
        if isinstance(shot, Mapping) and isinstance(shot.get("shot_id"), str)
    }


def _validate_many_declared_references(
    payload: Mapping[str, Any] | None,
    filename: str,
    collection_name: str,
    reference_name: str,
    declared: set[str],
    label: str,
    errors: list[str],
) -> None:
    if payload is None:
        return
    items = payload[collection_name]
    assert isinstance(items, list)
    for item_index, item in enumerate(items):
        assert isinstance(item, Mapping)
        references = item[reference_name]
        assert isinstance(references, list)
        for reference_index, reference in enumerate(references):
            assert isinstance(reference, str)
            if reference not in declared:
                errors.append(
                    f"{filename}: {collection_name}[{item_index}]."
                    f"{reference_name}[{reference_index}]: unknown {label} {reference}"
                )


def _validate_single_declared_references(
    payload: Mapping[str, Any] | None,
    filename: str,
    collection_name: str,
    reference_name: str,
    declared: set[str],
    label: str,
    errors: list[str],
) -> None:
    if payload is None:
        return
    items = payload[collection_name]
    assert isinstance(items, list)
    for item_index, item in enumerate(items):
        assert isinstance(item, Mapping)
        reference = item[reference_name]
        assert isinstance(reference, str)
        if reference not in declared:
            errors.append(
                f"{filename}: {collection_name}[{item_index}].{reference_name}: "
                f"unknown {label} {reference}"
            )


def _validate_full_shot_coverage(
    payloads: Mapping[str, Mapping[str, Any]], errors: list[str]
) -> None:
    declared_shots = _shot_ids(payloads.get("shot-list.json"))
    if declared_shots is None:
        return
    coverage_contracts = (
        ("lighting-plan.json", "setups", "shot_ids", False),
        ("sound-plan.json", "cues", "shot_ids", False),
        ("storyboard-plan.json", "panels", "shot_id", True),
        ("continuity-plan.json", "items", "shot_ids", False),
    )
    for filename, collection_name, reference_name, single in coverage_contracts:
        payload = payloads.get(filename)
        if payload is None:
            continue
        covered: set[str] = set()
        items = payload[collection_name]
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, Mapping)
            references = item[reference_name]
            if single:
                if isinstance(references, str):
                    covered.add(references)
            else:
                assert isinstance(references, list)
                covered.update(
                    reference for reference in references if isinstance(reference, str)
                )
        for shot_id in declared_shots - covered:
            errors.append(f"{filename}: uncovered shot {shot_id}")


def _validate_manifest_contract(
    payloads: Mapping[str, Mapping[str, Any]], errors: list[str]
) -> None:
    manifest = payloads.get("package-manifest.json")
    if manifest is None:
        return
    expected = [
        {
            "filename": filename,
            "schema_version": __version__,
            "dependency_order": order,
        }
        for order, filename in enumerate(FULL_MANIFEST_ARTIFACTS, start=1)
    ]
    if manifest["artifacts"] != expected:
        ordered_names = ", ".join(FULL_MANIFEST_ARTIFACTS)
        errors.append(
            "package-manifest.json: artifacts must list the exact scene-full "
            f"dependency order: {ordered_names}"
        )


def _package_scene_id(payloads: Mapping[str, Mapping[str, Any]]) -> str | None:
    for payload in payloads.values():
        scene_id = payload.get("scene_id")
        if isinstance(scene_id, str) and scene_id:
            return scene_id
    return None


def _validate_scene_ids(
    payloads: Mapping[str, Mapping[str, Any]], errors: list[str]
) -> None:
    scene_id = _package_scene_id(payloads)
    if scene_id is None:
        return
    for filename, payload in payloads.items():
        declared_scene_id = payload.get("scene_id")
        if declared_scene_id != scene_id:
            errors.append(
                f"{filename}: scene_id {declared_scene_id!r} does not match {scene_id!r}"
            )


def _validate_declared_ids(
    payloads: Mapping[str, Mapping[str, Any]], scene_id: str, errors: list[str]
) -> None:
    _validate_ids(
        payloads.get("scene-beats.json"),
        "scene-beats.json",
        "beats",
        "beat_id",
        "beat",
        scene_id,
        _BEAT_ID_SUFFIX,
        "B##",
        errors,
    )
    _validate_ids(
        payloads.get("camera-movement-plan.json"),
        "camera-movement-plan.json",
        "moves",
        "move_id",
        "movement",
        scene_id,
        _MOVEMENT_ID_SUFFIX,
        "M##",
        errors,
    )
    _validate_ids(
        payloads.get("shot-list.json"),
        "shot-list.json",
        "shots",
        "shot_id",
        "shot",
        scene_id,
        _SHOT_ID_SUFFIX,
        "SH###",
        errors,
    )


def _validate_ids(
    payload: Mapping[str, Any] | None,
    filename: str,
    collection_name: str,
    id_name: str,
    label: str,
    scene_id: str,
    suffix_pattern: str,
    suffix_example: str,
    errors: list[str],
) -> None:
    if payload is None:
        return
    items = payload[collection_name]
    assert isinstance(items, list)
    seen: set[str] = set()
    for index, item in enumerate(items):
        assert isinstance(item, Mapping)
        identifier = item[id_name]
        assert isinstance(identifier, str)
        location = f"{filename}: {collection_name}[{index}].{id_name}"
        if identifier in seen:
            errors.append(f"{location}: duplicate {label} ID {identifier}")
        else:
            seen.add(identifier)
        _validate_id_format(
            identifier,
            location,
            scene_id,
            suffix_pattern,
            suffix_example,
            errors,
        )


def _validate_id_format(
    identifier: str,
    location: str,
    scene_id: str,
    suffix_pattern: str,
    suffix_example: str,
    errors: list[str],
) -> None:
    if re.fullmatch(
        rf"{re.escape(scene_id)}-{suffix_pattern}", identifier
    ) is None:
        errors.append(
            f"{location}: {identifier!r} must match {scene_id}-{suffix_example} "
            f"with scene prefix {scene_id}-"
        )


def _beat_ids(payload: Mapping[str, Any] | None) -> set[str] | None:
    if payload is None:
        return None
    beats = payload["beats"]
    assert isinstance(beats, list)
    return {
        beat["beat_id"]
        for beat in beats
        if isinstance(beat, Mapping) and isinstance(beat.get("beat_id"), str)
    }


def _validate_beat_references(
    payloads: Mapping[str, Mapping[str, Any]], scene_id: str, errors: list[str]
) -> None:
    declared_beats = _beat_ids(payloads.get("scene-beats.json"))
    if declared_beats is None:
        return
    _validate_blocking_beat_references(
        payloads.get("blocking-plan.json"), declared_beats, scene_id, errors
    )
    _validate_many_beat_references(
        payloads.get("camera-movement-plan.json"),
        "camera-movement-plan.json",
        "moves",
        declared_beats,
        scene_id,
        errors,
    )
    _validate_many_beat_references(
        payloads.get("shot-list.json"),
        "shot-list.json",
        "shots",
        declared_beats,
        scene_id,
        errors,
    )


def _validate_blocking_beat_references(
    payload: Mapping[str, Any] | None,
    declared_beats: set[str],
    scene_id: str,
    errors: list[str],
) -> None:
    if payload is None:
        return
    moves = payload["moves"]
    assert isinstance(moves, list)
    for index, move in enumerate(moves):
        assert isinstance(move, Mapping)
        beat_id = move["beat_id"]
        assert isinstance(beat_id, str)
        location = f"blocking-plan.json: moves[{index}].beat_id"
        _validate_id_format(
            beat_id, location, scene_id, _BEAT_ID_SUFFIX, "B##", errors
        )
        if beat_id not in declared_beats:
            errors.append(f"{location}: unknown beat {beat_id}")


def _validate_many_beat_references(
    payload: Mapping[str, Any] | None,
    filename: str,
    collection_name: str,
    declared_beats: set[str],
    scene_id: str,
    errors: list[str],
) -> None:
    if payload is None:
        return
    items = payload[collection_name]
    assert isinstance(items, list)
    for item_index, item in enumerate(items):
        assert isinstance(item, Mapping)
        beat_ids = item["beat_ids"]
        assert isinstance(beat_ids, list)
        for beat_index, beat_id in enumerate(beat_ids):
            assert isinstance(beat_id, str)
            location = (
                f"{filename}: {collection_name}[{item_index}].beat_ids[{beat_index}]"
            )
            _validate_id_format(
                beat_id, location, scene_id, _BEAT_ID_SUFFIX, "B##", errors
            )
            if beat_id not in declared_beats:
                errors.append(f"{location}: unknown beat {beat_id}")


def _validate_shot_coverage(
    payloads: Mapping[str, Mapping[str, Any]], errors: list[str]
) -> None:
    declared_beats = _beat_ids(payloads.get("scene-beats.json"))
    shots = payloads.get("shot-list.json")
    if declared_beats is None or shots is None:
        return
    covered_beats: set[str] = set()
    shot_items = shots["shots"]
    assert isinstance(shot_items, list)
    for shot in shot_items:
        assert isinstance(shot, Mapping)
        beat_ids = shot["beat_ids"]
        assert isinstance(beat_ids, list)
        covered_beats.update(beat_id for beat_id in beat_ids if isinstance(beat_id, str))
    for beat_id in declared_beats - covered_beats:
        errors.append(f"shot-list.json: uncovered beat {beat_id}")

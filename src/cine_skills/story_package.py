"""Validation for story layers and screenplay unit packages."""

from __future__ import annotations

from collections.abc import Collection, Mapping
from pathlib import Path
from typing import Any

from .artifacts import (
    load_json_object,
    validate_character_arc_event_references,
)
from .fountain import inspect_fountain_file, validate_screenplay_metadata
from .package import FULL_PROFILE, validate_scene_package
from .project_contracts import (
    PROJECT_FORMATS,
    STORY_PROFILE,
    ArtifactContract,
    ProjectIndex,
    required_story_artifacts,
)
from .project_validation import (
    collect_ids,
    inspect_exact_entries,
    load_validated_artifacts,
    validate_layer_manifest,
)


SCRIPT_CONTRACTS = (
    ArtifactContract("unit-outline.json", "unit-outline", 1),
    ArtifactContract("screenplay.fountain", "fountain", 2),
    ArtifactContract("screenplay-metadata.json", "screenplay-metadata", 3),
    ArtifactContract("script-revision-plan.json", "script-revision-plan", 4),
    ArtifactContract("scenes", "scene-full", 5),
    ArtifactContract("script-manifest.json", "layer-manifest", 6),
)

_SCRIPT_JSON_CONTRACTS = tuple(
    contract
    for contract in SCRIPT_CONTRACTS
    if contract.filename.endswith(".json")
)


def _existing_contracts(
    directory: Path, contracts: Collection[ArtifactContract]
) -> tuple[ArtifactContract, ...]:
    return tuple(
        contract
        for contract in contracts
        if (Path(directory) / contract.filename).is_file()
    )


def _wrong_file_type_errors(
    directory: Path, contracts: Collection[ArtifactContract]
) -> list[str]:
    errors: list[str] = []
    for contract in contracts:
        path = Path(directory) / contract.filename
        if (path.exists() or path.is_symlink()) and not path.is_file():
            errors.append(f"{contract.filename}: required file is missing")
    return errors


def _project_id_errors(
    payloads: Mapping[str, Mapping[str, Any]], expected: str
) -> list[str]:
    errors: list[str] = []
    for filename, payload in payloads.items():
        project_id = payload.get("project_id")
        if isinstance(project_id, str) and project_id != expected:
            errors.append(
                f"{filename}: project_id {project_id} does not match {expected}"
            )
    return errors


def _manifest_context_errors(
    payload: Mapping[str, Any] | None, filename: str, layer: str
) -> list[str]:
    if payload is None:
        return []
    errors: list[str] = []
    if payload.get("layer") != layer:
        errors.append(
            f"{filename}: layer {payload.get('layer')} does not match {layer}"
        )
    if payload.get("profile") != STORY_PROFILE:
        errors.append(
            f"{filename}: profile {payload.get('profile')} does not match "
            f"{STORY_PROFILE}"
        )
    return errors


def _source_ids(payload: Mapping[str, Any], field: str) -> set[str]:
    values = payload.get(field)
    if not isinstance(values, list):
        return set()
    return {value for value in values if isinstance(value, str)}


def _exact_source_errors(
    payload: Mapping[str, Any],
    filename: str,
    field: str,
    expected: Collection[str],
    label: str,
) -> list[str]:
    values = payload.get(field)
    if not isinstance(values, list):
        return []
    if values == sorted(expected):
        return []
    return [
        f"{filename}: {field} must exactly match declared {label} IDs: "
        f"{', '.join(sorted(expected))}"
    ]


def validate_story_package(
    story_dir: Path, root: Path, project_format: str
) -> list[str]:
    """Validate exact story-layer membership, schemas, context, and references."""
    story = Path(story_dir)
    if project_format not in PROJECT_FORMATS:
        return [
            f"unknown project format {project_format}; allowed values: "
            f"{', '.join(sorted(PROJECT_FORMATS))}"
        ]
    contracts = required_story_artifacts(project_format)
    inventory_errors = inspect_exact_entries(
        story, {contract.filename for contract in contracts}, STORY_PROFILE
    )
    if any("unable to inspect" in error for error in inventory_errors):
        return inventory_errors

    payloads, errors = load_validated_artifacts(
        story, _existing_contracts(story, contracts), root
    )
    errors.extend(inventory_errors)
    errors.extend(_wrong_file_type_errors(story, contracts))

    concept = payloads.get("story-concept.json")
    if concept is not None:
        project_id = concept.get("project_id")
        if isinstance(project_id, str):
            errors.extend(_project_id_errors(payloads, project_id))
        declared_format = concept.get("project_format")
        if declared_format != project_format:
            errors.append(
                "story-concept.json: project_format "
                f"{declared_format} does not match {project_format}"
            )

    manifest = payloads.get("story-manifest.json")
    errors.extend(
        _manifest_context_errors(manifest, "story-manifest.json", "story")
    )
    if manifest is not None:
        errors.extend(
            validate_layer_manifest(manifest, contracts, "story-manifest.json")
        )

    structure = payloads.get("story-structure.json")
    arcs = payloads.get("character-arcs.json")
    if structure is not None and arcs is not None:
        event_ids = collect_ids(structure, "events", "event_id")
        errors.extend(
            f"character-arcs.json: {error}"
            for error in validate_character_arc_event_references(arcs, event_ids)
        )

    season = payloads.get("season-arc.json")
    if season is not None and structure is not None and arcs is not None:
        errors.extend(
            _exact_source_errors(
                season,
                "season-arc.json",
                "source_plotline_ids",
                collect_ids(structure, "plotlines", "plotline_id"),
                "story plotline",
            )
        )
        errors.extend(
            _exact_source_errors(
                season,
                "season-arc.json",
                "source_event_ids",
                collect_ids(structure, "events", "event_id"),
                "story event",
            )
        )
        errors.extend(
            _exact_source_errors(
                season,
                "season-arc.json",
                "source_character_ids",
                collect_ids(arcs, "characters", "character_id"),
                "story character",
            )
        )
    return sorted(set(errors))


def validate_script_package(
    script_dir: Path,
    root: Path,
    project_id: str,
    project_format: str,
) -> list[str]:
    """Validate one exact screenplay-unit package and its scene-full scenes."""
    script = Path(script_dir)
    expected_names = {contract.filename for contract in SCRIPT_CONTRACTS}
    inventory_errors = inspect_exact_entries(
        script, expected_names, f"{STORY_PROFILE} script"
    )
    if any("unable to inspect" in error for error in inventory_errors):
        return inventory_errors

    payloads, errors = load_validated_artifacts(
        script, _existing_contracts(script, _SCRIPT_JSON_CONTRACTS), root
    )
    errors.extend(inventory_errors)
    file_contracts = tuple(
        contract for contract in SCRIPT_CONTRACTS if contract.filename != "scenes"
    )
    errors.extend(_wrong_file_type_errors(script, file_contracts))
    scenes_entry = script / "scenes"
    if (scenes_entry.exists() or scenes_entry.is_symlink()) and not scenes_entry.is_dir():
        errors.append("scenes: required directory is missing")
    errors.extend(_project_id_errors(payloads, project_id))

    expected_unit_id = script.name
    for filename in (
        "unit-outline.json",
        "screenplay-metadata.json",
        "script-revision-plan.json",
    ):
        payload = payloads.get(filename)
        if payload is None:
            continue
        unit_id = payload.get("unit_id")
        if unit_id != expected_unit_id:
            errors.append(
                f"{filename}: unit_id {unit_id} does not match directory "
                f"{expected_unit_id}"
            )
    for filename in ("unit-outline.json", "script-revision-plan.json"):
        payload = payloads.get(filename)
        if payload is not None and payload.get("project_format") != project_format:
            errors.append(
                f"{filename}: project_format {payload.get('project_format')} "
                f"does not match {project_format}"
            )

    manifest = payloads.get("script-manifest.json")
    errors.extend(
        _manifest_context_errors(manifest, "script-manifest.json", "script")
    )
    if manifest is not None:
        errors.extend(
            validate_layer_manifest(
                manifest, SCRIPT_CONTRACTS, "script-manifest.json"
            )
        )

    summary = None
    fountain_path = script / "screenplay.fountain"
    if fountain_path.is_file():
        summary, fountain_errors = inspect_fountain_file(fountain_path)
        errors.extend(
            f"screenplay.fountain: {error}" for error in fountain_errors
        )
    metadata = payloads.get("screenplay-metadata.json")
    if metadata is not None and summary is not None:
        errors.extend(
            f"screenplay-metadata.json: {error}"
            for error in validate_screenplay_metadata(metadata, summary)
        )

    outline = payloads.get("unit-outline.json")
    if outline is not None and metadata is not None:
        if metadata.get("source_event_ids") != outline.get("source_event_ids"):
            errors.append(
                "screenplay-metadata.json: source_event_ids must exactly match "
                "unit-outline.json"
            )
        outline_scenes = [
            scene.get("scene_id")
            for scene in outline.get("scenes", [])
            if isinstance(scene, Mapping)
        ]
        metadata_scenes = [
            scene.get("scene_id")
            for scene in metadata.get("scene_mappings", [])
            if isinstance(scene, Mapping)
        ]
        if metadata_scenes != outline_scenes:
            errors.append(
                "screenplay-metadata.json: scene_mappings must exactly match "
                "unit-outline.json scene order"
            )

    scenes_dir = script / "scenes"
    if metadata is not None and scenes_dir.is_dir():
        scene_ids = {
            mapping.get("scene_id")
            for mapping in metadata.get("scene_mappings", [])
            if isinstance(mapping, Mapping)
            and isinstance(mapping.get("scene_id"), str)
        }
        scene_inventory_errors = inspect_exact_entries(
            scenes_dir, scene_ids, "scene-full scenes"
        )
        errors.extend(scene_inventory_errors)
        if not any("unable to inspect" in error for error in scene_inventory_errors):
            for scene_id in sorted(scene_ids):
                scene_path = scenes_dir / scene_id
                if not scene_path.is_dir():
                    continue
                scene_errors = validate_scene_package(
                    scene_path, root, FULL_PROFILE
                )
                errors.extend(
                    f"scenes/{scene_id}/{error}" for error in scene_errors
                )
                if scene_errors:
                    continue
                scene_beats, load_errors = load_json_object(
                    scene_path / "scene-beats.json"
                )
                if load_errors or scene_beats is None:
                    continue
                embedded_scene_id = scene_beats.get("scene_id")
                if (
                    isinstance(embedded_scene_id, str)
                    and embedded_scene_id != scene_id
                ):
                    errors.append(
                        f"scenes/{scene_id}/scene-beats.json: scene_id "
                        f"{embedded_scene_id} does not match metadata scene "
                        f"{scene_id}"
                    )
    return sorted(set(errors))


def _dangling_top_level_refs(
    payload: Mapping[str, Any],
    filename: str,
    field: str,
    declared: Collection[str],
    label: str,
) -> list[str]:
    values = payload.get(field)
    if not isinstance(values, list):
        return []
    known = set(declared)
    return [
        f"{filename}: {field}.{index}: dangling {label} reference {value}"
        for index, value in enumerate(values)
        if isinstance(value, str) and value not in known
    ]


def _metadata_story_reference_errors(
    payload: Mapping[str, Any],
    character_ids: Collection[str],
    location_ids: Collection[str],
) -> list[str]:
    errors: list[str] = []
    known_characters = set(character_ids)
    known_locations = set(location_ids)
    mappings = payload.get("character_mappings")
    if isinstance(mappings, list):
        for index, mapping in enumerate(mappings):
            if not isinstance(mapping, Mapping):
                continue
            value = mapping.get("character_id")
            if isinstance(value, str) and value not in known_characters:
                errors.append(
                    "screenplay-metadata.json: character_mappings."
                    f"{index}.character_id: dangling character reference {value}"
                )
    locations = payload.get("location_mappings")
    if isinstance(locations, list):
        for index, mapping in enumerate(locations):
            if not isinstance(mapping, Mapping):
                continue
            value = mapping.get("location_id")
            if isinstance(value, str) and value not in known_locations:
                errors.append(
                    "screenplay-metadata.json: location_mappings."
                    f"{index}.location_id: dangling world location reference {value}"
                )
    scenes = payload.get("scene_mappings")
    if isinstance(scenes, list):
        for scene_index, mapping in enumerate(scenes):
            if not isinstance(mapping, Mapping):
                continue
            values = mapping.get("character_ids")
            if isinstance(values, list):
                for value_index, value in enumerate(values):
                    if isinstance(value, str) and value not in known_characters:
                        errors.append(
                            "screenplay-metadata.json: scene_mappings."
                            f"{scene_index}.character_ids.{value_index}: dangling "
                            f"character reference {value}"
                        )
            location_id = mapping.get("location_id")
            if isinstance(location_id, str) and location_id not in known_locations:
                errors.append(
                    "screenplay-metadata.json: scene_mappings."
                    f"{scene_index}.location_id: dangling world reference "
                    f"{location_id}"
                )
    return errors


def _season_episode_events(season: Mapping[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    episodes = season.get("episodes")
    if not isinstance(episodes, list):
        return result
    for episode in episodes:
        if not isinstance(episode, Mapping):
            continue
        episode_id = episode.get("episode_id")
        if not isinstance(episode_id, str):
            continue
        events: set[str] = set()
        distribution = episode.get("plot_distribution")
        if isinstance(distribution, list):
            for plot in distribution:
                if isinstance(plot, Mapping):
                    values = plot.get("event_ids")
                    if isinstance(values, list):
                        events.update(
                            value for value in values if isinstance(value, str)
                        )
        result[episode_id] = events
    return result


def build_story_index(
    story_dir: Path, scripts_dir: Path, root: Path
) -> tuple[ProjectIndex | None, list[str]]:
    """Validate story and script layers and build their downstream ID index."""
    story = Path(story_dir)
    scripts = Path(scripts_dir)
    concept, concept_errors = load_json_object(story / "story-concept.json")
    if concept_errors:
        return None, sorted(
            f"story-concept.json: {error}" for error in concept_errors
        )
    assert concept is not None
    value = concept.get("project_format")
    project_format = value if isinstance(value, str) else ""
    story_errors = validate_story_package(story, root, project_format)
    if story_errors:
        return None, sorted(story_errors)
    assert concept is not None
    project_id = concept["project_id"]
    assert isinstance(project_id, str)

    story_contracts = required_story_artifacts(project_format)
    story_payloads, load_errors = load_validated_artifacts(
        story, story_contracts, root
    )
    if load_errors:
        return None, load_errors
    structure = story_payloads["story-structure.json"]
    arcs = story_payloads["character-arcs.json"]
    world = story_payloads["world-bible.json"]
    event_ids = collect_ids(structure, "events", "event_id")
    plotline_ids = collect_ids(structure, "plotlines", "plotline_id")
    character_ids = collect_ids(arcs, "characters", "character_id")
    location_ids = collect_ids(world, "locations", "location_id")
    rule_ids = collect_ids(world, "rules", "rule_id")
    asset_ids = collect_ids(world, "production_assets", "asset_id")
    world_ids = location_ids | rule_ids

    season = story_payloads.get("season-arc.json")
    if season is not None:
        expected_units = collect_ids(season, "episodes", "episode_id")
        expected_unit_events = _season_episode_events(season)
    else:
        expected_units = {f"{project_id}-U01"}
        expected_unit_events = {}

    try:
        actual_units = {entry.name for entry in scripts.iterdir()}
    except OSError as exc:
        return None, [
            f"{scripts}: unable to inspect {STORY_PROFILE} scripts directory: {exc}"
        ]
    errors = [
        f"{unit_id}: unexpected script unit directory"
        for unit_id in actual_units - expected_units
    ]
    errors.extend(
        f"{unit_id}: required script unit directory is missing"
        for unit_id in expected_units - actual_units
    )

    unit_payloads: dict[str, tuple[Mapping[str, Any], Mapping[str, Any]]] = {}
    for unit_id in sorted(expected_units & actual_units):
        unit_path = scripts / unit_id
        unit_errors = validate_script_package(
            unit_path, root, project_id, project_format
        )
        errors.extend(f"{unit_id}/{error}" for error in unit_errors)
        loaded, _load_errors = load_validated_artifacts(
            unit_path,
            _existing_contracts(unit_path, _SCRIPT_JSON_CONTRACTS),
            root,
        )
        outline = loaded.get("unit-outline.json")
        metadata = loaded.get("screenplay-metadata.json")
        if outline is None or metadata is None:
            continue
        unit_payloads[unit_id] = (outline, metadata)
        errors.extend(
            f"{unit_id}/{error}"
            for error in _dangling_top_level_refs(
                outline,
                "unit-outline.json",
                "source_event_ids",
                event_ids,
                "event",
            )
        )
        errors.extend(
            f"{unit_id}/{error}"
            for error in _dangling_top_level_refs(
                outline,
                "unit-outline.json",
                "source_plotline_ids",
                plotline_ids,
                "plotline",
            )
        )
        errors.extend(
            f"{unit_id}/{error}"
            for error in _metadata_story_reference_errors(
                metadata, character_ids, location_ids
            )
        )
        if unit_id in expected_unit_events:
            actual_events = _source_ids(outline, "source_event_ids")
            if actual_events != expected_unit_events[unit_id]:
                errors.append(
                    f"{unit_id}/unit-outline.json: source_event_ids must match "
                    "season episode event inventory: "
                    f"{', '.join(sorted(expected_unit_events[unit_id]))}"
                )

    covered_events: set[str] = set()
    for outline, _metadata in unit_payloads.values():
        covered_events.update(_source_ids(outline, "source_event_ids") & event_ids)
    for event_id in sorted(event_ids - covered_events):
        errors.append(f"story event {event_id} has no script unit coverage")
    if errors:
        return None, sorted(set(errors))

    scene_ids: set[str] = set()
    beat_ids: set[str] = set()
    shot_ids: set[str] = set()
    for unit_id, (_outline, metadata) in unit_payloads.items():
        mappings = metadata.get("scene_mappings")
        if not isinstance(mappings, list):
            continue
        for mapping in mappings:
            if not isinstance(mapping, Mapping):
                continue
            scene_id = mapping.get("scene_id")
            if not isinstance(scene_id, str):
                continue
            scene_ids.add(scene_id)
            for filename, collection, id_field, destination in (
                ("scene-beats.json", "beats", "beat_id", beat_ids),
                ("shot-list.json", "shots", "shot_id", shot_ids),
            ):
                payload, load_scene_errors = load_json_object(
                    scripts / unit_id / "scenes" / scene_id / filename
                )
                if load_scene_errors or payload is None:
                    continue
                destination.update(collect_ids(payload, collection, id_field))

    production_modes_value = concept.get("production_modes")
    production_modes = tuple(
        mode
        for mode in production_modes_value
        if isinstance(mode, str)
    ) if isinstance(production_modes_value, list) else ()
    return (
        ProjectIndex(
            project_id=project_id,
            project_format=project_format,
            production_modes=production_modes,
            unit_ids=frozenset(expected_units),
            scene_ids=frozenset(scene_ids),
            beat_ids=frozenset(beat_ids),
            shot_ids=frozenset(shot_ids),
            character_ids=frozenset(character_ids),
            event_ids=frozenset(event_ids),
            world_ids=frozenset(world_ids),
            asset_ids=frozenset(asset_ids),
            media_ids=frozenset(),
            edit_segment_ids=frozenset(),
        ),
        [],
    )

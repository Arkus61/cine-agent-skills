from __future__ import annotations

import io
import re
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MAX_FOUNTAIN_LINE_LENGTH = 16_384
MAX_FOUNTAIN_FILE_BYTES = 8 * 1024 * 1024

_SCENE_HEADING_RE = re.compile(
    r"^(?:INT\.|EXT\.|INT\./EXT\.|EXT\./INT\.|I/E\.)(?:\s+|$)\S.*$"
)
_CHARACTER_CUE_RE = re.compile(
    r"^@?([A-Z0-9][A-Z0-9 ._'\-]*?)(?:\s+\([^()\r\n]{1,32}\))?\s*\^?$"
)
_PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*$")


@dataclass(frozen=True, slots=True)
class FountainSummary:
    """A minimal structural summary, not a Fountain rendering model."""

    scene_headings: tuple[str, ...]
    character_cues: tuple[str, ...]


def _normalized_character_cue(line: str) -> str | None:
    if len(line) > 80 or line.endswith(":"):
        return None
    match = _CHARACTER_CUE_RE.fullmatch(line)
    if match is None:
        return None
    cue = match.group(1).strip()
    return cue or None


def inspect_fountain(
    document: str, filename: str = "screenplay.fountain"
) -> tuple[FountainSummary | None, list[str]]:
    """Inspect scene headings and character cues with a bounded line scan."""
    scene_headings: list[str] = []
    character_cues: list[str] = []
    seen_character_cues: set[str] = set()
    any_content = False
    previous_blank = True
    pending_character_cue: str | None = None

    for line_number, raw_line in enumerate(io.StringIO(document), start=1):
        line = raw_line.rstrip("\r\n")
        if len(line) > MAX_FOUNTAIN_LINE_LENGTH:
            return None, [
                f"Fountain screenplay {filename} line {line_number} exceeds "
                f"{MAX_FOUNTAIN_LINE_LENGTH} characters"
            ]
        stripped = line.strip()
        if stripped:
            any_content = True

        if pending_character_cue is not None and stripped:
            if pending_character_cue not in seen_character_cues:
                seen_character_cues.add(pending_character_cue)
                character_cues.append(pending_character_cue)
            pending_character_cue = None
        elif pending_character_cue is not None and not stripped:
            pending_character_cue = None

        if _SCENE_HEADING_RE.fullmatch(stripped) is not None:
            scene_headings.append(stripped)
        elif previous_blank and stripped:
            pending_character_cue = _normalized_character_cue(stripped)

        previous_blank = not stripped

    if not any_content:
        return None, [f"empty Fountain screenplay: {filename}"]
    if not scene_headings:
        return None, [f"no scene headings found in Fountain screenplay: {filename}"]
    return FountainSummary(tuple(scene_headings), tuple(character_cues)), []


def inspect_fountain_file(
    path: Path,
) -> tuple[FountainSummary | None, list[str]]:
    """Load one bounded UTF-8 Fountain file and inspect its structure."""
    source_path = Path(path)
    try:
        size = source_path.stat().st_size
        if size > MAX_FOUNTAIN_FILE_BYTES:
            return None, [
                f"Fountain screenplay {source_path} exceeds "
                f"{MAX_FOUNTAIN_FILE_BYTES} bytes"
            ]
        document = source_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return None, [f"invalid UTF-8 Fountain screenplay {source_path}: {exc}"]
    except OSError as exc:
        return None, [f"unable to read Fountain screenplay {source_path}: {exc}"]
    return inspect_fountain(document, str(source_path))


def _exact_id_pattern(project_id: str, suffix: str, width: int) -> re.Pattern[str]:
    if width == 2:
        number = r"(?:0[1-9]|[1-9][0-9])"
    else:
        number = r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
    return re.compile(rf"^{re.escape(project_id)}-{suffix}{number}$")


def validate_screenplay_metadata(
    payload: Mapping[str, Any], summary: FountainSummary | None = None
) -> list[str]:
    """Validate metadata IDs, references, and optional Fountain correspondence."""
    project_id = payload.get("project_id")
    unit_id = payload.get("unit_id")
    if not isinstance(project_id, str) or _PROJECT_ID_RE.fullmatch(project_id) is None:
        return []

    errors: list[str] = []
    unit_pattern = re.compile(
        rf"^{re.escape(project_id)}-(?:U|E)(?:0[1-9]|[1-9][0-9])$"
    )
    valid_unit = isinstance(unit_id, str) and unit_pattern.fullmatch(unit_id) is not None
    if isinstance(unit_id, str) and not valid_unit:
        errors.append(
            f"unit_id: {unit_id!r} must match {project_id}-U## or {project_id}-E##"
        )

    event_pattern = _exact_id_pattern(project_id, "EV", 3)
    character_pattern = _exact_id_pattern(project_id, "CH", 3)
    location_pattern = _exact_id_pattern(project_id, "LO", 3)
    scene_pattern = (
        re.compile(
            rf"^{re.escape(unit_id)}-SC(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{{2}})$"
        )
        if valid_unit
        else None
    )

    source_event_ids: set[str] = set()
    source_events = payload.get("source_event_ids")
    if isinstance(source_events, list):
        for index, event_id in enumerate(source_events):
            if not isinstance(event_id, str):
                continue
            if event_pattern.fullmatch(event_id) is None:
                errors.append(
                    f"source_event_ids.{index}: {event_id!r} must match "
                    f"{project_id}-EV###"
                )
            elif event_id in source_event_ids:
                errors.append(
                    f"source_event_ids.{index}: duplicate event ID {event_id}"
                )
            else:
                source_event_ids.add(event_id)

    character_ids: set[str] = set()
    mapped_cues: set[str] = set()
    character_mappings = payload.get("character_mappings")
    if isinstance(character_mappings, list):
        for index, mapping in enumerate(character_mappings):
            if not isinstance(mapping, Mapping):
                continue
            character_id = mapping.get("character_id")
            cue = mapping.get("cue")
            if isinstance(character_id, str):
                if character_pattern.fullmatch(character_id) is None:
                    errors.append(
                        f"character_mappings.{index}.character_id: "
                        f"{character_id!r} must match {project_id}-CH###"
                    )
                elif character_id in character_ids:
                    errors.append(
                        f"character_mappings.{index}.character_id: duplicate "
                        f"character mapping {character_id}"
                    )
                else:
                    character_ids.add(character_id)
            if isinstance(cue, str):
                if cue in mapped_cues:
                    errors.append(
                        f"character_mappings.{index}.cue: duplicate character cue {cue}"
                    )
                else:
                    mapped_cues.add(cue)

    location_ids: set[str] = set()
    location_mappings = payload.get("location_mappings")
    if isinstance(location_mappings, list):
        for index, mapping in enumerate(location_mappings):
            if not isinstance(mapping, Mapping):
                continue
            location_id = mapping.get("location_id")
            if not isinstance(location_id, str):
                continue
            if location_pattern.fullmatch(location_id) is None:
                errors.append(
                    f"location_mappings.{index}.location_id: {location_id!r} "
                    f"must match {project_id}-LO###"
                )
            elif location_id in location_ids:
                errors.append(
                    f"location_mappings.{index}.location_id: duplicate location "
                    f"mapping {location_id}"
                )
            else:
                location_ids.add(location_id)

    scene_ids: set[str] = set()
    mapped_event_ids: set[str] = set()
    scene_event_ids: dict[str, set[str]] = {}
    scene_mappings = payload.get("scene_mappings")
    if isinstance(scene_mappings, list):
        for index, mapping in enumerate(scene_mappings):
            if not isinstance(mapping, Mapping):
                continue
            scene_id = mapping.get("scene_id")
            if isinstance(scene_id, str):
                if scene_pattern is not None and scene_pattern.fullmatch(scene_id) is None:
                    errors.append(
                        f"scene_mappings.{index}.scene_id: {scene_id!r} must match "
                        f"{unit_id}-SC###"
                    )
                elif scene_id in scene_ids:
                    errors.append(
                        f"scene_mappings.{index}.scene_id: duplicate scene mapping "
                        f"{scene_id}"
                    )
                else:
                    scene_ids.add(scene_id)

            event_ids = mapping.get("event_ids")
            if isinstance(event_ids, list):
                for ref_index, event_id in enumerate(event_ids):
                    if not isinstance(event_id, str):
                        continue
                    location = f"scene_mappings.{index}.event_ids.{ref_index}"
                    if event_pattern.fullmatch(event_id) is None:
                        errors.append(
                            f"{location}: {event_id!r} must match {project_id}-EV###"
                        )
                    elif event_id not in source_event_ids:
                        errors.append(f"{location}: unknown event {event_id}")
                    else:
                        mapped_event_ids.add(event_id)
                        if isinstance(scene_id, str):
                            scene_event_ids.setdefault(scene_id, set()).add(event_id)

            mapped_character_ids = mapping.get("character_ids")
            if isinstance(mapped_character_ids, list):
                for ref_index, character_id in enumerate(mapped_character_ids):
                    if not isinstance(character_id, str):
                        continue
                    location = f"scene_mappings.{index}.character_ids.{ref_index}"
                    if character_pattern.fullmatch(character_id) is None:
                        errors.append(
                            f"{location}: {character_id!r} must match "
                            f"{project_id}-CH###"
                        )
                    elif character_id not in character_ids:
                        errors.append(f"{location}: unknown character {character_id}")

            location_id = mapping.get("location_id")
            if isinstance(location_id, str):
                location = f"scene_mappings.{index}.location_id"
                if location_pattern.fullmatch(location_id) is None:
                    errors.append(
                        f"{location}: {location_id!r} must match {project_id}-LO###"
                    )
                elif location_id not in location_ids:
                    errors.append(f"{location}: unknown location {location_id}")

    for event_id in sorted(source_event_ids - mapped_event_ids):
        errors.append(
            "scene_mappings: source event "
            f"{event_id} has no screenplay scene mapping"
        )

    setup_payoffs = payload.get("setup_payoffs")
    if isinstance(setup_payoffs, list):
        for index, mapping in enumerate(setup_payoffs):
            if not isinstance(mapping, Mapping):
                continue
            payoff_event_id = mapping.get("payoff_event_id")
            payoff_scene_id = mapping.get("payoff_scene_id")
            if (payoff_event_id is None) != (payoff_scene_id is None):
                errors.append(
                    f"setup_payoffs.{index}: payoff_event_id and payoff_scene_id "
                    "must both be null or both be IDs"
                )
            for field in ("setup_event_id", "payoff_event_id"):
                event_id = mapping.get(field)
                if event_id is None or not isinstance(event_id, str):
                    continue
                location = f"setup_payoffs.{index}.{field}"
                if event_pattern.fullmatch(event_id) is None:
                    errors.append(
                        f"{location}: {event_id!r} must match {project_id}-EV###"
                    )
                elif event_id not in source_event_ids:
                    errors.append(f"{location}: unknown event {event_id}")
            for field in ("setup_scene_id", "payoff_scene_id"):
                scene_id = mapping.get(field)
                if scene_id is None or not isinstance(scene_id, str):
                    continue
                location = f"setup_payoffs.{index}.{field}"
                if scene_pattern is not None and scene_pattern.fullmatch(scene_id) is None:
                    errors.append(
                        f"{location}: {scene_id!r} must match {unit_id}-SC###"
                    )
                elif scene_id not in scene_ids:
                    errors.append(f"{location}: unknown scene {scene_id}")
            for event_field, scene_field in (
                ("setup_event_id", "setup_scene_id"),
                ("payoff_event_id", "payoff_scene_id"),
            ):
                event_id = mapping.get(event_field)
                scene_id = mapping.get(scene_field)
                if not isinstance(event_id, str) or not isinstance(scene_id, str):
                    continue
                if event_id not in scene_event_ids.get(scene_id, set()):
                    errors.append(
                        f"setup_payoffs.{index}.{event_field}: {event_id} is not "
                        f"mapped to scene {scene_id}"
                    )

    if summary is not None:
        if isinstance(scene_mappings, list):
            metadata_headings = [
                mapping.get("heading") if isinstance(mapping, Mapping) else None
                for mapping in scene_mappings
            ]
            fountain_headings = summary.scene_headings
            comparable_headings = all(
                isinstance(heading, str) for heading in metadata_headings
            )
            order_only = (
                len(metadata_headings) == len(fountain_headings)
                and comparable_headings
                and Counter(metadata_headings) == Counter(fountain_headings)
            )
            shared_count = min(len(metadata_headings), len(fountain_headings))
            for index in range(shared_count):
                heading = metadata_headings[index]
                expected_heading = fountain_headings[index]
                if isinstance(heading, str) and heading != expected_heading:
                    mismatch = (
                        "heading order mismatch" if order_only else "heading mismatch"
                    )
                    errors.append(
                        f"scene_mappings.{index}.heading: {mismatch} at occurrence "
                        f"{index + 1}: expected {expected_heading!r}, got {heading!r}"
                    )
            for index in range(shared_count, len(fountain_headings)):
                errors.append(
                    f"scene_mappings.{index}: missing metadata scene mapping for "
                    f"Fountain heading occurrence {index + 1}: "
                    f"{fountain_headings[index]!r}"
                )
            for index in range(shared_count, len(metadata_headings)):
                heading = metadata_headings[index]
                if isinstance(heading, str):
                    errors.append(
                        f"scene_mappings.{index}: extra metadata scene mapping "
                        f"without Fountain heading occurrence {index + 1}: {heading!r}"
                    )
        for cue in dict.fromkeys(summary.character_cues):
            if cue not in mapped_cues:
                errors.append(
                    "character_mappings: Fountain character cue has no metadata "
                    f"mapping: {cue}"
                )
        fountain_cues = set(summary.character_cues)
        if isinstance(character_mappings, list):
            for index, mapping in enumerate(character_mappings):
                if not isinstance(mapping, Mapping):
                    continue
                cue = mapping.get("cue")
                if isinstance(cue, str) and cue not in fountain_cues:
                    errors.append(
                        f"character_mappings.{index}.cue: metadata character cue "
                        f"absent from Fountain: {cue}"
                    )

    return errors

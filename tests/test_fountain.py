from pathlib import Path

from cine_skills.fountain import (
    MAX_FOUNTAIN_LINE_LENGTH,
    FountainSummary,
    inspect_fountain,
    inspect_fountain_file,
    validate_screenplay_metadata,
)


def valid_metadata() -> dict[str, object]:
    return {
        "schema_version": "2.0",
        "project_id": "EMBER",
        "unit_id": "EMBER-U01",
        "source_event_ids": ["EMBER-EV001", "EMBER-EV002"],
        "scene_mappings": [
            {
                "scene_id": "EMBER-U01-SC001",
                "heading": "EXT. SALT ROAD - DUSK",
                "event_ids": ["EMBER-EV001", "EMBER-EV002"],
                "character_ids": ["EMBER-CH001", "EMBER-CH002"],
                "location_id": "EMBER-LO001",
                "objective": "Mara must secure passage before the storm reaches the road.",
                "conflict": "The keeper delays her without admitting why.",
                "turn": "Mara trades the map she needs for passage.",
            }
        ],
        "character_mappings": [
            {"character_id": "EMBER-CH001", "cue": "MARA"},
            {"character_id": "EMBER-CH002", "cue": "KEEPER"},
        ],
        "location_mappings": [
            {"location_id": "EMBER-LO001", "name": "Salt road checkpoint"}
        ],
        "setup_payoffs": [
            {
                "setup_event_id": "EMBER-EV001",
                "setup_scene_id": "EMBER-U01-SC001",
                "payoff_event_id": "EMBER-EV002",
                "payoff_scene_id": "EMBER-U01-SC001",
                "relationship": "The hidden map becomes the price of passage.",
            }
        ],
        "assumptions": [],
        "uncertainties": [],
    }


def test_inspect_fountain_returns_ordered_headings_and_normalized_cues() -> None:
    document = """Title: Ash Road
Credit: Written by Example

INT./EXT. WAYSTATION / SALT ROAD - DUSK

Rain needles the open doorway.

MARA (V.O.)
Keep the lamp dark.

KEEPER
(locking the gate)
Then stop asking for a road.

CUT TO:

EXT. SALT ROAD - NIGHT

Mara runs into the storm.
"""

    summary, errors = inspect_fountain(document, "ash-road.fountain")

    assert errors == []
    assert summary == FountainSummary(
        scene_headings=(
            "INT./EXT. WAYSTATION / SALT ROAD - DUSK",
            "EXT. SALT ROAD - NIGHT",
        ),
        character_cues=("MARA", "KEEPER"),
    )


def test_inspect_fountain_uses_anchored_scene_headings() -> None:
    document = """Title: False Positives

EXT. FIELD - DAY

The sign reads INT. OFFICE - NIGHT, but the field stays bright.
XINT. MACHINE ROOM - NIGHT

ADA
Not a new scene.
"""

    summary, errors = inspect_fountain(document)

    assert errors == []
    assert summary is not None
    assert summary.scene_headings == ("EXT. FIELD - DAY",)
    assert summary.character_cues == ("ADA",)


def test_inspect_fountain_rejects_empty_document() -> None:
    summary, errors = inspect_fountain(" \n\t\n", "blank.fountain")

    assert summary is None
    assert errors == ["empty Fountain screenplay: blank.fountain"]


def test_inspect_fountain_rejects_document_without_scene_headings() -> None:
    summary, errors = inspect_fountain("A figure crosses the room.\n", "missing.fountain")

    assert summary is None
    assert errors == ["no scene headings found in Fountain screenplay: missing.fountain"]


def test_inspect_fountain_file_reports_invalid_utf8(tmp_path: Path) -> None:
    path = tmp_path / "broken.fountain"
    path.write_bytes(b"EXT. FIELD - DAY\n\xff")

    summary, errors = inspect_fountain_file(path)

    assert summary is None
    assert len(errors) == 1
    assert errors[0].startswith(f"invalid UTF-8 Fountain screenplay {path}:")


def test_inspect_fountain_bounds_long_lines() -> None:
    document = "EXT. FIELD - DAY\n\n" + ("x" * (MAX_FOUNTAIN_LINE_LENGTH + 1))

    summary, errors = inspect_fountain(document, "long.fountain")

    assert summary is None
    assert errors == [
        f"Fountain screenplay long.fountain line 3 exceeds "
        f"{MAX_FOUNTAIN_LINE_LENGTH} characters"
    ]


def test_inspect_fountain_handles_one_hundred_thousand_formatting_markers() -> None:
    document = "EXT. FIELD - DAY\n\n" + ("*" * 100_000)

    summary, errors = inspect_fountain(document, "markers.fountain")

    assert summary is None
    assert errors == [
        f"Fountain screenplay markers.fountain line 3 exceeds "
        f"{MAX_FOUNTAIN_LINE_LENGTH} characters"
    ]


def test_screenplay_metadata_matches_fountain_summary() -> None:
    summary = FountainSummary(
        scene_headings=("EXT. SALT ROAD - DUSK",),
        character_cues=("MARA", "KEEPER"),
    )

    assert validate_screenplay_metadata(valid_metadata(), summary) == []


def test_screenplay_metadata_rejects_duplicate_scene_mapping() -> None:
    payload = valid_metadata()
    scene_mappings = payload["scene_mappings"]
    assert isinstance(scene_mappings, list)
    duplicate = dict(scene_mappings[0])
    duplicate["heading"] = "EXT. SECOND ROAD - NIGHT"
    scene_mappings.append(duplicate)
    summary = FountainSummary(
        scene_headings=("EXT. SALT ROAD - DUSK", "EXT. SECOND ROAD - NIGHT"),
        character_cues=("MARA", "KEEPER"),
    )

    errors = validate_screenplay_metadata(payload, summary)

    assert errors == [
        "scene_mappings.1.scene_id: duplicate scene mapping EMBER-U01-SC001"
    ]


def test_screenplay_metadata_rejects_heading_missing_from_fountain() -> None:
    payload = valid_metadata()
    scene_mappings = payload["scene_mappings"]
    assert isinstance(scene_mappings, list)
    first_mapping = scene_mappings[0]
    assert isinstance(first_mapping, dict)
    first_mapping["heading"] = "INT. INVENTED ROOM - NIGHT"
    summary = FountainSummary(
        scene_headings=("EXT. SALT ROAD - DUSK",),
        character_cues=("MARA", "KEEPER"),
    )

    errors = validate_screenplay_metadata(payload, summary)

    assert errors == [
        "scene_mappings.0.heading: heading mismatch at occurrence 1: expected "
        "'EXT. SALT ROAD - DUSK', got 'INT. INVENTED ROOM - NIGHT'"
    ]


def test_screenplay_metadata_rejects_extra_distinct_fountain_scene() -> None:
    summary, inspection_errors = inspect_fountain(
        """EXT. SALT ROAD - DUSK

Wind scours the road.

MARA
Wait.

KEEPER
No.

INT. UNTRACKED ROOM - NIGHT

A lamp burns in an otherwise empty room.
"""
    )
    assert inspection_errors == []
    assert summary is not None

    errors = validate_screenplay_metadata(valid_metadata(), summary)

    assert errors == [
        "scene_mappings.1: missing metadata scene mapping for Fountain heading "
        "occurrence 2: 'INT. UNTRACKED ROOM - NIGHT'"
    ]


def test_screenplay_metadata_counts_repeated_fountain_heading_occurrences() -> None:
    summary, inspection_errors = inspect_fountain(
        """EXT. SALT ROAD - DUSK

Mara reaches the eastern marker.

MARA
East.

KEEPER
Keep moving.

EXT. SALT ROAD - DUSK

She reaches the western marker.
"""
    )
    assert inspection_errors == []
    assert summary is not None

    errors = validate_screenplay_metadata(valid_metadata(), summary)

    assert errors == [
        "scene_mappings.1: missing metadata scene mapping for Fountain heading "
        "occurrence 2: 'EXT. SALT ROAD - DUSK'"
    ]


def test_screenplay_metadata_preserves_valid_repeated_heading_occurrences() -> None:
    payload = valid_metadata()
    scene_mappings = payload["scene_mappings"]
    assert isinstance(scene_mappings, list)
    second_mapping = dict(scene_mappings[0])
    second_mapping["scene_id"] = "EMBER-U01-SC002"
    scene_mappings.append(second_mapping)
    summary, inspection_errors = inspect_fountain(
        """EXT. SALT ROAD - DUSK

Mara reaches the eastern marker.

MARA
East.

KEEPER
Keep moving.

EXT. SALT ROAD - DUSK

She reaches the western marker.
"""
    )
    assert inspection_errors == []
    assert summary is not None

    assert validate_screenplay_metadata(payload, summary) == []


def test_screenplay_metadata_rejects_heading_order_mismatch() -> None:
    payload = valid_metadata()
    scene_mappings = payload["scene_mappings"]
    assert isinstance(scene_mappings, list)
    second_mapping = dict(scene_mappings[0])
    second_mapping["scene_id"] = "EMBER-U01-SC002"
    second_mapping["heading"] = "INT. STORE ROOM - NIGHT"
    scene_mappings.append(second_mapping)
    summary = FountainSummary(
        scene_headings=(
            "INT. STORE ROOM - NIGHT",
            "EXT. SALT ROAD - DUSK",
        ),
        character_cues=("MARA", "KEEPER"),
    )

    errors = validate_screenplay_metadata(payload, summary)

    assert errors == [
        "scene_mappings.0.heading: heading order mismatch at occurrence 1: "
        "expected 'INT. STORE ROOM - NIGHT', got 'EXT. SALT ROAD - DUSK'",
        "scene_mappings.1.heading: heading order mismatch at occurrence 2: "
        "expected 'EXT. SALT ROAD - DUSK', got 'INT. STORE ROOM - NIGHT'",
    ]


def test_screenplay_metadata_rejects_extra_metadata_scene_mapping() -> None:
    payload = valid_metadata()
    scene_mappings = payload["scene_mappings"]
    assert isinstance(scene_mappings, list)
    second_mapping = dict(scene_mappings[0])
    second_mapping["scene_id"] = "EMBER-U01-SC002"
    second_mapping["heading"] = "INT. EXTRA ROOM - NIGHT"
    scene_mappings.append(second_mapping)
    summary = FountainSummary(
        scene_headings=("EXT. SALT ROAD - DUSK",),
        character_cues=("MARA", "KEEPER"),
    )

    errors = validate_screenplay_metadata(payload, summary)

    assert errors == [
        "scene_mappings.1: extra metadata scene mapping without Fountain heading "
        "occurrence 2: 'INT. EXTRA ROOM - NIGHT'"
    ]


def test_screenplay_metadata_rejects_unmapped_character_cue() -> None:
    payload = valid_metadata()
    summary = FountainSummary(
        scene_headings=("EXT. SALT ROAD - DUSK",),
        character_cues=("MARA", "KEEPER", "STRANGER"),
    )

    errors = validate_screenplay_metadata(payload, summary)

    assert errors == [
        "character_mappings: Fountain character cue has no metadata mapping: STRANGER"
    ]


def test_screenplay_metadata_rejects_metadata_cue_absent_from_fountain() -> None:
    payload = valid_metadata()
    summary = FountainSummary(
        scene_headings=("EXT. SALT ROAD - DUSK",),
        character_cues=("MARA",),
    )

    errors = validate_screenplay_metadata(payload, summary)

    assert errors == [
        "character_mappings.1.cue: metadata character cue absent from Fountain: "
        "KEEPER"
    ]


def test_screenplay_metadata_compares_unique_fountain_cue_set() -> None:
    summary = FountainSummary(
        scene_headings=("EXT. SALT ROAD - DUSK",),
        character_cues=("MARA", "STRANGER", "STRANGER", "KEEPER"),
    )

    errors = validate_screenplay_metadata(valid_metadata(), summary)

    assert errors == [
        "character_mappings: Fountain character cue has no metadata mapping: STRANGER"
    ]

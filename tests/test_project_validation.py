import json
from pathlib import Path

import pytest

from cine_skills.project_contracts import ArtifactContract
from cine_skills.project_validation import (
    collect_ids,
    inspect_exact_entries,
    load_validated_artifacts,
    validate_layer_manifest,
    validate_references,
)


def test_exact_entries_rejects_unexpected_directory(tmp_path):
    package = tmp_path / "story"
    package.mkdir()
    (package / "expected.json").write_text("{}", encoding="utf-8")
    (package / "generated-media").mkdir()

    assert inspect_exact_entries(package, {"expected.json"}, "story") == [
        "generated-media: unexpected entry for story package"
    ]


def test_exact_entries_reports_unreadable_directory_without_traceback(
    tmp_path, monkeypatch
):
    package = tmp_path / "story"
    package.mkdir()

    def denied(_path):
        raise PermissionError("denied")

    monkeypatch.setattr(Path, "iterdir", denied)

    assert inspect_exact_entries(package, {"expected.json"}, "story") == [
        f"{package}: unable to inspect story package directory: denied"
    ]


def test_layer_manifest_must_match_contract_order():
    contracts = (
        ArtifactContract("a.json", "a", 1),
        ArtifactContract("b.json", "b", 2),
    )
    manifest = {"artifacts": [
        {"filename": "b.json", "schema_name": "b", "schema_version": "0.3.0", "dependency_order": 1},
        {"filename": "a.json", "schema_name": "a", "schema_version": "0.3.0", "dependency_order": 2},
    ]}

    assert validate_layer_manifest(manifest, contracts, "story-manifest.json") == [
        "story-manifest.json: artifacts must match the exact dependency order: a.json, b.json"
    ]


def test_load_validated_artifacts_qualifies_errors_and_excludes_invalid_payloads(
    tmp_path: Path,
):
    schema_root = tmp_path / "repository"
    (schema_root / "schemas").mkdir(parents=True)
    (schema_root / "schemas" / "thing.schema.json").write_text(
        json.dumps({"type": "object", "required": ["valid"]}), encoding="utf-8"
    )
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    (artifacts / "valid.json").write_text('{"valid": true}', encoding="utf-8")
    (artifacts / "invalid.json").write_text('{}', encoding="utf-8")
    contracts = (
        ArtifactContract("valid.json", "thing", 1),
        ArtifactContract("invalid.json", "thing", 2),
    )

    payloads, errors = load_validated_artifacts(artifacts, contracts, schema_root)

    assert payloads == {"valid.json": {"valid": True}}
    assert errors == ["invalid.json: $: 'valid' is a required property"]


def test_collect_ids_reports_duplicate_with_collection_index():
    payload = {"characters": [{"character_id": "C01"}, {"character_id": "C01"}]}

    with pytest.raises(ValueError, match=r"characters\.1\.character_id: duplicate ID C01"):
        collect_ids(payload, "characters", "character_id")


def test_validate_references_reports_each_dangling_many_reference_in_order():
    payload = {"beats": [{"event_ids": ["E02", "E01"]}]}

    assert validate_references(
        payload, "story-structure.json", "beats", "event_ids", {"E03"}, "event"
    ) == [
        "story-structure.json: beats.0.event_ids.0: dangling event reference E02",
        "story-structure.json: beats.0.event_ids.1: dangling event reference E01",
    ]


def test_validate_references_reports_dangling_one_reference():
    payload = {"relationships": [{"target_character_id": "C02"}]}

    assert validate_references(
        payload,
        "character-arcs.json",
        "relationships",
        "target_character_id",
        {"C01"},
        "character",
        cardinality="one",
    ) == [
        "character-arcs.json: relationships.0.target_character_id: dangling character reference C02"
    ]

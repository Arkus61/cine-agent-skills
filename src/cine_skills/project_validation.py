"""Shared validation primitives for creative-layer packages."""

from __future__ import annotations

from collections.abc import Collection, Mapping
from pathlib import Path
from typing import Any

from cine_skills.artifacts import load_json_object, validate_artifact
from cine_skills import __version__
from cine_skills.project_contracts import ArtifactContract


def inspect_exact_entries(
    directory: Path, expected: Collection[str], label: str
) -> list[str]:
    """Return deterministic errors for entries that differ from an exact inventory."""
    try:
        actual = {entry.name for entry in Path(directory).iterdir()}
    except OSError as exc:
        return [f"{directory}: unable to inspect {label} package directory: {exc}"]

    expected_names = set(expected)
    errors = [
        f"{name}: unexpected entry for {label} package"
        for name in actual - expected_names
    ]
    errors.extend(
        f"{name}: required file is missing" for name in expected_names - actual
    )
    return sorted(errors)


def load_validated_artifacts(
    directory: Path,
    contracts: Collection[ArtifactContract],
    root: Path,
) -> tuple[dict[str, Mapping[str, Any]], list[str]]:
    """Load only artifacts that are valid under their contracted schemas."""
    payloads: dict[str, Mapping[str, Any]] = {}
    errors: list[str] = []
    for contract in sorted(contracts, key=lambda item: item.filename):
        payload, load_errors = load_json_object(Path(directory) / contract.filename)
        if load_errors:
            errors.extend(f"{contract.filename}: {error}" for error in load_errors)
            continue
        assert payload is not None
        validation_errors = validate_artifact(contract.schema_name, payload, root)
        if validation_errors:
            errors.extend(
                f"{contract.filename}: {error}" for error in validation_errors
            )
            continue
        payloads[contract.filename] = payload
    return payloads, sorted(errors)


def validate_layer_manifest(
    payload: Mapping[str, Any],
    contracts: Collection[ArtifactContract],
    manifest_filename: str,
) -> list[str]:
    """Check that a layer inventory exactly describes its artifact contracts."""
    expected = [
        {
            "filename": contract.filename,
            "schema_name": contract.schema_name,
            "schema_version": __version__,
            "dependency_order": contract.dependency_order,
        }
        for contract in sorted(contracts, key=lambda item: item.dependency_order)
    ]
    if payload.get("artifacts") == expected:
        return []
    names = ", ".join(item["filename"] for item in expected)
    return [
        f"{manifest_filename}: artifacts must match the exact dependency order: {names}"
    ]


def collect_ids(
    payload: Mapping[str, Any], collection_name: str, id_name: str
) -> set[str]:
    """Collect declared identifiers, rejecting duplicate identifiers by index."""
    collection = payload.get(collection_name)
    if not isinstance(collection, list):
        return set()

    identifiers: set[str] = set()
    errors: list[str] = []
    for index, item in enumerate(collection):
        if not isinstance(item, Mapping):
            continue
        identifier = item.get(id_name)
        if not isinstance(identifier, str):
            continue
        location = f"{collection_name}.{index}.{id_name}"
        if identifier in identifiers:
            errors.append(f"{location}: duplicate ID {identifier}")
        else:
            identifiers.add(identifier)
    if errors:
        raise ValueError("\n".join(sorted(errors)))
    return identifiers


def validate_references(
    payload: Mapping[str, Any],
    filename: str,
    collection_name: str,
    reference_name: str,
    declared: Collection[str],
    label: str,
    cardinality: str = "many",
) -> list[str]:
    """Return indexed errors for references absent from a declared identifier set."""
    if cardinality not in {"many", "one"}:
        raise ValueError(f"unsupported reference cardinality: {cardinality}")
    collection = payload.get(collection_name)
    if not isinstance(collection, list):
        return []

    declared_ids = set(declared)
    errors: list[str] = []
    for item_index, item in enumerate(collection):
        if not isinstance(item, Mapping):
            continue
        references = item.get(reference_name)
        if cardinality == "one":
            values = [(reference_name, references)]
        elif isinstance(references, list):
            values = [
                (f"{reference_name}.{reference_index}", reference)
                for reference_index, reference in enumerate(references)
            ]
        else:
            continue
        for location, reference in values:
            if isinstance(reference, str) and reference not in declared_ids:
                errors.append(
                    f"{filename}: {collection_name}.{item_index}.{location}: "
                    f"dangling {label} reference {reference}"
                )
    return sorted(errors)

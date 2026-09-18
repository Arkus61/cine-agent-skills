"""Checked JSON Patch staging for one authoritative artifact at a time."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

import jsonpatch


_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_PROTECTED = {
    "approval",
    "evidence",
    "source_context",
    "project_id",
    "unit_id",
    "scene_id",
    "shot_id",
    "beat_id",
    "character_id",
    "asset_id",
}


def _pointer_segments(pointer: Any) -> list[str]:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ValueError("patch path must be a JSON Pointer")
    return [segment.replace("~1", "/").replace("~0", "~") for segment in pointer[1:].split("/")]


def _check_operation(operation: Any) -> None:
    if not isinstance(operation, Mapping):
        raise ValueError("patch operation must be an object")
    op = operation.get("op")
    if op not in {"add", "remove", "replace", "move", "copy", "test"}:
        raise ValueError(f"patch operation is unsupported: {op}")
    paths = [operation.get("path")]
    if op in {"move", "copy"}:
        paths.append(operation.get("from"))
    for pointer in paths:
        segments = _pointer_segments(pointer)
        if any(segment in _PROTECTED for segment in segments):
            if op != "test":
                raise ValueError("patch targets a protected identity/approval/evidence path")


def stage_json_patch(original: dict[str, Any], operations: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply a JSON Patch to a copy and reject protected fields."""

    if not isinstance(original, Mapping):
        raise ValueError("patch original must be an object")
    if not isinstance(operations, list):
        raise ValueError("patch operations must be an array")
    for operation in operations:
        _check_operation(operation)
    try:
        candidate = jsonpatch.JsonPatch(operations).apply(dict(original), in_place=False)
    except (jsonpatch.JsonPatchException, TypeError, ValueError) as exc:
        raise ValueError(f"patch could not be applied: {exc}") from exc
    if not isinstance(candidate, dict):
        raise ValueError("patch result must remain an object")
    return candidate


def check_base(actual_digest: str, expected_digest: str) -> list[str]:
    """Return a conflict diagnostic when a patch is based on stale bytes."""

    if not isinstance(actual_digest, str) or not _DIGEST.fullmatch(actual_digest):
        raise ValueError("actual_digest must be a lowercase SHA-256 digest")
    if not isinstance(expected_digest, str) or not _DIGEST.fullmatch(expected_digest):
        raise ValueError("expected_digest must be a lowercase SHA-256 digest")
    return [] if actual_digest == expected_digest else ["base-digest-mismatch"]

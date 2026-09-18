"""Conservative file-level source freshness comparison."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

from . import __version__


def _safe_file(project_dir: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"unsafe path {value!r}")
    relative = PurePosixPath(value)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError(f"unsafe path {value!r}")
    root = Path(project_dir).resolve(strict=True)
    candidate = root.joinpath(*relative.parts)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"symlink path is not allowed: {value}")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError) as exc:
        if isinstance(exc, FileNotFoundError) or not candidate.exists():
            raise ValueError(f"source missing: {value}") from exc
        raise ValueError(f"unsafe path {value!r}") from exc
    if not resolved.is_file():
        raise ValueError(f"source is not a regular file: {value}")
    return resolved


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_nodes(nodes: Any) -> list[Mapping[str, Any]]:
    if not isinstance(nodes, list):
        raise ValueError("freshness snapshot nodes must be an array")
    result: list[Mapping[str, Any]] = []
    keys: set[str] = set()
    for item in nodes:
        if not isinstance(item, Mapping):
            raise ValueError("freshness node must be an object")
        key, path = item.get("key"), item.get("path")
        if not isinstance(key, str) or not key:
            raise ValueError("freshness node key must be a non-empty string")
        if key in keys:
            raise ValueError(f"duplicate freshness node: {key}")
        if not isinstance(path, str) or not path:
            raise ValueError(f"freshness node {key} path must be a non-empty string")
        keys.add(key)
        result.append(item)
    return result


def capture_sources(project_dir: Path, nodes: list[dict[str, Any]]) -> dict[str, Any]:
    """Capture an explicit baseline; no validation call updates it implicitly."""

    records = _validate_nodes(nodes)
    captured: list[dict[str, Any]] = []
    for item in records:
        path = _safe_file(Path(project_dir), item["path"])
        record: dict[str, Any] = {
            "key": item["key"],
            "path": item["path"],
            "content_sha256": _sha256(path),
        }
        if item.get("pointer") is not None:
            pointer = item["pointer"]
            if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
                raise ValueError(f"freshness node {item['key']} pointer must be RFC 6901-like")
            record["pointer"] = pointer
        captured.append(record)
    captured.sort(key=lambda item: item["key"])
    return {
        "snapshot_version": __version__,
        "nodes": captured,
        "coverage": {"recorded": [item["key"] for item in captured], "unrecorded": []},
    }


def compare_sources(project_dir: Path, snapshot: Mapping[str, Any] | None) -> dict[str, Any]:
    """Compare current bytes against a baseline without writing any files."""

    if not isinstance(snapshot, Mapping) or "nodes" not in snapshot:
        return {
            "fresh": [],
            "stale": [],
            "unknown": ["__baseline__"],
            "reasons": ["missing-baseline"],
            "coverage": {"recorded": [], "unrecorded": []},
        }
    raw_nodes = snapshot["nodes"]
    if not isinstance(raw_nodes, list):
        return {
            "fresh": [],
            "stale": [],
            "unknown": ["__baseline__"],
            "reasons": ["invalid-baseline"],
            "coverage": {"recorded": [], "unrecorded": []},
        }
    fresh: list[str] = []
    stale: list[str] = []
    unknown: list[str] = []
    reasons: list[str] = []
    recorded: list[str] = []
    for item in raw_nodes:
        if not isinstance(item, Mapping) or not isinstance(item.get("key"), str):
            unknown.append("__baseline__")
            reasons.append("invalid-baseline")
            continue
        key = item["key"]
        recorded.append(key)
        expected = item.get("content_sha256")
        if not isinstance(expected, str) or len(expected) != 64:
            unknown.append(key)
            reasons.append(f"missing-baseline:{key}")
            continue
        try:
            path = _safe_file(Path(project_dir), item.get("path"))
        except ValueError as exc:
            message = str(exc)
            if "source missing" in message or "regular file" in message:
                stale.append(key)
                reasons.append(f"missing-source:{key}")
            elif "symlink" in message or "unsafe path" in message:
                unknown.append(key)
                reasons.append(f"unsafe-source:{key}")
            else:
                unknown.append(key)
                reasons.append(f"unreadable-source:{key}")
            continue
        try:
            actual = _sha256(path)
        except OSError:
            unknown.append(key)
            reasons.append(f"unreadable-source:{key}")
            continue
        if actual == expected:
            fresh.append(key)
        else:
            stale.append(key)
            reasons.append(f"changed-source:{key}")
    fresh.sort()
    stale.sort()
    unknown.sort()
    recorded.sort()
    return {
        "fresh": fresh,
        "stale": stale,
        "unknown": unknown,
        "reasons": sorted(set(reasons)),
        "coverage": {"recorded": recorded, "unrecorded": []},
    }

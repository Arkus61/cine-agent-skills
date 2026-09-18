"""Crash-safe publication of one staged artifact in a task workspace.

The helper deliberately stays below the workflow layer.  It gives a pilot a
small, auditable boundary for publishing bytes without pretending to be a
Blender connector or a general-purpose scheduler.
"""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from .state import append_event, read_events

_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")


class _UnsafePath(ValueError):
    """Internal marker for a target outside the exclusive task workspace."""


def _digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _digest_file(path: Path) -> str | None:
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise _UnsafePath(f"publish target is not a regular file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalise_digest(value: str | None, *, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ValueError(f"{field} must be a SHA-256 hex digest or None")
    return value.lower()


def _safe_target(workspace: Path, relative_path: str) -> tuple[str, Path]:
    root = Path(workspace)
    if not isinstance(relative_path, str) or not relative_path:
        raise _UnsafePath("relative_path must be a non-empty relative path")
    if "\x00" in relative_path:
        raise _UnsafePath("relative_path contains an embedded null")
    if root.is_symlink() or not root.exists() or not root.is_dir():
        raise _UnsafePath("workspace must be an existing regular directory")

    relative = Path(relative_path)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise _UnsafePath("relative_path must stay inside the workspace")
    if any(part in {"", "."} for part in relative.parts):
        raise _UnsafePath("relative_path contains an unsafe component")

    current = root
    for part in relative.parts[:-1]:
        current /= part
        if current.is_symlink():
            raise _UnsafePath("relative_path traverses a symlink")
        if current.exists():
            if not current.is_dir():
                raise _UnsafePath("relative_path traverses a non-directory")
        else:
            current.mkdir()

    target = root.joinpath(*relative.parts)
    if target.is_symlink():
        raise _UnsafePath("publish target cannot be a symlink")
    if target.exists() and not target.is_file():
        raise _UnsafePath("publish target must be a regular file")
    return relative.as_posix(), target


def _event_map(database: Path, operation_id: str) -> dict[str, dict[str, Any]]:
    events: dict[str, dict[str, Any]] = {}
    for event in read_events(database):
        if event.get("publish_operation_id") == operation_id:
            kind = event.get("kind")
            if isinstance(kind, str):
                events[kind] = event
    return events


def _operation_matches(
    event: Mapping[str, Any],
    *,
    relative_path: str,
    expected_base_sha256: str | None,
    candidate_sha256: str,
    candidate_bytes: int,
) -> bool:
    return (
        event.get("relative_path") == relative_path
        and event.get("expected_base_sha256") == expected_base_sha256
        and event.get("candidate_sha256") == candidate_sha256
        and event.get("bytes") == candidate_bytes
    )


def _intent_event(
    operation_id: str,
    *,
    relative_path: str,
    expected_base_sha256: str | None,
    candidate_sha256: str,
    candidate_bytes: int,
) -> dict[str, Any]:
    event_id = f"{operation_id}:intent"
    return {
        "operation_id": event_id,
        "event_id": event_id,
        "publish_operation_id": operation_id,
        "kind": "artifact-publish-intent",
        "relative_path": relative_path,
        "expected_base_sha256": expected_base_sha256,
        "candidate_sha256": candidate_sha256,
        "bytes": candidate_bytes,
    }


def _receipt_event(
    operation_id: str,
    *,
    relative_path: str,
    expected_base_sha256: str | None,
    previous_sha256: str | None,
    candidate_sha256: str,
    candidate_bytes: int,
    status: str,
) -> dict[str, Any]:
    event_id = f"{operation_id}:receipt"
    return {
        "operation_id": event_id,
        "event_id": event_id,
        "publish_operation_id": operation_id,
        "kind": "artifact-publish-receipt",
        "status": status,
        "relative_path": relative_path,
        "expected_base_sha256": expected_base_sha256,
        "previous_sha256": previous_sha256,
        "candidate_sha256": candidate_sha256,
        "bytes": candidate_bytes,
    }


def _blocked(relative_path: str, reason: str, **details: Any) -> dict[str, Any]:
    return {"status": "blocked", "reason": reason, "relative_path": relative_path, **details}


def publish_artifact(
    workspace: Path,
    relative_path: str,
    candidate_bytes: bytes,
    *,
    expected_base_sha256: str | None,
    database: Path,
    operation_id: str,
    validate_staged: Callable[[Path], None] | None = None,
) -> dict[str, Any]:
    """Publish one byte payload with base-digest and crash-recovery guards.

    ``workspace`` is the exclusive task workspace and ``relative_path`` is
    intentionally relative to it.  ``expected_base_sha256=None`` means the
    target must not exist.  The function journals an intent before replacing
    the file and a receipt after replacement.  If the process stops between
    those writes, a retry reconciles only an exact candidate digest; unknown
    bytes are reported as a conflict and are never overwritten.
    """

    if not isinstance(candidate_bytes, (bytes, bytearray, memoryview)):
        raise ValueError("candidate_bytes must be bytes-like")
    if not isinstance(operation_id, str) or not operation_id:
        raise ValueError("operation_id must be a non-empty string")
    expected_base_sha256 = _normalise_digest(
        expected_base_sha256, field="expected_base_sha256"
    )
    candidate = bytes(candidate_bytes)
    candidate_sha256 = _digest_bytes(candidate)
    candidate_size = len(candidate)

    try:
        safe_path, target = _safe_target(Path(workspace), relative_path)
    except _UnsafePath as exc:
        return _blocked(relative_path, "unsafe-path", message=str(exc))

    database = Path(database)
    journal = _event_map(database, operation_id)
    intent = journal.get("artifact-publish-intent")
    receipt = journal.get("artifact-publish-receipt")
    if receipt is not None:
        if not _operation_matches(
            receipt,
            relative_path=safe_path,
            expected_base_sha256=expected_base_sha256,
            candidate_sha256=candidate_sha256,
            candidate_bytes=candidate_size,
        ):
            return _blocked(safe_path, "operation-conflict")
        try:
            receipt_current_sha256 = _digest_file(target)
        except _UnsafePath as exc:
            return _blocked(safe_path, "unsafe-path", message=str(exc))
        if receipt_current_sha256 != receipt.get("candidate_sha256"):
            return _blocked(
                safe_path,
                "publish-outcome-unknown",
                current_sha256=receipt_current_sha256,
                candidate_sha256=candidate_sha256,
            )
        return {"status": "reused", "receipt": receipt}
    if intent is not None and not _operation_matches(
        intent,
        relative_path=safe_path,
        expected_base_sha256=expected_base_sha256,
        candidate_sha256=candidate_sha256,
        candidate_bytes=candidate_size,
    ):
        return _blocked(safe_path, "operation-conflict")

    try:
        current_sha256 = _digest_file(target)
    except _UnsafePath as exc:
        return _blocked(safe_path, "unsafe-path", message=str(exc))

    if intent is not None:
        if current_sha256 == candidate_sha256:
            reconciled = _receipt_event(
                operation_id,
                relative_path=safe_path,
                expected_base_sha256=expected_base_sha256,
                previous_sha256=expected_base_sha256,
                candidate_sha256=candidate_sha256,
                candidate_bytes=candidate_size,
                status="reconciled",
            )
            try:
                append_event(database, reconciled)
            except Exception as exc:  # pragma: no cover - exercised through retry tests
                return {
                    "status": "outcome-unknown",
                    "reason": "receipt-write-failed",
                    "relative_path": safe_path,
                    "candidate_sha256": candidate_sha256,
                    "message": str(exc),
                }
            return {"status": "reconciled", "receipt": reconciled}
        if current_sha256 != expected_base_sha256:
            return _blocked(
                safe_path,
                "publish-outcome-unknown",
                current_sha256=current_sha256,
                candidate_sha256=candidate_sha256,
            )

    staged: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".stage",
            delete=False,
        ) as handle:
            staged = Path(handle.name)
            handle.write(candidate)
            handle.flush()
            os.fsync(handle.fileno())

        if validate_staged is not None:
            try:
                validate_staged(staged)
            except Exception as exc:
                return {
                    "status": "blocked",
                    "reason": "validation-failed",
                    "relative_path": safe_path,
                    "message": str(exc),
                }

        staged_sha256 = _digest_file(staged)
        if staged_sha256 != candidate_sha256:
            return {
                "status": "blocked",
                "reason": "staged-bytes-changed",
                "relative_path": safe_path,
                "candidate_sha256": candidate_sha256,
                "staged_sha256": staged_sha256,
            }

        try:
            current_sha256 = _digest_file(target)
        except _UnsafePath as exc:
            return _blocked(safe_path, "unsafe-path", message=str(exc))
        if current_sha256 != expected_base_sha256:
            return _blocked(
                safe_path,
                "base-digest-mismatch",
                current_sha256=current_sha256,
                expected_base_sha256=expected_base_sha256,
            )

        if intent is None:
            intent = _intent_event(
                operation_id,
                relative_path=safe_path,
                expected_base_sha256=expected_base_sha256,
                candidate_sha256=candidate_sha256,
                candidate_bytes=candidate_size,
            )
            try:
                append_event(database, intent)
            except Exception as exc:
                return _blocked(safe_path, "intent-write-failed", message=str(exc))

        try:
            current_sha256 = _digest_file(target)
        except _UnsafePath as exc:
            return _blocked(safe_path, "unsafe-path", message=str(exc))
        if current_sha256 != expected_base_sha256:
            return _blocked(
                safe_path,
                "base-digest-mismatch",
                current_sha256=current_sha256,
                expected_base_sha256=expected_base_sha256,
            )

        os.replace(staged, target)
        staged = None
        try:
            directory_fd = os.open(target.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except OSError:
            # The rename is still atomic; a platform may simply not support
            # directory fsync.  The journal remains the recovery authority.
            pass

        receipt = _receipt_event(
            operation_id,
            relative_path=safe_path,
            expected_base_sha256=expected_base_sha256,
            previous_sha256=current_sha256,
            candidate_sha256=candidate_sha256,
            candidate_bytes=candidate_size,
            status="published",
        )
        try:
            append_event(database, receipt)
        except Exception as exc:
            return {
                "status": "outcome-unknown",
                "reason": "receipt-write-failed",
                "relative_path": safe_path,
                "candidate_sha256": candidate_sha256,
                "message": str(exc),
            }
        return {"status": "published", "receipt": receipt}
    except OSError as exc:
        return _blocked(safe_path, "publish-failed", message=str(exc))
    finally:
        if staged is not None:
            try:
                staged.unlink()
            except FileNotFoundError:
                pass


__all__ = ["publish_artifact"]

"""Small append-only SQLite journal for runtime evidence."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def _canonical(event: Mapping[str, Any]) -> tuple[str, str]:
    try:
        payload = json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"event is not JSON serializable: {exc}") from exc
    return payload, hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _connect(database: Path) -> sqlite3.Connection:
    path = Path(database)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            sequence INTEGER PRIMARY KEY AUTOINCREMENT,
            operation_id TEXT NOT NULL UNIQUE,
            event_id TEXT NOT NULL,
            payload_sha256 TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )
        """
    )
    connection.commit()
    return connection


def append_event(database: Path, event: Mapping[str, Any]) -> str:
    """Append an event, or return the same ID for an identical operation.

    There is intentionally no update/delete API. SQLite protects the local
    journal from accidental concurrent writes; it is not a tamper-proof log
    against an owner who can edit the database file directly.
    """

    if not isinstance(event, Mapping):
        raise ValueError("event must be an object")
    operation_id = event.get("operation_id")
    if not isinstance(operation_id, str) or not operation_id:
        raise ValueError("event operation_id must be a non-empty string")
    payload, digest = _canonical(event)
    event_id = event.get("event_id", operation_id)
    if not isinstance(event_id, str) or not event_id:
        raise ValueError("event event_id must be a non-empty string")
    connection = _connect(Path(database))
    try:
        with connection:
            existing = connection.execute(
                "SELECT event_id, payload_sha256 FROM events WHERE operation_id = ?",
                (operation_id,),
            ).fetchone()
            if existing is not None:
                if existing[1] != digest:
                    raise ValueError(f"conflicting event reuse for operation_id {operation_id}")
                return str(existing[0])
            connection.execute(
                "INSERT INTO events(operation_id, event_id, payload_sha256, payload_json) VALUES (?, ?, ?, ?)",
                (operation_id, event_id, digest, payload),
            )
        return event_id
    finally:
        connection.close()


def read_events(database: Path) -> list[dict[str, Any]]:
    connection = _connect(Path(database))
    try:
        rows = connection.execute(
            "SELECT payload_json FROM events ORDER BY sequence"
        ).fetchall()
        return [json.loads(row[0]) for row in rows]
    finally:
        connection.close()

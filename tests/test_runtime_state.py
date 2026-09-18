from __future__ import annotations

from pathlib import Path

import pytest


def test_append_event_is_idempotent_for_identical_operation(tmp_path: Path) -> None:
    from cine_skills.runtime.state import append_event, read_events

    db = tmp_path / "state.sqlite3"
    event = {"operation_id": "op-1", "kind": "context-compiled", "input_digest": "a" * 64}
    first = append_event(db, event)
    second = append_event(db, dict(event))

    assert first == second == "op-1"
    assert read_events(db) == [event]


def test_append_event_rejects_conflicting_reuse_and_does_not_update(tmp_path: Path) -> None:
    from cine_skills.runtime.state import append_event, read_events

    db = tmp_path / "state.sqlite3"
    append_event(db, {"operation_id": "op-1", "kind": "tool-call"})
    with pytest.raises(ValueError, match="conflicting"):
        append_event(db, {"operation_id": "op-1", "kind": "different"})
    assert read_events(db) == [{"operation_id": "op-1", "kind": "tool-call"}]


def test_append_event_requires_an_operation_id(tmp_path: Path) -> None:
    from cine_skills.runtime.state import append_event

    with pytest.raises(ValueError, match="operation_id"):
        append_event(tmp_path / "state.sqlite3", {"kind": "missing-id"})

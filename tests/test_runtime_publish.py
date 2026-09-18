from __future__ import annotations

import hashlib
from pathlib import Path

import pytest


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _publish(workspace: Path, relative_path: str, candidate: bytes, expected: str | None, database: Path, operation_id: str, **kwargs):
    from cine_skills.runtime.publish import publish_artifact

    return publish_artifact(
        workspace,
        relative_path,
        candidate,
        expected_base_sha256=expected,
        database=database,
        operation_id=operation_id,
        **kwargs,
    )


def test_publish_atomically_replaces_after_base_check_and_journals_receipt(tmp_path: Path) -> None:
    from cine_skills.runtime.state import read_events

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "scene.json"
    original = b'{"version": 1}\n'
    candidate = b'{"version": 2}\n'
    target.write_bytes(original)

    result = _publish(
        workspace,
        "scene.json",
        candidate,
        _digest(original),
        tmp_path / "state.sqlite3",
        "publish-1",
    )

    assert result["status"] == "published"
    assert result["receipt"]["candidate_sha256"] == _digest(candidate)
    assert result["receipt"]["previous_sha256"] == _digest(original)
    assert target.read_bytes() == candidate
    events = read_events(tmp_path / "state.sqlite3")
    assert [event["kind"] for event in events] == [
        "artifact-publish-intent",
        "artifact-publish-receipt",
    ]
    assert list(workspace.iterdir()) == [target]

    replay = _publish(
        workspace,
        "scene.json",
        candidate,
        _digest(original),
        tmp_path / "state.sqlite3",
        "publish-1",
    )
    assert replay["status"] == "reused"


def test_publish_does_not_hide_drift_after_a_receipt(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "scene.json"
    original = b"original\n"
    candidate = b"candidate\n"
    target.write_bytes(original)
    database = tmp_path / "state.sqlite3"

    _publish(
        workspace,
        "scene.json",
        candidate,
        _digest(original),
        database,
        "publish-drift",
    )
    target.write_bytes(b"edited-by-other-writer\n")

    result = _publish(
        workspace,
        "scene.json",
        candidate,
        _digest(original),
        database,
        "publish-drift",
    )

    assert result["status"] == "blocked"
    assert result["reason"] == "publish-outcome-unknown"
    assert target.read_bytes() == b"edited-by-other-writer\n"


def test_publish_can_create_a_missing_target_when_base_is_none(tmp_path: Path) -> None:
    from cine_skills.runtime.state import read_events

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    candidate = b"new-artifact\n"
    database = tmp_path / "state.sqlite3"

    result = _publish(
        workspace,
        "nested/scene.json",
        candidate,
        None,
        database,
        "publish-new",
    )

    assert result["status"] == "published"
    assert (workspace / "nested/scene.json").read_bytes() == candidate
    assert read_events(database)[0]["expected_base_sha256"] is None


def test_publish_rejects_stale_base_and_preserves_target(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "scene.json"
    current = b'{"version": 3}\n'
    target.write_bytes(current)

    result = _publish(
        workspace,
        "scene.json",
        b'{"version": 4}\n',
        _digest(b'{"version": 2}\n'),
        tmp_path / "state.sqlite3",
        "publish-stale",
    )

    assert result == {
        "status": "blocked",
        "reason": "base-digest-mismatch",
        "relative_path": "scene.json",
        "current_sha256": _digest(current),
        "expected_base_sha256": _digest(b'{"version": 2}\n'),
    }
    assert target.read_bytes() == current


def test_publish_reconciles_after_receipt_gap_without_overwriting_unknown_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from cine_skills.runtime import publish as publish_module
    from cine_skills.runtime.state import append_event, read_events

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "scene.json"
    original = b"original\n"
    candidate = b"candidate\n"
    target.write_bytes(original)
    database = tmp_path / "state.sqlite3"
    operation_id = "publish-gap"
    real_append_event = publish_module.append_event

    def fail_receipt(database_path: Path, event: dict) -> str:
        if event.get("operation_id") == f"{operation_id}:receipt":
            raise OSError("simulated journal outage")
        return real_append_event(database_path, event)

    monkeypatch.setattr(publish_module, "append_event", fail_receipt)
    first = _publish(
        workspace,
        "scene.json",
        candidate,
        _digest(original),
        database,
        operation_id,
    )
    assert first["status"] == "outcome-unknown"
    assert target.read_bytes() == candidate

    monkeypatch.setattr(publish_module, "append_event", real_append_event)
    second = _publish(
        workspace,
        "scene.json",
        candidate,
        _digest(original),
        database,
        operation_id,
    )
    assert second["status"] == "reconciled"
    assert target.read_bytes() == candidate
    assert [event["kind"] for event in read_events(database)] == [
        "artifact-publish-intent",
        "artifact-publish-receipt",
    ]


def test_publish_blocks_unknown_bytes_after_unjournaled_outcome(tmp_path: Path) -> None:
    from cine_skills.runtime.state import append_event

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "scene.json"
    original = b"original\n"
    candidate = b"candidate\n"
    unknown = b"unknown-writer\n"
    target.write_bytes(unknown)
    database = tmp_path / "state.sqlite3"
    append_event(
        database,
        {
            "operation_id": "publish-unknown:intent",
            "event_id": "publish-unknown:intent",
            "kind": "artifact-publish-intent",
            "publish_operation_id": "publish-unknown",
            "relative_path": "scene.json",
            "expected_base_sha256": _digest(original),
            "candidate_sha256": _digest(candidate),
            "bytes": len(candidate),
        },
    )

    result = _publish(
        workspace,
        "scene.json",
        candidate,
        _digest(original),
        database,
        "publish-unknown",
    )

    assert result == {
        "status": "blocked",
        "reason": "publish-outcome-unknown",
        "relative_path": "scene.json",
        "current_sha256": _digest(unknown),
        "candidate_sha256": _digest(candidate),
    }
    assert target.read_bytes() == unknown


def test_publish_validation_and_path_safety_preserve_original(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "scene.json"
    original = b"original\n"
    target.write_bytes(original)
    database = tmp_path / "state.sqlite3"

    def reject(_: Path) -> None:
        raise ValueError("validator rejected staged artifact")

    rejected = _publish(
        workspace,
        "scene.json",
        b"candidate\n",
        _digest(original),
        database,
        "publish-validation",
        validate_staged=reject,
    )
    assert rejected == {
        "status": "blocked",
        "reason": "validation-failed",
        "relative_path": "scene.json",
        "message": "validator rejected staged artifact",
    }
    assert target.read_bytes() == original

    traversal = _publish(
        workspace,
        "../outside.json",
        b"candidate\n",
        _digest(original),
        database,
        "publish-traversal",
    )
    assert traversal["status"] == "blocked"
    assert traversal["reason"] == "unsafe-path"

    outside = tmp_path / "outside.json"
    outside.write_bytes(b"outside\n")
    (workspace / "linked.json").symlink_to(outside)
    symlink = _publish(
        workspace,
        "linked.json",
        b"candidate\n",
        _digest(b"outside\n"),
        database,
        "publish-symlink",
    )
    assert symlink["status"] == "blocked"
    assert symlink["reason"] == "unsafe-path"
    assert outside.read_bytes() == b"outside\n"

    null_path = _publish(
        workspace,
        "bad\x00.json",
        b"candidate\n",
        _digest(original),
        database,
        "publish-null-path",
    )
    assert null_path["status"] == "blocked"
    assert null_path["reason"] == "unsafe-path"

    for unsafe_path in (r"\outside.json", r"D:outside.json", r"D:\\outside.json"):
        operation_suffix = unsafe_path.replace(":", "-").replace("\\", "_")
        windows_path = _publish(
            workspace,
            unsafe_path,
            b"candidate\n",
            _digest(original),
            database,
            f"publish-{operation_suffix}",
        )
        assert windows_path["status"] == "blocked"
        assert windows_path["reason"] == "unsafe-path"


def test_publish_rechecks_bytes_after_staged_validation(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "scene.json"
    original = b"original\n"
    target.write_bytes(original)

    def mutate_staged(path: Path) -> None:
        path.write_bytes(b"mutated-by-validator\n")

    result = _publish(
        workspace,
        "scene.json",
        b"candidate\n",
        _digest(original),
        tmp_path / "state.sqlite3",
        "publish-mutated-stage",
        validate_staged=mutate_staged,
    )

    assert result == {
        "status": "blocked",
        "reason": "staged-bytes-changed",
        "relative_path": "scene.json",
        "candidate_sha256": _digest(b"candidate\n"),
        "staged_sha256": _digest(b"mutated-by-validator\n"),
    }
    assert target.read_bytes() == original

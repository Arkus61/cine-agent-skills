from __future__ import annotations

from pathlib import Path

import pytest


pytest.importorskip("langgraph")
pytest.importorskip("langgraph.checkpoint.sqlite")


def _task(task_id: str = "camera-1", *, requires_review: bool = False) -> dict:
    return {
        "task_id": task_id,
        "inputs": [],
        "outputs": [task_id],
        "skill_name": "camera-movement-designer",
        "operation_kind": "generate",
        "requires_review": requires_review,
    }


def _config(*, execute, choose_context=None, after_receipt=None) -> dict:
    callbacks = {"execute": execute}
    if choose_context is not None:
        callbacks["choose_context"] = choose_context
    if after_receipt is not None:
        callbacks["after_receipt"] = after_receipt
    return {"callbacks": callbacks}


def test_workflow_runs_finite_task_and_persists_checkpoint(tmp_path: Path) -> None:
    from cine_skills.runtime.workflow import build_workflow

    calls: list[str] = []

    def execute(state: dict) -> dict:
        calls.append(state["current_task"]["task_id"])
        return {
            "candidate": {"shot_id": "SH001", "x": 1},
            "receipt": {"receipt_id": "receipt-1", "output_digest": "a" * 64},
        }

    graph = build_workflow(_config(execute=execute), tmp_path / "state")
    config = {"configurable": {"thread_id": "run-1"}}
    result = graph.invoke(
        {"run_id": "run-1", "project_id": "demo", "tasks": [_task()]},
        config,
    )

    assert result["outcome"] == "completed"
    assert result["results"][0]["task_id"] == "camera-1"
    assert calls == ["camera-1"]
    assert (tmp_path / "state" / "workflow-checkpoints.sqlite3").is_file()


def test_review_interrupt_resumes_with_same_thread(tmp_path: Path) -> None:
    from langgraph.types import Command

    from cine_skills.runtime.workflow import build_workflow

    def execute(state: dict) -> dict:
        return {
            "candidate": {"shot_id": "SH001"},
            "receipt": {"receipt_id": "receipt-review", "output_digest": "b" * 64},
        }

    graph = build_workflow(_config(execute=execute), tmp_path / "state")
    config = {"configurable": {"thread_id": "review-1"}}
    initial = graph.invoke(
        {"run_id": "review-1", "tasks": [_task(requires_review=True)]},
        config,
    )

    assert initial["__interrupt__"]
    resumed = graph.invoke(Command(resume={"approved": True}), config)
    assert resumed["outcome"] == "completed"
    assert resumed["results"][0]["review"] == "approved"


def test_restart_after_context_boundary_recomputes_without_partial_publish(tmp_path: Path) -> None:
    from cine_skills.runtime.workflow import build_workflow

    crash_marker = tmp_path / "context-crashed"
    execute_calls: list[str] = []

    def after_context(state: dict) -> None:
        if not crash_marker.exists():
            crash_marker.write_text("crashed", encoding="utf-8")
            raise RuntimeError("simulated context boundary stop")

    def execute(state: dict) -> dict:
        execute_calls.append(state["current_task"]["task_id"])
        return {
            "candidate": {"shot_id": "SH001"},
            "receipt": {"receipt_id": "receipt-context", "output_digest": "d" * 64},
        }

    config_data = _config(execute=execute, after_receipt=None)
    config_data["callbacks"]["after_context"] = after_context
    config = {"configurable": {"thread_id": "context-1"}}
    first = build_workflow(config_data, tmp_path / "state")
    with pytest.raises(RuntimeError, match="context boundary stop"):
        first.invoke({"run_id": "context-1", "tasks": [_task()]}, config)

    resumed = build_workflow(config_data, tmp_path / "state")
    result = resumed.invoke({}, config)
    assert result["outcome"] == "completed"
    assert execute_calls == ["camera-1"]


def test_resume_uses_journaled_receipt_after_checkpoint_gap(tmp_path: Path) -> None:
    from cine_skills.runtime.workflow import build_workflow

    counter = tmp_path / "external-counter.txt"
    crash_marker = tmp_path / "crashed"

    def execute(state: dict) -> dict:
        current = int(counter.read_text(encoding="utf-8")) if counter.exists() else 0
        counter.write_text(str(current + 1), encoding="utf-8")
        return {
            "candidate": {"shot_id": "SH001", "revision": current + 1},
            "receipt": {"receipt_id": "receipt-crash", "output_digest": "c" * 64},
        }

    def after_receipt(state: dict) -> None:
        if not crash_marker.exists():
            crash_marker.write_text("crashed", encoding="utf-8")
            raise RuntimeError("simulated process termination")

    config_data = _config(execute=execute, after_receipt=after_receipt)
    config = {"configurable": {"thread_id": "crash-1"}}
    first = build_workflow(config_data, tmp_path / "state")
    with pytest.raises(RuntimeError, match="simulated process termination"):
        first.invoke({"run_id": "crash-1", "tasks": [_task()]}, config)

    resumed = build_workflow(config_data, tmp_path / "state")
    result = resumed.invoke({}, config)
    assert result["outcome"] == "completed"
    assert result["results"][0]["receipt"]["receipt_id"] == "receipt-crash"
    assert counter.read_text(encoding="utf-8") == "1"


def test_missing_receipt_is_outcome_unknown_and_not_replayed(tmp_path: Path) -> None:
    from cine_skills.runtime.workflow import ExternalOutcomeUnknown, build_workflow

    calls: list[str] = []

    def execute(state: dict) -> dict:
        calls.append(state["current_task"]["task_id"])
        raise ExternalOutcomeUnknown("server disconnected after write")

    graph = build_workflow(_config(execute=execute), tmp_path / "state")
    config = {"configurable": {"thread_id": "unknown-1"}}
    result = graph.invoke(
        {"run_id": "unknown-1", "tasks": [_task()]},
        config,
    )

    assert result["outcome"] == "outcome-unknown"
    assert result["blocked_reason"] == "server disconnected after write"
    assert calls == ["camera-1"]

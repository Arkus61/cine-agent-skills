"""A bounded, resumable Film OS workflow built on LangGraph.

The module is an adapter around the community LangGraph state machine and
SQLite checkpointer.  It does not implement another scheduler or persistence
protocol.  Film OS owns the task contract, receipt semantics and conservative
outcome handling; LangGraph owns graph execution, checkpointing and
interrupt/resume mechanics.

The dependency is intentionally optional.  Core validators and the other
offline runtime helpers remain importable when the runtime extra is not
installed.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, TypedDict

from .state import append_event, read_events


class WorkflowUnavailableError(RuntimeError):
    """Raised when the optional LangGraph runtime is not installed."""


class ExternalOutcomeUnknown(RuntimeError):
    """Raised when an external action may have happened without a receipt."""


class WorkflowState(TypedDict, total=False):
    """JSON-serializable state kept in a LangGraph checkpoint."""

    run_id: str
    project_id: str
    tasks: list[dict[str, Any]]
    current_index: int
    current_task: dict[str, Any]
    task_status: str
    context: dict[str, Any]
    candidate: dict[str, Any]
    validation: dict[str, Any]
    review: str
    receipt: dict[str, Any]
    publish_receipt: dict[str, Any]
    published: dict[str, Any]
    results: list[dict[str, Any]]
    outcome: str
    blocked_reason: str


Callback = Callable[[dict[str, Any]], Mapping[str, Any] | None]
_TASK_KINDS = {"reuse", "generate", "blocked"}
_STOP_OUTCOMES = {
    "blocked",
    "needs-context",
    "outcome-unknown",
    "validation-failed",
    "review-rejected",
}


def _load_langgraph() -> tuple[Any, Any, Any, Any, Any, Any]:
    """Load the maintained community runtime only when a workflow is built."""

    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
        from langgraph.graph import END, START, StateGraph
        from langgraph.types import interrupt
    except ImportError as exc:  # pragma: no cover - exercised without extra
        raise WorkflowUnavailableError(
            "LangGraph workflow is optional; install the 'runtime' extra "
            "(langgraph and langgraph-checkpoint-sqlite)"
        ) from exc
    return StateGraph, START, END, SqliteSaver, interrupt, sqlite3


def _json_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object")
    try:
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False)
        decoded = json.loads(encoded)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"{field} must be JSON serializable: {exc}") from exc
    if not isinstance(decoded, dict):
        raise ValueError(f"{field} must be an object")
    return decoded


def _state_dir(value: Path) -> Path:
    directory = Path(value)
    if directory.exists() and directory.is_symlink():
        raise ValueError("workflow state directory must not be a symlink")
    directory.mkdir(parents=True, exist_ok=True)
    if not directory.is_dir():
        raise ValueError("workflow state path must be a directory")
    return directory.resolve()


def _task(value: Any) -> dict[str, Any]:
    task = _json_object(value, "task")
    task_id = task.get("task_id")
    if not isinstance(task_id, str) or not task_id:
        raise ValueError("task_id must be a non-empty string")
    operation_kind = task.get("operation_kind")
    if operation_kind not in _TASK_KINDS:
        raise ValueError(f"unsupported operation_kind for {task_id}: {operation_kind!r}")
    for field in ("inputs", "outputs"):
        values = task.get(field, [])
        if not isinstance(values, list) or not all(isinstance(item, str) and item for item in values):
            raise ValueError(f"task {task_id} {field} must be an array of names")
    skill_name = task.get("skill_name")
    if not isinstance(skill_name, str) or not skill_name:
        raise ValueError(f"task {task_id} skill_name must be a non-empty string")
    return task


def _normalise_tasks(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValueError("tasks must be a non-empty array")
    tasks = [_task(item) for item in value]
    ids = [item["task_id"] for item in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("tasks must not contain duplicate task_id values")
    return tasks


def _callback(callbacks: Mapping[str, Any], name: str, state: WorkflowState) -> dict[str, Any] | None:
    candidate = callbacks.get(name)
    if candidate is None:
        return None
    if not callable(candidate):
        raise ValueError(f"workflow callback {name} must be callable")
    result = candidate(dict(state))
    if result is None:
        return None
    return _json_object(result, f"workflow callback {name} result")


def _operation_id(state: WorkflowState, suffix: str = "execute") -> str:
    run_id = state.get("run_id")
    task = state.get("current_task") or {}
    task_id = task.get("task_id")
    if not isinstance(run_id, str) or not run_id or not isinstance(task_id, str) or not task_id:
        raise ValueError("workflow state is missing run_id/current task")
    return f"{run_id}:{task_id}:{suffix}"


def _journal_event(database: Path, operation_id: str, event: Mapping[str, Any]) -> dict[str, Any]:
    payload = _json_object(event, "journal event")
    payload["operation_id"] = operation_id
    payload.setdefault("event_id", operation_id)
    append_event(database, payload)
    return payload


def _find_receipt(database: Path, operation_id: str, kind: str) -> dict[str, Any] | None:
    for event in read_events(database):
        if event.get("operation_id") == operation_id and event.get("kind") == kind:
            return event
    return None


def _blocked(state: WorkflowState, outcome: str, reason: str) -> dict[str, Any]:
    return {"task_status": outcome, "outcome": outcome, "blocked_reason": reason}


def build_workflow(config: Mapping[str, Any], state_dir: Path) -> Any:
    """Build a LangGraph workflow with a persistent SQLite checkpointer.

    ``config['callbacks']`` may provide small domain adapters with this common
    contract: each callback receives a JSON-compatible state dictionary and
    returns a JSON-compatible mapping.  Supported names are
    ``choose_context``, ``reuse``, ``execute``, ``validate_candidate``,
    ``publish``, ``after_context`` and ``after_receipt``.  The callbacks are held by the graph
    closure, never serialized into checkpoint state.

    A generated task must return ``candidate`` and ``receipt``.  The receipt is
    journaled before the node returns, so a process termination after the
    external action can resume without replaying it.  Missing or ambiguous
    receipts produce ``outcome-unknown`` and are never presented as success.
    """

    if not isinstance(config, Mapping):
        raise ValueError("workflow config must be an object")
    callbacks = config.get("callbacks", {})
    if not isinstance(callbacks, Mapping):
        raise ValueError("workflow callbacks must be an object")
    for name, callback in callbacks.items():
        if not isinstance(name, str) or not callable(callback):
            raise ValueError(f"workflow callback {name!r} must be callable")
    require_review = config.get("require_review", False)
    if not isinstance(require_review, bool):
        raise ValueError("require_review must be boolean")
    directory = _state_dir(Path(state_dir))
    checkpoint_path = directory / "workflow-checkpoints.sqlite3"
    if checkpoint_path.exists() and checkpoint_path.is_symlink():
        raise ValueError("workflow checkpoint file must not be a symlink")

    StateGraph, START, END, SqliteSaver, interrupt, sqlite_module = _load_langgraph()
    connection = sqlite_module.connect(str(checkpoint_path), check_same_thread=False)
    checkpointer = SqliteSaver(connection)
    checkpointer.setup()

    def validate_inputs(state: WorkflowState) -> dict[str, Any]:
        run_id = state.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            return _blocked(state, "blocked", "missing-run-id")
        try:
            tasks = _normalise_tasks(state.get("tasks"))
        except ValueError as exc:
            return _blocked(state, "blocked", str(exc))
        index = state.get("current_index", 0)
        if isinstance(index, bool) or not isinstance(index, int) or index < 0:
            return _blocked(state, "blocked", "invalid-current-index")
        if index >= len(tasks):
            return {"tasks": tasks, "outcome": "completed", "task_status": "completed"}
        current = tasks[index]
        result: dict[str, Any] = {
            "tasks": tasks,
            "current_index": index,
            "current_task": current,
            "task_status": "running",
            "context": {},
            "candidate": {},
            "validation": {},
            "review": "pending",
            "receipt": {},
            "publish_receipt": {},
            "published": {},
            "blocked_reason": "",
        }
        if current["operation_kind"] == "blocked":
            result.update(_blocked(state, "blocked", "blocked-input-task"))
        return result

    def choose_context(state: WorkflowState) -> dict[str, Any]:
        if state.get("task_status") == "blocked":
            return {}
        try:
            result = _callback(callbacks, "choose_context", state)
        except Exception as exc:
            return _blocked(state, "blocked", f"context-selection-error:{exc}")
        if result is None:
            result = {"status": "ready"}
        status = result.get("status", "ready")
        if status not in {"ready", "needs-context", "blocked"}:
            return _blocked(state, "blocked", "invalid-context-status")
        if status != "ready":
            return {"context": result, **_blocked(state, status, result.get("reason", status))}
        after_context = callbacks.get("after_context")
        if after_context is not None:
            if not callable(after_context):
                raise ValueError("workflow callback after_context must be callable")
            # A checkpoint is written after this node returns.  A caller may
            # use this hook to model a process stop at that boundary; the
            # context compiler is deterministic and safe to rerun.
            after_context(dict(state, context=result))
        return {"context": result, "task_status": "context-ready", "outcome": "running"}

    def reuse_or_execute(state: WorkflowState) -> dict[str, Any]:
        if state.get("task_status") in _STOP_OUTCOMES or state.get("outcome") in _STOP_OUTCOMES:
            return {}
        task = state["current_task"]
        if task["operation_kind"] == "reuse":
            result = _callback(callbacks, "reuse", state)
            if result is None:
                cached = task.get("cached_result")
                result = {"candidate": cached} if isinstance(cached, Mapping) else None
            if result is None or not isinstance(result.get("candidate"), Mapping):
                return _blocked(state, "blocked", "missing-reuse-result")
            return {
                "candidate": _json_object(result["candidate"], "reused candidate"),
                "receipt": {"kind": "cache-reuse", "operation_id": _operation_id(state)},
                "task_status": "executed",
                "outcome": "running",
            }

        operation_id = _operation_id(state)
        existing = _find_receipt(database_path, operation_id, "external-receipt")
        if existing is not None:
            return {
                "candidate": _json_object(existing.get("candidate"), "journaled candidate"),
                "receipt": _json_object(existing.get("receipt"), "journaled receipt"),
                "task_status": "reused-receipt",
                "outcome": "running",
            }
        try:
            callback_result = _callback(callbacks, "execute", state)
        except ExternalOutcomeUnknown as exc:
            return _blocked(state, "outcome-unknown", str(exc) or "external-outcome-unknown")
        except Exception as exc:
            # A callback may have reached an external system before failing.
            # Without a durable receipt it is unsafe to retry automatically.
            return _blocked(state, "outcome-unknown", f"execution-error:{exc}")
        if callback_result is None:
            return _blocked(state, "blocked", "missing-executor")
        candidate = callback_result.get("candidate", callback_result.get("result"))
        receipt = callback_result.get("receipt")
        if not isinstance(candidate, Mapping) or not isinstance(receipt, Mapping):
            return _blocked(state, "outcome-unknown", "execution-receipt-missing")
        try:
            candidate_json = _json_object(candidate, "execution candidate")
            receipt_json = _json_object(receipt, "execution receipt")
            _journal_event(
                database_path,
                operation_id,
                {
                    "kind": "external-receipt",
                    "run_id": state["run_id"],
                    "task_id": task["task_id"],
                    "candidate": candidate_json,
                    "receipt": receipt_json,
                },
            )
        except (TypeError, ValueError) as exc:
            return _blocked(state, "outcome-unknown", f"receipt-journal-failed:{exc}")
        after_receipt = callbacks.get("after_receipt")
        if after_receipt is not None:
            if not callable(after_receipt):
                raise ValueError("workflow callback after_receipt must be callable")
            # This hook intentionally runs after the durable receipt.  A
            # process may terminate here; a retry sees the journal and skips
            # the external action.
            after_receipt(dict(state, candidate=candidate_json, receipt=receipt_json))
        return {
            "candidate": candidate_json,
            "receipt": receipt_json,
            "task_status": "executed",
            "outcome": "running",
        }

    def validate_candidate(state: WorkflowState) -> dict[str, Any]:
        if state.get("task_status") in _STOP_OUTCOMES or state.get("outcome") in _STOP_OUTCOMES:
            return {}
        candidate = state.get("candidate")
        if not isinstance(candidate, Mapping):
            return _blocked(state, "validation-failed", "candidate-missing")
        try:
            result = _callback(callbacks, "validate_candidate", state)
        except Exception as exc:
            return _blocked(state, "validation-failed", f"validation-error:{exc}")
        if result is None:
            result = {"status": "valid"}
        status = result.get("status")
        if status != "valid":
            reason = result.get("reason", "candidate-invalid")
            return {"validation": result, **_blocked(state, "validation-failed", str(reason))}
        return {"validation": result, "task_status": "valid", "outcome": "running"}

    def review(state: WorkflowState) -> dict[str, Any]:
        if state.get("task_status") != "valid":
            return {}
        task = state["current_task"]
        needed = require_review or bool(task.get("requires_review", False))
        if not needed:
            return {"review": "not-required", "task_status": "reviewed", "outcome": "running"}
        decision = interrupt(
            {
                "kind": "creative-review",
                "run_id": state["run_id"],
                "task_id": task["task_id"],
                "candidate": state.get("candidate", {}),
                "validation": state.get("validation", {}),
            }
        )
        approved = decision is True or (
            isinstance(decision, Mapping)
            and decision.get("approved") is True
        )
        if not approved:
            return _blocked(state, "review-rejected", "creative-review-rejected") | {"review": "rejected"}
        return {"review": "approved", "task_status": "reviewed", "outcome": "running"}

    def publish(state: WorkflowState) -> dict[str, Any]:
        if state.get("task_status") != "reviewed":
            return {}
        publisher = callbacks.get("publish")
        if publisher is None:
            return {"published": {"candidate": state.get("candidate", {})}, "task_status": "published"}
        if not callable(publisher):
            raise ValueError("workflow callback publish must be callable")
        operation_id = _operation_id(state, "publish")
        existing = _find_receipt(database_path, operation_id, "publish-receipt")
        if existing is not None:
            return {
                "published": _json_object(existing.get("published"), "journaled publication"),
                "publish_receipt": _json_object(existing.get("receipt"), "journaled publish receipt"),
                "task_status": "published",
            }
        try:
            result = _callback(callbacks, "publish", state)
        except ExternalOutcomeUnknown as exc:
            return _blocked(state, "outcome-unknown", str(exc) or "publish-outcome-unknown")
        except Exception as exc:
            return _blocked(state, "outcome-unknown", f"publish-error:{exc}")
        if result is None:
            return _blocked(state, "outcome-unknown", "publish-result-missing")
        published = result.get("published", result.get("result"))
        receipt = result.get("receipt")
        if not isinstance(published, Mapping) or not isinstance(receipt, Mapping):
            return _blocked(state, "outcome-unknown", "publish-receipt-missing")
        published_json = _json_object(published, "publication")
        receipt_json = _json_object(receipt, "publish receipt")
        try:
            _journal_event(
                database_path,
                operation_id,
                {
                    "kind": "publish-receipt",
                    "run_id": state["run_id"],
                    "task_id": state["current_task"]["task_id"],
                    "published": published_json,
                    "receipt": receipt_json,
                },
            )
        except (TypeError, ValueError, OSError, sqlite3.Error) as exc:
            return _blocked(state, "outcome-unknown", f"publish-receipt-journal-failed:{exc}")
        return {
            "published": published_json,
            "publish_receipt": receipt_json,
            "task_status": "published",
        }

    def record_result(state: WorkflowState) -> dict[str, Any]:
        task = state.get("current_task") or {}
        task_id = task.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            return _blocked(state, "blocked", "missing-current-task")
        result = {
            "task_id": task_id,
            "status": state.get("task_status", "blocked"),
            "context_status": (state.get("context") or {}).get("status"),
            "candidate": state.get("candidate", {}),
            "receipt": state.get("receipt", {}),
            "publish_receipt": state.get("publish_receipt", {}),
            "published": state.get("published", {}),
            "review": state.get("review", "pending"),
            "validation": state.get("validation", {}),
        }
        operation_id = _operation_id(state, "result")
        existing = _find_receipt(database_path, operation_id, "result-recorded")
        if existing is None:
            _journal_event(
                database_path,
                operation_id,
                {
                    "kind": "result-recorded",
                    "run_id": state["run_id"],
                    "task_id": task_id,
                    "result": result,
                },
            )
        else:
            stored = existing.get("result")
            if isinstance(stored, Mapping):
                result = _json_object(stored, "journaled result")
        results = list(state.get("results", []))
        if not any(isinstance(item, Mapping) and item.get("task_id") == task_id for item in results):
            results.append(result)
        if state.get("task_status") in _STOP_OUTCOMES or state.get("outcome") in _STOP_OUTCOMES:
            return {"results": results}
        next_index = state.get("current_index", 0) + 1
        tasks = state.get("tasks", [])
        outcome = "completed" if next_index >= len(tasks) else "running"
        return {"results": results, "current_index": next_index, "outcome": outcome}

    def route_after_validate_inputs(state: WorkflowState) -> str:
        if state.get("outcome") in _STOP_OUTCOMES or state.get("outcome") == "completed":
            return END
        if state.get("task_status") == "blocked":
            return "record_result"
        return "choose_context"

    def route_after_context(state: WorkflowState) -> str:
        if state.get("task_status") in _STOP_OUTCOMES or state.get("outcome") in _STOP_OUTCOMES:
            return "record_result"
        return "reuse_or_execute"

    def route_after_execute(state: WorkflowState) -> str:
        if state.get("task_status") in _STOP_OUTCOMES or state.get("outcome") in _STOP_OUTCOMES:
            return "record_result"
        return "validate_candidate"

    def route_after_validation(state: WorkflowState) -> str:
        return "review" if state.get("task_status") == "valid" else "record_result"

    def route_after_review(state: WorkflowState) -> str:
        return "publish" if state.get("task_status") == "reviewed" else "record_result"

    def route_after_record(state: WorkflowState) -> str:
        if state.get("outcome") in _STOP_OUTCOMES or state.get("outcome") == "completed":
            return END
        return "validate_inputs"

    builder = StateGraph(WorkflowState)
    builder.add_node("validate_inputs", validate_inputs)
    builder.add_node("choose_context", choose_context)
    builder.add_node("reuse_or_execute", reuse_or_execute)
    builder.add_node("validate_candidate", validate_candidate)
    builder.add_node("review", review)
    builder.add_node("publish", publish)
    builder.add_node("record_result", record_result)
    builder.add_edge(START, "validate_inputs")
    builder.add_conditional_edges("validate_inputs", route_after_validate_inputs)
    builder.add_conditional_edges("choose_context", route_after_context)
    builder.add_conditional_edges("reuse_or_execute", route_after_execute)
    builder.add_conditional_edges("validate_candidate", route_after_validation)
    builder.add_conditional_edges("review", route_after_review)
    builder.add_edge("publish", "record_result")
    builder.add_conditional_edges("record_result", route_after_record)
    graph = builder.compile(checkpointer=checkpointer)

    # LangGraph does not own the application connection lifetime.  Keep it on
    # the compiled graph and expose a small close hook for long-lived callers.
    database_path = checkpoint_path
    setattr(graph, "_film_os_connection", connection)
    setattr(graph, "_film_os_checkpointer", checkpointer)

    def close() -> None:
        if not connection is None:
            connection.close()

    setattr(graph, "close", close)
    return graph


__all__ = [
    "ExternalOutcomeUnknown",
    "WorkflowState",
    "WorkflowUnavailableError",
    "build_workflow",
]

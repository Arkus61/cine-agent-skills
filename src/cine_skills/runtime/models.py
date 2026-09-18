"""Offline-first model policy with finite call accounting."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def remaining_calls(limit: int, used: int) -> int:
    """Return available calls, clamped at zero for exhausted budgets."""

    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
        raise ValueError("limit must be a non-negative integer")
    if isinstance(used, bool) or not isinstance(used, int) or used < 0:
        raise ValueError("used must be a non-negative integer")
    return max(0, limit - used)


def _candidate_name(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, Mapping):
        for key in ("name", "model", "id"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
        return None
    return None


def select_model(task_class: str, available: dict[str, Any]) -> str | None:
    """Select the first configured model for a task, without making a call."""

    if not isinstance(task_class, str) or not task_class:
        raise ValueError("task_class must be a non-empty string")
    if not isinstance(available, Mapping):
        raise ValueError("available must be a mapping")
    if available.get("enabled", True) is False:
        return None
    models = available.get("models", available)
    if not isinstance(models, Mapping):
        raise ValueError("available models must be a mapping")
    configured = models.get(task_class)
    if configured is None:
        return None
    if isinstance(configured, list):
        for item in configured:
            name = _candidate_name(item)
            if name is not None:
                return name
        return None
    return _candidate_name(configured)

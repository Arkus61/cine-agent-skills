"""Decision evidence records bound to the append-only runtime journal."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .state import append_event


_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def _digest(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")
    return value


def record_decision(database: Path, decision: dict[str, Any]) -> str:
    """Validate a decision's candidate/evidence binding before journaling it."""

    if not isinstance(decision, Mapping):
        raise ValueError("decision must be an object")
    operation_id = decision.get("operation_id")
    if not isinstance(operation_id, str) or not operation_id:
        raise ValueError("decision operation_id must be a non-empty string")
    decision_id = decision.get("decision_id", operation_id)
    if not isinstance(decision_id, str) or not decision_id:
        raise ValueError("decision decision_id must be a non-empty string")
    _digest(decision.get("candidate_digest"), "candidate_digest")
    _digest(decision.get("evidence_digest"), "evidence_digest")
    for field in ("choice", "rationale"):
        if not isinstance(decision.get(field), str) or not decision[field].strip():
            raise ValueError(f"decision {field} must be a non-empty string")
    event = dict(decision)
    event.setdefault("kind", "decision")
    event["event_id"] = decision_id
    return append_event(Path(database), event)

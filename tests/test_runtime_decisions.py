from __future__ import annotations

from pathlib import Path

import pytest


def _decision() -> dict[str, str]:
    return {
        "operation_id": "op-decision-1",
        "decision_id": "decision-1",
        "candidate_digest": "a" * 64,
        "evidence_digest": "b" * 64,
        "choice": "keep-static",
        "rationale": "Static framing preserves the reveal.",
    }


def test_record_decision_binds_candidate_and_evidence(tmp_path: Path) -> None:
    from cine_skills.runtime.decisions import record_decision
    from cine_skills.runtime.state import read_events

    db = tmp_path / "state.sqlite3"
    decision = _decision()
    assert record_decision(db, decision) == "decision-1"
    assert read_events(db) == [
        {**decision, "kind": "decision", "event_id": "decision-1"}
    ]


def test_record_decision_rejects_missing_evidence_binding(tmp_path: Path) -> None:
    from cine_skills.runtime.decisions import record_decision

    decision = _decision()
    decision.pop("evidence_digest")
    with pytest.raises(ValueError, match="evidence_digest"):
        record_decision(tmp_path / "state.sqlite3", decision)


def test_record_decision_rejects_non_digest_values(tmp_path: Path) -> None:
    from cine_skills.runtime.decisions import record_decision

    decision = _decision()
    decision["candidate_digest"] = "unknown"
    with pytest.raises(ValueError, match="candidate_digest"):
        record_decision(tmp_path / "state.sqlite3", decision)

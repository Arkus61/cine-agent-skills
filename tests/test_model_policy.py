from __future__ import annotations

import pytest


def test_budget_cannot_become_negative() -> None:
    from cine_skills.runtime.models import remaining_calls

    assert remaining_calls(limit=2, used=2) == 0
    assert remaining_calls(limit=2, used=3) == 0


def test_unconfigured_policy_does_not_select_a_provider() -> None:
    from cine_skills.runtime.models import select_model

    assert select_model("small-context", {}) is None
    assert select_model("small-context", {"enabled": False, "models": {"small-context": ["paid"]}}) is None


def test_selection_is_deterministic_and_uses_first_available_name() -> None:
    from cine_skills.runtime.models import select_model

    available = {
        "enabled": True,
        "models": {
            "small-context": ["local/fast", "remote/fallback"],
            "difficult-decision": {"name": "local/quality"},
        },
    }
    assert select_model("small-context", available) == "local/fast"
    assert select_model("difficult-decision", available) == "local/quality"
    assert select_model("unknown", available) is None


def test_selection_rejects_malformed_policy() -> None:
    from cine_skills.runtime.models import select_model

    with pytest.raises(ValueError, match="available"):
        select_model("small-context", {"models": "not-a-mapping"})

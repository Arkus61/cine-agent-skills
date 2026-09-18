from __future__ import annotations

import pytest


def test_patch_does_not_mutate_its_input() -> None:
    from cine_skills.runtime.patches import stage_json_patch

    original = {"camera": {"x": 0}}
    candidate = stage_json_patch(
        original, [{"op": "replace", "path": "/camera/x", "value": 1}]
    )

    assert original["camera"]["x"] == 0
    assert candidate["camera"]["x"] == 1


def test_patch_rejects_protected_identity_and_approval_paths() -> None:
    from cine_skills.runtime.patches import stage_json_patch

    for path in ("/shot_id", "/approval/state", "/evidence/items"):
        with pytest.raises(ValueError, match="protected"):
            stage_json_patch({"shot_id": "S01-SH001", "approval": {}}, [{"op": "replace", "path": path, "value": "x"}])


def test_patch_rejects_invalid_operations() -> None:
    from cine_skills.runtime.patches import stage_json_patch

    with pytest.raises(ValueError, match="patch"):
        stage_json_patch({}, [{"op": "remove", "path": "/missing"}])


def test_check_base_reports_conflicts() -> None:
    from cine_skills.runtime.patches import check_base

    assert check_base("a" * 64, "a" * 64) == []
    assert check_base("a" * 64, "b" * 64) == ["base-digest-mismatch"]

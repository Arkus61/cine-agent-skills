from __future__ import annotations

import json
from pathlib import Path


def _manifest() -> dict[str, object]:
    return {
        "input_digests": {"camera-1": "a" * 64},
        "skill_digest": "b" * 64,
        "schema_digest": "c" * 64,
        "approval": {"state": "planned"},
    }


def test_unchanged_result_is_a_cache_hit(tmp_path: Path) -> None:
    from cine_skills.runtime.result_cache import lookup_result, result_key, store_result

    manifest = _manifest()
    execution = {"model": "local", "tool_config": {"blender": "mcp-1"}}
    key = result_key(manifest, execution)
    store_result(tmp_path, key, {"status": "validated", "value": 3})

    assert lookup_result(tmp_path, key) == {"status": "validated", "value": 3}


def test_input_model_and_approval_changes_do_not_reuse_result() -> None:
    from cine_skills.runtime.result_cache import result_key

    manifest = _manifest()
    assert result_key(manifest, {"model": "A"}) != result_key(manifest, {"model": "B"})
    changed_source = {**manifest, "input_digests": {"camera-1": "d" * 64}}
    assert result_key(manifest, {"model": "A"}) != result_key(changed_source, {"model": "A"})
    changed_approval = {**manifest, "approval": {"state": "approved"}}
    assert result_key(manifest, {"model": "A"}) != result_key(changed_approval, {"model": "A"})


def test_corrupt_payload_is_not_returned(tmp_path: Path) -> None:
    from diskcache import Cache

    from cine_skills.runtime.result_cache import lookup_result

    key = "e" * 64
    with Cache(str(tmp_path)) as cache:
        cache.set(key, b"not-json")

    assert lookup_result(tmp_path, key) is None


def test_expired_result_is_not_returned(tmp_path: Path) -> None:
    from cine_skills.runtime.result_cache import lookup_result, store_result

    store_result(tmp_path, "f" * 64, {"status": "temporary"}, expire=0.01)
    import time

    time.sleep(0.03)
    assert lookup_result(tmp_path, "f" * 64) is None


def test_cache_does_not_store_non_json_objects(tmp_path: Path) -> None:
    import pytest

    from cine_skills.runtime.result_cache import store_result

    with pytest.raises(ValueError, match="JSON"):
        store_result(tmp_path, "1" * 64, {"bad": object()})

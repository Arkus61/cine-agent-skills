from __future__ import annotations

from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
RECIPE_PATH = ROOT / "src" / "cine_skills" / "runtime" / "recipes" / "ninel-blocking.yaml"
CONTRACT_PATH = ROOT / "evals" / "film_os" / "pilot-contract.yaml"


def _load(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_blocked_recipe_is_source_bound_and_has_no_arbitrary_execution() -> None:
    recipe = _load(RECIPE_PATH)

    assert recipe["system_version"] == "0.3.0"
    assert recipe["status"] == "blocked"
    assert recipe["source"]["project"] == "examples/scene-full"
    assert recipe["source"]["scene_id"] == "S01"
    assert {shot["shot_id"] for shot in recipe["shots"]} == {"S01-SH001", "S01-SH004"}
    assert recipe["execution"]["transport"] == "standard-mcp"
    assert recipe["execution"]["arbitrary_python"] is False
    assert set(recipe["blocking_reasons"]) == {
        "configured_server_identity_unavailable",
        "numeric_transforms_require_review",
    }

    source_root = (ROOT / recipe["source"]["project"] / "scenes" / "S01").resolve()
    assert (source_root / "blocking-plan.json").is_file()
    assert (source_root / "camera-movement-plan.json").is_file()
    assert (source_root / "shot-list.json").is_file()
    output_root = (ROOT / recipe["output"]["root"]).resolve()
    assert source_root not in output_root.parents
    assert output_root != source_root


def test_pilot_contract_keeps_all_live_acceptance_gates_open() -> None:
    contract = _load(CONTRACT_PATH)

    assert contract["system_version"] == "0.3.0"
    assert contract["status"] == "blocked"
    assert contract["recipe"] == "src/cine_skills/runtime/recipes/ninel-blocking.yaml"
    checks = contract["acceptance_checks"]
    assert isinstance(checks, list) and checks
    assert all(check["status"] in {"blocked", "pending"} for check in checks)
    assert not any(check["status"] == "passed" for check in checks)
    assert "live Blender evidence" in contract["not_claimed"]
    assert "creative approval" in contract["not_claimed"]


def test_pilot_contract_rejects_missing_files_without_blindly_falling_back() -> None:
    contract = _load(CONTRACT_PATH)

    for check in contract["acceptance_checks"]:
        assert check["evidence_required"]
        assert check["on_missing"] == "block"


@pytest.mark.parametrize("path", [RECIPE_PATH, CONTRACT_PATH])
def test_pilot_yaml_is_utf8_and_deterministic(path: Path) -> None:
    first = path.read_bytes()
    second = path.read_text(encoding="utf-8").encode("utf-8")
    assert first == second

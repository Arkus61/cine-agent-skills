from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "evals" / "film_os"


def test_film_os_suite_has_six_fixed_sanitized_cases() -> None:
    payload = yaml.safe_load((EVAL_DIR / "cases.yaml").read_text(encoding="utf-8"))
    assert payload["system_version"] == "0.3.0"
    cases = payload["cases"]
    assert len(cases) == 6
    assert [case["id"] for case in cases] == [
        "task-capsule-one-scene",
        "camera-revision",
        "character-look-two-scenes",
        "unchanged-rerun",
        "interrupted-run",
        "missing-media",
    ]
    serialized = json.dumps(payload, ensure_ascii=False)
    assert "private" not in serialized.lower()
    assert "api_key" not in serialized.lower()


def test_replay_baseline_is_explicitly_estimated_and_makes_no_savings_claim() -> None:
    report = json.loads(
        (EVAL_DIR / "replay-baseline.json").read_text(encoding="utf-8")
    )
    assert len(report["cases"]) == 6
    assert report["mode"] == "replay-estimate"
    assert report["provider_calls"] == 0
    assert report["token_savings_claimed"] is False
    assert all(case["usage_source"] == "estimate" for case in report["cases"])
    assert all(case["cost"] is None for case in report["cases"])


def test_promptfoo_provider_returns_labeled_replay_estimate() -> None:
    import sys

    sys.path.insert(0, str(EVAL_DIR))
    try:
        import provider

        case = provider.generate_cases()[0]
        prompt = provider.build_prompt({"vars": case["vars"]})
        result = provider.call_api(prompt, {"config": {"mode": "replay-estimate"}}, {"vars": case["vars"]})
    finally:
        sys.path.pop(0)

    payload = json.loads(result["output"])
    assert payload["source_mode"] == "replay-estimate"
    assert result["metadata"]["usage_source"] == "estimate"
    assert result["metadata"]["usage"]["input_tokens"] is not None
    assert result["metadata"]["usage"]["output_tokens"] is not None
    assert result["tokenUsage"]["total"] > 0


def test_promptfoo_provider_keeps_provider_usage_distinct_from_estimate() -> None:
    import sys

    sys.path.insert(0, str(EVAL_DIR))
    try:
        import provider

        case = provider.generate_cases()[0]["vars"]
        prompt = provider.build_prompt({"vars": case})
        result = provider.call_api(
            prompt,
            {
                "config": {
                    "mode": "provider",
                    "usage": {"prompt_tokens": 321, "completion_tokens": 12},
                }
            },
            {"vars": case},
        )
    finally:
        sys.path.pop(0)

    assert result["metadata"]["usage_source"] == "provider"
    assert result["metadata"]["usage"]["input_tokens"] == 321
    assert result["metadata"]["usage"]["output_tokens"] == 12


def test_assertions_call_scene_validator() -> None:
    import sys

    sys.path.insert(0, str(EVAL_DIR))
    try:
        import assertions
        import provider

        case = provider.generate_cases()[0]["vars"]
        prompt = provider.build_prompt({"vars": case})
        output = provider.call_api(prompt, {"config": {"mode": "replay-unavailable"}}, {"vars": case})["output"]
        result = assertions.get_assert(output, {"vars": case})
    finally:
        sys.path.pop(0)

    assert result["pass"] is True
    assert result["metadata"]["validator_errors"] == []


def test_assertions_do_not_pass_unknown_validator_target() -> None:
    import sys

    sys.path.insert(0, str(EVAL_DIR))
    try:
        import assertions
    finally:
        sys.path.pop(0)

    result = assertions.get_assert(
        json.dumps(
            {
                "contract": "film-os-eval-replay-v1",
                "system_version": "0.3.0",
                "case_id": "bad",
                "status": "replay",
            }
        ),
        {
            "vars": {
                "id": "bad",
                "kind": "task_capsule",
                "validation": {"kind": "scene-full", "target": "missing"},
            }
        },
    )
    assert result["pass"] is False

from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_record_usage_preserves_unknown_provider_counters() -> None:
    from cine_skills.runtime.telemetry import record_usage

    row = record_usage("run-1", "camera-1", {}, "provider")

    assert row == {
        "run_id": "run-1",
        "task_id": "camera-1",
        "source": "provider",
        "input_tokens": None,
        "output_tokens": None,
        "cached_input_tokens": None,
        "reasoning_output_tokens": None,
        "cost": None,
    }


def test_record_usage_accepts_measured_values_without_filling_missing_cost() -> None:
    from cine_skills.runtime.telemetry import record_usage

    row = record_usage(
        "run-2",
        "story-1",
        {"prompt_tokens": 120, "completion_tokens": 40, "cached_tokens": 20},
        "provider",
    )

    assert row["input_tokens"] == 120
    assert row["output_tokens"] == 40
    assert row["cached_input_tokens"] == 20
    assert row["cost"] is None


def test_record_usage_rejects_unknown_source() -> None:
    from cine_skills.runtime.telemetry import record_usage

    with pytest.raises(ValueError, match="source"):
        record_usage("run-1", "task-1", {}, "guess")


def test_recorder_exports_spans_without_raw_project_text(tmp_path: Path) -> None:
    from cine_skills.runtime.telemetry import TelemetryRecorder

    recorder = TelemetryRecorder()
    with recorder.span(
        "film_os.context_selection",
        task_id="camera-1",
        input_tokens=120,
        prompt="private source text must not be exported",
    ) as item:
        assert item.name == "film_os.context_selection"

    output = tmp_path / "telemetry.jsonl"
    assert recorder.export_jsonl(output) == 1
    row = json.loads(output.read_text(encoding="utf-8"))
    assert row["name"] == "film_os.context_selection"
    assert row["attributes"]["input_tokens"] == 120
    assert "prompt" not in row["attributes"]


def test_recorder_keeps_failed_span_for_local_diagnostics() -> None:
    from cine_skills.runtime.telemetry import TelemetryRecorder

    recorder = TelemetryRecorder()
    with pytest.raises(RuntimeError, match="boom"):
        with recorder.span("film_os.validation", status="error"):
            raise RuntimeError("boom")
    assert len(recorder.spans) == 1
    assert recorder.spans[0].duration_ms is not None

"""Promptfoo Python provider for the sanitized Film OS replay baseline.

This provider intentionally does not call a model by default.  It exercises
the same bounded prompt shape and returns a labelled replay result so the
evaluation harness can validate project contracts before a real provider is
configured.  A real provider may supply usage counters through the Promptfoo
provider options; missing counters remain ``null`` in the telemetry record.
"""

from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
from typing import Any

import yaml

from cine_skills.runtime.telemetry import TelemetryRecorder, record_usage


HERE = Path(__file__).resolve().parent
CASES_FILE = HERE / "cases.yaml"


def _cases() -> list[dict[str, Any]]:
    payload = yaml.safe_load(CASES_FILE.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("system_version") != "0.3.0":
        raise ValueError("Film OS eval cases must declare system_version 0.3.0")
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != 6:
        raise ValueError("Film OS replay suite must contain exactly six cases")
    result: list[dict[str, Any]] = []
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str):
            raise ValueError("each Film OS eval case needs a string id")
        result.append(case)
    return result


def generate_cases(config: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Load fixed cases in deterministic file order for Promptfoo."""

    return [
        {"description": case["description"], "vars": dict(case)}
        for case in _cases()
    ]


def build_prompt(context: dict[str, Any]) -> str:
    """Build a small, case-scoped prompt instead of an all-files replay."""

    variables = context.get("vars", {}) if isinstance(context, dict) else {}
    if not isinstance(variables, dict):
        raise ValueError("Promptfoo context vars must be an object")
    case_id = variables.get("id")
    brief = variables.get("brief")
    kind = variables.get("kind")
    if not all(isinstance(value, str) and value for value in (case_id, brief, kind)):
        raise ValueError("Film OS eval vars require id, kind, and brief")
    return (
        "Film OS replay task. Preserve stable IDs, distinguish facts from "
        "assumptions, and do not claim media or creative approval.\n"
        f"case_id={case_id}\nkind={kind}\nbrief={brief}\n"
        "Return a compact JSON observation envelope; do not include project source text."
    )


def _provider_config(options: Any) -> dict[str, Any]:
    if not isinstance(options, dict):
        return {}
    config = options.get("config", {})
    return config if isinstance(config, dict) else {}


def _estimated_usage(prompt: str, output: str) -> dict[str, int]:
    # This is a labelled replay estimate, not a tokenizer claim.  The prompt
    # is intentionally scoped to one case and never reads the whole project.
    input_tokens = max(1, (len(prompt.encode("utf-8")) + 3) // 4)
    output_tokens = max(1, (len(output.encode("utf-8")) + 3) // 4)
    return {
        "prompt": input_tokens,
        "completion": output_tokens,
        "total": input_tokens + output_tokens,
    }


def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Return a replay envelope using Promptfoo's Python provider contract."""

    variables = context.get("vars", {}) if isinstance(context, dict) else {}
    if not isinstance(variables, dict):
        raise ValueError("Promptfoo context vars must be an object")
    case_id = variables.get("id")
    if not isinstance(case_id, str) or not case_id:
        raise ValueError("Film OS eval case id is required")
    config = _provider_config(options)
    mode = config.get("mode", "replay-estimate")
    if mode not in {"replay-estimate", "replay-unavailable", "provider"}:
        raise ValueError("provider mode must be replay-estimate, replay-unavailable, or provider")

    payload = {
        "contract": "film-os-eval-replay-v1",
        "system_version": "0.3.0",
        "case_id": case_id,
        "kind": variables.get("kind"),
        "variant": config.get("variant", "replay-baseline"),
        "status": "replay",
        "expected": variables.get("expected", {}),
        "synthetic_fault": variables.get("synthetic_fault"),
        "source_mode": "replay-estimate" if mode == "replay-estimate" else mode,
    }
    output = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    reported_usage = config.get("usage")
    usage_source = "provider" if mode == "provider" and isinstance(reported_usage, dict) else "estimate"
    raw_usage = reported_usage if usage_source == "provider" else (
        _estimated_usage(prompt, output) if mode == "replay-estimate" else {}
    )
    usage_row = record_usage(case_id, case_id, raw_usage, usage_source)

    recorder = TelemetryRecorder()
    with recorder.span("film_os.task", task_id=case_id, case_kind=variables.get("kind")):
        with recorder.span("film_os.context_selection", task_id=case_id):
            pass
        with recorder.span("film_os.validation", task_id=case_id):
            pass
        with recorder.span(
            "film_os.model_call",
            task_id=case_id,
            model=config.get("model"),
            input_tokens=usage_row["input_tokens"],
            output_tokens=usage_row["output_tokens"],
            cached_input_tokens=usage_row["cached_input_tokens"],
            model_calls=0,
            repair_calls=0,
        ):
            pass
        with recorder.span("film_os.tool_call", task_id=case_id, tool_calls=0):
            pass
    telemetry_path = os.environ.get("FILM_OS_TELEMETRY_PATH")
    if telemetry_path:
        recorder.export_jsonl(Path(telemetry_path))

    response: dict[str, Any] = {
        "output": output,
        "metadata": {
            "usage": usage_row,
            "usage_source": usage_source,
            "case_id": case_id,
            "raw_output_digest": hashlib.sha256(output.encode("utf-8")).hexdigest(),
        },
    }
    if usage_source == "provider":
        response["tokenUsage"] = {
            key: value
            for key, value in {
                "prompt": usage_row["input_tokens"],
                "completion": usage_row["output_tokens"],
                "total": (
                    usage_row["input_tokens"] + usage_row["output_tokens"]
                    if usage_row["input_tokens"] is not None and usage_row["output_tokens"] is not None
                    else None
                ),
            }.items()
            if value is not None
        }
    elif mode == "replay-estimate":
        response["tokenUsage"] = raw_usage
    return response


__all__ = ["build_prompt", "call_api", "generate_cases"]

"""Promptfoo assertions backed by the repository's existing validators."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from cine_skills.package import validate_scene_package
from cine_skills.project_package import validate_project


REPO_ROOT = Path(__file__).resolve().parents[2]


def _parse_output(output: Any) -> tuple[dict[str, Any] | None, list[str]]:
    if isinstance(output, dict):
        payload = output
    elif isinstance(output, str):
        try:
            payload = json.loads(output)
        except json.JSONDecodeError as exc:
            return None, [f"output is not JSON: {exc}"]
    else:
        return None, ["output must be JSON text or an object"]
    if not isinstance(payload, dict):
        return None, ["output JSON must be an object"]
    return payload, []


def _validator_errors(case: dict[str, Any]) -> list[str]:
    validation = case.get("validation")
    if not isinstance(validation, dict):
        return ["case is missing validation declaration"]
    kind = validation.get("kind")
    target = validation.get("target")
    if not isinstance(kind, str) or not isinstance(target, str):
        return ["validation kind and target are required"]
    target_path = (REPO_ROOT / target).resolve()
    try:
        target_path.relative_to(REPO_ROOT)
    except ValueError:
        return ["validation target escapes repository root"]
    if kind == "scene-full":
        return validate_scene_package(target_path, REPO_ROOT, "scene-full")
    if kind == "project":
        return validate_project(target_path, REPO_ROOT, "full-creative")
    return [f"unsupported validator kind: {kind}"]


def get_assert(output: Any, context: dict[str, Any]) -> dict[str, Any]:
    """Return a detailed Promptfoo assertion without treating prose as proof."""

    variables = context.get("vars", {}) if isinstance(context, dict) else {}
    case = variables if isinstance(variables, dict) else {}
    payload, errors = _parse_output(output)
    if payload is not None:
        if payload.get("contract") != "film-os-eval-replay-v1":
            errors.append("unexpected evaluation contract")
        if payload.get("system_version") != "0.3.0":
            errors.append("unexpected system version")
        if payload.get("case_id") != case.get("id"):
            errors.append("output case_id does not match test case")
        if payload.get("status") != "replay":
            errors.append("replay provider did not label output as replay")
        if case.get("kind") == "missing_media" and payload.get("synthetic_fault") != "synthetic-missing-preview":
            errors.append("missing-media case lost its explicit synthetic fault")
        if case.get("kind") == "unchanged_rerun" and payload.get("expected", {}).get("model_calls") != 0:
            errors.append("unchanged-rerun case must declare zero model calls")
    errors.extend(_validator_errors(case))
    digest = hashlib.sha256(
        (output if isinstance(output, str) else json.dumps(output, sort_keys=True)).encode("utf-8")
    ).hexdigest()
    return {
        "pass": not errors,
        "score": 1.0 if not errors else 0.0,
        "reason": "; ".join(errors) if errors else "existing validator and replay-envelope checks passed",
        "metadata": {
            "case_id": case.get("id"),
            "validator_errors": _validator_errors(case),
            "raw_output_digest": digest,
        },
    }


__all__ = ["get_assert"]

from __future__ import annotations

import json

from . import __version__


_SUCCESS_MESSAGES = {
    "validate": "Repository validation passed.",
    "validate-artifact": "Artifact validation passed.",
    "validate-package": "Scene package validation passed.",
}


def render_validation_report(
    command: str,
    errors: list[str],
    output_format: str,
    profile: str | None = None,
) -> str:
    """Render deterministic validation output for humans or machines."""
    ordered_errors = sorted(errors)
    if output_format == "json":
        payload: dict[str, object] = {
            "command": command,
            "errors": ordered_errors,
            "system_version": __version__,
            "valid": not ordered_errors,
        }
        if profile is not None:
            payload["profile"] = profile
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)

    if ordered_errors:
        return "\n".join(f"ERROR: {error}" for error in ordered_errors)
    return _SUCCESS_MESSAGES[command]

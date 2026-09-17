"""Validation for the exact post-v2 package boundary."""
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import re
from typing import Any

from .project_contracts import POST_PROFILE, ProjectIndex, required_post_artifacts
from .project_validation import inspect_exact_entries, load_validated_artifacts, validate_layer_manifest


def _strings(value: Any) -> set[str]:
    return {item for item in value if isinstance(item, str)} if isinstance(value, list) else set()


def _context_refs(payload: Mapping[str, Any]) -> set[str]:
    context = payload.get("source_context")
    if not isinstance(context, Mapping):
        return set()
    refs = set(_strings(context.get("edit_segment_ids")))
    refs |= {str(item.get("segment_id")) for item in context.get("edit_segments", [])
             if isinstance(item, Mapping) and isinstance(item.get("segment_id"), str)}
    return refs


def _walk_references(value: Any, field: str = "") -> dict[str, set[str]]:
    """Collect only identifier fields whose ownership is defined upstream."""
    found = {"shot": set(), "media": set(), "segment": set()}
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in {"shot_id", "shot_ids"}:
                found["shot"] |= set(_strings(child)) if key.endswith("s") else ({child} if isinstance(child, str) else set())
            elif key in {"media_id", "media_ids", "media_version_id", "media_version_ids"}:
                found["media"] |= set(_strings(child)) if key.endswith("s") else ({child} if isinstance(child, str) else set())
            elif key in {"segment_id", "segment_ids", "edit_segment_id", "edit_segment_ids"}:
                found["segment"] |= set(_strings(child)) if key.endswith("s") else ({child} if isinstance(child, str) else set())
            nested = _walk_references(child, key)
            for kind, refs in nested.items():
                found[kind] |= refs
    elif isinstance(value, list):
        for child in value:
            nested = _walk_references(child, field)
            for kind, refs in nested.items():
                found[kind] |= refs
    return found


def _unit_from_id(identifier: str) -> str | None:
    parts = identifier.split("-")
    for index, part in enumerate(parts):
        if len(part) == 3 and part[:1] in {"U", "E"} and part[1:].isdigit():
            return "-".join(parts[: index + 1])
    return None


def validate_post_package(package_dir: Path, root: Path, upstream: ProjectIndex) -> list[str]:
    package = Path(package_dir)
    contracts = required_post_artifacts()
    errors = inspect_exact_entries(package, [c.filename for c in contracts], "post")
    if errors:
        # Still load available files so malformed packages provide useful diagnostics.
        pass
    payloads, load_errors = load_validated_artifacts(package, contracts, Path(root))
    errors.extend(load_errors)
    project_id = upstream.project_id
    unit_ids = set(upstream.unit_ids)
    canonical_unit = payloads.get("edit-plan.json", {}).get("unit_id")
    if not isinstance(canonical_unit, str):
        canonical_unit = sorted(unit_ids)[0] if unit_ids else None
    canonical_segments = {
        ref for ref in upstream.edit_segment_ids
        if _unit_from_id(ref) == canonical_unit and re.fullmatch(r".+-ED\d+", ref)
    }
    for filename, payload in payloads.items():
        if payload.get("project_id") != project_id:
            errors.append(f"{filename}: project_id must equal upstream project {project_id}")
        if "unit_id" in payload and payload.get("unit_id") not in unit_ids:
            errors.append(f"{filename}: unit_id must belong to upstream unit registry")
        if canonical_unit and payload.get("unit_id") != canonical_unit and filename != "post-manifest.json":
            errors.append(f"{filename}: unit_id must equal canonical edit-plan unit {canonical_unit}")
        refs = _context_refs(payload)
        unknown = refs - set(upstream.edit_segment_ids)
        errors.extend(f"{filename}: unknown upstream edit segment {ref}" for ref in sorted(unknown))
        all_refs = _walk_references(payload)
        for ref in sorted(all_refs["segment"]):
            if canonical_unit and _unit_from_id(ref) not in {None, canonical_unit}:
                errors.append(f"{filename}: edit segment {ref} must belong to canonical unit {canonical_unit}")
        for kind, allowed in (("shot", upstream.shot_ids), ("media", upstream.media_ids), ("segment", canonical_segments)):
            for ref in sorted(all_refs[kind] - set(allowed)):
                errors.append(f"{filename}: unknown upstream {kind} {ref}")
        if filename not in {"post-manifest.json", "mastering-qc-plan.json"} and canonical_segments:
            missing = canonical_segments - all_refs["segment"]
            errors.extend(f"{filename}: missing coverage for upstream edit segment {ref}" for ref in sorted(missing))

    manifest = payloads.get("post-manifest.json")
    if manifest is not None:
        errors.extend(validate_layer_manifest(manifest, contracts, "post-manifest.json"))
    return sorted(set(errors))


__all__ = ["POST_PROFILE", "validate_post_package"]

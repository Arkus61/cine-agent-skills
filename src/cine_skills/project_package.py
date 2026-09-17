"""Validation and indexing for a complete full-creative-v2 project."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from .artifacts import load_json_object, validate_artifact
from .project_contracts import FULL_CREATIVE_PROFILE, ProjectIndex
from .project_validation import load_validated_artifacts
from .production_package import derive_production_index_at, validate_production_package
from .post_package import validate_post_package
from .story_package import build_story_index


def _with_edit_segments(package: Path, root: Path, upstream: ProjectIndex) -> tuple[ProjectIndex, list[str]]:
    """Index declarations from a valid edit plan, never downstream copied registries."""
    payload, errors = load_json_object(package / "edit-plan.json")
    if errors or payload is None:
        return upstream, errors
    errors = validate_artifact("edit-plan", payload, root)
    if errors:
        return upstream, errors
    return replace(upstream, edit_segment_ids=frozenset(
        item["segment_id"] for item in payload["segments"]
    )), []


def _safe_path(project: Path, value: Any) -> tuple[Path | None, str | None]:
    if not isinstance(value, str) or not value or "\\" in value:
        return None, f"unsafe relative layer path {value!r}"
    try:
        candidate = (project / value).resolve()
    except (OSError, RuntimeError) as exc:
        return None, f"unable to resolve layer path {value!r}: {exc}"
    try:
        candidate.relative_to(project.resolve())
    except ValueError:
        return None, f"layer path escapes project root: {value}"
    if value.startswith("/") or ".." in Path(value).parts:
        return None, f"unsafe relative layer path {value}"
    return candidate, None


def _manifest(project: Path, root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    payload, errors = load_json_object(project / "creative-manifest.json")
    if errors or payload is None:
        return None, errors
    errors = validate_artifact("creative-manifest", payload, root)
    return (payload if not errors else None), errors


def build_project_index(project_dir: Path, root: Path) -> tuple[ProjectIndex | None, list[str]]:
    project = Path(project_dir)
    manifest, errors = _manifest(project, Path(root))
    if manifest is None:
        return None, sorted(errors)
    layers = manifest["layers"]
    resolved: dict[str, Path] = {}
    for name in ("story", "production", "post"):
        path, error = _safe_path(project, layers.get(name))
        if error:
            errors.append(f"creative-manifest.json: layers.{name}: {error}")
        elif path is not None:
            resolved[name] = path
    if errors:
        return None, sorted(set(errors))
    project_id = manifest["project_id"]
    scripts, script_error = _safe_path(project, "scripts")
    if script_error or scripts is None:
        return None, [script_error or "scripts directory is missing"]
    story, story_errors = build_story_index(resolved["story"], scripts, root)
    errors.extend(story_errors)
    if story is None:
        return None, sorted(set(errors))
    if set(manifest["units"]) != set(story.unit_ids):
        errors.append("creative-manifest.json: units must exactly match story unit IDs")
    if project_id != story.project_id:
        errors.append(f"creative-manifest.json: project_id {project_id} does not match story project {story.project_id}")
    if manifest["project_format"] != story.project_format:
        errors.append("creative-manifest.json: project_format must exactly match story concept")
    if tuple(manifest["production_modes"]) != tuple(story.production_modes):
        errors.append("creative-manifest.json: production_modes must exactly match story concept")
    production, production_load_errors = derive_production_index_at(
        resolved["production"], root, manifest["production_modes"]
    )
    errors.extend(production_load_errors)
    production_errors = validate_production_package(
        resolved["production"], root, manifest["production_modes"], story,
        enforce_directory_name=False,
    )
    errors.extend(production_errors)
    if production is not None and production.project_id != project_id:
        errors.append(f"production package project_id {production.project_id} does not match {project_id}")
    upstream = story
    # A derived index is usable downstream only when the production package
    # itself passed validation; otherwise it may contain untrusted IDs.
    if production is not None and not production_load_errors and not production_errors:
        upstream = replace(story, media_ids=production.media_ids,
                           asset_ids=story.asset_ids | production.asset_ids,
                           sound_ids=production.sound_ids or story.sound_ids)
    upstream, edit_errors = _with_edit_segments(resolved["post"], root, upstream)
    errors.extend(edit_errors)
    errors.extend(validate_post_package(resolved["post"], root, upstream))
    if errors:
        return None, sorted(set(errors))
    return ProjectIndex(
        project_id=project_id, project_format=manifest["project_format"],
        production_modes=tuple(manifest["production_modes"]),
        unit_ids=story.unit_ids, scene_ids=story.scene_ids, beat_ids=story.beat_ids,
        shot_ids=story.shot_ids, character_ids=story.character_ids,
        event_ids=story.event_ids, world_ids=story.world_ids, asset_ids=upstream.asset_ids,
        sound_ids=upstream.sound_ids, media_ids=upstream.media_ids,
        edit_segment_ids=upstream.edit_segment_ids,
    ), []


def validate_project(project_dir: Path, root: Path, profile: str = FULL_CREATIVE_PROFILE) -> list[str]:
    project = Path(project_dir)
    if profile != FULL_CREATIVE_PROFILE:
        return [f"unknown project profile {profile}; allowed values: {FULL_CREATIVE_PROFILE}"]
    try:
        entries = {entry.name for entry in project.iterdir()}
    except OSError as exc:
        return [f"{project}: unable to inspect project directory: {exc}"]
    errors: list[str] = []
    expected = {"creative-manifest.json", "scripts"}
    manifest, manifest_errors = _manifest(project, Path(root))
    errors.extend(manifest_errors)
    if manifest is not None:
        expected |= {Path(value).parts[0] for value in manifest["layers"].values() if isinstance(value, str) and value}
    errors.extend(f"{name}: unexpected project entry" for name in entries - expected)
    errors.extend(f"{name}: required project entry is missing" for name in expected - entries)
    if not manifest_errors:
        _index, layer_errors = build_project_index(project, Path(root))
        errors.extend(layer_errors)
    return sorted(set(errors))

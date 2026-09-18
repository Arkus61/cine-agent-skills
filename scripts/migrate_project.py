"""Migrate known pre-0.3 project metadata into a new directory.

The migration is intentionally conservative: validation never changes an input
directory, and this command only rewrites the version/profile fields documented
by the active versioning policy. Creative content, identifiers, approvals and
media revisions are copied as data and are not synthesized.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from cine_skills import __version__  # noqa: E402
from cine_skills.package import validate_scene_package  # noqa: E402
from cine_skills.project_package import validate_project  # noqa: E402


TARGET_VERSION = __version__

LEGACY_SCHEMA_VERSIONS = {"1.0", "2.0"}
LEGACY_RELEASE_VERSIONS = {"1.0.0", "2.0.0"}
PROFILE_RENAMES = {
    "core-v0.1": "scene-core",
    "full-v1": "scene-full",
    "story-v2": "story",
    "production-v2": "production",
    "post-v2": "post",
    "full-creative-v2": "full-creative",
}

SCENE_CORE_FILES = {
    "source-scene.md",
    "scene-beats.json",
    "directing-plan.json",
    "blocking-plan.json",
    "camera-movement-plan.json",
    "shot-list.json",
}
SCENE_FULL_FILES = SCENE_CORE_FILES | {
    "source-scene.md",
    "visual-language-plan.json",
    "lighting-plan.json",
    "sound-plan.json",
    "storyboard-plan.json",
    "production-breakdown.json",
    "continuity-plan.json",
    "package-manifest.json",
}


@dataclass(frozen=True)
class SourceInfo:
    kind: str
    version_family: str
    changed_files: tuple[str, ...]


def _error(message: str) -> dict[str, Any]:
    return {
        "status": "blocked",
        "source_kind": "unknown",
        "target_version": TARGET_VERSION,
        "changed_files": [],
        "errors": [message],
    }


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _resolved_under(path: Path, root: Path, label: str) -> tuple[Path | None, str | None]:
    try:
        resolved = path.resolve(strict=False)
        root_resolved = root.resolve(strict=True)
    except OSError as exc:
        return None, f"{label}: cannot resolve path: {exc}"
    try:
        resolved.relative_to(root_resolved)
    except ValueError:
        return None, f"{label}: path must remain inside --root"
    return resolved, None


def _reject_symlinks(path: Path, label: str) -> str | None:
    if path.is_symlink():
        return f"{label}: symlinks are not allowed"
    try:
        for entry in path.rglob("*"):
            if entry.is_symlink():
                return f"{label}: symlink entry is not allowed: {entry.name}"
    except OSError as exc:
        return f"{label}: cannot inspect entries: {exc}"
    return None


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, f"{path.name}: invalid JSON: {exc}"
    if not isinstance(payload, dict):
        return None, f"{path.name}: top-level JSON value must be an object"
    return payload, None


def _json_files(source: Path) -> tuple[list[tuple[Path, dict[str, Any]]], list[str]]:
    records: list[tuple[Path, dict[str, Any]]] = []
    errors: list[str] = []
    try:
        paths = sorted(source.rglob("*.json"))
    except OSError as exc:
        return [], [f"source: cannot inspect JSON files: {exc}"]
    for path in paths:
        payload, error = _read_json(path)
        if error:
            errors.append(f"{path.relative_to(source).as_posix()}: {error}")
        elif payload is not None:
            records.append((path, payload))
    return records, sorted(errors)


def _version_markers(records: list[tuple[Path, dict[str, Any]]]) -> tuple[set[str], set[str]]:
    schema_versions: set[str] = set()
    release_versions: set[str] = set()
    for _path, payload in records:
        for key, values in (
            ("schema_version", schema_versions),
            ("release_version", release_versions),
        ):
            value = payload.get(key)
            if isinstance(value, str):
                values.add(value)
            artifacts = payload.get("artifacts")
            if isinstance(artifacts, list):
                for item in artifacts:
                    if isinstance(item, dict) and isinstance(item.get(key), str):
                        values.add(item[key])
    return schema_versions, release_versions


def _profile_values(records: list[tuple[Path, dict[str, Any]]]) -> set[str]:
    values: set[str] = set()
    for _path, payload in records:
        if isinstance(payload.get("profile"), str):
            values.add(payload["profile"])
        layers = payload.get("layers")
        if isinstance(layers, dict):
            values.update(value for value in layers.values() if isinstance(value, str))
        artifacts = payload.get("artifacts")
        if isinstance(artifacts, list):
            for item in artifacts:
                if isinstance(item, dict) and isinstance(item.get("schema_name"), str):
                    values.add(item["schema_name"])
    return values


def _classify(source: Path) -> tuple[SourceInfo | None, list[str]]:
    records, errors = _json_files(source)
    if errors:
        return None, errors
    names = {path.name for path in source.iterdir()}
    schemas, releases = _version_markers(records)
    profiles = _profile_values(records)

    if "creative-manifest.json" in names:
        manifest = next(
            (payload for path, payload in records if path.name == "creative-manifest.json"),
            {},
        )
        if (
            manifest.get("schema_version") != "2.0"
            or manifest.get("release_version") != "2.0.0"
            or manifest.get("profile") != "full-creative-v2"
        ):
            if manifest.get("schema_version") == TARGET_VERSION and manifest.get("profile") == "full-creative":
                if not schemas.issubset({TARGET_VERSION}) or not releases.issubset({TARGET_VERSION}):
                    return None, ["project contains mixed active and legacy version markers"]
                if profiles.intersection(PROFILE_RENAMES):
                    return None, ["project contains a legacy profile in an active manifest"]
                return SourceInfo("full-creative", "current", ()), []
            return None, [
                "creative-manifest.json: unsupported version/profile; expected legacy 2.0.0/full-creative-v2"
            ]
        if not schemas.issubset(LEGACY_SCHEMA_VERSIONS) or not releases.issubset(LEGACY_RELEASE_VERSIONS):
            return None, ["project contains mixed or unknown legacy version markers"]
        changed = tuple(sorted(_relative(path, source) for path, payload in records if _needs_change(payload)))
        return SourceInfo("full-creative", "legacy-v2", changed), []

    if "package-manifest.json" in names:
        manifest = next(
            (payload for path, payload in records if path.name == "package-manifest.json"),
            {},
        )
        if (
            manifest.get("release_version") != "1.0.0"
            or manifest.get("profile") != "full-v1"
        ):
            if manifest.get("release_version") == TARGET_VERSION and manifest.get("profile") == "scene-full":
                if not schemas.issubset({TARGET_VERSION}) or not releases.issubset({TARGET_VERSION}):
                    return None, ["scene-full package contains mixed active and legacy version markers"]
                if profiles.intersection(PROFILE_RENAMES):
                    return None, ["scene-full package contains a legacy profile in an active manifest"]
                return SourceInfo("scene-full", "current", ()), []
            return None, [
                "package-manifest.json: unsupported version/profile; expected legacy 1.0.0/full-v1"
            ]
        if not schemas.issubset({"1.0"}) or not releases.issubset({"1.0.0"}):
            return None, ["scene-full package contains mixed or unknown legacy version markers"]
        if names != SCENE_FULL_FILES:
            return None, ["scene-full package does not have the exact legacy file inventory"]
        changed = tuple(sorted(_relative(path, source) for path, payload in records if _needs_change(payload)))
        return SourceInfo("scene-full", "legacy-v1", changed), []

    if names != SCENE_CORE_FILES:
        return None, ["source is not a recognized scene-core package"]
    if not schemas.issubset({"1.0"}):
        if schemas == {TARGET_VERSION}:
            return SourceInfo("scene-core", "current", ()), []
        return None, ["scene-core package contains mixed or unknown legacy schema markers"]
    changed = tuple(sorted(_relative(path, source) for path, payload in records if _needs_change(payload)))
    return SourceInfo("scene-core", "legacy-v0.1", changed), []


def _needs_change(payload: dict[str, Any]) -> bool:
    for key, value in payload.items():
        if key in {"schema_version", "release_version"} and value in LEGACY_SCHEMA_VERSIONS | LEGACY_RELEASE_VERSIONS:
            return True
        if key == "profile" and value in PROFILE_RENAMES:
            return True
        if key == "layers" and isinstance(value, dict) and any(item in PROFILE_RENAMES for item in value.values()):
            return True
        if key == "artifacts" and isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and (
                    item.get("schema_version") in LEGACY_SCHEMA_VERSIONS
                    or item.get("schema_name") in PROFILE_RENAMES
                ):
                    return True
    return False


def _migrate_value(key: str, value: Any) -> Any:
    if key in {"schema_version", "release_version"} and value in LEGACY_SCHEMA_VERSIONS | LEGACY_RELEASE_VERSIONS:
        return TARGET_VERSION
    if key in {"profile", "schema_name"} and value in PROFILE_RENAMES:
        return PROFILE_RENAMES[value]
    if key == "layers" and isinstance(value, dict):
        return {name: PROFILE_RENAMES.get(item, item) for name, item in value.items()}
    if key == "artifacts" and isinstance(value, list):
        return [_migrate_object(item) if isinstance(item, dict) else item for item in value]
    return value


def _migrate_object(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: _migrate_value(key, value) for key, value in payload.items()}


def _copy_and_migrate(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, symlinks=False)
    for path in sorted(destination.rglob("*.json")):
        payload, error = _read_json(path)
        if error or payload is None:
            raise ValueError(error or f"{path.name}: invalid JSON")
        path.write_text(
            json.dumps(_migrate_object(payload), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def _validate_candidate(kind: str, candidate: Path, root: Path) -> list[str]:
    if kind == "scene-core":
        return validate_scene_package(candidate, root, profile="scene-core")
    if kind == "scene-full":
        return validate_scene_package(candidate, root, profile="scene-full")
    if kind == "full-creative":
        return validate_project(candidate, root)
    return [f"unsupported source kind {kind}"]


def migrate(
    root: Path, source: Path, output: Path, *, dry_run: bool = False
) -> dict[str, Any]:
    root_resolved, root_error = _resolved_under(root, root, "--root")
    if root_error or root_resolved is None or not root_resolved.is_dir():
        return _error(root_error or "--root: directory does not exist")
    source_resolved, source_error = _resolved_under(source, root_resolved, "--source")
    output_resolved, output_error = _resolved_under(output, root_resolved, "--output")
    if source_error:
        return _error(source_error)
    if output_error:
        return _error(output_error)
    assert source_resolved is not None and output_resolved is not None
    if not source_resolved.is_dir():
        return _error("--source: directory does not exist")
    if source_resolved == output_resolved:
        return _error("--output: must be different from --source")
    try:
        source_resolved.relative_to(output_resolved)
        return _error("--output: cannot contain --source")
    except ValueError:
        pass
    try:
        output_resolved.relative_to(source_resolved)
        return _error("--source: cannot contain --output")
    except ValueError:
        pass
    source_symlink_error = _reject_symlinks(source_resolved, "--source")
    if source_symlink_error:
        return _error(source_symlink_error)
    if output_resolved.exists() or output_resolved.is_symlink():
        return _error("--output: destination already exists")

    info, errors = _classify(source_resolved)
    if errors or info is None:
        result = _error("; ".join(errors) if errors else "source could not be classified")
        result["source_kind"] = info.kind if info else "unknown"
        return result
    if info.version_family == "current":
        return {
            "status": "ready",
            "source_kind": info.kind,
            "target_version": TARGET_VERSION,
            "changed_files": [],
            "errors": [],
        }

    changed_files = list(info.changed_files)
    stage_parent = root_resolved
    try:
        with tempfile.TemporaryDirectory(prefix=".migration-", dir=stage_parent) as temporary:
            stage = Path(temporary) / "output"
            _copy_and_migrate(source_resolved, stage)
            validation_errors = _validate_candidate(info.kind, stage, root_resolved)
            if validation_errors:
                return {
                    "status": "blocked",
                    "source_kind": info.kind,
                    "target_version": TARGET_VERSION,
                    "changed_files": changed_files,
                    "errors": sorted(validation_errors),
                }
            if dry_run:
                return {
                    "status": "ready",
                    "source_kind": info.kind,
                    "target_version": TARGET_VERSION,
                    "changed_files": changed_files,
                    "errors": [],
                }
            output_resolved.parent.mkdir(parents=True, exist_ok=True)
            os.replace(stage, output_resolved)
    except (OSError, ValueError, shutil.Error) as exc:
        return {
            "status": "blocked",
            "source_kind": info.kind,
            "target_version": TARGET_VERSION,
            "changed_files": changed_files,
            "errors": [f"migration failed before publication: {exc}"],
        }

    return {
        "status": "migrated",
        "source_kind": info.kind,
        "target_version": TARGET_VERSION,
        "changed_files": changed_files,
        "errors": [],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="repository root")
    parser.add_argument("--source", required=True, help="legacy package or project")
    parser.add_argument("--output", required=True, help="new migration output directory")
    parser.add_argument("--dry-run", action="store_true", help="validate without writing output")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = migrate(Path(args.root), Path(args.source), Path(args.output), dry_run=args.dry_run)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    else:
        print(f"{result['status']}: {result['source_kind']}")
        for item in result["changed_files"]:
            print(f"changed: {item}")
        for error in result["errors"]:
            print(f"error: {error}")
    return 0 if result["status"] in {"ready", "migrated"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

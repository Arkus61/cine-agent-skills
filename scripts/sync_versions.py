"""Synchronize the small set of generated release metadata files.

The release number is intentionally read from ``pyproject.toml``.  This
module has an explicit allowlist of derived files so a version check cannot
silently rewrite arbitrary project JSON, historical documents, or user data.
The set will grow as the unified-versioning transition moves individual
contracts to the active release.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
import tomllib
from pathlib import Path
from typing import Any


_VERSION_ASSIGNMENT = re.compile(
    r'(?m)^(?P<prefix>\s*__version__\s*=\s*)(?P<quote>["\'])(?P<value>[^"\']+)(?P=quote)(?P<suffix>\s*)$'
)
_SEMVER = re.compile(r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)$")
_RUNTIME_VERSION = Path("src/cine_skills/__init__.py")
_SYSTEM_MANIFEST = Path("system-manifest.json")
_ACTIVE_YAML = (
    Path("src/cine_skills/runtime/recipes/ninel-blocking.yaml"),
    Path("evals/film_os/pilot-contract.yaml"),
)
_YAML_VERSION_ASSIGNMENT = re.compile(
    r'(?m)^(?P<prefix>\s*system_version\s*:\s*)(?P<quote>["\']?)(?P<value>[^\s"\']+)(?P=quote)(?P<suffix>\s*)$'
)
_PROFILE_RENAMES = {
    "core-v0.1": "scene-core",
    "full-v1": "scene-full",
    "story-v2": "story",
    "production-v2": "production",
    "post-v2": "post",
    "full-creative-v2": "full-creative",
}


def _root(value: Path) -> Path:
    path = Path(value)
    if not path.exists() or not path.is_dir():
        raise ValueError(f"repository root is not a directory: {value}")
    return path.resolve()


def read_release_version(root: Path) -> str:
    """Return the one editable release version from ``pyproject.toml``."""

    repository = _root(Path(root))
    path = repository / "pyproject.toml"
    try:
        metadata = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(f"unable to read pyproject.toml: {exc}") from exc
    try:
        version = metadata["project"]["version"]
    except (KeyError, TypeError) as exc:
        raise ValueError("pyproject.toml is missing project.version") from exc
    if not isinstance(version, str) or not _SEMVER.fullmatch(version):
        raise ValueError("project.version must be a numeric MAJOR.MINOR.PATCH string")
    return version


def _runtime_bytes(repository: Path, version: str) -> bytes:
    path = repository / _RUNTIME_VERSION
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"unable to read {_RUNTIME_VERSION}: {exc}") from exc
    matches = list(_VERSION_ASSIGNMENT.finditer(text))
    if len(matches) != 1:
        raise ValueError(
            f"{_RUNTIME_VERSION} must contain exactly one __version__ assignment"
        )
    match = matches[0]
    replacement = (
        f"{match.group('prefix')}\"{version}\"{match.group('suffix')}"
    )
    return (text[: match.start()] + replacement + text[match.end() :]).encode("utf-8")


def _skill_names(repository: Path) -> list[str]:
    skills_root = repository / ".agents" / "skills"
    if not skills_root.is_dir():
        raise ValueError(".agents/skills directory is missing")
    names = sorted(
        path.name
        for path in skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )
    if not names:
        raise ValueError(".agents/skills contains no SKILL.md files")
    return names


def _manifest_bytes(repository: Path, version: str) -> bytes:
    manifest = {"release_version": version, "skills": _skill_names(repository)}
    return (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _active_json_paths(repository: Path) -> list[Path]:
    """Return JSON files whose contract metadata belongs to the active release."""

    paths: set[Path] = set((repository / "schemas").glob("*.schema.json"))
    paths.update((repository / "evals").glob("*.json"))
    paths.update((repository / "examples").rglob("*.json"))
    skills_root = repository / ".agents" / "skills"
    if skills_root.is_dir():
        paths.update(skills_root.rglob("assets/*.json"))
    return sorted(path for path in paths if path.is_file() and not path.is_symlink())


def _rename_profile(value: Any) -> Any:
    if isinstance(value, str):
        return _PROFILE_RENAMES.get(value, value)
    if isinstance(value, list):
        return [_rename_profile(item) for item in value]
    return value


def _update_contract_values(value: Any, version: str, *, schema: bool, eval_root: bool = False) -> Any:
    if isinstance(value, list):
        return [_update_contract_values(item, version, schema=schema) for item in value]
    if not isinstance(value, dict):
        return value
    updated: dict[str, Any] = {}
    for key, item in value.items():
        if key in {"schema_version", "release_version"} and isinstance(item, str):
            updated[key] = version
        elif key == "profile" and isinstance(item, (str, list)):
            updated[key] = _rename_profile(item)
        elif key == "profile":
            updated[key] = _update_contract_values(item, version, schema=schema)
        elif key == "schema_name" and item == "full-v1":
            updated[key] = "scene-full"
        elif eval_root and key == "version":
            updated[key] = version
        elif schema and key == "const":
            updated[key] = _PROFILE_RENAMES.get(item, version if item in {"1.0", "2.0", "1.0.0", "2.0.0"} else item)
        elif schema and key == "enum" and isinstance(item, list):
            updated[key] = _rename_profile(item)
        else:
            updated[key] = _update_contract_values(item, version, schema=schema)
    return updated


def _active_json_bytes(path: Path, version: str) -> bytes:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"unable to parse active JSON {path}: {exc}") from exc
    schema = path.name.endswith(".schema.json")
    replacements = {
        "core-v0.1": "scene-core",
        "full-v1": "scene-full",
        "story-v2": "story",
        "production-v2": "production",
        "post-v2": "post",
        "full-creative-v2": "full-creative",
    }
    for old, new in replacements.items():
        text = text.replace(f'"{old}"', f'"{new}"')
    if schema:
        text = re.sub(
            r'("const"\s*:\s*")(?:1\.0|2\.0|1\.0\.0|2\.0\.0)(")',
            rf'\g<1>{version}\g<2>',
            text,
        )
    else:
        text = re.sub(
            r'("(?:schema_version|release_version)"\s*:\s*")(?:1\.0|2\.0|1\.0\.0|2\.0\.0)(")',
            rf'\g<1>{version}\g<2>',
            text,
        )
        text = text.replace('"schema_name": "full-v1"', '"schema_name": "scene-full"')
        if path.parent.name == "evals":
            text = re.sub(
                r'(^\s*"version"\s*:\s*")(?:1\.0|2\.0|1\.0\.0|2\.0\.0)(")',
                rf'\g<1>{version}\g<2>',
                text,
                flags=re.MULTILINE,
            )
    try:
        json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"active JSON became invalid {path}: {exc}") from exc
    return text.encode("utf-8")


def _active_yaml_bytes(path: Path, version: str) -> bytes:
    """Update only the explicit system_version field in active YAML contracts."""

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"unable to parse active YAML {path}: {exc}") from exc
    matches = list(_YAML_VERSION_ASSIGNMENT.finditer(text))
    if len(matches) != 1:
        raise ValueError(f"{path} must contain exactly one system_version field")
    match = matches[0]
    replacement = (
        f"{match.group('prefix')}{match.group('quote')}{version}"
        f"{match.group('quote')}{match.group('suffix')}"
    )
    return (text[: match.start()] + replacement + text[match.end() :]).encode("utf-8")


def planned_updates(root: Path) -> dict[Path, bytes]:
    """Return desired bytes for every currently allowlisted derivative file."""

    repository = _root(Path(root))
    version = read_release_version(repository)
    updates: dict[Path, bytes] = {
        repository / _RUNTIME_VERSION: _runtime_bytes(repository, version),
        repository / _SYSTEM_MANIFEST: _manifest_bytes(repository, version),
    }
    for path in _active_json_paths(repository):
        updates[path] = _active_json_bytes(path, version)
    for relative in _ACTIVE_YAML:
        path = repository / relative
        if path.is_file() and not path.is_symlink():
            updates[path] = _active_yaml_bytes(path, version)
    return updates


def _relative(repository: Path, path: Path) -> str:
    return path.relative_to(repository).as_posix()


def check_versions(root: Path) -> list[str]:
    """Return deterministic drift diagnostics without changing any file."""

    repository = _root(Path(root))
    updates = planned_updates(repository)
    problems: list[str] = []
    for path, expected in updates.items():
        relative = _relative(repository, path)
        try:
            actual = path.read_bytes()
        except OSError:
            problems.append(f"{relative}: file is missing or unreadable")
            continue
        if actual != expected:
            problems.append(f"{relative}: differs from pyproject.toml project.version")
    return sorted(problems)


def _write_updates(updates: dict[Path, bytes]) -> list[str]:
    """Apply prepared updates after all source data has been parsed."""

    temporary: list[tuple[Path, Path]] = []
    changed: list[str] = []
    try:
        for destination, content in updates.items():
            if destination.exists() and destination.read_bytes() == content:
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            descriptor, name = tempfile.mkstemp(
                prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
            )
            temporary_path = Path(name)
            try:
                with os.fdopen(descriptor, "wb") as stream:
                    stream.write(content)
                    stream.flush()
                    os.fsync(stream.fileno())
            except BaseException:
                try:
                    temporary_path.unlink()
                except FileNotFoundError:
                    pass
                raise
            temporary.append((temporary_path, destination))
            changed.append(destination.as_posix())
        for temporary_path, destination in temporary:
            os.replace(temporary_path, destination)
        return changed
    finally:
        for temporary_path, _destination in temporary:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.check:
            problems = check_versions(args.root)
            if problems:
                print("\n".join(problems))
                return 1
            print("version metadata is synchronized")
            return 0
        updates = planned_updates(args.root)
        repository = _root(args.root)
        changed = _write_updates(updates)
        print(
            json.dumps(
                {"updated": sorted(_relative(repository, Path(path)) for path in changed)},
                ensure_ascii=False,
            )
        )
        return 0
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

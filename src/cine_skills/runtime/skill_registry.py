"""Discovery metadata for the repository's portable Agent Skills."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


def _read_frontmatter(path: Path) -> dict[str, Any]:
    """Read only the YAML header; instruction bodies stay unopened."""

    try:
        with path.open("rb") as stream:
            if stream.readline() != b"---\n":
                raise ValueError(f"{path}: SKILL.md must start with YAML frontmatter")
            header: list[bytes] = []
            for line in stream:
                if line == b"---\n":
                    break
                header.append(line)
            else:
                raise ValueError(f"{path}: YAML frontmatter is not closed")
    except OSError as exc:
        raise ValueError(f"{path}: cannot read file: {exc}") from exc
    try:
        parsed = yaml.safe_load(b"".join(header).decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError, RecursionError) as exc:
        raise ValueError(f"{path}: invalid YAML frontmatter: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping")
    return parsed


def _bundle_digest(skill_dir: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(
        path for path in skill_dir.rglob("*") if path.is_file()
    )
    for index, path in enumerate(files):
        if path.is_symlink():
            raise ValueError(f"{path}: symlinked skill resource is not allowed")
        relative = path.relative_to(skill_dir).as_posix()
        if index:
            digest.update(b"\x00")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\x00")
        try:
            digest.update(path.read_bytes())
        except OSError as exc:
            raise ValueError(f"{path}: cannot read skill resource: {exc}") from exc
    return digest.hexdigest()


def _validate_ref(skill_dir: Path, value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"{skill_dir.name}: {label} must be a relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"{skill_dir.name}: {label} must stay inside the skill")
    target = skill_dir.joinpath(*path.parts)
    if not target.is_file() or target.is_symlink():
        raise ValueError(f"{skill_dir.name}: {label} does not exist: {value}")
    return value


def _load_rules(repository: Path) -> dict[str, Mapping[str, Any]]:
    path = repository / "runtime/config/skill-context.yaml"
    if not path.is_file():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError, RecursionError) as exc:
        raise ValueError(f"{path}: invalid skill context config: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, Mapping) or not isinstance(data.get("skills", {}), Mapping):
        raise ValueError(f"{path}: expected a skills mapping")
    result: dict[str, Mapping[str, Any]] = {}
    for name, rule in data.get("skills", {}).items():
        if not isinstance(name, str) or not isinstance(rule, Mapping):
            raise ValueError(f"{path}: every skill rule must be a mapping")
        result[name] = rule
    return result


def _manifest_names(repository: Path) -> list[str] | None:
    path = repository / "system-manifest.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: invalid system manifest: {exc}") from exc
    names = data.get("skills") if isinstance(data, Mapping) else None
    if not isinstance(names, list) or not all(isinstance(item, str) for item in names):
        raise ValueError(f"{path}: skills must be an array of names")
    if len(names) != len(set(names)):
        raise ValueError(f"{path}: skills contains duplicate names")
    return list(names)


def build_skill_registry(skills_dir: Path) -> list[dict[str, Any]]:
    """Build sorted discovery records without loading instruction bodies."""

    root = Path(skills_dir)
    if not root.is_dir():
        raise ValueError(f"skills directory does not exist: {skills_dir}")
    repository = root.parent.parent
    rules = _load_rules(repository)
    skill_dirs = sorted(path for path in root.iterdir() if path.is_dir())
    records: list[dict[str, Any]] = []
    discovered: list[str] = []
    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file() or skill_file.is_symlink():
            raise ValueError(f"{skill_file}: missing or unsafe SKILL.md")
        frontmatter = _read_frontmatter(skill_file)
        name = frontmatter.get("name")
        description = frontmatter.get("description")
        if name != skill_dir.name:
            raise ValueError(f"{skill_file}: name must match directory {skill_dir.name}")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"{skill_file}: description must be non-empty")
        rule = rules.get(name, {})
        required = rule.get("required_refs", [])
        conditional = rule.get("conditional_refs", [])
        if not isinstance(required, list) or not isinstance(conditional, list):
            raise ValueError(f"{name}: context reference rules must be arrays")
        required_refs = [_validate_ref(skill_dir, item, "required_refs entry") for item in required]
        conditional_refs: list[dict[str, str]] = []
        for item in conditional:
            if not isinstance(item, Mapping):
                raise ValueError(f"{name}: conditional_refs entries must be objects")
            when = item.get("when")
            if not isinstance(when, str) or not when:
                raise ValueError(f"{name}: conditional reference needs a when value")
            conditional_refs.append(
                {
                    "path": _validate_ref(skill_dir, item.get("path"), "conditional reference"),
                    "when": when,
                }
            )
        records.append(
            {
                "name": name,
                "description": description.strip(),
                "path": skill_dir.relative_to(root).as_posix(),
                "digest": _bundle_digest(skill_dir),
                "required_refs": required_refs,
                "conditional_refs": conditional_refs,
            }
        )
        discovered.append(name)
    manifest_names = _manifest_names(repository)
    if manifest_names is not None and sorted(manifest_names) != sorted(discovered):
        missing = sorted(set(manifest_names).difference(discovered))
        extra = sorted(set(discovered).difference(manifest_names))
        raise ValueError(f"system manifest skill membership differs (missing={missing}, extra={extra})")
    return sorted(records, key=lambda item: item["name"])

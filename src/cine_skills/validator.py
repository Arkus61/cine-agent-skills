from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from .artifacts import strict_json_loads

_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_ALLOWED_FRONTMATTER = {"name", "description"}


def _parse_skill(path: Path) -> tuple[dict[str, Any] | None, str, list[str]]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return None, "", [f"{path}: invalid UTF-8 SKILL.md: {exc}"]
    except OSError as exc:
        return None, "", [f"{path}: cannot read file: {exc}"]

    if not text.startswith("---\n"):
        return None, text, [f"{path}: SKILL.md must start with YAML frontmatter"]

    try:
        closing = text.index("\n---\n", 4)
    except ValueError:
        return None, text, [f"{path}: YAML frontmatter is not closed"]

    raw_frontmatter = text[4:closing]
    body = text[closing + 5 :]
    try:
        parsed = yaml.safe_load(raw_frontmatter)
    except RecursionError:
        return None, body, [f"{path}: invalid YAML frontmatter: document exceeds nesting limit"]
    except yaml.YAMLError as exc:
        return None, body, [f"{path}: invalid YAML frontmatter: {exc}"]

    if not isinstance(parsed, dict):
        return None, body, [f"{path}: frontmatter must be a mapping"]
    return parsed, body, errors


def _validate_openai_metadata(skill_dir: Path, skill_name: str) -> list[str]:
    path = skill_dir / "agents" / "openai.yaml"
    if not path.exists():
        return [f"{path}: missing Codex UI metadata"]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        return [f"{path}: invalid UTF-8 YAML: {exc}"]
    except RecursionError:
        return [f"{path}: invalid YAML: document exceeds nesting limit"]
    except (OSError, yaml.YAMLError) as exc:
        return [f"{path}: invalid YAML: {exc}"]

    errors: list[str] = []
    interface = data.get("interface") if isinstance(data, dict) else None
    if not isinstance(interface, dict):
        return [f"{path}: must contain an interface mapping"]

    display_name = interface.get("display_name")
    short_description = interface.get("short_description")
    default_prompt = interface.get("default_prompt")
    if not isinstance(display_name, str) or not display_name.strip():
        errors.append(f"{path}: interface.display_name must be a non-empty string")
    if not isinstance(short_description, str) or not 25 <= len(short_description) <= 64:
        errors.append(f"{path}: interface.short_description must contain 25-64 characters")
    if not isinstance(default_prompt, str) or f"${skill_name}" not in default_prompt:
        errors.append(f"{path}: interface.default_prompt must mention ${skill_name}")
    return errors


def _validate_relative_links(skill_file: Path, body: str) -> list[str]:
    errors: list[str] = []
    for raw_target in _LINK_RE.findall(body):
        target = raw_target.split("#", 1)[0].strip()
        if not target or "://" in target or target.startswith(("mailto:", "#")):
            continue
        try:
            skill_root = skill_file.parent.resolve()
            resolved = (skill_file.parent / target).resolve()
        except (OSError, RuntimeError) as exc:
            errors.append(
                f"{skill_file}: cannot resolve relative reference: {target}: {exc}"
            )
            continue
        try:
            resolved.relative_to(skill_root)
        except ValueError:
            errors.append(f"{skill_file}: relative reference escapes skill directory: {target}")
            continue
        if not resolved.exists():
            errors.append(f"{skill_file}: missing relative reference: {target}")
    return errors


def _validate_schemas(root: Path) -> list[str]:
    schema_dir = root / "schemas"
    if not schema_dir.is_dir():
        return []

    errors: list[str] = []
    try:
        schema_paths = sorted(
            path
            for path in schema_dir.iterdir()
            if path.name.endswith(".schema.json")
        )
    except OSError as exc:
        return [f"{schema_dir}: cannot inspect schema directory: {exc}"]
    for schema_path in schema_paths:
        try:
            schema = strict_json_loads(schema_path.read_text(encoding="utf-8"))
        except UnicodeDecodeError as exc:
            errors.append(f"{schema_path}: invalid UTF-8 JSON schema: {exc}")
            continue
        except RecursionError:
            errors.append(
                f"{schema_path}: invalid JSON schema: document exceeds nesting limit"
            )
            continue
        except (OSError, ValueError) as exc:
            errors.append(f"{schema_path}: invalid JSON schema: {exc}")
            continue
        try:
            Draft202012Validator.check_schema(schema)
        except RecursionError:
            errors.append(
                f"{schema_path}: invalid JSON schema: schema exceeds nesting limit"
            )
        except SchemaError as exc:
            errors.append(f"{schema_path}: invalid JSON schema: {exc.message}")
    return errors


def validate_repository(root: Path) -> list[str]:
    """Return repository validation errors. An empty list means valid."""
    root = Path(root)
    errors = _validate_schemas(root)
    skills_root = root / ".agents" / "skills"
    if not skills_root.is_dir():
        return errors + [f"{skills_root}: skills directory does not exist"]

    try:
        skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir())
    except OSError as exc:
        return errors + [f"{skills_root}: cannot inspect skills directory: {exc}"]
    if not skill_dirs:
        return errors + [f"{skills_root}: no skills found"]

    seen_names: set[str] = set()
    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            errors.append(f"{skill_file}: missing SKILL.md")
            continue

        frontmatter, body, parse_errors = _parse_skill(skill_file)
        errors.extend(parse_errors)
        if frontmatter is None:
            continue

        extra_fields = sorted(set(frontmatter) - _ALLOWED_FRONTMATTER)
        if extra_fields:
            errors.append(
                f"{skill_file}: unsupported frontmatter fields: {', '.join(extra_fields)}"
            )

        name = frontmatter.get("name")
        description = frontmatter.get("description")
        if not isinstance(name, str) or not _NAME_RE.fullmatch(name):
            errors.append(f"{skill_file}: name must use lowercase alphanumerics and single hyphens")
            name = skill_dir.name
        if name != skill_dir.name:
            errors.append(f"{skill_file}: name '{name}' must match directory '{skill_dir.name}'")
        if name in seen_names:
            errors.append(f"{skill_file}: duplicate skill name '{name}'")
        seen_names.add(name)

        if not isinstance(description, str) or not description.strip():
            errors.append(f"{skill_file}: description must be a non-empty string")
        elif len(description) > 1024:
            errors.append(f"{skill_file}: description must not exceed 1024 characters")

        if not body.strip():
            errors.append(f"{skill_file}: instruction body must not be empty")

        errors.extend(_validate_openai_metadata(skill_dir, name))
        errors.extend(_validate_relative_links(skill_file, body))

    return errors

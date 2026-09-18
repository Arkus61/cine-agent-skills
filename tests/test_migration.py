from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.migrate_project import migrate
from cine_skills.package import validate_scene_package
from cine_skills.project_package import validate_project


def _digest_tree(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        if item.is_file():
            digest.update(item.relative_to(path).as_posix().encode())
            digest.update(item.read_bytes())
    return digest.hexdigest()


def _without_metadata(value, key: str | None = None):
    if key == "layers" and isinstance(value, dict):
        return {name: "<profile>" if isinstance(item, str) else _without_metadata(item, name) for name, item in value.items()}
    if isinstance(value, dict):
        return {
            name: _without_metadata(item, name)
            for name, item in value.items()
            if name not in {"schema_version", "release_version", "profile", "schema_name"}
        }
    if isinstance(value, list):
        return [_without_metadata(item, key) for item in value]
    return value


def _assert_json_content_preserved(source: Path, output: Path) -> None:
    for source_file in sorted(source.rglob("*.json")):
        relative = source_file.relative_to(source)
        output_file = output / relative
        assert _without_metadata(json.loads(source_file.read_text())) == _without_metadata(
            json.loads(output_file.read_text())
        )


def _rewrite_json(path: Path, *, project: bool) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    nested_scene = "scenes" in path.parts

    def visit(value, key: str | None = None):
        if key == "layers" and isinstance(value, dict):
            return {
                name: (f"{item}-v2" if item in {"story", "production", "post"} else item)
                for name, item in value.items()
            }
        if isinstance(value, dict):
            return {name: visit(item, name) for name, item in value.items()}
        if isinstance(value, list):
            return [visit(item, key) for item in value]
        if project and key == "schema_version" and isinstance(value, str):
            return "1.0" if nested_scene else "2.0"
        if project and key == "release_version" and isinstance(value, str):
            return "1.0.0" if nested_scene else "2.0.0"
        if not project and key == "schema_version" and isinstance(value, str):
            return "1.0"
        if not project and key == "release_version" and isinstance(value, str):
            return "1.0.0"
        if key == "profile" and value == "scene-full":
            return "full-v1"
        if key == "profile" and value == "full-creative":
            return "full-creative-v2"
        if key == "profile" and value in {"story", "production", "post"}:
            return f"{value}-v2"
        if key == "schema_name" and value == "scene-full":
            return "full-v1"
        return value

    path.write_text(json.dumps(visit(payload), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _sandbox(tmp_path: Path, repository_root: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    shutil.copytree(repository_root / "schemas", root / "schemas")
    return root


def _legacy_scene_core(root: Path, repository_root: Path) -> Path:
    source = root / "legacy-core"
    shutil.copytree(repository_root / "examples/scene-core/scenes/S01", source)
    for path in source.glob("*.json"):
        _rewrite_json(path, project=False)
    return source


def _legacy_scene_full(root: Path, repository_root: Path) -> Path:
    source = root / "legacy-full"
    shutil.copytree(repository_root / "examples/scene-full/scenes/S01", source)
    for path in source.glob("*.json"):
        _rewrite_json(path, project=False)
    return source


def _legacy_project(root: Path, repository_root: Path) -> Path:
    source = root / "legacy-project"
    shutil.copytree(repository_root / "examples/ninel", source)
    for path in source.rglob("*.json"):
        _rewrite_json(path, project=True)
    return source


def test_core_dry_run_is_non_destructive(tmp_path: Path, repository_root: Path) -> None:
    root = _sandbox(tmp_path, repository_root)
    source = _legacy_scene_core(root, repository_root)
    before = _digest_tree(source)
    output = root / "migrated-core"

    result = migrate(root, source, output, dry_run=True)

    assert result["status"] == "ready"
    assert result["source_kind"] == "scene-core"
    assert result["changed_files"] == sorted(path.name for path in source.glob("*.json"))
    assert not output.exists()
    assert _digest_tree(source) == before


def test_full_scene_migration_writes_new_valid_package(
    tmp_path: Path, repository_root: Path
) -> None:
    root = _sandbox(tmp_path, repository_root)
    source = _legacy_scene_full(root, repository_root)
    before = _digest_tree(source)
    output = root / "migrated-full"

    result = migrate(root, source, output)

    assert result["status"] == "migrated"
    assert result["source_kind"] == "scene-full"
    assert validate_scene_package(output, repository_root, profile="scene-full") == []
    assert _digest_tree(source) == before
    _assert_json_content_preserved(source, output)
    manifest = json.loads((output / "package-manifest.json").read_text(encoding="utf-8"))
    assert manifest["profile"] == "scene-full"
    assert manifest["release_version"] == "0.3.0"
    assert manifest["artifacts"][0]["schema_version"] == "0.3.0"


def test_layered_project_migration_preserves_project_validity(
    tmp_path: Path, repository_root: Path
) -> None:
    root = _sandbox(tmp_path, repository_root)
    source = _legacy_project(root, repository_root)
    output = root / "migrated-project"

    result = migrate(root, source, output)

    assert result["status"] == "migrated"
    assert result["source_kind"] == "full-creative"
    assert validate_project(output, repository_root) == []
    _assert_json_content_preserved(source, output)
    manifest = json.loads((output / "creative-manifest.json").read_text(encoding="utf-8"))
    assert manifest["profile"] == "full-creative"
    assert manifest["release_version"] == "0.3.0"
    nested = json.loads(
        (output / "scripts/NINEL-E01/script-manifest.json").read_text(encoding="utf-8")
    )
    assert nested["artifacts"][-2]["schema_name"] == "scene-full"


def test_current_source_is_ready_without_copying(
    tmp_path: Path, repository_root: Path
) -> None:
    root = _sandbox(tmp_path, repository_root)
    source = root / "current-core"
    shutil.copytree(repository_root / "examples/scene-core/scenes/S01", source)
    output = root / "not-created"

    result = migrate(root, source, output)

    assert result == {
        "status": "ready",
        "source_kind": "scene-core",
        "target_version": "0.3.0",
        "changed_files": [],
        "errors": [],
    }
    assert not output.exists()


def test_migration_cli_emits_machine_readable_report(
    tmp_path: Path, repository_root: Path
) -> None:
    root = _sandbox(tmp_path, repository_root)
    source = _legacy_scene_core(root, repository_root)
    output = root / "cli-output"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/migrate_project.py",
            "--root",
            str(root),
            "--source",
            str(source),
            "--output",
            str(output),
            "--dry-run",
            "--format",
            "json",
        ],
        cwd=repository_root,
        env={"PYTHONPATH": str(repository_root / "src")},
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["status"] == "ready"
    assert not output.exists()


@pytest.mark.parametrize(
    "mutation",
    [
        "mixed-version",
        "malformed-json",
        "existing-output",
        "symlink",
        "outside-root",
    ],
)
def test_unsafe_or_unknown_inputs_are_blocked(
    tmp_path: Path, repository_root: Path, mutation: str
) -> None:
    root = _sandbox(tmp_path, repository_root)
    source = _legacy_scene_core(root, repository_root)
    output = root / "output"
    if mutation == "mixed-version":
        path = source / "shot-list.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["schema_version"] = "future"
        path.write_text(json.dumps(payload), encoding="utf-8")
    elif mutation == "malformed-json":
        (source / "shot-list.json").write_text("{", encoding="utf-8")
    elif mutation == "existing-output":
        output.mkdir()
    elif mutation == "symlink":
        target = source / "scene-beats.json"
        target.unlink()
        target.symlink_to(repository_root / "examples/scene-core/scenes/S01/scene-beats.json")
    elif mutation == "outside-root":
        source = tmp_path / "outside"
        source.mkdir()

    result = migrate(root, source, output)

    assert result["status"] == "blocked"
    assert result["errors"]
    if mutation != "existing-output":
        assert not output.exists()

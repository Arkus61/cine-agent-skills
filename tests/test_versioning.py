from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _minimal_repository(root: Path) -> None:
    (root / "src/cine_skills").mkdir(parents=True)
    (root / ".agents/skills/scene-planner").mkdir(parents=True)
    (root / "src/cine_skills/__init__.py").write_text(
        '__version__ = "2.0.0"\n', encoding="utf-8"
    )
    (root / "pyproject.toml").write_text(
        '[project]\nname = "cine-agent-skills"\nversion = "2.0.0"\n',
        encoding="utf-8",
    )
    (root / ".agents/skills/scene-planner/SKILL.md").write_text(
        "---\nname: scene-planner\ndescription: plan scenes\n---\n", encoding="utf-8"
    )


def test_release_source(repository_root: Path) -> None:
    import tomllib

    from scripts.sync_versions import read_release_version

    expected = tomllib.loads(
        (repository_root / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]["version"]
    assert read_release_version(repository_root) == expected


def test_active_pilot_yaml_is_part_of_version_sync(repository_root: Path) -> None:
    from scripts.sync_versions import planned_updates

    updates = planned_updates(repository_root)

    assert repository_root / "src/cine_skills/runtime/recipes/ninel-blocking.yaml" in updates
    assert repository_root / "evals/film_os/pilot-contract.yaml" in updates


def test_check_versions_reports_derived_drift_without_writing(tmp_path: Path) -> None:
    from scripts.sync_versions import check_versions

    _minimal_repository(tmp_path)
    runtime = tmp_path / "src/cine_skills/__init__.py"
    runtime.write_text('__version__ = "1.0.0"\n', encoding="utf-8")
    before = runtime.read_bytes()

    problems = check_versions(tmp_path)

    assert any("src/cine_skills/__init__.py" in problem for problem in problems)
    assert runtime.read_bytes() == before


def test_write_is_idempotent_and_only_updates_allowlisted_derivatives(tmp_path: Path) -> None:
    from scripts.sync_versions import check_versions, planned_updates

    _minimal_repository(tmp_path)
    (tmp_path / "system-manifest.json").write_text(
        json.dumps({"release_version": "1.0.0", "skills": ["scene-planner"]}),
        encoding="utf-8",
    )

    updates = planned_updates(tmp_path)
    for path, content in updates.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    assert check_versions(tmp_path) == []
    snapshot = {path: path.read_bytes() for path in updates}
    for path, content in snapshot.items():
        path.write_bytes(content)
    assert check_versions(tmp_path) == []


def test_cli_check_returns_nonzero_for_drift_and_write_repairs_it(tmp_path: Path) -> None:
    from scripts.sync_versions import check_versions

    _minimal_repository(tmp_path)
    (tmp_path / "system-manifest.json").write_text(
        '{"release_version":"1.0.0","skills":[]}', encoding="utf-8"
    )
    script = Path(__file__).parents[1] / "scripts/sync_versions.py"

    check = subprocess.run(
        [sys.executable, str(script), "--root", str(tmp_path), "--check"],
        capture_output=True,
        text=True,
    )
    assert check.returncode == 1
    assert "system-manifest.json" in check.stdout

    write = subprocess.run(
        [sys.executable, str(script), "--root", str(tmp_path), "--write"],
        capture_output=True,
        text=True,
    )
    assert write.returncode == 0
    assert json.loads((tmp_path / "system-manifest.json").read_text())[
        "release_version"
    ] == "2.0.0"
    assert json.loads((tmp_path / "system-manifest.json").read_text())["skills"] == [
        "scene-planner"
    ]
    assert check_versions(tmp_path) == []


def test_planned_updates_rejects_missing_project_version(tmp_path: Path) -> None:
    from scripts.sync_versions import read_release_version

    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'x'\n", encoding="utf-8")
    with pytest.raises(ValueError, match="project.version"):
        read_release_version(tmp_path)

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from scripts.build_release_archive import build_archive


def test_release_archive_is_safe_and_reproducible(
    repository_root: Path, tmp_path: Path
) -> None:
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"

    first_digest = build_archive(repository_root, first)
    second_digest = build_archive(repository_root, second)

    assert first_digest == second_digest
    with zipfile.ZipFile(first) as archive:
        assert archive.testzip() is None
        infos = archive.infolist()
        names = [info.filename for info in infos]
        assert names == sorted(names)
        assert names
        assert all(name.startswith("cine-agent-skills/") for name in names)
        assert all(
            not any(part in {".git", ".venv", ".pytest_cache", "__pycache__", "dist", "build"}
                       for part in Path(name).parts)
            for name in names
        )
        assert all(not name.endswith((".pyc", ".pyo", ".zip")) for name in names)
        assert all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in infos)


def test_release_archive_rejects_unsafe_tracked_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import build_release_archive as builder

    (tmp_path / ".git").mkdir()

    class Result:
        stdout = b"../escape.txt\x00"

    monkeypatch.setattr(builder.subprocess, "run", lambda *args, **kwargs: Result())

    with pytest.raises(ValueError, match="unsafe tracked path"):
        build_archive(tmp_path, tmp_path / "release.zip")


def test_release_archive_rejects_unsafe_prefix(
    repository_root: Path, tmp_path: Path
) -> None:
    with pytest.raises(ValueError, match="unsafe archive prefix"):
        build_archive(repository_root, tmp_path / "release.zip", prefix="../")


def test_release_archive_works_from_a_git_archive_snapshot(tmp_path: Path) -> None:
    snapshot = tmp_path / "snapshot"
    (snapshot / "docs").mkdir(parents=True)
    (snapshot / "docs" / "README.md").write_text("tracked", encoding="utf-8")
    (snapshot / ".venv").mkdir()
    (snapshot / ".venv" / "ignored.txt").write_text("ignored", encoding="utf-8")
    (snapshot / "cine_agent_skills.egg-info").mkdir()
    (snapshot / "cine_agent_skills.egg-info" / "PKG-INFO").write_text(
        "generated", encoding="utf-8"
    )

    output = tmp_path / "snapshot.zip"
    build_archive(snapshot, output)

    with zipfile.ZipFile(output) as archive:
        assert archive.namelist() == ["cine-agent-skills/docs/README.md"]

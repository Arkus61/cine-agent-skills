from __future__ import annotations

from pathlib import Path

import pytest


def test_changed_source_under_stable_id_is_stale(tmp_path: Path) -> None:
    from cine_skills.project_freshness import capture_sources, compare_sources

    source = tmp_path / "camera.json"
    source.write_text('{"shot_id":"S01-SH001","x":0}', encoding="utf-8")
    snapshot = capture_sources(tmp_path, [{"key": "camera-1", "path": "camera.json"}])
    source.write_text('{"shot_id":"S01-SH001","x":1}', encoding="utf-8")

    report = compare_sources(tmp_path, snapshot)

    assert report["fresh"] == []
    assert report["stale"] == ["camera-1"]
    assert report["unknown"] == []
    assert report["reasons"] == ["changed-source:camera-1"]


def test_unchanged_sources_are_fresh_and_compare_is_read_only(tmp_path: Path) -> None:
    from cine_skills.project_freshness import capture_sources, compare_sources

    source = tmp_path / "camera.json"
    source.write_text("{}", encoding="utf-8")
    snapshot = capture_sources(tmp_path, [{"key": "camera-1", "path": "camera.json"}])
    before = source.read_bytes()

    assert compare_sources(tmp_path, snapshot) == {
        "fresh": ["camera-1"],
        "stale": [],
        "unknown": [],
        "reasons": [],
        "coverage": {"recorded": ["camera-1"], "unrecorded": []},
    }
    assert source.read_bytes() == before


def test_deleted_source_is_stale_and_missing_baseline_is_unknown(tmp_path: Path) -> None:
    from cine_skills.project_freshness import capture_sources, compare_sources

    source = tmp_path / "camera.json"
    source.write_text("{}", encoding="utf-8")
    snapshot = capture_sources(tmp_path, [{"key": "camera-1", "path": "camera.json"}])
    source.unlink()
    report = compare_sources(tmp_path, snapshot)
    assert report["stale"] == ["camera-1"]
    assert report["reasons"] == ["missing-source:camera-1"]

    unknown = compare_sources(
        tmp_path,
        {"nodes": [{"key": "camera-1", "path": "camera.json"}]},
    )
    assert unknown["unknown"] == ["camera-1"]
    assert unknown["reasons"] == ["missing-baseline:camera-1"]


def test_freshness_rejects_traversal_and_symlink(tmp_path: Path) -> None:
    from cine_skills.project_freshness import capture_sources

    outside = tmp_path.parent / "outside-film-os.json"
    outside.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="unsafe path"):
        capture_sources(tmp_path, [{"key": "escape", "path": "../outside-film-os.json"}])

    link = tmp_path / "link.json"
    link.symlink_to(outside)
    with pytest.raises(ValueError, match="symlink"):
        capture_sources(tmp_path, [{"key": "link", "path": "link.json"}])

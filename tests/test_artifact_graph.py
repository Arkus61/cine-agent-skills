from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_affected_nodes_returns_changed_nodes_and_downstream_closure() -> None:
    import networkx as nx

    from cine_skills.runtime.artifact_graph import affected_nodes

    graph = nx.DiGraph(
        [("camera-1", "preview-1"), ("camera-2", "preview-2"), ("preview-1", "review-1")]
    )

    assert affected_nodes(graph, {"camera-1"}) == ["camera-1", "preview-1", "review-1"]


def test_build_artifact_graph_records_declared_digest_and_edges(tmp_path: Path) -> None:
    from cine_skills.runtime.artifact_graph import build_artifact_graph

    (tmp_path / "camera.json").write_text('{"shot_id":"S01-SH001"}', encoding="utf-8")
    (tmp_path / "preview.json").write_text("{}", encoding="utf-8")
    graph = build_artifact_graph(
        tmp_path,
        tmp_path,
        {
            "nodes": [
                {"key": "camera-1", "path": "camera.json", "kind": "source"},
                {"key": "preview-1", "path": "preview.json", "kind": "result"},
            ],
            "edges": [{"upstream": "camera-1", "downstream": "preview-1", "reason": "camera drives preview"}],
        },
    )

    assert list(graph.edges) == [("camera-1", "preview-1")]
    assert len(graph.nodes["camera-1"]["content_sha256"]) == 64
    assert graph.nodes["camera-1"]["kind"] == "source"


def test_build_artifact_graph_rejects_missing_endpoint_and_cycle(tmp_path: Path) -> None:
    from cine_skills.runtime.artifact_graph import build_artifact_graph

    (tmp_path / "a.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="unknown upstream"):
        build_artifact_graph(
            tmp_path,
            tmp_path,
            {"nodes": [{"key": "a", "path": "a.json"}], "edges": [{"upstream": "missing", "downstream": "a"}]},
        )

    with pytest.raises(ValueError, match="cycle"):
        build_artifact_graph(
            tmp_path,
            tmp_path,
            {
                "nodes": [{"key": "a", "path": "a.json"}, {"key": "b", "path": "a.json"}],
                "edges": [{"upstream": "a", "downstream": "b"}, {"upstream": "b", "downstream": "a"}],
            },
        )


def test_build_artifact_graph_rejects_escaping_path(tmp_path: Path) -> None:
    from cine_skills.runtime.artifact_graph import build_artifact_graph

    with pytest.raises(ValueError, match="unsafe path"):
        build_artifact_graph(
            tmp_path,
            tmp_path,
            {"nodes": [{"key": "outside", "path": "../outside.json"}], "edges": []},
        )

from __future__ import annotations

import networkx as nx
import pytest


def test_scene_plan_orders_dependencies_and_reuses_fresh_nodes() -> None:
    from cine_skills.runtime.scene_plan import compile_scene_plan

    graph = nx.DiGraph(
        [
            ("camera-1", "preview-1"),
            ("preview-1", "review-1"),
            ("camera-2", "preview-2"),
        ]
    )
    graph.nodes["camera-1"]["skill_name"] = "camera-movement-designer"
    graph.nodes["preview-1"]["skill_name"] = "storyboard-designer"
    graph.nodes["review-1"]["skill_name"] = "media-review-supervisor"
    graph.nodes["camera-2"]["skill_name"] = "camera-movement-designer"

    plan = compile_scene_plan(
        graph,
        ["review-1"],
        {"fresh": ["camera-1", "preview-1"], "stale": ["review-1"], "unknown": []},
    )

    assert [task["task_id"] for task in plan] == [
        "artifact:camera-1",
        "artifact:preview-1",
        "artifact:review-1",
    ]
    assert [task["operation_kind"] for task in plan] == ["reuse", "reuse", "generate"]
    assert plan[-1]["inputs"] == ["preview-1"]
    assert all("camera-2" not in task["task_id"] for task in plan)


def test_scene_plan_includes_unknown_inputs_as_blocked_tasks() -> None:
    from cine_skills.runtime.scene_plan import compile_scene_plan

    graph = nx.DiGraph([("source", "result")])
    plan = compile_scene_plan(graph, ["result"], {"fresh": [], "stale": [], "unknown": ["source"]})

    assert plan[0]["operation_kind"] == "blocked"
    assert plan[0]["task_id"] == "artifact:source"
    assert plan[1]["operation_kind"] == "generate"


def test_scene_plan_rejects_unknown_target() -> None:
    from cine_skills.runtime.scene_plan import compile_scene_plan

    with pytest.raises(ValueError, match="unknown target"):
        compile_scene_plan(nx.DiGraph(), ["missing"], {})

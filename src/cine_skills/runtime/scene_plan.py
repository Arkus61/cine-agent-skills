"""Compile a finite execution list from the declared artifact DAG."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import networkx as nx


def _names(value: Any, field: str) -> set[str]:
    if value is None:
        return set()
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"freshness.{field} must be an array of names")
    return set(value)


def compile_scene_plan(
    graph: nx.DiGraph, targets: list[str], freshness: Mapping[str, Any] | None
) -> list[dict[str, Any]]:
    """Return topologically ordered task records for target artifacts."""

    if not isinstance(graph, nx.DiGraph):
        raise ValueError("graph must be a networkx.DiGraph")
    if not isinstance(targets, list) or not targets or not all(isinstance(item, str) and item for item in targets):
        raise ValueError("targets must be a non-empty array of names")
    missing_targets = sorted(set(targets).difference(graph.nodes))
    if missing_targets:
        raise ValueError(f"unknown target artifacts: {', '.join(missing_targets)}")
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("artifact graph must be acyclic")
    freshness = freshness if isinstance(freshness, Mapping) else {}
    fresh = _names(freshness.get("fresh"), "fresh")
    stale = _names(freshness.get("stale"), "stale")
    unknown = _names(freshness.get("unknown"), "unknown")
    selected = set(targets)
    for target in targets:
        selected.update(nx.ancestors(graph, target))
    subgraph = graph.subgraph(selected)
    order = list(nx.lexicographical_topological_sort(subgraph, key=str))
    plan: list[dict[str, Any]] = []
    for key in order:
        attrs = graph.nodes[key]
        if key in unknown:
            operation_kind = "blocked"
        elif key in fresh and key not in stale:
            operation_kind = "reuse"
        else:
            operation_kind = "generate"
        skill_name = attrs.get("skill_name") if isinstance(attrs, Mapping) else None
        if not isinstance(skill_name, str) or not skill_name:
            skill_name = "deterministic-validator"
        plan.append(
            {
                "task_id": f"artifact:{key}",
                "inputs": sorted(predecessor for predecessor in graph.predecessors(key) if predecessor in selected),
                "outputs": [key],
                "skill_name": skill_name,
                "operation_kind": operation_kind,
            }
        )
    return plan

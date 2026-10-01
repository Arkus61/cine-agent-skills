"""Film artifact dependency projection backed by NetworkX."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

import networkx as nx


def _safe_project_file(project_dir: Path, value: Any, *, allow_missing: bool) -> tuple[Path, str]:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"unsafe path {value!r}")
    relative = PurePosixPath(value)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError(f"unsafe path {value!r}")
    root = Path(project_dir).resolve(strict=True)
    candidate = root.joinpath(*relative.parts)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"symlink path is not allowed: {value}")
    try:
        resolved = candidate.resolve(strict=not allow_missing)
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError) as exc:
        if allow_missing and not candidate.exists():
            return candidate, "missing"
        raise ValueError(f"unsafe path {value!r}") from exc
    if not resolved.is_file():
        if allow_missing and not resolved.exists():
            return candidate, "missing"
        raise ValueError(f"artifact path is not a regular file: {value}")
    return resolved, "present"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifact_graph(
    project_dir: Path, root: Path, declarations: Mapping[str, Any]
) -> nx.DiGraph:
    """Build a validated directed dependency graph from explicit declarations.

    ``root`` is retained in the interface for callers that build the graph
    beside repository validators. The graph only trusts declarations supplied
    by the caller; prose similarity never creates an edge.
    """

    del root
    if not isinstance(declarations, Mapping):
        raise ValueError("artifact graph declarations must be an object")
    raw_nodes = declarations.get("nodes")
    raw_edges = declarations.get("edges", [])
    if not isinstance(raw_nodes, list) or not isinstance(raw_edges, list):
        raise ValueError("artifact graph nodes and edges must be arrays")
    graph = nx.DiGraph()
    for item in raw_nodes:
        if not isinstance(item, Mapping):
            raise ValueError("artifact graph node must be an object")
        key = item.get("key")
        if not isinstance(key, str) or not key:
            raise ValueError("artifact graph node key must be a non-empty string")
        if key in graph:
            raise ValueError(f"duplicate artifact node: {key}")
        path, availability = _safe_project_file(
            Path(project_dir), item.get("path"), allow_missing=True
        )
        attrs: dict[str, Any] = {
            "artifact_key": key,
            "path": str(item["path"]),
            "kind": item.get("kind", "artifact"),
            "pointer": item.get("pointer"),
            "entity_ids": tuple(sorted(item.get("entity_ids", [])))
            if isinstance(item.get("entity_ids", []), list)
            else (),
            "availability": availability,
        }
        if availability == "present":
            attrs["content_sha256"] = _digest(path)
        else:
            attrs["content_sha256"] = None
        graph.add_node(key, **attrs)

    for item in raw_edges:
        if not isinstance(item, Mapping):
            raise ValueError("artifact graph edge must be an object")
        upstream, downstream = item.get("upstream"), item.get("downstream")
        if upstream not in graph:
            raise ValueError(f"unknown upstream artifact node: {upstream}")
        if downstream not in graph:
            raise ValueError(f"unknown downstream artifact node: {downstream}")
        graph.add_edge(upstream, downstream, reason=item.get("reason", ""))

    if not nx.is_directed_acyclic_graph(graph):
        cycle = nx.find_cycle(graph)
        members = ", ".join(sorted({edge[0] for edge in cycle}))
        raise ValueError(f"artifact dependency cycle: {members}")
    return graph


def affected_nodes(graph: nx.DiGraph, changed: set[str]) -> list[str]:
    """Return changed nodes and their declared downstream closure."""

    if not isinstance(graph, nx.DiGraph):
        raise ValueError("graph must be a networkx.DiGraph")
    missing = sorted(set(changed).difference(graph.nodes))
    if missing:
        raise ValueError(f"unknown changed artifact nodes: {', '.join(missing)}")
    affected = set(changed)
    for key in changed:
        affected.update(nx.descendants(graph, key))
    return sorted(affected)

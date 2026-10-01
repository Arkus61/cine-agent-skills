"""Semantic validation for exact, version-bound VFX post plans."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


_POSITIVE = r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"


def validate_vfx_post_plan_contract(payload: Mapping[str, Any]) -> list[str]:
    """Validate local ownership, bindings, dependencies, review, and delivery gates."""
    errors: list[str] = []
    project_id, unit_id = payload.get("project_id"), payload.get("unit_id")
    if not isinstance(project_id, str) or not isinstance(unit_id, str):
        return errors
    if re.fullmatch(rf"{re.escape(project_id)}-(?:U|E)(?:0[1-9]|[1-9][0-9])", unit_id) is None:
        errors.append(f"unit_id: {unit_id!r} must match declared project {project_id} as {project_id}-U## or {project_id}-E##")
    context = payload.get("source_context")
    items = payload.get("items")
    dependencies = payload.get("dependencies")
    if not isinstance(context, Mapping) or not isinstance(items, list) or not isinstance(dependencies, list):
        return errors

    effects = _registry(context.get("preproduction_effects"), "effect_id", rf"{re.escape(project_id)}-FX{_POSITIVE}", "preproduction effect ID", f"{project_id}-FX###", errors)
    segments = _registry(context.get("edit_segments"), "segment_id", rf"{re.escape(unit_id)}-ED{_POSITIVE}", "edit segment ID", f"{unit_id}-ED###", errors)
    media_records = context.get("media_versions")
    versions = _registry(media_records, "version_id", rf"{re.escape(project_id)}-MD{_POSITIVE}-v[0-9]{{3,}}", "media version ID", f"{project_id}-MD###-v###", errors)
    version_roles: dict[str, set[str]] = {}
    for index, record in enumerate(media_records if isinstance(media_records, list) else []):
        if not isinstance(record, Mapping):
            continue
        media_id, version_id = record.get("media_id"), record.get("version_id")
        if isinstance(media_id, str) and re.fullmatch(rf"{re.escape(project_id)}-MD{_POSITIVE}", media_id) is None:
            errors.append(f"source_context.media_versions.{index}.media_id: media ID {media_id!r} must match {project_id}-MD###")
        if isinstance(media_id, str) and isinstance(version_id, str) and not version_id.startswith(f"{media_id}-v"):
            errors.append(f"source_context.media_versions.{index}.version_id: version ID {version_id!r} must belong to declared media ID {media_id}")
        if isinstance(version_id, str):
            version_roles[version_id] = set(record.get("roles", []))
    targets = _registry(context.get("delivery_targets"), "target_id", rf"{re.escape(project_id)}-DT{_POSITIVE}", "delivery target ID", f"{project_id}-DT###", errors)

    item_pattern = re.compile(rf"{re.escape(unit_id)}-FX{_POSITIVE}")
    item_records: dict[str, Mapping[str, Any]] = {}
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            continue
        location = f"items.{index}"
        item_id = item.get("item_id")
        if isinstance(item_id, str):
            if item_id in item_records:
                errors.append(f"{location}.item_id: duplicate post item ID {item_id}")
            item_records[item_id] = item
            if item_pattern.fullmatch(item_id) is None:
                errors.append(f"{location}.item_id: post item ID {item_id!r} must match {unit_id}-FX###")
        effect_ids = item.get("preproduction_effect_ids", [])
        if not isinstance(effect_ids, list) or not effect_ids:
            errors.append(f"{location}.preproduction_effect_ids: at least one preproduction VFX link is required")
        else:
            _unknown(effect_ids, effects, f"{location}.preproduction_effect_ids", "preproduction effect", errors)
        _unknown(item.get("edit_segment_ids", []), segments, f"{location}.edit_segment_ids", "edit segment", errors)
        source_version_ids = item.get("source_version_ids", [])
        _unknown(source_version_ids, versions, f"{location}.source_version_ids", "media version", errors)
        for source_version_id in source_version_ids if isinstance(source_version_ids, list) else []:
            if source_version_id in versions and not version_roles.get(source_version_id, set()) & {"source", "plate"}:
                errors.append(f"{location}.source_version_ids: media version {source_version_id} requires a source-capable role")

    evidence_records: dict[str, Mapping[str, Any]] = {}
    for index, record in enumerate(context.get("evidence", [])):
        if not isinstance(record, Mapping):
            continue
        evidence_id = record.get("evidence_id")
        if isinstance(evidence_id, str):
            if evidence_id in evidence_records:
                errors.append(f"source_context.evidence.{index}.evidence_id: duplicate evidence ID {evidence_id}")
            evidence_records[evidence_id] = record
            if re.fullmatch(rf"{re.escape(project_id)}-EV{_POSITIVE}", evidence_id) is None:
                errors.append(f"source_context.evidence.{index}.evidence_id: evidence ID {evidence_id!r} must match {project_id}-EV###")
        item_id, version_id = record.get("item_id"), record.get("version_id")
        if isinstance(item_id, str) and item_id not in item_records:
            errors.append(f"source_context.evidence.{index}.item_id: unknown post item ID {item_id}")
        if isinstance(version_id, str) and version_id not in versions:
            errors.append(f"source_context.evidence.{index}.version_id: unknown media version ID {version_id}")

    dependency_records: dict[str, Mapping[str, Any]] = {}
    orders: list[int] = []
    graph: dict[str, set[str]] = {item_id: set() for item_id in item_records}
    for index, dependency in enumerate(dependencies):
        if not isinstance(dependency, Mapping):
            continue
        dep_id = dependency.get("dependency_id")
        if isinstance(dep_id, str):
            if dep_id in dependency_records:
                errors.append(f"dependencies.{index}.dependency_id: duplicate dependency ID {dep_id}")
            dependency_records[dep_id] = dependency
            if re.fullmatch(rf"{re.escape(project_id)}-DEP{_POSITIVE}", dep_id) is None:
                errors.append(f"dependencies.{index}.dependency_id: dependency ID {dep_id!r} must match {project_id}-DEP###")
        upstream, downstream = dependency.get("upstream_item_id"), dependency.get("downstream_item_id")
        for field, value in (("upstream_item_id", upstream), ("downstream_item_id", downstream)):
            if isinstance(value, str) and value not in item_records:
                errors.append(f"dependencies.{index}.{field}: unknown post item ID {value}")
        if isinstance(upstream, str) and isinstance(downstream, str) and upstream in graph and downstream in graph:
            graph[upstream].add(downstream)
        order = dependency.get("order")
        if isinstance(order, int):
            orders.append(order)
    if orders != sorted(orders) or len(orders) != len(set(orders)):
        errors.append("dependencies: dependency order must be strictly ascending and unique")
    if _has_cycle(graph):
        errors.append("dependencies: dependency cycle is not allowed")
    dependency_orders = {
        (record.get("upstream_item_id"), record.get("downstream_item_id")): record.get("order")
        for record in dependency_records.values()
    }
    if any(
        isinstance(first_order, int) and isinstance(second_order, int) and first_order >= second_order
        for (upstream, middle), first_order in dependency_orders.items()
        for (next_upstream, downstream), second_order in dependency_orders.items()
        if middle == next_upstream
    ):
        errors.append("dependencies: dependency order contradicts execution order")

    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            continue
        location = f"items.{index}"
        item_id, version_id = item.get("item_id"), item.get("current_output_version_id")
        if version_id is not None and version_id not in versions:
            errors.append(f"{location}.current_output_version_id: unknown current output version ID {version_id}")
        elif version_id is not None and "output" not in version_roles.get(version_id, set()):
            errors.append(f"{location}.current_output_version_id: current output version {version_id} requires the output role")
        for dep_id in item.get("dependency_ids", []):
            dep = dependency_records.get(dep_id) if isinstance(dep_id, str) else None
            if dep is None:
                errors.append(f"{location}.dependency_ids: unknown dependency ID {dep_id}")
            elif dep.get("downstream_item_id") != item_id:
                errors.append(f"{location}.dependency_ids: dependency {dep_id} is not bound to this downstream item")
        review_evidence = _bound_evidence(item.get("review_evidence_ids", []), evidence_records, item_id, version_id, location, "review", version_roles, errors)
        if any(
            workstream.get("applicability") == "complete"
            for workstream in item.get("workstreams", [])
            if isinstance(workstream, Mapping)
        ) and not any(record.get("evidence_type") == "inspection" for record in review_evidence):
            errors.append(f"{location}.workstreams: complete requires inspection evidence for the current version")
        review_status = item.get("review_status")
        if review_status in {"candidate", "changes-requested"} and (
            version_id not in versions or "output" not in version_roles.get(version_id, set())
        ):
            errors.append(f"{location}.review_status: {review_status} requires a known current output version")
        if review_status == "approved":
            kinds = {record.get("evidence_type") for record in review_evidence}
            if version_id not in versions or not {"inspection", "human-approval"} <= kinds:
                errors.append(f"{location}.review_status: approved requires inspection and human-approval evidence for current version {version_id}")
        delivery = item.get("delivery")
        if isinstance(delivery, Mapping):
            target_id = delivery.get("target_id")
            if target_id is not None and target_id not in targets:
                errors.append(f"{location}.delivery.target_id: unknown delivery target ID {target_id}")
            delivery_evidence = _bound_evidence(delivery.get("evidence_ids", []), evidence_records, item_id, version_id, f"{location}.delivery", "delivery", version_roles, errors)
        if isinstance(delivery, Mapping) and delivery.get("status") == "verified":
            target_id = delivery.get("target_id")
            if target_id not in targets:
                errors.append(f"{location}.delivery.target_id: verified delivery requires a declared target")
            if "delivery-verification" not in {record.get("evidence_type") for record in delivery_evidence}:
                errors.append(f"{location}.delivery.evidence_ids: verified delivery requires delivery-verification evidence for the exact item and current version")
            for record in delivery_evidence:
                if record.get("evidence_type") == "delivery-verification" and record.get("target_id") != target_id:
                    errors.append(f"{location}.delivery.evidence_ids: delivery-verification evidence does not attest exact delivery target {target_id}")
    for dependency_id, dependency in dependency_records.items():
        downstream = item_records.get(dependency.get("downstream_item_id"))
        if downstream is not None and dependency_id not in downstream.get("dependency_ids", []):
            errors.append(f"dependencies: {dependency_id} is missing from downstream item {dependency.get('downstream_item_id')}")
    return errors


def _registry(records: Any, key: str, pattern: str, label: str, expected: str, errors: list[str]) -> set[str]:
    result: set[str] = set()
    for index, record in enumerate(records if isinstance(records, list) else []):
        if not isinstance(record, Mapping) or not isinstance(record.get(key), str):
            continue
        value = record[key]
        if value in result:
            errors.append(f"source_context.{index}.{key}: duplicate {label} {value}")
        result.add(value)
        if re.fullmatch(pattern, value) is None:
            errors.append(f"source_context.{index}.{key}: {label} {value!r} must match {expected}")
    return result


def _unknown(values: Any, known: set[str], location: str, label: str, errors: list[str]) -> None:
    for value in values if isinstance(values, list) else []:
        if isinstance(value, str) and value not in known:
            errors.append(f"{location}: unknown {label} ID {value}")


def _bound_evidence(ids: Any, records: Mapping[str, Mapping[str, Any]], item_id: Any, version_id: Any, location: str, purpose: str, version_roles: Mapping[str, set[str]], errors: list[str]) -> list[Mapping[str, Any]]:
    bound: list[Mapping[str, Any]] = []
    for evidence_id in ids if isinstance(ids, list) else []:
        record = records.get(evidence_id) if isinstance(evidence_id, str) else None
        if record is None:
            errors.append(f"{location}: unknown evidence ID {evidence_id}")
        elif record.get("item_id") != item_id or record.get("version_id") != version_id:
            errors.append(f"{location}: evidence {evidence_id} does not attest exact item and current version")
        elif "output" not in version_roles.get(record.get("version_id"), set()):
            errors.append(f"{location}: {purpose} evidence {evidence_id} must attest a media version with the output role")
        else:
            bound.append(record)
    return bound


def _has_cycle(graph: Mapping[str, set[str]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(next_node) for next_node in graph[node]):
            return True
        visiting.remove(node)
        visited.add(node)
        return False
    return any(visit(node) for node in graph)

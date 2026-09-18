"""Semantic validation for source-, value-, and version-bound color plans."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


_POSITIVE = r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"


def validate_color_plan_contract(payload: Mapping[str, Any]) -> list[str]:
    """Validate ownership, references, metadata declarations, and approvals."""
    errors: list[str] = []
    project_id, unit_id = payload.get("project_id"), payload.get("unit_id")
    if not isinstance(project_id, str) or not isinstance(unit_id, str):
        return errors
    if re.fullmatch(rf"{re.escape(project_id)}-(?:U|E)(?:0[1-9]|[1-9][0-9])", unit_id) is None:
        errors.append(f"unit_id: {unit_id!r} must match declared project {project_id} as {project_id}-U## or {project_id}-E##")
    context, items = payload.get("source_context"), payload.get("items")
    if not isinstance(context, Mapping) or not isinstance(items, list):
        return errors

    segments = _registry(context.get("edit_segments"), "segment_id", rf"{re.escape(unit_id)}-ED{_POSITIVE}", "edit segment ID", f"{unit_id}-ED###", errors)
    vfx_items = _registry(context.get("vfx_items"), "item_id", rf"{re.escape(unit_id)}-FX{_POSITIVE}", "VFX post item ID", f"{unit_id}-FX###", errors)
    media_records = context.get("media_versions")
    versions = _registry(media_records, "version_id", rf"{re.escape(project_id)}-MD{_POSITIVE}-v[0-9]{{3,}}", "media version ID", f"{project_id}-MD###-v###", errors)
    version_roles: dict[str, set[str]] = {}
    version_segments: dict[str, set[str]] = {}
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
            version_segments[version_id] = set(record.get("segment_ids", []))
        _unknown(record.get("segment_ids", []), segments, f"source_context.media_versions.{index}.segment_ids", "edit segment", errors)

    metadata_records: dict[str, Mapping[str, Any]] = {}
    for index, record in enumerate(context.get("metadata_records", [])):
        if not isinstance(record, Mapping):
            continue
        metadata_id = record.get("metadata_id")
        if isinstance(metadata_id, str):
            if metadata_id in metadata_records:
                errors.append(f"source_context.metadata_records.{index}.metadata_id: duplicate metadata ID {metadata_id}")
            metadata_records[metadata_id] = record
            if re.fullmatch(rf"{re.escape(project_id)}-CM{_POSITIVE}", metadata_id) is None:
                errors.append(f"source_context.metadata_records.{index}.metadata_id: metadata ID {metadata_id!r} must match {project_id}-CM###")
        if record.get("segment_id") not in segments:
            errors.append(f"source_context.metadata_records.{index}.segment_id: unknown edit segment ID {record.get('segment_id')}")
        if record.get("version_id") not in versions:
            errors.append(f"source_context.metadata_records.{index}.version_id: unknown media version ID {record.get('version_id')}")
        elif record.get("segment_id") not in version_segments.get(record.get("version_id"), set()):
            errors.append(f"source_context.metadata_records.{index}.segment_id: edit segment {record.get('segment_id')} is not covered by media version {record.get('version_id')}")

    item_records: dict[str, Mapping[str, Any]] = {}
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            continue
        item_id = item.get("item_id")
        if isinstance(item_id, str):
            if item_id in item_records:
                errors.append(f"items.{index}.item_id: duplicate color item ID {item_id}")
            item_records[item_id] = item
            if re.fullmatch(rf"{re.escape(unit_id)}-CL{_POSITIVE}", item_id) is None:
                errors.append(f"items.{index}.item_id: color item ID {item_id!r} must match {unit_id}-CL###")

    evidence_records: dict[str, Mapping[str, Any]] = {}
    for index, record in enumerate(context.get("evidence", [])):
        if not isinstance(record, Mapping):
            continue
        evidence_id = record.get("evidence_id")
        if isinstance(evidence_id, str):
            if evidence_id in evidence_records:
                errors.append(f"source_context.evidence.{index}.evidence_id: duplicate evidence ID {evidence_id}")
            evidence_records[evidence_id] = record
            if re.fullmatch(rf"{re.escape(project_id)}-CE{_POSITIVE}", evidence_id) is None:
                errors.append(f"source_context.evidence.{index}.evidence_id: evidence ID {evidence_id!r} must match {project_id}-CE###")
        if record.get("item_id") not in item_records:
            errors.append(f"source_context.evidence.{index}.item_id: unknown color item ID {record.get('item_id')}")
        if record.get("version_id") not in versions:
            errors.append(f"source_context.evidence.{index}.version_id: unknown media version ID {record.get('version_id')}")
        _unknown(record.get("segment_ids", []), segments, f"source_context.evidence.{index}.segment_ids", "edit segment", errors)
        item = item_records.get(record.get("item_id"))
        if item is not None:
            item_segments = set(item.get("edit_segment_ids", []))
            evidence_segments = set(record.get("segment_ids", []))
            if evidence_segments != item_segments:
                errors.append(f"source_context.evidence.{index}.segment_ids: evidence must attest the complete target item segment set")
            version_id = record.get("version_id")
            if version_id in versions and not item_segments <= version_segments.get(version_id, set()):
                errors.append(f"source_context.evidence.{index}.version_id: media version {version_id} does not cover the complete target item segment set")
            if record.get("claim") == "observed-input" and version_id not in item.get("source_version_ids", []):
                errors.append(f"source_context.evidence.{index}.version_id: observed-input evidence requires an item source version")
            if record.get("claim") in {"shot-match", "display-review", "approval"} and version_id != item.get("graded_version_id"):
                errors.append(f"source_context.evidence.{index}.version_id: {record.get('claim')} evidence requires the item's graded-output version")

    targets = _registry(payload.get("display_targets"), "target_id", rf"{re.escape(project_id)}-DT{_POSITIVE}", "display target ID", f"{project_id}-DT###", errors)
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            continue
        location, item_id = f"items.{index}", item.get("item_id")
        segment_ids = item.get("edit_segment_ids", [])
        _unknown(segment_ids, segments, f"{location}.edit_segment_ids", "edit segment", errors)
        _unknown(item.get("vfx_item_ids", []), vfx_items, f"{location}.vfx_item_ids", "VFX post item", errors)
        _unknown(item.get("source_version_ids", []), versions, f"{location}.source_version_ids", "source media version", errors)
        for source_version_id in item.get("source_version_ids", []):
            if source_version_id in versions and not version_roles.get(source_version_id, set()) & {"source", "vfx-source"}:
                errors.append(f"{location}.source_version_ids: media version {source_version_id} requires a source-capable role")
        graded_version = item.get("graded_version_id")
        if graded_version is not None and graded_version not in versions:
            errors.append(f"{location}.graded_version_id: unknown graded media version ID {graded_version}")
        elif graded_version is not None and "graded-output" not in version_roles.get(graded_version, set()):
            errors.append(f"{location}.graded_version_id: graded media version {graded_version} requires graded-output role")
        _unknown(item.get("display_target_ids", []), targets, f"{location}.display_target_ids", "display target", errors)
        input_encoding = item.get("input_encoding")
        if isinstance(input_encoding, Mapping):
            metadata_ids = input_encoding.get("metadata_record_ids", [])
            for metadata_id in metadata_ids if isinstance(metadata_ids, list) else []:
                if metadata_id not in metadata_records:
                    errors.append(f"{location}.input_encoding.metadata_record_ids: unknown metadata ID {metadata_id}")
            if input_encoding.get("state") == "declared":
                source_version_ids = item.get("source_version_ids", [])
                applicable_pairs = [
                    (source_version_id, segment_id)
                    for source_version_id in source_version_ids
                    for segment_id in set(segment_ids if isinstance(segment_ids, list) else []) & version_segments.get(source_version_id, set())
                ]
                if not applicable_pairs:
                    errors.append(f"{location}.input_encoding: declared input encoding requires an applicable source version")
                for source_version_id, segment_id in applicable_pairs:
                    matching = [metadata_records[mid] for mid in metadata_ids if mid in metadata_records and metadata_records[mid].get("segment_id") == segment_id and metadata_records[mid].get("version_id") == source_version_id]
                    if not matching:
                        errors.append(f"{location}.input_encoding: declared input encoding lacks applicable metadata for {segment_id} and {source_version_id}")
                    elif not any(record.get("field") == "input-encoding" and record.get("value") == input_encoding.get("value") for record in matching):
                        errors.append(f"{location}.input_encoding: metadata for {segment_id} does not attest exact input-encoding value and source version")
        bound = _bound_evidence(item.get("evidence_ids", []), evidence_records, item_id, segment_ids, graded_version, location, errors)
        observation = item.get("observed_input")
        if isinstance(observation, Mapping):
            findings = observation.get("findings", [])
            source_version = observation.get("source_version_id")
            if source_version is not None and source_version not in item.get("source_version_ids", []):
                errors.append(f"{location}.observed_input.source_version_id: unknown item source media version ID {source_version}")
            observation_bound = _bound_evidence(observation.get("evidence_ids", []), evidence_records, item_id, segment_ids, source_version, f"{location}.observed_input", errors)
            if observation.get("state") == "uninspected" and findings:
                errors.append(f"{location}.observed_input: uninspected input cannot contain findings")
            inspection_values = {record.get("value") for record in observation_bound if record.get("evidence_type") == "inspection" and record.get("claim") == "observed-input"}
            if observation.get("state") == "inspected" and (not findings or source_version is None or not inspection_values):
                errors.append(f"{location}.observed_input: observed input requires inspection evidence for exact item, segments, and source version")
            for finding in findings if isinstance(findings, list) else []:
                if observation.get("state") == "inspected" and finding not in inspection_values:
                    errors.append(f"{location}.observed_input: finding lacks exact source-version inspection evidence: {finding}")
        if item.get("match_state") == "approved" and not any(record.get("evidence_type") == "inspection" and record.get("claim") == "shot-match" for record in bound):
            errors.append(f"{location}.match_state: approved match requires inspection evidence for exact item, segments, and graded version")
        approval = item.get("approval")
        if isinstance(approval, Mapping):
            approval_bound = _bound_evidence(approval.get("evidence_ids", []), evidence_records, item_id, segment_ids, graded_version, f"{location}.approval", errors)
            if approval.get("state") == "approved":
                inspections = {r.get("value") for r in approval_bound if r.get("evidence_type") == "inspection" and r.get("claim") == "shot-match"}
                approvals = {r.get("value") for r in approval_bound if r.get("evidence_type") == "human-approval" and r.get("claim") == "approval"}
                if not inspections or not approvals or inspections.isdisjoint(approvals):
                    errors.append(f"{location}.approval: approval evidence requires inspection and human approval with the same claimed value")
    return errors


def _registry(records: Any, key: str, pattern: str, label: str, expected: str, errors: list[str]) -> set[str]:
    result: set[str] = set()
    for index, record in enumerate(records if isinstance(records, list) else []):
        if not isinstance(record, Mapping) or not isinstance(record.get(key), str):
            continue
        value = record[key]
        if value in result:
            errors.append(f"registry.{index}.{key}: duplicate {label} {value}")
        result.add(value)
        if re.fullmatch(pattern, value) is None:
            errors.append(f"registry.{index}.{key}: {label} {value!r} must match {expected}")
    return result


def _unknown(values: Any, known: set[str], location: str, label: str, errors: list[str]) -> None:
    for value in values if isinstance(values, list) else []:
        if isinstance(value, str) and value not in known:
            errors.append(f"{location}: unknown {label} ID {value}")


def _bound_evidence(ids: Any, records: Mapping[str, Mapping[str, Any]], item_id: Any, segment_ids: Any, version_id: Any, location: str, errors: list[str]) -> list[Mapping[str, Any]]:
    bound: list[Mapping[str, Any]] = []
    for evidence_id in ids if isinstance(ids, list) else []:
        record = records.get(evidence_id) if isinstance(evidence_id, str) else None
        if record is None:
            errors.append(f"{location}: unknown evidence ID {evidence_id}")
        elif record.get("item_id") != item_id or set(record.get("segment_ids", [])) != set(segment_ids if isinstance(segment_ids, list) else []) or record.get("version_id") != version_id:
            errors.append(f"{location}: evidence {evidence_id} does not attest exact item, segments, and graded version")
        else:
            bound.append(record)
    return bound

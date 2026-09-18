"""Semantic validation for source- and edit-bound titles and captions plans."""

from __future__ import annotations

import re
from collections.abc import Mapping
from fractions import Fraction
from typing import Any


_POSITIVE = r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"


def validate_titles_captions_plan_contract(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    project, unit = payload.get("project_id"), payload.get("unit_id")
    if not isinstance(project, str) or not isinstance(unit, str):
        return errors
    if re.fullmatch(rf"{re.escape(project)}-(?:U|E)(?:0[1-9]|[1-9][0-9])", unit) is None:
        errors.append(f"unit_id: {unit!r} must belong to project {project}")
    context, items_value = payload.get("source_context"), payload.get("items")
    if not isinstance(context, Mapping) or not isinstance(items_value, list):
        return errors

    segments = _registry(context.get("edit_segments"), "segment_id", rf"{re.escape(unit)}-ED{_POSITIVE}", f"{unit}-ED###", "edit segment", errors)
    items = _registry(items_value, "item_id", rf"{re.escape(unit)}-TT{_POSITIVE}", f"{unit}-TT###", "titles/captions item", errors)
    sources = _registry(context.get("text_sources"), "text_source_id", rf"{re.escape(project)}-TS{_POSITIVE}", f"{project}-TS###", "text source", errors)
    versions = _registry(context.get("edit_versions"), "edit_version_id", rf"{re.escape(project)}-EV{_POSITIVE}", f"{project}-EV###", "edit version", errors)
    timings = _registry(context.get("timing_records"), "timing_record_id", rf"{re.escape(project)}-TM{_POSITIVE}", f"{project}-TM###", "timing record", errors)
    evidence = _registry(context.get("evidence"), "evidence_id", rf"{re.escape(project)}-TE{_POSITIVE}", f"{project}-TE###", "evidence", errors)

    version_segments: dict[str, set[str]] = {}
    for index, record in enumerate(context.get("edit_versions", [])):
        if not isinstance(record, Mapping):
            continue
        version_id = record.get("edit_version_id")
        if re.fullmatch(rf"{re.escape(project)}-LK{_POSITIVE}", str(record.get("lock_decision_id"))) is None:
            errors.append(f"source_context.edit_versions.{index}.lock_decision_id: lock decision ID must match {project}-LK###")
        segment_ids = set(record.get("segment_ids", []))
        _unknown(segment_ids, segments, f"source_context.edit_versions.{index}.segment_ids", "edit segment", errors)
        if isinstance(version_id, str):
            version_segments[version_id] = segment_ids

    source_records = {r["text_source_id"]: r for r in context.get("text_sources", []) if isinstance(r, Mapping) and isinstance(r.get("text_source_id"), str)}
    item_records = {r["item_id"]: r for r in items_value if isinstance(r, Mapping) and isinstance(r.get("item_id"), str)}
    timing_records = {r["timing_record_id"]: r for r in context.get("timing_records", []) if isinstance(r, Mapping) and isinstance(r.get("timing_record_id"), str)}
    evidence_records = {r["evidence_id"]: r for r in context.get("evidence", []) if isinstance(r, Mapping) and isinstance(r.get("evidence_id"), str)}

    for index, record in enumerate(context.get("timing_records", [])):
        if not isinstance(record, Mapping):
            continue
        location = f"source_context.timing_records.{index}"
        _known(record.get("item_id"), items, location + ".item_id", "titles/captions item", errors)
        _known(record.get("segment_id"), segments, location + ".segment_id", "edit segment", errors)
        _known(record.get("edit_version_id"), versions, location + ".edit_version_id", "edit version", errors)
        item = item_records.get(record.get("item_id"))
        if item is not None and record.get("segment_id") != item.get("edit_segment_id"):
            errors.append(f"{location}.segment_id: timing record must match its target item's edit segment")
        if record.get("edit_version_id") in version_segments and record.get("segment_id") not in version_segments[record.get("edit_version_id")]:
            errors.append(f"{location}.segment_id: edit version does not cover edit segment")
        if record.get("coordinate_space") != "output-timeline":
            errors.append(f"{location}.coordinate_space: exact cue timing must use output-timeline coordinates, not source-media timecode")
        if isinstance(record.get("start_frame"), int) and isinstance(record.get("end_frame"), int) and record["start_frame"] >= record["end_frame"]:
            errors.append(f"{location}: exact timing requires ordered bounds")
        _check_timecodes(record, location, errors)

    for index, record in enumerate(context.get("evidence", [])):
        if not isinstance(record, Mapping):
            continue
        location = f"source_context.evidence.{index}"
        _known(record.get("item_id"), items, location + ".item_id", "titles/captions item", errors)
        _known(record.get("segment_id"), segments, location + ".segment_id", "edit segment", errors)
        _known(record.get("edit_version_id"), versions, location + ".edit_version_id", "edit version", errors)
        _known(record.get("timing_record_id"), timings, location + ".timing_record_id", "timing record", errors)
        item = item_records.get(record.get("item_id"))
        timing = timing_records.get(record.get("timing_record_id"))
        if item is not None and not _evidence_matches(record, item, timing, source_records):
            errors.append(f"{location}: evidence must attest exact current item content, revision, placement, timing, segment, and edit version")
        expected_claim = "current-item-review" if record.get("evidence_type") == "review" else "approval"
        if record.get("claim") != expected_claim:
            errors.append(f"{location}.claim: evidence type requires claim {expected_claim}")

    for index, item in enumerate(items_value):
        if not isinstance(item, Mapping):
            continue
        location = f"items.{index}"
        _known(item.get("edit_segment_id"), segments, location + ".edit_segment_id", "edit segment", errors)
        item_type, text = item.get("type"), item.get("text")
        if item_type in {"subtitle", "accessibility-caption"} and not item.get("language"):
            errors.append(f"{location}.language: caption or subtitle requires a language")
        if isinstance(text, Mapping):
            source_id = text.get("text_source_id")
            content_kind = text.get("content_kind")
            allowed_kinds = {
                "main-title": {"title"}, "intertitle": {"title"}, "lower-third": {"title"},
                "credit": {"credit"}, "subtitle": {"dialogue"},
                "accessibility-caption": {"dialogue", "nonspeech"},
            }
            if content_kind not in allowed_kinds.get(item_type, set()):
                errors.append(f"{location}.text.content_kind: content kind is incompatible with item type {item_type}")
            _known(source_id, sources, location + ".text.text_source_id", "text source", errors)
            if item_type in {"subtitle", "accessibility-caption"} and content_kind == "dialogue" and (source_id not in sources or source_records.get(source_id, {}).get("kind") != "supplied-dialogue"):
                errors.append(f"{location}.text.text_source_id: dialogue caption requires a supplied-dialogue source reference")
            if content_kind == "nonspeech" and (item_type != "accessibility-caption" or text.get("state") != "proposed" or source_records.get(source_id, {}).get("kind") != "editorial-proposal"):
                errors.append(f"{location}.text: nonspeech caption requires proposed text with an editorial-proposal source reference")
            if text.get("state") == "supplied":
                if source_id not in sources:
                    errors.append(f"{location}.text.text_source_id: supplied text requires a resolved source reference")
                elif text.get("content") != source_records[source_id].get("text"):
                    errors.append(f"{location}.text.content: supplied content must equal its supplied text source")
        placement = item.get("placement")
        if isinstance(placement, Mapping) and placement.get("safe_area_state") == "exception" and not placement.get("exception_rationale"):
            errors.append(f"{location}.placement.exception_rationale: unsafe placement exception requires an exception rationale")
        timing = item.get("timing")
        if isinstance(timing, Mapping):
            timing_id = timing.get("timing_record_id")
            if timing.get("mode") == "creative-intent" and timing_id is not None:
                errors.append(f"{location}.timing: creative timing intent cannot cite exact timing metadata")
            if timing.get("mode") == "exact-supplied":
                record = timing_records.get(timing_id)
                if record is None or record.get("item_id") != item.get("item_id") or record.get("segment_id") != item.get("edit_segment_id") or record.get("edit_version_id") not in versions or record.get("coordinate_space") != "output-timeline":
                    errors.append(f"{location}.timing: exact timing requires applicable current locked-edit output-timeline metadata for the same item and segment")
        approval = item.get("approval")
        if isinstance(approval, Mapping):
            bound = []
            for evidence_id in approval.get("evidence_ids", []):
                record = evidence_records.get(evidence_id)
                if record is None:
                    errors.append(f"{location}.approval: unknown evidence ID {evidence_id}")
                elif _evidence_matches(record, item, timing_records.get(record.get("timing_record_id")), source_records):
                    bound.append(record)
                else:
                    errors.append(f"{location}.approval: evidence {evidence_id} does not bind the exact current item")
            if approval.get("state") == "approved":
                reviews = {r.get("decision_value") for r in bound if r.get("evidence_type") == "review" and r.get("claim") == "current-item-review"}
                approvals = {r.get("decision_value") for r in bound if r.get("evidence_type") == "human-approval" and r.get("claim") == "approval"}
                if not reviews or not approvals or reviews.isdisjoint(approvals):
                    errors.append(f"{location}.approval: final approval requires current review and human approval evidence with the same decision value")
    return errors


def _registry(records: Any, key: str, pattern: str, expected: str, label: str, errors: list[str]) -> set[str]:
    result: set[str] = set()
    for index, record in enumerate(records if isinstance(records, list) else []):
        if not isinstance(record, Mapping) or not isinstance(record.get(key), str):
            continue
        value = record[key]
        if value in result:
            errors.append(f"registry.{index}.{key}: duplicate {label} ID {value}")
        result.add(value)
        if re.fullmatch(pattern, value) is None:
            errors.append(f"registry.{index}.{key}: {label} ID {value!r} must match {expected}")
    return result


def _unknown(values: Any, known: set[str], location: str, label: str, errors: list[str]) -> None:
    for value in values if isinstance(values, (list, set)) else []:
        _known(value, known, location, label, errors)


def _known(value: Any, known: set[str], location: str, label: str, errors: list[str]) -> None:
    if isinstance(value, str) and value not in known:
        errors.append(f"{location}: unknown {label} ID {value}")


def _evidence_matches(record: Mapping[str, Any], item: Mapping[str, Any], timing: Mapping[str, Any] | None, sources: Mapping[str, Mapping[str, Any]]) -> bool:
    text, placement, item_timing = item.get("text"), item.get("placement"), item.get("timing")
    return isinstance(text, Mapping) and isinstance(placement, Mapping) and isinstance(item_timing, Mapping) and timing is not None and record.get("item_id") == item.get("item_id") and record.get("segment_id") == item.get("edit_segment_id") and record.get("revision") == item.get("revision") and record.get("content") == text.get("content") and record.get("content_kind") == text.get("content_kind") and record.get("text_state") == text.get("state") and record.get("text_source") == sources.get(text.get("text_source_id")) and record.get("language") == item.get("language") and record.get("speaker_identification") == item.get("speaker_identification") and record.get("sound_description") == item.get("sound_description") and record.get("placement_region") == placement.get("region") and record.get("timing_record_id") == item_timing.get("timing_record_id") and timing.get("item_id") == item.get("item_id") and timing.get("segment_id") == item.get("edit_segment_id") and timing.get("edit_version_id") == record.get("edit_version_id")


def _check_timecodes(record: Mapping[str, Any], location: str, errors: list[str]) -> None:
    timebase = record.get("timebase")
    if not isinstance(timebase, Mapping):
        return
    try:
        fps = Fraction(str(timebase.get("frames_per_second")))
    except (ValueError, ZeroDivisionError):
        return
    if fps.denominator != 1 or timebase.get("drop_frame"):
        return
    nominal = fps.numerator
    for frame_key, tc_key in (("start_frame", "start_timecode"), ("end_frame", "end_timecode")):
        frame, tc = record.get(frame_key), record.get(tc_key)
        if not isinstance(frame, int) or not isinstance(tc, str):
            continue
        match = re.fullmatch(r"([0-9]{2,}):([0-5][0-9]):([0-5][0-9])[=:;]([0-9]{2})", tc)
        if match:
            h, m, s, f = map(int, match.groups())
            if f >= nominal:
                errors.append(f"{location}.{tc_key}: frame component must be less than nominal frames per second")
            elif ((h * 3600 + m * 60 + s) * nominal + f) != frame:
                errors.append(f"{location}.{tc_key}: timecode does not match {frame_key} at declared timebase")

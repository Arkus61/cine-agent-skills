"""Semantic validation for source-bound film edit plans."""

from __future__ import annotations

import re
from collections.abc import Iterator, Mapping
from typing import Any


_POSITIVE_ID = r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
_POSITIVE_PAIR = r"(?:0[1-9]|[1-9][0-9])"
_TIMECODE = re.compile(
    r"(?<![0-9])(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]:[0-9]{2,3}(?![0-9])"
)


def _references(
    errors: list[str],
    item: Mapping[str, Any],
    location: str,
    field: str,
    declared: set[str],
    label: str,
) -> None:
    values = item.get(field)
    if not isinstance(values, list):
        return
    for value_index, value in enumerate(values):
        if isinstance(value, str) and value not in declared:
            errors.append(
                f"{location}.{field}.{value_index}: unknown {label} ID {value}"
            )


def _prose_timecodes(value: Any, location: str) -> Iterator[tuple[str, str]]:
    if isinstance(value, str):
        for match in _TIMECODE.finditer(value):
            yield location, match.group(0)
        return
    if isinstance(value, list):
        for value_index, item in enumerate(value):
            yield from _prose_timecodes(item, f"{location}.{value_index}")
        return
    if isinstance(value, Mapping):
        for field, item in value.items():
            if field in {"exact_source_in", "exact_source_out"}:
                continue
            yield from _prose_timecodes(item, f"{location}.{field}")


def validate_edit_plan_contract(payload: Mapping[str, Any]) -> list[str]:
    """Validate edit-plan identity, references, order, and evidence gates."""
    errors: list[str] = []
    project_id = payload.get("project_id")
    unit_id = payload.get("unit_id")
    if not isinstance(project_id, str) or not isinstance(unit_id, str):
        return errors

    unit_pattern = re.compile(rf"{re.escape(project_id)}-(?:U|E){_POSITIVE_PAIR}")
    if unit_pattern.fullmatch(unit_id) is None:
        errors.append(
            f"unit_id: {unit_id!r} must match declared project {project_id} "
            f"as {project_id}-U## or {project_id}-E##"
        )

    scene_suffix = rf"(?:S{_POSITIVE_PAIR}|SC{_POSITIVE_ID})"
    scene_pattern = re.compile(rf"{re.escape(unit_id)}-{scene_suffix}")
    shot_pattern = re.compile(
        rf"{re.escape(unit_id)}-{scene_suffix}-SH{_POSITIVE_ID}"
    )
    media_pattern = re.compile(rf"{re.escape(project_id)}-MD{_POSITIVE_ID}")
    timing_pattern = re.compile(rf"{re.escape(project_id)}-TM{_POSITIVE_ID}")
    lock_pattern = re.compile(rf"{re.escape(project_id)}-LK{_POSITIVE_ID}")

    source_context = payload.get("source_context")
    shots_value = source_context.get("shots") if isinstance(source_context, Mapping) else None
    media_value = (
        source_context.get("media_items") if isinstance(source_context, Mapping) else None
    )
    timing_value = (
        source_context.get("timing_evidence")
        if isinstance(source_context, Mapping)
        else None
    )
    lock_value = (
        source_context.get("lock_decisions")
        if isinstance(source_context, Mapping)
        else None
    )

    shot_ids: set[str] = set()
    if isinstance(shots_value, list):
        for shot_index, shot in enumerate(shots_value):
            if not isinstance(shot, Mapping):
                continue
            shot_id = shot.get("shot_id")
            scene_id = shot.get("scene_id")
            if isinstance(shot_id, str):
                if shot_id in shot_ids:
                    errors.append(
                        f"source_context.shots.{shot_index}.shot_id: "
                        f"duplicate supplied shot ID {shot_id}"
                    )
                else:
                    shot_ids.add(shot_id)
                if shot_pattern.fullmatch(shot_id) is None:
                    errors.append(
                        f"source_context.shots.{shot_index}.shot_id: {shot_id!r} "
                        f"must match {unit_id}-S##-SH###"
                    )
            if isinstance(scene_id, str):
                if scene_pattern.fullmatch(scene_id) is None:
                    errors.append(
                        f"source_context.shots.{shot_index}.scene_id: {scene_id!r} "
                        f"must belong to unit {unit_id}"
                    )
                if isinstance(shot_id, str) and re.fullmatch(
                    rf"{re.escape(scene_id)}-SH{_POSITIVE_ID}", shot_id
                ) is None:
                    errors.append(
                        f"source_context.shots.{shot_index}.shot_id: {shot_id} "
                        f"does not match declared scene {scene_id}"
                    )

    media_ids: set[str] = set()
    media_to_shot: dict[str, str] = {}
    media_status: dict[str, str] = {}
    if isinstance(media_value, list):
        for media_index, media in enumerate(media_value):
            if not isinstance(media, Mapping):
                continue
            media_id = media.get("media_id")
            shot_id = media.get("shot_id")
            review_status = media.get("review_status")
            if isinstance(media_id, str):
                if media_id in media_ids:
                    errors.append(
                        f"source_context.media_items.{media_index}.media_id: "
                        f"duplicate supplied media ID {media_id}"
                    )
                else:
                    media_ids.add(media_id)
                if media_pattern.fullmatch(media_id) is None:
                    errors.append(
                        f"source_context.media_items.{media_index}.media_id: "
                        f"{media_id!r} must match {project_id}-MD###"
                    )
                if isinstance(shot_id, str):
                    media_to_shot[media_id] = shot_id
                if isinstance(review_status, str):
                    media_status[media_id] = review_status
            if isinstance(shot_id, str) and shot_id not in shot_ids:
                errors.append(
                    f"source_context.media_items.{media_index}.shot_id: "
                    f"unknown shot ID {shot_id}"
                )

    timing_records: dict[str, Mapping[str, Any]] = {}
    if isinstance(timing_value, list):
        for timing_index, timing in enumerate(timing_value):
            if not isinstance(timing, Mapping):
                continue
            timing_id = timing.get("timing_evidence_id")
            media_id = timing.get("media_id")
            if isinstance(timing_id, str):
                if timing_id in timing_records:
                    errors.append(
                        f"source_context.timing_evidence.{timing_index}."
                        f"timing_evidence_id: duplicate timing evidence ID {timing_id}"
                    )
                else:
                    timing_records[timing_id] = timing
                if timing_pattern.fullmatch(timing_id) is None:
                    errors.append(
                        f"source_context.timing_evidence.{timing_index}."
                        f"timing_evidence_id: {timing_id!r} must match "
                        f"{project_id}-TM###"
                    )
            if isinstance(media_id, str) and media_id not in media_ids:
                errors.append(
                    f"source_context.timing_evidence.{timing_index}.media_id: "
                    f"unknown media ID {media_id}"
                )

    lock_records: dict[str, Mapping[str, Any]] = {}
    if isinstance(lock_value, list):
        for lock_index, lock in enumerate(lock_value):
            if not isinstance(lock, Mapping):
                continue
            lock_id = lock.get("lock_decision_id")
            if isinstance(lock_id, str):
                if lock_id in lock_records:
                    errors.append(
                        f"source_context.lock_decisions.{lock_index}.lock_decision_id: "
                        f"duplicate lock decision ID {lock_id}"
                    )
                else:
                    lock_records[lock_id] = lock
                if lock_pattern.fullmatch(lock_id) is None:
                    errors.append(
                        f"source_context.lock_decisions.{lock_index}.lock_decision_id: "
                        f"{lock_id!r} must match {project_id}-LK###"
                    )
            _references(
                errors,
                lock,
                f"source_context.lock_decisions.{lock_index}",
                "source_media_ids",
                media_ids,
                "media",
            )

    segments = payload.get("segments")
    if not isinstance(segments, list):
        return errors

    segment_ids = {
        segment.get("segment_id")
        for segment in segments
        if isinstance(segment, Mapping) and isinstance(segment.get("segment_id"), str)
    }
    for lock_index, lock in enumerate(lock_value if isinstance(lock_value, list) else []):
        if not isinstance(lock, Mapping):
            continue
        segment_id = lock.get("segment_id")
        if isinstance(segment_id, str) and segment_id not in segment_ids:
            errors.append(
                f"source_context.lock_decisions.{lock_index}.segment_id: "
                f"unknown segment ID {segment_id}"
            )

    seen_segment_ids: set[str] = set()
    previous_order: int | None = None
    segment_pattern = re.compile(rf"{re.escape(unit_id)}-ED{_POSITIVE_ID}")
    for segment_index, segment in enumerate(segments):
        if not isinstance(segment, Mapping):
            continue
        location = f"segments.{segment_index}"
        segment_id = segment.get("segment_id")
        if isinstance(segment_id, str):
            if segment_id in seen_segment_ids:
                errors.append(f"{location}.segment_id: duplicate segment ID {segment_id}")
            else:
                seen_segment_ids.add(segment_id)
            if segment_pattern.fullmatch(segment_id) is None:
                errors.append(
                    f"{location}.segment_id: {segment_id!r} must match {unit_id}-ED###"
                )

        assembly_order = segment.get("assembly_order")
        if isinstance(assembly_order, int):
            if previous_order is not None and assembly_order <= previous_order:
                errors.append(
                    f"{location}.assembly_order: must be greater than the previous "
                    "assembly order"
                )
            previous_order = assembly_order

        _references(errors, segment, location, "source_shot_ids", shot_ids, "shot")
        _references(errors, segment, location, "source_media_ids", media_ids, "media")
        source_shot_values = segment.get("source_shot_ids")
        source_media_values = segment.get("source_media_ids")
        source_shot_set = (
            {value for value in source_shot_values if isinstance(value, str)}
            if isinstance(source_shot_values, list)
            else set()
        )
        source_media_set = (
            {value for value in source_media_values if isinstance(value, str)}
            if isinstance(source_media_values, list)
            else set()
        )
        if isinstance(source_media_values, list):
            for media_index, media_id in enumerate(source_media_values):
                linked_shot = media_to_shot.get(media_id) if isinstance(media_id, str) else None
                if linked_shot is not None and linked_shot not in source_shot_set:
                    errors.append(
                        f"{location}.source_media_ids.{media_index}: media ID {media_id} "
                        f"belongs to unreferenced shot {linked_shot}"
                    )

        alternatives = segment.get("alternatives")
        if isinstance(alternatives, list):
            for alternative_index, alternative in enumerate(alternatives):
                if not isinstance(alternative, Mapping):
                    continue
                alternative_location = f"{location}.alternatives.{alternative_index}"
                _references(
                    errors,
                    alternative,
                    alternative_location,
                    "source_shot_ids",
                    shot_ids,
                    "shot",
                )
                _references(
                    errors,
                    alternative,
                    alternative_location,
                    "source_media_ids",
                    media_ids,
                    "media",
                )
                alternative_shots = alternative.get("source_shot_ids")
                alternative_shot_set = (
                    {value for value in alternative_shots if isinstance(value, str)}
                    if isinstance(alternative_shots, list)
                    else set()
                )
                alternative_media = alternative.get("source_media_ids")
                if isinstance(alternative_media, list):
                    for media_index, media_id in enumerate(alternative_media):
                        linked_shot = (
                            media_to_shot.get(media_id)
                            if isinstance(media_id, str)
                            else None
                        )
                        if linked_shot is not None and linked_shot not in alternative_shot_set:
                            errors.append(
                                f"{alternative_location}.source_media_ids.{media_index}: "
                                f"media ID {media_id} belongs to unreferenced shot "
                                f"{linked_shot}"
                            )

        evidence_status = segment.get("evidence_status")
        if evidence_status == "inspected" and source_media_values == []:
            errors.append(
                f"{location}.evidence_status: inspected requires at least one "
                "source media ID"
            )

        in_out_intent = segment.get("in_out_intent")
        exact_in = (
            in_out_intent.get("exact_source_in")
            if isinstance(in_out_intent, Mapping)
            else None
        )
        exact_out = (
            in_out_intent.get("exact_source_out")
            if isinstance(in_out_intent, Mapping)
            else None
        )
        has_exact_boundaries = isinstance(exact_in, str) or isinstance(exact_out, str)
        timing_id = segment.get("timing_evidence_id")
        timing_record = timing_records.get(timing_id) if isinstance(timing_id, str) else None
        if evidence_status == "planned" and has_exact_boundaries:
            errors.append(
                f"{location}.in_out_intent: exact source timecodes require "
                "inspected evidence"
            )
        if has_exact_boundaries and not isinstance(timing_id, str):
            errors.append(
                f"{location}.in_out_intent: exact source timecodes require "
                "source-bound timing evidence"
            )
        if isinstance(timing_id, str) and timing_record is None:
            errors.append(f"{location}.timing_evidence_id: unknown timing evidence ID {timing_id}")
        if evidence_status == "planned" and isinstance(timing_id, str):
            errors.append(
                f"{location}.timing_evidence_id: planned segments cannot bind "
                "inspected timing evidence"
            )
        if timing_record is not None:
            timing_media_id = timing_record.get("media_id")
            if isinstance(timing_media_id, str) and timing_media_id not in source_media_set:
                errors.append(
                    f"{location}.timing_evidence_id: {timing_id} belongs to "
                    f"unreferenced media {timing_media_id}"
                )
            if has_exact_boundaries and (
                exact_in != timing_record.get("exact_source_in")
                or exact_out != timing_record.get("exact_source_out")
            ):
                errors.append(
                    f"{location}.timing_evidence_id: {timing_id} does not establish "
                    f"exact boundaries {exact_in}-{exact_out}"
                )

        established_timecodes = (
            {
                timing_record.get("exact_source_in"),
                timing_record.get("exact_source_out"),
            }
            if timing_record is not None
            else set()
        )
        for prose_location, timecode in _prose_timecodes(segment, location):
            if timing_record is None:
                errors.append(
                    f"{prose_location}: exact timecode {timecode} requires "
                    "applicable timing evidence"
                )
            elif timecode not in established_timecodes:
                errors.append(
                    f"{prose_location}: exact timecode {timecode} is not "
                    f"established by {timing_id}"
                )

        lock_status = segment.get("lock_status")
        lock_id = segment.get("lock_decision_id")
        lock_record = lock_records.get(lock_id) if isinstance(lock_id, str) else None
        if lock_status == "picture-locked" and evidence_status != "inspected":
            errors.append(
                f"{location}.lock_status: picture-locked requires inspected evidence"
            )
        if lock_status == "picture-locked" and not isinstance(lock_id, str):
            errors.append(
                f"{location}.lock_status: picture-locked requires a supplied "
                "current lock decision"
            )
        if isinstance(lock_id, str) and lock_record is None:
            errors.append(f"{location}.lock_decision_id: unknown lock decision ID {lock_id}")
        if lock_status != "picture-locked" and isinstance(lock_id, str):
            errors.append(
                f"{location}.lock_decision_id: lock decision requires "
                "lock_status picture-locked"
            )
        if lock_status == "picture-locked":
            for media_id in source_media_values if isinstance(source_media_values, list) else []:
                status = media_status.get(media_id) if isinstance(media_id, str) else None
                if status is not None and status != "approved":
                    errors.append(
                        f"{location}.lock_status: picture-locked requires approved "
                        f"source media; {media_id} is {status}"
                    )
            if lock_record is not None:
                if lock_record.get("segment_id") != segment_id:
                    errors.append(
                        f"{location}.lock_decision_id: {lock_id} must bind segment "
                        f"{segment_id}"
                    )
                decision_media = lock_record.get("source_media_ids")
                decision_media_set = (
                    {value for value in decision_media if isinstance(value, str)}
                    if isinstance(decision_media, list)
                    else set()
                )
                if decision_media_set != source_media_set:
                    errors.append(
                        f"{location}.lock_decision_id: {lock_id} must bind exactly "
                        "the segment source media IDs"
                    )

    return errors

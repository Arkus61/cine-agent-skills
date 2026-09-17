"""Semantic validation for source-bound sound post plans."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping
from typing import Any


_POSITIVE_ID = r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
_RESPONSIBILITIES = {
    "dialogue-edit", "repair", "adr", "foley", "ambience", "effects",
    "sound-design", "transition", "intentional-silence", "premix-group",
    "automation", "mix-priority", "accessibility", "loudness-assumption", "mastering",
}
_METRIC_CATEGORIES = {
    "integrated-loudness": "loudness", "short-term-loudness": "loudness",
    "momentary-loudness": "loudness", "true-peak": "peak", "sample-peak": "peak",
    "noise-floor": "noise", "dialogue-intelligibility": "intelligibility",
}
_INSPECTION_KINDS_BY_RESPONSIBILITY = {
    "dialogue-edit": {"audio"}, "repair": {"audio"}, "adr": {"audio"},
    "foley": {"audio", "picture"}, "ambience": {"audio", "picture"},
    "effects": {"audio", "picture"}, "sound-design": {"audio", "picture"},
    "transition": {"audio", "picture"}, "intentional-silence": {"audio", "picture"},
    "premix-group": {"audio", "mix-session"}, "automation": {"audio", "mix-session"},
    "mix-priority": {"audio", "mix-session"},
    "accessibility": {"audio", "picture", "transcript", "metadata"},
    "loudness-assumption": {"audio", "mix-session", "delivery-specification"},
    "mastering": {"mix-session", "delivery-specification"},
}
_PERSPECTIVE_MODES_BY_RESPONSIBILITY = {
    "dialogue-edit": {"dialogue-focus", "objective", "spatial-focus", "not-applicable-from-supplied-material"},
    "repair": {"dialogue-focus", "objective", "spatial-focus", "not-applicable-from-supplied-material"},
    "adr": {"dialogue-focus", "objective", "spatial-focus", "not-applicable-from-supplied-material"},
    "foley": {"objective", "subjective", "spatial-focus", "not-applicable-from-supplied-material"},
    "ambience": {"objective", "subjective", "spatial-focus", "not-applicable-from-supplied-material"},
    "effects": {"objective", "subjective", "spatial-focus", "not-applicable-from-supplied-material"},
    "sound-design": {"objective", "subjective", "spatial-focus", "not-applicable-from-supplied-material"},
    "transition": {"objective", "subjective", "spatial-focus", "not-applicable-from-supplied-material"},
    "intentional-silence": {"objective", "subjective", "spatial-focus", "not-applicable-from-supplied-material"},
    "premix-group": {"objective", "subjective", "spatial-focus", "dialogue-focus", "not-applicable-from-supplied-material"},
    "automation": {"objective", "subjective", "spatial-focus", "dialogue-focus", "not-applicable-from-supplied-material"},
    "mix-priority": {"objective", "subjective", "spatial-focus", "dialogue-focus", "not-applicable-from-supplied-material"},
    "accessibility": {"accessibility", "not-applicable-from-supplied-material"},
    "loudness-assumption": {"objective", "subjective", "spatial-focus", "dialogue-focus", "not-applicable-from-supplied-material"},
    "mastering": {"objective", "subjective", "spatial-focus", "dialogue-focus", "not-applicable-from-supplied-material"},
}
_PLACEHOLDER_ONLY_VALUES = {
    "tbd", "pending", "unknown", "na", "none", "tobedetermined", "notapplicable",
}
_MEASUREMENT_UNIT_SYNTAX = re.compile(
    r"(?<![A-Za-z0-9-])[+-]?\d+(?:\.\d+)?\s*(?:LUFS|LKFS|dBTP|dBFS|dBA|dB|kHz|Hz)(?![A-Za-z])",
    re.IGNORECASE,
)
_ASSERTIVE_PROHIBITED_CLAIM = re.compile(
    r"\b(?:was|were|is|are|has been|have been)\s+"
    r"(?:measured|metered|verified|approved|compliant|certified|mastered|delivered|"
    r"completed|finalized|signed off|inspected|reviewed)\b|"
    r"\b(?:approval|compliance|delivery)\s+(?:is\s+)?(?:confirmed|complete|approved)|"
    r"\b(?:final\s+)?master\s+(?:is\s+)?(?:complete|completed|delivered|approved|compliant)|"
    r"\bapproval\s+(?:received|obtained|confirmed)|"
    r"\b(?:mastering|master|delivery)\s+(?:complete|completed|sent|delivered|approved)|"
    r"\b(?:measured|metered|verified|approved|compliant|certified|mastered|delivered|completed|finalized)\b|"
    r"\b(?:QC|quality control)\s+(?:passed|pass)\b",
    re.IGNORECASE,
)
_SAFE_CLAIM_QUALIFIER = re.compile(
    r"\b(?:not|no|never|without|awaiting|pending|unmeasured|unresolved|unless|until|if|after|only after|remain(?:s)?)\b",
    re.IGNORECASE,
)
_CLAUSE_BOUNDARY = re.compile(
    r"[.;!?]+|[—–]|(?:,?\s+)\b(?:but|however|yet|although|while)\b\s*|"
    r"\s+\band\b\s+(?=(?:(?:the|a|an)\s+)?(?:final\s+)?"
    r"(?:master|delivery|approval|compliance|mastering|mix|audio|dialogue|loudness|measurement)\s+"
    r"(?:(?:was|were|is|are|has been|have been)\s+(?:measured|metered|verified|approved|"
    r"compliant|certified|mastered|delivered|completed|finalized)|"
    r"(?:received|complete|completed|sent|delivered|approved|compliant|measured|metered|"
    r"verified|mastered|finalized))\b)",
    re.IGNORECASE,
)
_LEADING_ADVERSATIVE_CLAUSE = re.compile(r"^\s*(?:although|while)\b[^,]*,\s*", re.IGNORECASE)
_PROVISIONAL_TARGET_LANGUAGE = re.compile(
    r"\b(?:provisional|target|assumed|assumption|conditional|if|unless|until|pending)\b",
    re.IGNORECASE,
)
_OBSERVED_VALUE_LANGUAGE = re.compile(
    r"\b(?:observed|actual|reading|readout|measured|metered)\b", re.IGNORECASE
)
_METRIC_PROSE_PATTERNS = {
    "integrated-loudness": re.compile(r"\bintegrated(?:[-\s]+loudness)?\b", re.IGNORECASE),
    "short-term-loudness": re.compile(r"\bshort[-\s]+term(?:[-\s]+loudness)?\b", re.IGNORECASE),
    "momentary-loudness": re.compile(r"\bmomentary(?:[-\s]+loudness)?\b", re.IGNORECASE),
    "true-peak": re.compile(r"\btrue[-\s]+peak\b", re.IGNORECASE),
    "sample-peak": re.compile(r"\bsample[-\s]+peak\b", re.IGNORECASE),
    "noise-floor": re.compile(r"\bnoise[-\s]+floor\b", re.IGNORECASE),
    "dialogue-intelligibility": re.compile(r"\bdialogue[-\s]+intelligibility\b", re.IGNORECASE),
}


def _is_placeholder_only(value: object) -> bool:
    if not isinstance(value, str):
        return False
    token = "".join(
        character
        for character in unicodedata.normalize("NFKC", value).casefold()
        if unicodedata.category(character)[0] not in {"P", "Z"}
    )
    return token in _PLACEHOLDER_ONLY_VALUES


def _has_assertive_prohibited_claim(value: str) -> bool:
    """Reject completed claims while retaining negative and conditional handoffs."""
    clauses: list[str] = []
    for clause in _CLAUSE_BOUNDARY.split(value):
        leading_adversative = _LEADING_ADVERSATIVE_CLAUSE.match(clause)
        if leading_adversative:
            clauses.extend((clause[:leading_adversative.end()], clause[leading_adversative.end():]))
        else:
            clauses.append(clause)
    for clause in clauses:
        if _SAFE_CLAIM_QUALIFIER.search(clause):
            continue
        if _ASSERTIVE_PROHIBITED_CLAIM.search(clause):
            return True
    return False


def validate_sound_post_plan_contract(payload: Mapping[str, Any]) -> list[str]:
    """Validate sound-post identity, evidence, coverage, and prohibited assertions."""
    errors: list[str] = []
    project_id = payload.get("project_id")
    unit_id = payload.get("unit_id")
    if not isinstance(project_id, str) or not isinstance(unit_id, str):
        return errors

    unit_pattern = re.compile(rf"{re.escape(project_id)}-(?:U|E)(?:0[1-9]|[1-9][0-9])")
    if unit_pattern.fullmatch(unit_id) is None:
        errors.append(
            f"unit_id: {unit_id!r} must match declared project {project_id} as "
            f"{project_id}-U## or {project_id}-E##"
        )

    context = payload.get("source_context")
    declared_segments: set[str] = set()
    if isinstance(context, Mapping):
        source_segments = context.get("edit_segments")
        if isinstance(source_segments, list):
            pattern = re.compile(rf"{re.escape(unit_id)}-ED{_POSITIVE_ID}")
            for index, segment in enumerate(source_segments):
                if not isinstance(segment, Mapping):
                    continue
                segment_id = segment.get("segment_id")
                if not isinstance(segment_id, str):
                    continue
                if segment_id in declared_segments:
                    errors.append(
                        f"source_context.edit_segments.{index}.segment_id: duplicate "
                        f"declared edit segment ID {segment_id}"
                    )
                else:
                    declared_segments.add(segment_id)
                if pattern.fullmatch(segment_id) is None:
                    errors.append(
                        f"source_context.edit_segments.{index}.segment_id: {segment_id!r} "
                        f"must match {unit_id}-ED###"
                    )

    measurement_evidence = _register_measurement_evidence(context, project_id, errors)
    inspection_evidence = _register_inspection_evidence(context, project_id, errors)
    items = payload.get("items")
    if not isinstance(items, list):
        return errors

    seen_item_ids: set[str] = set()
    covered_segments: set[str] = set()
    responsibilities: set[str] = set()
    item_pattern = re.compile(rf"{re.escape(unit_id)}-PS{_POSITIVE_ID}")
    for item_index, item in enumerate(items):
        if not isinstance(item, Mapping):
            continue
        location = f"items.{item_index}"
        item_id = item.get("sound_post_item_id")
        if isinstance(item_id, str):
            if item_id in seen_item_ids:
                errors.append(f"{location}.sound_post_item_id: duplicate sound post item ID {item_id}")
            else:
                seen_item_ids.add(item_id)
            if item_pattern.fullmatch(item_id) is None:
                errors.append(f"{location}.sound_post_item_id: {item_id!r} must match {unit_id}-PS###")
        responsibility = item.get("responsibility")
        if isinstance(responsibility, str):
            responsibilities.add(responsibility)
        segment_ids = item.get("edit_segment_ids")
        if isinstance(segment_ids, list):
            for segment_index, segment_id in enumerate(segment_ids):
                if isinstance(segment_id, str):
                    if segment_id not in declared_segments:
                        errors.append(f"{location}.edit_segment_ids.{segment_index}: unknown edit segment ID {segment_id}")
                    else:
                        covered_segments.add(segment_id)
        _validate_perspective(item, responsibility, location, errors)
        _validate_silence_purpose(item, responsibility, location, errors)
        _validate_item_evidence(item, responsibility, location, inspection_evidence, errors)
        _validate_free_text(item, responsibility, location, errors)
        _validate_numeric_measurements(item, location, measurement_evidence, errors)

    _validate_plan_free_text(payload, errors)
    for segment_id in sorted(declared_segments - covered_segments):
        errors.append(f"source_context.edit_segments: declared edit segment {segment_id} is not covered")
    for responsibility in sorted(_RESPONSIBILITIES - responsibilities):
        errors.append(f"items: missing required sound post responsibility {responsibility}")
    return errors


def _register_measurement_evidence(context: object, project_id: str, errors: list[str]) -> dict[str, Mapping[str, Any]]:
    registered: dict[str, Mapping[str, Any]] = {}
    if not isinstance(context, Mapping) or not isinstance(context.get("measurement_evidence"), list):
        return registered
    pattern = re.compile(rf"{re.escape(project_id)}-MS{_POSITIVE_ID}")
    for index, record in enumerate(context["measurement_evidence"]):
        if not isinstance(record, Mapping) or not isinstance(record.get("measurement_id"), str):
            continue
        measurement_id = record["measurement_id"]
        if measurement_id in registered:
            errors.append(f"source_context.measurement_evidence.{index}.measurement_id: duplicate measurement evidence ID {measurement_id}")
        else:
            registered[measurement_id] = record
        if pattern.fullmatch(measurement_id) is None:
            errors.append(f"source_context.measurement_evidence.{index}.measurement_id: {measurement_id!r} must match {project_id}-MS###")
        metric = record.get("metric")
        if isinstance(metric, str) and _METRIC_CATEGORIES.get(metric) != record.get("category"):
            errors.append(f"source_context.measurement_evidence.{index}: metric {metric!r} must use category {_METRIC_CATEGORIES.get(metric)!r}")
    return registered


def _register_inspection_evidence(context: object, project_id: str, errors: list[str]) -> dict[str, Mapping[str, Any]]:
    registered: dict[str, Mapping[str, Any]] = {}
    if not isinstance(context, Mapping) or not isinstance(context.get("inspection_evidence"), list):
        return registered
    pattern = re.compile(rf"{re.escape(project_id)}-IN{_POSITIVE_ID}")
    for index, record in enumerate(context["inspection_evidence"]):
        if not isinstance(record, Mapping) or not isinstance(record.get("evidence_id"), str):
            continue
        evidence_id = record["evidence_id"]
        if evidence_id in registered:
            errors.append(f"source_context.inspection_evidence.{index}.evidence_id: duplicate inspection evidence ID {evidence_id}")
        else:
            registered[evidence_id] = record
        if pattern.fullmatch(evidence_id) is None:
            errors.append(f"source_context.inspection_evidence.{index}.evidence_id: {evidence_id!r} must match {project_id}-IN###")
    return registered


def _validate_perspective(item: Mapping[str, Any], responsibility: object, location: str, errors: list[str]) -> None:
    perspective = item.get("perspective")
    if not isinstance(perspective, Mapping):
        return
    intent = perspective.get("intent")
    if _is_placeholder_only(intent):
        errors.append(f"{location}.perspective.intent: must not be a placeholder-only value")
    if isinstance(intent, str):
        if _MEASUREMENT_UNIT_SYNTAX.search(intent):
            errors.append(f"{location}.perspective.intent: measurement-unit syntax is allowed only in numeric_measurements")
        if _has_assertive_prohibited_claim(intent):
            errors.append(f"{location}.perspective.intent: assertive prohibited claim")
        if item.get("state") in {"planned", "awaiting-input"} and re.search(r"\b(?:was|were|has been|have been)\s+(?:inspected|reviewed)\b|\binspection\s+complete(?:d)?\b", intent, re.IGNORECASE):
            errors.append(f"{location}.perspective.intent: {item.get('state')} cannot imply inspection")
    mode = perspective.get("mode")
    allowed_modes = _PERSPECTIVE_MODES_BY_RESPONSIBILITY.get(responsibility, set())
    if mode not in allowed_modes:
        errors.append(f"{location}.perspective.mode: {responsibility} does not allow {mode!r}")


def _validate_silence_purpose(item: Mapping[str, Any], responsibility: object, location: str, errors: list[str]) -> None:
    if responsibility == "intentional-silence" and _is_placeholder_only(item.get("dramatic_purpose")):
        errors.append(f"{location}.dramatic_purpose: intentional-silence cannot use a placeholder-only purpose")


def _validate_item_evidence(item: Mapping[str, Any], responsibility: object, location: str, inspection_evidence: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    state = item.get("state")
    evidence_ids = item.get("inspection_evidence_ids")
    if state == "inspected":
        if not isinstance(evidence_ids, list) or not evidence_ids:
            errors.append(f"{location}.inspection_evidence_ids: inspected requires at least one applicable named evidence ID")
            return
        allowed_kinds = _INSPECTION_KINDS_BY_RESPONSIBILITY.get(responsibility, set())
        for evidence_id in evidence_ids:
            evidence = inspection_evidence.get(evidence_id) if isinstance(evidence_id, str) else None
            if evidence is None:
                errors.append(f"{location}.inspection_evidence_ids: unknown inspection evidence ID {evidence_id}")
            elif evidence.get("evidence_kind") not in allowed_kinds:
                errors.append(f"{location}.inspection_evidence_ids: evidence {evidence_id} is not applicable to {responsibility} inspection")
    elif isinstance(evidence_ids, list) and evidence_ids:
        errors.append(f"{location}.inspection_evidence_ids: only inspected items may bind inspection evidence")


def _validate_free_text(
    item: Mapping[str, Any], responsibility: object, location: str, errors: list[str]
) -> None:
    state = item.get("state")
    for field_name in ("dramatic_purpose", "instruction", "delivery_assumption"):
        value = item.get(field_name)
        if not isinstance(value, str):
            continue
        if _MEASUREMENT_UNIT_SYNTAX.search(value):
            if field_name == "delivery_assumption" and responsibility == "loudness-assumption":
                if _OBSERVED_VALUE_LANGUAGE.search(value):
                    errors.append(
                        f"{location}.{field_name}: numeric delivery assumption cannot describe an observed reading"
                    )
                if not _PROVISIONAL_TARGET_LANGUAGE.search(value):
                    errors.append(
                        f"{location}.{field_name}: numeric target must be marked provisional, "
                        "target, assumed, or conditional"
                    )
            elif field_name == "delivery_assumption":
                errors.append(
                    f"{location}.{field_name}: only loudness-assumption may declare a numeric target"
                )
            else:
                errors.append(f"{location}.{field_name}: measurement-unit syntax is allowed only in numeric_measurements")
        if _has_assertive_prohibited_claim(value):
            errors.append(f"{location}.{field_name}: assertive prohibited claim")
        if state in {"planned", "awaiting-input"} and re.search(r"\b(?:was|were|has been|have been)\s+(?:inspected|reviewed)\b|\binspection\s+complete(?:d)?\b", value, re.IGNORECASE):
            errors.append(f"{location}.{field_name}: {state} cannot imply inspection")


def _validate_numeric_measurements(item: Mapping[str, Any], location: str, measurement_evidence: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    measurements = item.get("numeric_measurements")
    if not isinstance(measurements, list):
        return
    for index, measurement in enumerate(measurements):
        if not isinstance(measurement, Mapping):
            continue
        measurement_id = measurement.get("measurement_id")
        measurement_location = f"{location}.numeric_measurements.{index}"
        evidence = measurement_evidence.get(measurement_id) if isinstance(measurement_id, str) else None
        if evidence is None:
            errors.append(f"{measurement_location}.measurement_id: unknown measurement evidence ID {measurement_id}")
            continue
        if any(measurement.get(field) != evidence.get(field) for field in ("category", "metric", "value", "unit")):
            errors.append(f"{measurement_location}: category, metric, value, and unit must exactly match measurement evidence {measurement_id}")
        metric = measurement.get("metric")
        if isinstance(metric, str) and _METRIC_CATEGORIES.get(metric) != measurement.get("category"):
            errors.append(f"{measurement_location}: metric {metric!r} must use category {_METRIC_CATEGORIES.get(metric)!r}")
        claim = measurement.get("claim")
        if isinstance(claim, str):
            if _has_assertive_prohibited_claim(claim):
                errors.append(f"{measurement_location}.claim: assertive prohibited claim")
            if _MEASUREMENT_UNIT_SYNTAX.search(claim):
                errors.append(
                    f"{measurement_location}.claim: measurement-unit syntax is allowed only in "
                    "structured measurement fields"
                )
            structured_metric = measurement.get("metric")
            for metric, pattern in _METRIC_PROSE_PATTERNS.items():
                if pattern.search(claim) and metric != structured_metric:
                    errors.append(
                        f"{measurement_location}.claim: contradicts structured metric {structured_metric}"
                    )
                    break


def _validate_plan_free_text(payload: Mapping[str, Any], errors: list[str]) -> None:
    for field_name in ("assumptions", "uncertainties"):
        values = payload.get(field_name)
        if not isinstance(values, list):
            continue
        for index, value in enumerate(values):
            if not isinstance(value, str):
                continue
            location = f"{field_name}.{index}"
            if _MEASUREMENT_UNIT_SYNTAX.search(value):
                errors.append(f"{location}: measurement-unit syntax is allowed only in numeric_measurements")
            if _has_assertive_prohibited_claim(value):
                errors.append(f"{location}: assertive prohibited claim")

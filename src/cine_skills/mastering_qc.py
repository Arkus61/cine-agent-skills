"""Semantic validation for version- and evidence-bound mastering/QC plans."""

from __future__ import annotations

import math
import posixpath
import re
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlsplit


_POSITIVE = r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"

REQUIRED_QC_CATEGORIES = frozenset(
    {
        "video-resolution",
        "frame-rate",
        "aspect-ratio",
        "duration",
        "audio-channel-count",
        "audio-channel-layout",
        "av-sync",
        "missing-frames",
        "duplicate-frames",
        "black-frames",
        "video-levels",
        "audio-clipping",
        "audio-sample-peak",
        "audio-true-peak",
        "audio-loudness",
        "captions-presence",
        "captions-accuracy",
        "titles-presence",
        "title-safe",
        "title-readability",
        "compression-artifacts",
        "vfx-completion",
        "color-completion",
        "deliverable-integrity",
    }
)

_MEASUREMENT_CATEGORIES = frozenset(
    {
        "video-resolution",
        "frame-rate",
        "aspect-ratio",
        "duration",
        "audio-channel-count",
        "audio-channel-layout",
        "audio-sample-peak",
        "audio-true-peak",
        "audio-loudness",
    }
)

_NUMERIC_MEASUREMENT_CATEGORIES = frozenset(
    {
        "frame-rate",
        "duration",
        "audio-channel-count",
        "audio-sample-peak",
        "audio-true-peak",
        "audio-loudness",
    }
)

_STRING_MEASUREMENT_CATEGORIES = frozenset(
    {
        "video-resolution",
        "aspect-ratio",
        "audio-channel-layout",
    }
)

_POSITIVE_MEASUREMENT_CATEGORIES = frozenset({"frame-rate", "duration"})
_PRESENCE_CATEGORIES = frozenset({"captions-presence", "titles-presence"})

_MACHINE_OPERATORS = frozenset(
    {"equals", "less-than-or-equal", "greater-than-or-equal", "present", "absent"}
)

_CATEGORY_UNITS = {
    "video-resolution": "pixels",
    "frame-rate": "fps",
    "aspect-ratio": "ratio",
    "duration": "seconds",
    "audio-channel-count": "channels",
    "audio-channel-layout": "layout",
    "audio-sample-peak": "dBFS",
    "audio-true-peak": "dBTP",
    "audio-loudness": "LUFS",
}

_EVIDENCE_SOURCE_KINDS = {
    "measurement": "supplied-measurement-report",
    "inspection": "supplied-inspection-record",
    "deliverable-verification": "supplied-deliverable-record",
    "human-approval": "supplied-human-decision",
}


def validate_mastering_qc_plan_contract(payload: Mapping[str, Any]) -> list[str]:
    """Return deterministic instance-wide mastering/QC contract errors."""
    errors: list[str] = []
    project, unit = payload.get("project_id"), payload.get("unit_id")
    if not isinstance(project, str) or not isinstance(unit, str):
        return errors
    if re.fullmatch(rf"{re.escape(project)}-(?:U|E)(?:0[1-9]|[1-9][0-9])", unit) is None:
        errors.append(f"unit_id: {unit!r} must belong to project {project}")

    context = payload.get("source_context")
    checks_value = payload.get("checks")
    deliverables_value = payload.get("deliverables")
    if not isinstance(context, Mapping) or not isinstance(checks_value, list) or not isinstance(deliverables_value, list):
        return errors

    master_versions = _registry(
        context.get("master_versions"),
        "master_version_id",
        rf"{re.escape(unit)}-MV{_POSITIVE}",
        f"{unit}-MV###",
        "master version",
        errors,
    )
    checks = _registry(
        checks_value,
        "check_id",
        rf"{re.escape(unit)}-QC{_POSITIVE}",
        f"{unit}-QC###",
        "QC check",
        errors,
    )
    deliverables = _registry(
        deliverables_value,
        "deliverable_id",
        rf"{re.escape(unit)}-DL{_POSITIVE}",
        f"{unit}-DL###",
        "deliverable",
        errors,
    )
    title_items = _registry(context.get("title_items"), "item_id", rf"{re.escape(unit)}-TT{_POSITIVE}", f"{unit}-TT###", "title item", errors)
    sound_items = _registry(context.get("sound_items"), "item_id", rf"{re.escape(unit)}-PS{_POSITIVE}", f"{unit}-PS###", "sound item", errors)
    color_items = _registry(context.get("color_items"), "item_id", rf"{re.escape(unit)}-CL{_POSITIVE}", f"{unit}-CL###", "color item", errors)
    vfx_items = _registry(context.get("vfx_items"), "item_id", rf"{re.escape(unit)}-FX{_POSITIVE}", f"{unit}-FX###", "VFX item", errors)
    evidence_ids = _registry(
        context.get("evidence"),
        "evidence_id",
        rf"{re.escape(project)}-QE{_POSITIVE}",
        f"{project}-QE###",
        "QC evidence",
        errors,
    )

    current_version = context.get("current_master_version_id")
    if current_version is not None and current_version not in master_versions:
        errors.append("source_context.current_master_version_id: unknown master version")

    check_records = {
        record["check_id"]: record
        for record in checks_value
        if isinstance(record, Mapping) and isinstance(record.get("check_id"), str)
    }
    deliverable_records = {
        record["deliverable_id"]: record
        for record in deliverables_value
        if isinstance(record, Mapping) and isinstance(record.get("deliverable_id"), str)
    }
    evidence_records = {
        record["evidence_id"]: record
        for record in context.get("evidence", [])
        if isinstance(record, Mapping) and isinstance(record.get("evidence_id"), str)
    }
    master_version_records = {
        record["master_version_id"]: record
        for record in context.get("master_versions", [])
        if isinstance(record, Mapping) and isinstance(record.get("master_version_id"), str)
    }
    approval_value = payload.get("approval")

    for index, record in enumerate(context.get("evidence", [])):
        if not isinstance(record, Mapping):
            continue
        location = f"source_context.evidence.{index}"
        target_check = record.get("target_check_id")
        target_deliverable = record.get("target_deliverable_id")
        if target_check is not None and target_check not in checks:
            errors.append(f"{location}.target_check_id: unknown QC check {target_check}")
        if target_deliverable is not None and target_deliverable not in deliverables:
            errors.append(f"{location}.target_deliverable_id: unknown deliverable {target_deliverable}")
        if record.get("master_version_id") not in master_versions:
            errors.append(f"{location}.master_version_id: unknown master version {record.get('master_version_id')}")
        applicability = record.get("applicability")
        if applicability == "applicable" and record.get("master_version_id") != current_version:
            errors.append(f"{location}: applicable evidence must use the current master version")
        evidence_master = master_version_records.get(record.get("master_version_id"))
        if (
            isinstance(evidence_master, Mapping)
            and _same_source_reference(record.get("source_reference"), evidence_master.get("source_reference"))
        ):
            errors.append(f"{location}.source_reference: a master filename or source is not QC evidence")
        kind = record.get("kind")
        expected_source_kind = _EVIDENCE_SOURCE_KINDS.get(kind)
        if expected_source_kind is not None and record.get("source_kind") != expected_source_kind:
            errors.append(f"{location}.source_kind: source_kind must be {expected_source_kind} for {kind} evidence")
        if kind in {"measurement", "inspection"}:
            if target_check is None or target_deliverable is not None or not isinstance(record.get("criterion"), Mapping):
                errors.append(f"{location}: measurement or inspection evidence must target exactly one QC check and include its criterion")
            target_record = check_records.get(target_check)
            if target_record is not None:
                target_criterion = target_record.get("criterion")
                evidence_criterion = record.get("criterion")
                exact_current_criterion = record.get("criterion") == target_criterion
                historical_metric_matches = (
                    isinstance(evidence_criterion, Mapping)
                    and evidence_criterion.get("metric") == target_record.get("category")
                )
                if (
                    record.get("scope") != f"check:{target_check}"
                    or (applicability == "applicable" and not exact_current_criterion)
                    or (applicability != "applicable" and not historical_metric_matches)
                ):
                    errors.append(f"{location}: evidence criterion and scope must match its target QC check")
                expected_kind = "measurement" if target_record.get("category") in _MEASUREMENT_CATEGORIES else "inspection"
                if kind != expected_kind:
                    errors.append(f"{location}.kind: evidence kind must be {expected_kind} for {target_record.get('category')}")
                target_units = _CATEGORY_UNITS.get(str(target_record.get("category")))
                if target_units is None and isinstance(evidence_criterion, Mapping):
                    target_units = evidence_criterion.get("units")
                if record.get("units") != target_units:
                    errors.append(f"{location}.units: evidence units must match its target QC metric")
                if isinstance(evidence_criterion, Mapping) and record.get("units") != evidence_criterion.get("units"):
                    errors.append(f"{location}.units: evidence criterion units must match its observed units")
                _validate_value_types(
                    target_record.get("category"),
                    evidence_criterion,
                    record.get("observed_value"),
                    location,
                    errors,
                )
                if applicability == "applicable":
                    observation = target_record.get("observed")
                    referenced = isinstance(observation, Mapping) and record.get("evidence_id") in observation.get("evidence_ids", [])
                    exact_observation = (
                        isinstance(observation, Mapping)
                        and record.get("observed_value") == observation.get("value")
                        and record.get("units") == observation.get("units")
                        and record.get("master_version_id") == observation.get("master_version_id")
                    )
                    if not referenced or not exact_observation:
                        errors.append(f"{location}: applicable check evidence must be bound to the target observation")
        elif kind == "deliverable-verification":
            if target_check is not None or target_deliverable is None or record.get("criterion") is not None:
                errors.append(f"{location}: deliverable evidence must target exactly one deliverable")
            target_record = deliverable_records.get(target_deliverable)
            if (
                target_record is not None
                and (
                    record.get("scope") != f"deliverable:{target_deliverable}"
                    or record.get("observed_value") != "verified"
                    or record.get("units") is not None
                )
            ):
                errors.append(f"{location}: deliverable evidence must be internally consistent with its target deliverable")
            if applicability == "applicable" and target_record is not None and (
                record.get("evidence_id") not in target_record.get("evidence_ids", [])
                or target_record.get("status") != "verified"
                or record.get("master_version_id") != target_record.get("master_version_id")
            ):
                errors.append(f"{location}: applicable deliverable evidence must be bound to the verified target deliverable")
        elif kind == "human-approval":
            if target_check is not None or target_deliverable is not None or record.get("criterion") is not None:
                errors.append(f"{location}: human approval evidence must use approval scope rather than a check or deliverable target")
            approval_scope = record.get("scope")
            if (
                not isinstance(approval_scope, str)
                or not approval_scope.strip()
                or record.get("observed_value") != "approved"
                or record.get("units") is not None
            ):
                errors.append(f"{location}: approval evidence must be internally consistent and use a nonempty scope")
            if applicability == "applicable" and (
                not isinstance(approval_value, Mapping)
                or record.get("evidence_id") not in approval_value.get("evidence_ids", [])
                or approval_value.get("state") != "approved"
                or record.get("master_version_id") != approval_value.get("master_version_id")
                or record.get("scope") != approval_value.get("scope")
                or record.get("observed_value") != "approved"
                or record.get("units") is not None
            ):
                errors.append(f"{location}: applicable approval evidence must be bound to the current approval record")

    seen_categories: set[str] = set()
    for index, check in enumerate(checks_value):
        if not isinstance(check, Mapping):
            continue
        location = f"checks.{index}"
        category = check.get("category")
        if isinstance(category, str):
            if category in seen_categories:
                errors.append(f"{location}.category: duplicate QC category {category}")
            seen_categories.add(category)
        criterion = check.get("criterion")
        if isinstance(criterion, Mapping):
            if criterion.get("metric") != category:
                errors.append(f"{location}.criterion.metric: criterion metric must equal check category")
            required_units = _CATEGORY_UNITS.get(str(category))
            if required_units is not None and criterion.get("units") != required_units:
                errors.append(f"{location}.criterion.units: {category} requires units {required_units}")
            if criterion.get("state") == "unresolved" and criterion.get("operator") != "review":
                errors.append(f"{location}.criterion: unresolved criterion must use review operator")
            if (
                category in _MEASUREMENT_CATEGORIES
                and criterion.get("state") == "supplied"
                and criterion.get("operator") not in _MACHINE_OPERATORS
            ):
                errors.append(f"{location}.criterion: measurable supplied criterion must use a machine-comparable operator")
            if (
                category in _PRESENCE_CATEGORIES
                and criterion.get("state") == "supplied"
                and criterion.get("operator") not in {"present", "absent"}
            ):
                errors.append(f"{location}.criterion: presence check must use present or absent operator")
            if criterion.get("state") == "supplied" and criterion.get("operator") in {"present", "absent"}:
                expected_presence = criterion.get("operator") == "present"
                if criterion.get("expected_value") is not expected_presence:
                    expected_label = "true" if expected_presence else "false"
                    errors.append(
                        f"{location}.criterion: presence operator {criterion.get('operator')} requires expected_value {expected_label}"
                    )

        references = check.get("upstream_references")
        if isinstance(references, Mapping):
            _unknown(references.get("title_item_ids"), title_items, location + ".upstream_references.title_item_ids", "title item", errors)
            _unknown(references.get("sound_item_ids"), sound_items, location + ".upstream_references.sound_item_ids", "sound item", errors)
            _unknown(references.get("color_item_ids"), color_items, location + ".upstream_references.color_item_ids", "color item", errors)
            _unknown(references.get("vfx_item_ids"), vfx_items, location + ".upstream_references.vfx_item_ids", "VFX item", errors)

        observed = check.get("observed")
        if not isinstance(observed, Mapping):
            continue
        bound_evidence: list[Mapping[str, Any]] = []
        for evidence_id in observed.get("evidence_ids", []):
            record = evidence_records.get(evidence_id)
            if record is None:
                errors.append(f"{location}.observed.evidence_ids: unknown QC evidence {evidence_id}")
                continue
            if _evidence_matches_check(record, check, current_version):
                bound_evidence.append(record)
            else:
                errors.append(
                    f"{location}.observed: evidence {evidence_id} must bind the exact check, criterion, observed value, units, and current master version"
                )

        result = check.get("result")
        if observed.get("value") is not None and isinstance(criterion, Mapping) and observed.get("units") != criterion.get("units"):
            errors.append(f"{location}.observed.units: observed units must equal criterion units")
        _validate_value_types(category, criterion, observed.get("value"), location, errors)
        if isinstance(criterion, Mapping) and criterion.get("state") == "unresolved" and result in {"pass", "fail"}:
            errors.append(f"{location}.result: unresolved criterion cannot pass or fail")
        if result in {"pass", "fail"}:
            expected_kind = "measurement" if category in _MEASUREMENT_CATEGORIES else "inspection"
            applicable = [
                record
                for record in bound_evidence
                if record.get("applicability") == "applicable" and record.get("kind") == expected_kind
            ]
            if current_version is None or observed.get("value") is None or observed.get("master_version_id") != current_version or not applicable:
                errors.append(f"{location}: pass/fail requires applicable current-master evidence")
            comparison = _comparison_result(criterion, observed.get("value"))
            if (
                isinstance(criterion, Mapping)
                and criterion.get("state") == "supplied"
                and criterion.get("operator") in _MACHINE_OPERATORS
                and comparison is None
            ):
                errors.append(f"{location}.result: machine-comparable criterion has incompatible operands")
            elif comparison is not None and ((result == "pass") != comparison):
                errors.append(f"{location}.result: {result} disagrees with the machine-comparable criterion")
        elif observed.get("value") is not None and not bound_evidence:
            errors.append(f"{location}.observed: an observed value requires applicable evidence")

    for category in sorted(REQUIRED_QC_CATEGORIES - seen_categories):
        errors.append(f"checks: missing required QC category {category}")
    for index, check in enumerate(checks_value):
        if isinstance(check, Mapping) and check.get("category") in REQUIRED_QC_CATEGORIES and check.get("required") is not True:
            errors.append(f"checks.{index}.required: required QC category must be marked required")

    for index, deliverable in enumerate(deliverables_value):
        if not isinstance(deliverable, Mapping):
            continue
        location = f"deliverables.{index}"
        if deliverable.get("kind") == "qc-report" and deliverable.get("status") == "verified":
            current_master = master_version_records.get(current_version)
            if (
                isinstance(current_master, Mapping)
                and _same_source_reference(deliverable.get("source_reference"), current_master.get("source_reference"))
            ):
                errors.append(f"{location}.source_reference: verified QC report must be distinct from the current master source")
        bound_evidence = []
        for evidence_id in deliverable.get("evidence_ids", []):
            record = evidence_records.get(evidence_id)
            if record is None:
                errors.append(f"{location}.evidence_ids: unknown QC evidence {evidence_id}")
            elif _evidence_matches_deliverable(record, deliverable, current_version):
                bound_evidence.append(record)
            else:
                errors.append(f"{location}: evidence {evidence_id} must bind the exact deliverable and current master version")
        if deliverable.get("status") == "verified" and (
            current_version is None
            or deliverable.get("master_version_id") != current_version
            or not deliverable.get("source_reference")
            or not bound_evidence
        ):
            errors.append(f"{location}: verified deliverable requires applicable current-master evidence")

    required_deliverable_kinds = {
        deliverable.get("kind")
        for deliverable in deliverables_value
        if isinstance(deliverable, Mapping) and deliverable.get("required") is True
    }
    for kind in sorted({"picture-sound-master", "qc-report"} - required_deliverable_kinds):
        errors.append(f"deliverables: missing required deliverable kind {kind}")

    approval = payload.get("approval")
    if isinstance(approval, Mapping):
        approval_evidence = []
        for evidence_id in approval.get("evidence_ids", []):
            record = evidence_records.get(evidence_id)
            if record is None:
                errors.append(f"approval.evidence_ids: unknown QC evidence {evidence_id}")
            elif _evidence_matches_approval(record, approval, current_version):
                approval_evidence.append(record)
            else:
                errors.append("approval: approval evidence must bind the exact current master version and review scope")
        if approval.get("state") == "approved" and (
            current_version is None
            or approval.get("master_version_id") != current_version
            or not approval_evidence
        ):
            errors.append("approval: approved state requires applicable human approval evidence for the exact current master and scope")
        if approval.get("state") == "approved" and approval.get("scope") != "delivery-master-and-qc":
            errors.append("approval.scope: approved readiness scope must be delivery-master-and-qc")

    readiness = payload.get("readiness")
    if isinstance(readiness, Mapping):
        required_check_ids = {
            check.get("check_id")
            for check in checks_value
            if isinstance(check, Mapping) and check.get("required") is True
        }
        if set(readiness.get("required_check_ids", [])) != required_check_ids:
            errors.append("readiness.required_check_ids: must equal all required QC check IDs")
        required_deliverable_ids = {
            deliverable.get("deliverable_id")
            for deliverable in deliverables_value
            if isinstance(deliverable, Mapping) and deliverable.get("required") is True
        }
        if set(readiness.get("required_deliverable_ids", [])) != required_deliverable_ids:
            errors.append("readiness.required_deliverable_ids: must equal all required deliverable IDs")
        if readiness.get("state") == "ready":
            if any(check.get("result") != "pass" for check in check_records.values() if check.get("required") is True):
                errors.append("readiness.state: required checks must all pass before readiness")
            if any(deliverable.get("status") != "verified" for deliverable in deliverable_records.values() if deliverable.get("required") is True):
                errors.append("readiness.state: required deliverables must all be verified before readiness")
            if current_version is None:
                errors.append("readiness.state: readiness requires an exact current master version")
            if not isinstance(approval, Mapping) or approval.get("state") != "approved":
                errors.append("readiness.state: readiness requires current scoped human approval")
            elif approval.get("scope") != "delivery-master-and-qc":
                errors.append("readiness.state: approved readiness scope must be delivery-master-and-qc")

    return errors


def _registry(
    records: Any,
    key: str,
    pattern: str,
    expected: str,
    label: str,
    errors: list[str],
) -> set[str]:
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
    for value in values if isinstance(values, list) else []:
        if isinstance(value, str) and value not in known:
            errors.append(f"{location}: unknown {label} {value}")


def _evidence_matches_check(record: Mapping[str, Any], check: Mapping[str, Any], current_version: Any) -> bool:
    observed = check.get("observed")
    return (
        isinstance(observed, Mapping)
        and record.get("target_check_id") == check.get("check_id")
        and record.get("target_deliverable_id") is None
        and record.get("criterion") == check.get("criterion")
        and record.get("observed_value") == observed.get("value")
        and record.get("units") == observed.get("units")
        and record.get("master_version_id") == observed.get("master_version_id") == current_version
        and record.get("scope") == f"check:{check.get('check_id')}"
    )


def _evidence_matches_deliverable(record: Mapping[str, Any], deliverable: Mapping[str, Any], current_version: Any) -> bool:
    return (
        record.get("kind") == "deliverable-verification"
        and record.get("applicability") == "applicable"
        and record.get("target_check_id") is None
        and record.get("target_deliverable_id") == deliverable.get("deliverable_id")
        and record.get("criterion") is None
        and record.get("observed_value") == "verified"
        and record.get("units") is None
        and record.get("master_version_id") == deliverable.get("master_version_id") == current_version
        and record.get("scope") == f"deliverable:{deliverable.get('deliverable_id')}"
    )


def _evidence_matches_approval(record: Mapping[str, Any], approval: Mapping[str, Any], current_version: Any) -> bool:
    return (
        record.get("kind") == "human-approval"
        and record.get("applicability") == "applicable"
        and record.get("target_check_id") is None
        and record.get("target_deliverable_id") is None
        and record.get("criterion") is None
        and record.get("observed_value") == "approved"
        and record.get("units") is None
        and record.get("master_version_id") == approval.get("master_version_id") == current_version
        and record.get("scope") == approval.get("scope")
    )


def _comparison_result(criterion: Any, observed: Any) -> bool | None:
    if not isinstance(criterion, Mapping):
        return None
    if criterion.get("state") != "supplied":
        return None
    operator, expected = criterion.get("operator"), criterion.get("expected_value")
    if operator == "equals":
        if _is_finite_number(observed) and _is_finite_number(expected):
            return observed == expected
        if isinstance(observed, bool) and isinstance(expected, bool):
            return observed is expected
        if isinstance(observed, str) and isinstance(expected, str):
            return observed == expected
        return None
    if operator in {"present", "absent"}:
        if not isinstance(observed, bool) or not isinstance(expected, bool):
            return None
        if operator == "present":
            return expected is True and observed is True
        return expected is False and observed is False
    if operator in {"less-than-or-equal", "greater-than-or-equal"}:
        if not _is_finite_number(observed) or not _is_finite_number(expected):
            return None
        return observed <= expected if operator == "less-than-or-equal" else observed >= expected
    return None


def _validate_value_types(
    category: Any,
    criterion: Any,
    observed: Any,
    location: str,
    errors: list[str],
) -> None:
    if not isinstance(criterion, Mapping):
        return
    operator = criterion.get("operator")
    expected = criterion.get("expected_value")
    if criterion.get("state") == "supplied":
        if category in _NUMERIC_MEASUREMENT_CATEGORIES:
            if not _is_finite_number(expected):
                errors.append(f"{location}.criterion.expected_value: numeric value type must be a finite number")
            elif category in _POSITIVE_MEASUREMENT_CATEGORIES and expected <= 0:
                errors.append(f"{location}.criterion.expected_value: value must be greater than zero")
            elif category == "audio-channel-count" and not _is_positive_integer(expected):
                errors.append(f"{location}.criterion.expected_value: value must be a positive integer")
        elif category in _STRING_MEASUREMENT_CATEGORIES:
            if not isinstance(expected, str):
                errors.append(f"{location}.criterion.expected_value: value type must be string")
            elif not expected.strip():
                errors.append(f"{location}.criterion.expected_value: value must be a non-empty string")
        if category in _PRESENCE_CATEGORIES:
            if not isinstance(expected, bool):
                errors.append(f"{location}.criterion.expected_value: presence value type must be boolean")
        elif operator in {"present", "absent"} and not isinstance(expected, bool):
            errors.append(f"{location}.criterion.expected_value: present/absent value type must be boolean")
    if observed is None:
        return
    if category in _NUMERIC_MEASUREMENT_CATEGORIES:
        if not _is_finite_number(observed):
            errors.append(f"{location}.observed_value: numeric value type must be a finite number")
        elif category in _POSITIVE_MEASUREMENT_CATEGORIES and observed <= 0:
            errors.append(f"{location}.observed_value: value must be greater than zero")
        elif category == "audio-channel-count" and not _is_positive_integer(observed):
            errors.append(f"{location}.observed_value: value must be a positive integer")
    elif category in _STRING_MEASUREMENT_CATEGORIES:
        if not isinstance(observed, str):
            errors.append(f"{location}.observed_value: value type must be string")
        elif not observed.strip():
            errors.append(f"{location}.observed_value: value must be a non-empty string")
    if category in _PRESENCE_CATEGORIES:
        if not isinstance(observed, bool):
            errors.append(f"{location}.observed_value: presence value type must be boolean")
    elif operator in {"present", "absent"} and not isinstance(observed, bool):
        errors.append(f"{location}.observed_value: present/absent value type must be boolean")


def _is_finite_number(value: Any) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        return False


def _is_positive_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _same_source_reference(left: Any, right: Any) -> bool:
    normalized_left = _normalize_source_reference(left)
    normalized_right = _normalize_source_reference(right)
    return normalized_left is not None and normalized_right is not None and normalized_left == normalized_right


def _normalize_source_reference(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    parts = urlsplit(value.strip().replace("\\", "/"))
    normalized_path = posixpath.normpath(parts.path)
    if parts.scheme or parts.netloc:
        return f"{parts.scheme.lower()}://{parts.netloc.lower()}{normalized_path}"
    return normalized_path

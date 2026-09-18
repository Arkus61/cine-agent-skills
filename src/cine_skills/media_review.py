"""Semantic checks for evidence-based media review reports."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


_POSITIVE_ID = r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
_EVIDENCE_BY_MODALITY = {
    "still": {"static-visible"},
    "motion": {"static-visible", "motion"},
    "audio": {"audio"},
    "audiovisual": {"static-visible", "motion", "audio"},
    "metadata": {"measurable-metadata"},
}
_EVIDENCE_BY_DIMENSION = {
    "movement": "motion",
    "sound": "audio",
}


def _matches_project_id(value: Any, project_id: str, suffix: str) -> bool:
    return isinstance(value, str) and re.fullmatch(
        rf"{re.escape(project_id)}-{suffix}{_POSITIVE_ID}", value
    ) is not None


def _reference_pairs(value: Any) -> set[tuple[str, str]] | None:
    if not isinstance(value, list):
        return None
    pairs: set[tuple[str, str]] = set()
    for reference in value:
        if not isinstance(reference, Mapping):
            return None
        kind = reference.get("kind")
        identifier = reference.get("id")
        if not isinstance(kind, str) or not isinstance(identifier, str):
            return None
        pairs.add((kind, identifier))
    return pairs


def _declared_registries(payload: Mapping[str, Any]) -> dict[str, set[str]]:
    context = payload.get("source_context")
    if not isinstance(context, Mapping):
        return {}
    registries = context.get("registries")
    if not isinstance(registries, Mapping):
        return {}
    return {
        kind: {
            identifier
            for identifier in registries.get(f"{kind}_ids", [])
            if isinstance(identifier, str)
        }
        for kind in ("character", "scene", "shot", "asset", "world", "beat", "sound")
    }


def validate_media_review_report_contract(payload: Mapping[str, Any]) -> list[str]:
    """Validate cross-field media-review invariants after schema validation."""
    errors: list[str] = []
    project_id = payload.get("project_id")
    if not isinstance(project_id, str):
        return errors
    registries = _declared_registries(payload)
    _validate_declared_registries(errors, payload, project_id)
    context = payload.get("source_context")
    prompts_value = context.get("prompt_packages") if isinstance(context, Mapping) else None
    prompts: dict[str, tuple[set[tuple[str, str]], dict[str, Mapping[str, Any]]]] = {}
    if isinstance(prompts_value, list):
        for prompt_index, prompt in enumerate(prompts_value):
            if not isinstance(prompt, Mapping):
                continue
            prompt_id = prompt.get("prompt_id")
            if not _matches_project_id(prompt_id, project_id, "MP"):
                errors.append(
                    f"source_context.prompt_packages.{prompt_index}.prompt_id: "
                    f"{prompt_id!r} must match {project_id}-MP###"
                )
                continue
            assert isinstance(prompt_id, str)
            if prompt_id in prompts:
                errors.append(
                    f"source_context.prompt_packages.{prompt_index}.prompt_id: "
                    f"duplicate prompt ID {prompt_id}"
                )
                continue
            references = _reference_pairs(prompt.get("upstream_references"))
            if references is None:
                continue
            _validate_references(
                errors,
                f"source_context.prompt_packages.{prompt_index}.upstream_references",
                references,
                registries,
            )
            criteria: dict[str, Mapping[str, Any]] = {}
            criteria_value = prompt.get("acceptance_criteria")
            if isinstance(criteria_value, list):
                for criterion_index, criterion in enumerate(criteria_value):
                    if not isinstance(criterion, Mapping):
                        continue
                    criterion_id = criterion.get("criterion_id")
                    location = (
                        "source_context.prompt_packages."
                        f"{prompt_index}.acceptance_criteria.{criterion_index}.criterion_id"
                    )
                    if not _matches_project_id(criterion_id, project_id, "AC"):
                        errors.append(
                            f"{location}: {criterion_id!r} must match {project_id}-AC###"
                        )
                        continue
                    assert isinstance(criterion_id, str)
                    if criterion_id in criteria:
                        errors.append(f"{location}: duplicate acceptance criterion {criterion_id}")
                    else:
                        criteria[criterion_id] = criterion
                    source_reference = criterion.get("source_reference")
                    expected_source_location = (
                        f"/prompts/{prompt_id}/acceptance_criteria/{criterion_index}"
                    )
                    expected_source_reference = (
                        f"media-prompt-package.json#{expected_source_location}"
                    )
                    if source_reference != expected_source_reference:
                        errors.append(
                            f"{location.rsplit('.', 1)[0]}.source_reference: "
                            f"must bind prompt {prompt_id} at {expected_source_location} "
                            "using the canonical source reference "
                            f"{expected_source_reference}"
                        )
                    dimension = criterion.get("dimension")
                    required_evidence = criterion.get("required_evidence")
                    required_for_dimension = _EVIDENCE_BY_DIMENSION.get(dimension)
                    if (
                        required_for_dimension is not None
                        and required_evidence != required_for_dimension
                    ):
                        errors.append(
                            f"{location.rsplit('.', 1)[0]}.required_evidence: "
                            f"{dimension} dimension requires {required_for_dimension} evidence"
                        )
            prompts[prompt_id] = (references, criteria)

    package_status = payload.get("package_status")
    missing_inputs = payload.get("missing_inputs")
    blockers = payload.get("blockers")
    if package_status == "awaiting-media" and isinstance(missing_inputs, list):
        kinds = {
            item.get("kind")
            for item in missing_inputs
            if isinstance(item, Mapping) and isinstance(item.get("kind"), str)
        }
        if not kinds.intersection({"media", "metadata"}) or "criterion" not in kinds:
            errors.append(
                "awaiting-media report must explicitly name missing media or metadata and criteria"
            )
    if package_status == "reviewed" and isinstance(blockers, list) and blockers:
        errors.append("reviewed report cannot contain blockers")

    items = payload.get("items")
    seen_media_ids: set[str] = set()
    seen_input_ids: set[str] = set()
    seen_evidence_ids: set[str] = set()
    has_human_review = False
    if not isinstance(items, list):
        return errors
    for item_index, item in enumerate(items):
        if not isinstance(item, Mapping):
            continue
        location = f"items.{item_index}"
        media_id = item.get("media_id")
        if not _matches_project_id(media_id, project_id, "MD"):
            errors.append(f"{location}.media_id: {media_id!r} must match {project_id}-MD###")
        elif media_id in seen_media_ids:
            errors.append(f"{location}.media_id: duplicate media ID {media_id}")
        else:
            seen_media_ids.add(media_id)
        if item.get("status") == "human-review":
            has_human_review = True
        prompt_id = item.get("prompt_id")
        prompt = prompts.get(prompt_id) if isinstance(prompt_id, str) else None
        if prompt is None:
            errors.append(f"{location}.prompt_id: unknown prompt {prompt_id}")
            continue
        prompt_references, criteria = prompt
        item_references = _reference_pairs(item.get("upstream_references"))
        if item_references is not None:
            _validate_references(errors, f"{location}.upstream_references", item_references, registries)
            if item_references != prompt_references:
                errors.append(
                    f"{location}.upstream_references: must exactly match prompt {prompt_id}"
                )
        _validate_item(
            errors,
            item,
            location,
            project_id,
            criteria,
            seen_input_ids,
            seen_evidence_ids,
        )
    if has_human_review and package_status != "blocked":
        errors.append("package_status: human-review item requires package_status blocked")
    return errors


def _validate_declared_registries(
    errors: list[str], payload: Mapping[str, Any], project_id: str
) -> None:
    context = payload.get("source_context")
    registries = context.get("registries") if isinstance(context, Mapping) else None
    if not isinstance(registries, Mapping):
        return
    for kind in ("character", "scene", "shot", "asset", "world", "beat", "sound"):
        values = registries.get(f"{kind}_ids")
        if not isinstance(values, list):
            continue
        for index, identifier in enumerate(values):
            if isinstance(identifier, str) and not identifier.startswith(f"{project_id}-"):
                errors.append(
                    f"source_context.registries.{kind}_ids.{index}: "
                    f"{identifier!r} must belong to project {project_id}"
                )


def _validate_references(
    errors: list[str],
    location: str,
    references: set[tuple[str, str]],
    registries: dict[str, set[str]],
) -> None:
    for kind, identifier in sorted(references):
        if identifier not in registries.get(kind, set()):
            errors.append(f"{location}: unknown {kind} reference {identifier}")


def _validate_deviations(
    errors: list[str],
    item: Mapping[str, Any],
    location: str,
    criteria: dict[str, Mapping[str, Any]],
) -> None:
    deviations = item.get("deviations")
    if not isinstance(deviations, list):
        return
    for deviation_index, deviation in enumerate(deviations):
        if not isinstance(deviation, Mapping):
            continue
        criterion_id = deviation.get("criterion_id")
        if not isinstance(criterion_id, str) or criterion_id not in criteria:
            errors.append(
                f"{location}.deviations.{deviation_index}.criterion_id: "
                f"unknown acceptance criterion {criterion_id}"
            )


def _validate_item(
    errors: list[str],
    item: Mapping[str, Any],
    location: str,
    project_id: str,
    criteria: dict[str, Mapping[str, Any]],
    seen_input_ids: set[str],
    seen_evidence_ids: set[str],
) -> None:
    inspected_input = item.get("inspected_input")
    if not isinstance(inspected_input, Mapping):
        return
    input_id = inspected_input.get("input_id")
    if not _matches_project_id(input_id, project_id, "IN"):
        errors.append(
            f"{location}.inspected_input.input_id: {input_id!r} must match {project_id}-IN###"
        )
    elif input_id in seen_input_ids:
        errors.append(f"{location}.inspected_input.input_id: duplicate input ID {input_id}")
    else:
        seen_input_ids.add(input_id)
    modality = inspected_input.get("modality")
    supported_evidence = _EVIDENCE_BY_MODALITY.get(modality, set())
    evidence_by_id: dict[str, Mapping[str, Any]] = {}
    evidence_value = item.get("inspection_evidence")
    if isinstance(evidence_value, list):
        for evidence_index, evidence in enumerate(evidence_value):
            if not isinstance(evidence, Mapping):
                continue
            evidence_location = f"{location}.inspection_evidence.{evidence_index}"
            evidence_id = evidence.get("evidence_id")
            if not _matches_project_id(evidence_id, project_id, "ME"):
                errors.append(
                    f"{evidence_location}.evidence_id: {evidence_id!r} must match {project_id}-ME###"
                )
            elif evidence_id in seen_evidence_ids:
                errors.append(f"{evidence_location}.evidence_id: duplicate evidence ID {evidence_id}")
            else:
                seen_evidence_ids.add(evidence_id)
                evidence_by_id[evidence_id] = evidence
            if evidence.get("input_id") != input_id:
                errors.append(
                    f"{evidence_location}.input_id: must bind inspected input {input_id}"
                )
            criterion_id = evidence.get("criterion_id")
            criterion = criteria.get(criterion_id) if isinstance(criterion_id, str) else None
            if criterion is None:
                errors.append(
                    f"{evidence_location}.criterion_id: unknown acceptance criterion {criterion_id}"
                )
                continue
            required_evidence = criterion.get("required_evidence")
            if evidence.get("kind") == "direct-inspection" and modality == "metadata":
                errors.append(f"{evidence_location}.kind: metadata requires measurable-metadata evidence")
            if evidence.get("kind") == "measurable-metadata" and modality != "metadata":
                errors.append(f"{evidence_location}.kind: measurable metadata must bind metadata input")
            if required_evidence not in supported_evidence:
                errors.append(
                    f"{evidence_location}: {modality} evidence cannot support {required_evidence}"
                )
    _validate_outcomes(errors, item, location, criteria, evidence_by_id)
    _validate_deviations(errors, item, location, criteria)
    _validate_decision(errors, item, location)


def _validate_outcomes(
    errors: list[str],
    item: Mapping[str, Any],
    location: str,
    criteria: dict[str, Mapping[str, Any]],
    evidence_by_id: dict[str, Mapping[str, Any]],
) -> None:
    outcomes = item.get("criterion_outcomes")
    if not isinstance(outcomes, list):
        return
    outcome_ids: set[str] = set()
    for outcome_index, outcome in enumerate(outcomes):
        if not isinstance(outcome, Mapping):
            continue
        outcome_location = f"{location}.criterion_outcomes.{outcome_index}"
        criterion_id = outcome.get("criterion_id")
        if not isinstance(criterion_id, str) or criterion_id not in criteria:
            errors.append(f"{outcome_location}.criterion_id: unknown acceptance criterion {criterion_id}")
            continue
        if criterion_id in outcome_ids:
            errors.append(f"{outcome_location}.criterion_id: duplicate criterion outcome {criterion_id}")
        outcome_ids.add(criterion_id)
        evidence_ids = outcome.get("evidence_ids")
        if isinstance(evidence_ids, list):
            for evidence_id in evidence_ids:
                evidence = evidence_by_id.get(evidence_id)
                if evidence is None:
                    errors.append(f"{outcome_location}.evidence_ids: unknown evidence {evidence_id}")
                elif evidence.get("criterion_id") != criterion_id:
                    errors.append(
                        f"{outcome_location}.evidence_ids: {evidence_id} does not support {criterion_id}"
                    )
    if outcome_ids != set(criteria):
        errors.append(f"{location}.criterion_outcomes: must cover exactly the prompt acceptance criteria")


def _validate_decision(errors: list[str], item: Mapping[str, Any], location: str) -> None:
    deviations = item.get("deviations")
    unresolved = [
        deviation
        for deviation in deviations if isinstance(deviation, Mapping) and not deviation.get("resolved")
    ] if isinstance(deviations, list) else []
    status = item.get("status")
    scope = item.get("repair_scope")
    outcomes = item.get("criterion_outcomes")
    outcome_values = {
        outcome.get("outcome") for outcome in outcomes if isinstance(outcome, Mapping)
    } if isinstance(outcomes, list) else set()
    failed_criteria = {
        outcome.get("criterion_id")
        for outcome in outcomes
        if isinstance(outcome, Mapping) and outcome.get("outcome") == "fail"
    } if isinstance(outcomes, list) else set()
    not_assessable_criteria = {
        outcome.get("criterion_id")
        for outcome in outcomes
        if isinstance(outcome, Mapping) and outcome.get("outcome") == "not-assessable"
    } if isinstance(outcomes, list) else set()
    unresolved_criteria = {
        deviation.get("criterion_id")
        for deviation in unresolved
        if isinstance(deviation.get("criterion_id"), str)
    }
    if status == "approved":
        if unresolved or scope != "none" or outcome_values != {"pass"}:
            errors.append(f"{location}.status: approved requires passed outcomes, no unresolved deviation, and repair_scope none")
    elif status == "repair":
        if scope != "localized" or not any(
            deviation.get("severity") == "localized" for deviation in unresolved
        ) or any(deviation.get("severity") != "localized" for deviation in unresolved):
            errors.append(f"{location}.status: repair requires an unresolved localized deviation")
        if "fail" not in outcome_values:
            errors.append(f"{location}.status: repair requires a failing criterion outcome")
        if unresolved_criteria != failed_criteria:
            errors.append(
                f"{location}.status: repair decision must bind unresolved deviations "
                "to failed criteria"
            )
    elif status == "regenerate":
        if scope != "foundational" or not any(
            deviation.get("severity") == "foundational" for deviation in unresolved
        ) or any(deviation.get("severity") != "foundational" for deviation in unresolved):
            errors.append(f"{location}.status: regenerate requires an unresolved foundational deviation")
            if any(deviation.get("severity") != "foundational" for deviation in unresolved):
                errors.append(
                    f"{location}.status: regenerate requires unresolved foundational deviations only"
                )
        if "fail" not in outcome_values:
            errors.append(f"{location}.status: regenerate requires a failing criterion outcome")
        if unresolved_criteria != failed_criteria:
            errors.append(
                f"{location}.status: regenerate decision must bind unresolved deviations "
                "to failed criteria"
            )
    elif status == "human-review":
        handoff = item.get("human_review_handoff")
        reasons = {"subjective", "rights", "safety"}
        unresolved_reasons = {
            deviation.get("severity")
            for deviation in unresolved
            if deviation.get("severity") in reasons
        }
        if (
            scope != "human-handoff"
            or not any(deviation.get("severity") in reasons for deviation in unresolved)
            or not isinstance(handoff, Mapping)
            or handoff.get("reason") not in reasons
        ):
            errors.append(
                f"{location}.status: human-review requires an unresolved subjective, rights, or safety deviation and handoff"
            )
        if (
            isinstance(handoff, Mapping)
            and handoff.get("reason") in reasons
            and unresolved_reasons
            and handoff.get("reason") not in unresolved_reasons
        ):
            errors.append(
                f"{location}.human_review_handoff.reason: handoff reason "
                f"{handoff.get('reason')} must match an unresolved deviation"
            )
        if "not-assessable" not in outcome_values:
            errors.append(f"{location}.status: human-review requires a not-assessable criterion outcome")
        if unresolved_criteria != not_assessable_criteria:
            errors.append(
                f"{location}.status: human-review decision must bind unresolved deviations "
                "to not-assessable criteria"
            )

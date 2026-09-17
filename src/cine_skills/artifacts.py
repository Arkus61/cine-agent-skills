from __future__ import annotations

import json
import re
from collections.abc import Collection, Iterator
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing.exceptions import Unresolvable

from .edit_plans import validate_edit_plan_contract
from .fountain import validate_screenplay_metadata
from .media_prompts import validate_media_prompt_package_contract
from .media_review import validate_media_review_report_contract
from .music_plans import validate_music_plan_contract
from .sound_post_plans import validate_sound_post_plan_contract
from .vfx_post_plans import validate_vfx_post_plan_contract
from .color_plans import validate_color_plan_contract
from .titles_captions import validate_titles_captions_plan_contract
from .mastering_qc import validate_mastering_qc_plan_contract


_IDENTIFIER_CONTRACTS = {
    "visual-language-plan": (
        "rules",
        "rule_id",
        r"V[0-9]{2,}",
        "V##",
        (("beat_ids", r"B[0-9]{2,}", "B##"),),
    ),
    "lighting-plan": (
        "setups",
        "setup_id",
        r"L[0-9]{2,}",
        "L##",
        (
            ("beat_ids", r"B[0-9]{2,}", "B##"),
            ("shot_ids", r"SH[0-9]{3,}", "SH###"),
        ),
    ),
    "sound-plan": (
        "cues",
        "cue_id",
        r"A[0-9]{2,}",
        "A##",
        (
            ("beat_ids", r"B[0-9]{2,}", "B##"),
            ("shot_ids", r"SH[0-9]{3,}", "SH###"),
        ),
    ),
    "storyboard-plan": (
        "panels",
        "panel_id",
        r"SB[0-9]{3,}",
        "SB###",
        (("shot_id", r"SH[0-9]{3,}", "SH###", "single"),),
    ),
    "production-breakdown": (
        "items",
        "item_id",
        r"PD[0-9]{3,}",
        "PD###",
        (
            ("beat_ids", r"B[0-9]{2,}", "B##"),
            ("shot_ids", r"SH[0-9]{3,}", "SH###"),
        ),
    ),
    "continuity-plan": (
        "items",
        "continuity_id",
        r"CN[0-9]{3,}",
        "CN###",
        (("shot_ids", r"SH[0-9]{3,}", "SH###"),),
    ),
}


def _reject_nonstandard_json_constant(constant: str) -> None:
    raise ValueError(f"non-standard JSON constant {constant} is not permitted")


def strict_json_loads(document: str) -> Any:
    """Parse a standards-compliant JSON document."""
    return json.loads(document, parse_constant=_reject_nonstandard_json_constant)


def load_json_object(path: Path) -> tuple[Mapping[str, Any] | None, list[str]]:
    """Load a UTF-8 JSON object from a file."""
    try:
        payload = strict_json_loads(Path(path).read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        return None, [f"invalid UTF-8 JSON {path}: {exc}"]
    except OSError as exc:
        return None, [f"unable to read JSON {path}: {exc}"]
    except RecursionError:
        return None, [f"invalid JSON {path}: document exceeds nesting limit"]
    except ValueError as exc:
        return None, [f"invalid JSON {path}: {exc}"]

    if not isinstance(payload, dict):
        return None, [f"JSON object required: {path}"]
    return payload, []


def validate_artifact(
    schema_name: str, payload: Mapping[str, Any], root: Path
) -> list[str]:
    """Validate an artifact against a repository JSON schema."""
    schema_path = Path(root) / "schemas" / f"{schema_name}.schema.json"
    if not schema_path.exists():
        return [f"schema not found: {schema_path}"]
    try:
        schema = strict_json_loads(schema_path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        return [f"invalid UTF-8 schema {schema_path}: {exc}"]
    except RecursionError:
        return [f"invalid schema {schema_path}: document exceeds nesting limit"]
    except (OSError, ValueError) as exc:
        return [f"invalid schema {schema_path}: {exc}"]

    try:
        Draft202012Validator.check_schema(schema)
    except RecursionError:
        return [f"invalid schema {schema_path}: schema exceeds nesting limit"]
    except SchemaError as exc:
        return [f"invalid schema {schema_path}: {exc.message}"]

    try:
        validation_errors = sorted(
            Draft202012Validator(schema).iter_errors(payload),
            key=lambda item: list(item.path),
        )
    except Unresolvable as exc:
        return [f"invalid schema reference {schema_path}: {exc}"]
    except RecursionError:
        return [f"artifact validation for {schema_path} exceeds nesting limit"]

    errors = []
    for error in validation_errors:
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        errors.append(f"{location}: {error.message}")
    if schema_name == "media-review-report" and errors:
        return errors
    if schema_name == "edit-plan" and errors:
        return errors
    if schema_name == "sound-post-plan" and errors:
        return errors
    if schema_name == "music-plan" and errors:
        return errors
    if schema_name == "vfx-post-plan" and errors:
        return errors
    if schema_name == "color-plan" and errors:
        return errors
    if schema_name == "titles-captions-plan" and errors:
        return errors
    if schema_name == "mastering-qc-plan" and errors:
        return errors
    if schema_name in _IDENTIFIER_CONTRACTS:
        errors.extend(_validate_artifact_identifiers(schema_name, payload))
    if schema_name == "story-structure":
        errors.extend(_validate_story_structure_identifiers(payload))
    if schema_name == "story-concept":
        errors.extend(_validate_story_concept_contract(payload))
    if schema_name == "character-arcs":
        errors.extend(_validate_character_arc_identifiers(payload))
    if schema_name == "world-bible":
        errors.extend(_validate_world_bible_contract(payload))
    if schema_name == "season-arc":
        errors.extend(_validate_season_arc_contract(payload))
    if schema_name == "unit-outline":
        errors.extend(_validate_unit_outline_contract(payload))
    if schema_name == "screenplay-metadata":
        errors.extend(validate_screenplay_metadata(payload))
    if schema_name == "script-revision-plan":
        errors.extend(_validate_script_revision_plan_contract(payload))
    if schema_name == "production-design-plan":
        errors.extend(_validate_production_design_plan_contract(payload))
    if schema_name == "character-look-bible":
        errors.extend(_validate_character_look_bible_contract(payload))
    if schema_name == "animation-plan":
        errors.extend(_validate_animation_plan_contract(payload))
    if schema_name == "vfx-plan":
        errors.extend(_validate_vfx_plan_contract(payload))
    if schema_name == "media-prompt-package":
        errors.extend(validate_media_prompt_package_contract(payload))
    if schema_name == "media-review-report":
        errors.extend(validate_media_review_report_contract(payload))
    if schema_name == "edit-plan":
        errors.extend(validate_edit_plan_contract(payload))
    if schema_name == "sound-post-plan":
        errors.extend(validate_sound_post_plan_contract(payload))
    if schema_name == "music-plan":
        errors.extend(validate_music_plan_contract(payload))
    if schema_name == "vfx-post-plan":
        errors.extend(validate_vfx_post_plan_contract(payload))
    if schema_name == "color-plan":
        errors.extend(validate_color_plan_contract(payload))
    if schema_name == "titles-captions-plan":
        errors.extend(validate_titles_captions_plan_contract(payload))
    if schema_name == "mastering-qc-plan":
        errors.extend(validate_mastering_qc_plan_contract(payload))
    return errors


def _validate_vfx_plan_contract(payload: Mapping[str, Any]) -> list[str]:
    """Validate VFX references that JSON Schema cannot resolve."""
    errors: list[str] = []
    project_id = payload.get("project_id")
    project = project_id if isinstance(project_id, str) else ""
    context = payload.get("source_context")
    source_scene_ids: set[str] = set()
    source_shots: dict[str, Mapping[str, Any]] = {}
    source_fact_records: dict[str, set[tuple[str, str, str]]] = {}
    supplied_source_references: set[str] = set()
    if isinstance(context, Mapping):
        scenes = context.get("scenes")
        if isinstance(scenes, list):
            for scene_index, scene in enumerate(scenes):
                if not isinstance(scene, Mapping):
                    continue
                scene_id = scene.get("scene_id")
                source_reference = scene.get("source_reference")
                if isinstance(source_reference, str):
                    supplied_source_references.add(source_reference)
                if not isinstance(scene_id, str):
                    continue
                if scene_id in source_scene_ids:
                    errors.append(
                        f"source_context.scenes.{scene_index}.scene_id: duplicate "
                        f"supplied scene ID {scene_id}"
                    )
                else:
                    source_scene_ids.add(scene_id)
                if not scene_id.startswith(f"{project}-"):
                    errors.append(
                        f"source_context.scenes.{scene_index}.scene_id: "
                        f"{scene_id!r} must belong to project {project}"
                    )
        shots = context.get("shots")
        if isinstance(shots, list):
            for shot_index, shot in enumerate(shots):
                if not isinstance(shot, Mapping):
                    continue
                shot_id = shot.get("shot_id")
                scene_id = shot.get("scene_id")
                if not isinstance(shot_id, str):
                    continue
                if shot_id in source_shots:
                    errors.append(
                        f"source_context.shots.{shot_index}.shot_id: duplicate "
                        f"supplied shot ID {shot_id}"
                    )
                else:
                    source_shots[shot_id] = shot
                if not shot_id.startswith(f"{project}-"):
                    errors.append(
                        f"source_context.shots.{shot_index}.shot_id: "
                        f"{shot_id!r} must belong to project {project}"
                    )
                facts = shot.get("supplied_facts")
                shot_records = source_fact_records.setdefault(shot_id, set())
                if isinstance(facts, list):
                    fact_categories: set[str] = set()
                    for fact_index, fact in enumerate(facts):
                        if not isinstance(fact, Mapping):
                            continue
                        category = fact.get("category")
                        if isinstance(category, str):
                            fact_categories.add(category)
                        value = fact.get("value")
                        source_reference = fact.get("source_reference")
                        if not (
                            isinstance(category, str)
                            and isinstance(value, str)
                            and isinstance(source_reference, str)
                        ):
                            continue
                        supplied_source_references.add(source_reference)
                        record = (category, value, source_reference)
                        if record in shot_records:
                            errors.append(
                                f"source_context.shots.{shot_index}."
                                f"supplied_facts.{fact_index}: duplicate "
                                f"supplied fact for shot {shot_id}"
                            )
                        else:
                            shot_records.add(record)
                    for missing_category in sorted(
                        {"visual", "camera", "lens", "lighting", "performance"}
                        - fact_categories
                    ):
                        errors.append(
                            f"source_context.shots.{shot_index}.supplied_facts: "
                            f"missing required category {missing_category}"
                        )
                matching_scenes = [
                    supplied_scene
                    for supplied_scene in source_scene_ids
                    if shot_id.startswith(f"{supplied_scene}-SH")
                ]
                if (
                    len(matching_scenes) == 1
                    and isinstance(scene_id, str)
                    and scene_id != matching_scenes[0]
                ):
                    errors.append(
                        f"source_context.shots.{shot_index}.scene_id: {scene_id} "
                        f"does not match scene {matching_scenes[0]} encoded by "
                        f"shot {shot_id}"
                    )
                if (
                    isinstance(scene_id, str)
                    and scene_id not in source_scene_ids
                ):
                    errors.append(
                        f"source_context.shots.{shot_index}.scene_id: {scene_id} "
                        "is not declared in source_context.scenes"
                    )
                elif (
                    isinstance(scene_id, str)
                    and re.fullmatch(
                        rf"{re.escape(scene_id)}-SH[0-9]{{3,}}", shot_id
                    )
                    is None
                ):
                    errors.append(
                        f"source_context.shots.{shot_index}.shot_id: {shot_id} "
                        f"must encode declared scene {scene_id} as "
                        f"{scene_id}-SH###"
                    )
        if isinstance(scenes, list):
            supplied_scene_ids = {
                shot.get("scene_id")
                for shot in source_shots.values()
                if isinstance(shot.get("scene_id"), str)
            }
            for scene_index, scene in enumerate(scenes):
                scene_id = scene.get("scene_id") if isinstance(scene, Mapping) else None
                if isinstance(scene_id, str) and scene_id not in supplied_scene_ids:
                    errors.append(
                        f"source_context.scenes.{scene_index}.scene_id: declared scene "
                        f"{scene_id} has no supplied shot"
                    )

    uncertainties = payload.get("uncertainties")
    uncertainty_ids: set[str] = set()
    uncertainty_records: dict[str, Mapping[str, Any]] = {}
    positive_three = r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
    uncertainty_pattern = rf"{re.escape(project)}-UNC{positive_three}"
    if isinstance(uncertainties, list):
        for uncertainty_index, uncertainty in enumerate(uncertainties):
            if (
                isinstance(uncertainty, Mapping)
                and isinstance(uncertainty.get("uncertainty_id"), str)
            ):
                uncertainty_id = uncertainty["uncertainty_id"]
                if re.fullmatch(uncertainty_pattern, uncertainty_id) is None:
                    errors.append(
                        f"uncertainties.{uncertainty_index}.uncertainty_id: "
                        f"{uncertainty_id!r} must match {project}-UNC###"
                    )
                if uncertainty_id in uncertainty_ids:
                    errors.append(
                        f"uncertainties.{uncertainty_index}.uncertainty_id: "
                        f"duplicate uncertainty ID {uncertainty_id}"
                    )
                else:
                    uncertainty_ids.add(uncertainty_id)
                    uncertainty_records[uncertainty_id] = uncertainty

    approval_records: dict[str, Mapping[str, Any]] = {}
    approval_ids: set[str] = set()
    approval_pattern = rf"{re.escape(project)}-APR{positive_three}"
    approval_evidence = payload.get("approval_evidence")
    if isinstance(approval_evidence, list):
        for approval_index, approval in enumerate(approval_evidence):
            if not (
                isinstance(approval, Mapping)
                and isinstance(approval.get("approval_id"), str)
            ):
                continue
            approval_id = approval["approval_id"]
            if re.fullmatch(approval_pattern, approval_id) is None:
                errors.append(
                    f"approval_evidence.{approval_index}.approval_id: "
                    f"{approval_id!r} must match {project}-APR###"
                )
            if approval_id in approval_ids:
                errors.append(
                    f"approval_evidence.{approval_index}.approval_id: duplicate "
                    f"approval ID {approval_id}"
                )
            else:
                approval_ids.add(approval_id)
                approval_records[approval_id] = approval

    supplied_boundary_records: dict[str, Mapping[str, Any]] = {}
    supplied_boundary_ids: set[str] = set()
    supplied_boundary_pattern = rf"{re.escape(project)}-SBE{positive_three}"
    supplied_boundary_evidence = payload.get("supplied_boundary_evidence")
    if isinstance(supplied_boundary_evidence, list):
        for evidence_index, evidence in enumerate(supplied_boundary_evidence):
            if not (
                isinstance(evidence, Mapping)
                and isinstance(evidence.get("supplied_evidence_id"), str)
            ):
                continue
            evidence_id = evidence["supplied_evidence_id"]
            if re.fullmatch(supplied_boundary_pattern, evidence_id) is None:
                errors.append(
                    f"supplied_boundary_evidence.{evidence_index}."
                    f"supplied_evidence_id: {evidence_id!r} must match "
                    f"{project}-SBE###"
                )
            if evidence_id in supplied_boundary_ids:
                errors.append(
                    f"supplied_boundary_evidence.{evidence_index}."
                    f"supplied_evidence_id: duplicate supplied boundary evidence "
                    f"ID {evidence_id}"
                )
            else:
                supplied_boundary_ids.add(evidence_id)
                supplied_boundary_records[evidence_id] = evidence
            source_reference = evidence.get("source_reference")
            if (
                isinstance(source_reference, str)
                and source_reference not in supplied_source_references
            ):
                errors.append(
                    f"supplied_boundary_evidence.{evidence_index}."
                    f"source_reference: {source_reference} is not declared in "
                    "source_context"
                )

    effects = payload.get("effects")
    declared_effect_ids: set[str] = set()
    effect_shots: dict[str, set[str]] = {}
    effect_indices: dict[str, int] = {}
    effect_uncertainty_ids: dict[str, set[str]] = {}
    effect_pattern = rf"{re.escape(project)}-FX{positive_three}"
    if isinstance(effects, list):
        for effect_index, effect in enumerate(effects):
            if not isinstance(effect, Mapping):
                continue
            effect_id = effect.get("effect_id")
            if isinstance(effect_id, str):
                if re.fullmatch(effect_pattern, effect_id) is None:
                    errors.append(
                        f"effects.{effect_index}.effect_id: {effect_id!r} must "
                        f"match {project}-FX###"
                    )
                if effect_id in declared_effect_ids:
                    errors.append(
                        f"effects.{effect_index}.effect_id: duplicate effect ID "
                        f"{effect_id}"
                    )
                else:
                    declared_effect_ids.add(effect_id)
            shot_ids = effect.get("shot_ids")
            declared_effect_shots = {
                shot_id for shot_id in shot_ids if isinstance(shot_id, str)
            } if isinstance(shot_ids, list) else set()
            if isinstance(effect_id, str):
                effect_shots.setdefault(effect_id, declared_effect_shots)
                effect_indices.setdefault(effect_id, effect_index)
            uncertainty_values = effect.get("uncertainty_ids")
            declared_effect_uncertainties = {
                uncertainty_id
                for uncertainty_id in uncertainty_values
                if isinstance(uncertainty_id, str)
            } if isinstance(uncertainty_values, list) else set()
            if isinstance(effect_id, str):
                effect_uncertainty_ids.setdefault(
                    effect_id, declared_effect_uncertainties
                )
            if isinstance(uncertainty_values, list):
                for uncertainty_index, uncertainty_id in enumerate(uncertainty_values):
                    if (
                        isinstance(uncertainty_id, str)
                        and uncertainty_id not in uncertainty_ids
                    ):
                        errors.append(
                            f"effects.{effect_index}.uncertainty_ids."
                            f"{uncertainty_index}: unknown uncertainty "
                            f"{uncertainty_id}"
                        )
            if isinstance(shot_ids, list):
                for shot_index, shot_id in enumerate(shot_ids):
                    if isinstance(shot_id, str) and shot_id not in source_shots:
                        errors.append(
                            f"effects.{effect_index}.shot_ids.{shot_index}: "
                            f"unknown shot reference {shot_id}"
                        )
            boundary = effect.get("practical_digital_boundary")
            for container_name, state_name in (
                ("practical_digital_boundary", "status"),
                ("clean_plate", "decision"),
                ("tracking", "decision"),
                ("simulation", "status"),
            ):
                decision = effect.get(container_name)
                if not isinstance(decision, Mapping):
                    continue
                state = decision.get(state_name)
                uncertainty_id = decision.get("uncertainty_id")
                if state == "unresolved":
                    if not isinstance(uncertainty_id, str):
                        errors.append(
                            f"effects.{effect_index}.{container_name}."
                            "uncertainty_id: unresolved decision requires "
                            "uncertainty_id"
                        )
                    elif uncertainty_id not in uncertainty_ids:
                        errors.append(
                            f"effects.{effect_index}.{container_name}."
                            f"uncertainty_id: unknown uncertainty {uncertainty_id}"
                        )
                    else:
                        uncertainty = uncertainty_records.get(uncertainty_id)
                        owned_effects = (
                            uncertainty.get("effect_ids")
                            if isinstance(uncertainty, Mapping)
                            else None
                        )
                        if (
                            isinstance(effect_id, str)
                            and isinstance(owned_effects, list)
                            and effect_id not in owned_effects
                        ):
                            errors.append(
                                f"effects.{effect_index}.{container_name}."
                                f"uncertainty_id: {uncertainty_id} does not list "
                                f"effect {effect_id}"
                            )
                        owned_shots = (
                            uncertainty.get("shot_ids")
                            if isinstance(uncertainty, Mapping)
                            else None
                        )
                        if isinstance(owned_shots, list):
                            for shot_id in sorted(declared_effect_shots):
                                if shot_id not in owned_shots:
                                    errors.append(
                                        f"effects.{effect_index}.{container_name}."
                                        f"uncertainty_id: {uncertainty_id} does "
                                        f"not list shot {shot_id}"
                                    )
                elif state == "confirmed" and uncertainty_id is not None:
                    errors.append(
                        f"effects.{effect_index}.{container_name}."
                        "uncertainty_id: confirmed decision cannot retain "
                        "uncertainty_id"
                    )
                elif (
                    state in {"required", "waived", "not-required"}
                    and uncertainty_id is not None
                ):
                    errors.append(
                        f"effects.{effect_index}.{container_name}."
                        "uncertainty_id: resolved decision cannot retain "
                        "uncertainty_id"
                    )

                approval_kind = {
                    "practical_digital_boundary": "practical-digital-boundary",
                    "simulation": "simulation",
                }.get(container_name)
                if approval_kind is None:
                    continue
                approval_id = decision.get("approval_id")
                supplied_evidence_id = (
                    decision.get("supplied_evidence_id")
                    if container_name == "practical_digital_boundary"
                    else None
                )
                if state != "confirmed":
                    if approval_id is not None:
                        errors.append(
                            f"effects.{effect_index}.{container_name}."
                            "approval_id: unconfirmed decision cannot retain "
                            "approval_id"
                        )
                    if supplied_evidence_id is not None:
                        errors.append(
                            f"effects.{effect_index}.{container_name}."
                            "supplied_evidence_id: unconfirmed decision cannot "
                            "retain supplied_evidence_id"
                        )
                    continue
                if container_name == "practical_digital_boundary":
                    if approval_id is not None and supplied_evidence_id is not None:
                        errors.append(
                            f"effects.{effect_index}.practical_digital_boundary: "
                            "confirmed decision cannot retain both approval_id and "
                            "supplied_evidence_id"
                        )
                        continue
                    if isinstance(supplied_evidence_id, str):
                        supplied_evidence = supplied_boundary_records.get(
                            supplied_evidence_id
                        )
                        if supplied_evidence is None:
                            errors.append(
                                f"effects.{effect_index}."
                                "practical_digital_boundary.supplied_evidence_id: "
                                "unknown supplied boundary evidence "
                                f"{supplied_evidence_id}"
                            )
                            continue
                        supplied_shot_ids = supplied_evidence.get("shot_ids")
                        supplied_shot_set = {
                            shot_id
                            for shot_id in supplied_shot_ids
                            if isinstance(shot_id, str)
                        } if isinstance(supplied_shot_ids, list) else set()
                        if not (
                            supplied_evidence.get("effect_id") == effect_id
                            and supplied_shot_set == declared_effect_shots
                            and supplied_evidence.get("practical_scope")
                            == decision.get("practical_scope")
                            and supplied_evidence.get("digital_scope")
                            == decision.get("digital_scope")
                        ):
                            errors.append(
                                f"effects.{effect_index}."
                                "practical_digital_boundary.supplied_evidence_id: "
                                "supplied boundary evidence "
                                f"{supplied_evidence_id} does not exactly bind "
                                "this confirmed decision"
                            )
                        continue
                if not isinstance(approval_id, str):
                    evidence_requirement = (
                        "source-bound approval evidence or supplied boundary evidence"
                        if container_name == "practical_digital_boundary"
                        else "source-bound approval evidence"
                    )
                    errors.append(
                        f"effects.{effect_index}.{container_name}: confirmed "
                        f"decision requires {evidence_requirement}"
                    )
                    continue
                approval = approval_records.get(approval_id)
                if approval is None:
                    errors.append(
                        f"effects.{effect_index}.{container_name}.approval_id: "
                        f"unknown approval evidence {approval_id}"
                    )
                    continue
                approval_shot_ids = approval.get("shot_ids")
                approval_shot_set = {
                    shot_id
                    for shot_id in approval_shot_ids
                    if isinstance(shot_id, str)
                } if isinstance(approval_shot_ids, list) else set()
                approval_binds_decision = (
                    approval.get("kind") == approval_kind
                    and approval.get("effect_id") == effect_id
                    and approval_shot_set == declared_effect_shots
                )
                if not approval_binds_decision:
                    errors.append(
                        f"effects.{effect_index}.{container_name}.approval_id: "
                        f"approval evidence {approval_id} does not exactly bind "
                        "this confirmed decision"
                    )
                elif approval_kind == "simulation" and (
                    decision.get("requirements") != approval.get("requirements")
                ):
                    errors.append(
                        f"effects.{effect_index}.simulation.requirements: must "
                        f"exactly match approval evidence {approval_id}"
                    )
                elif approval_kind == "practical-digital-boundary":
                    for field in ("practical_scope", "digital_scope"):
                        if decision.get(field) != approval.get(field):
                            errors.append(
                                f"effects.{effect_index}."
                                f"practical_digital_boundary.{field}: must exactly "
                                f"match approval evidence {approval_id}"
                            )

            tracking = effect.get("tracking")
            if isinstance(tracking, Mapping):
                tracking_state = tracking.get("decision")
                tracking_requirements = tracking.get("requirements")
                if (
                    tracking_state == "required"
                    and isinstance(tracking_requirements, list)
                    and not tracking_requirements
                ):
                    errors.append(
                        f"effects.{effect_index}.tracking.requirements: "
                        "required tracking needs requirements"
                    )
                if (
                    tracking_state == "not-required"
                    and isinstance(tracking_requirements, list)
                    and tracking_requirements
                ):
                    errors.append(
                        f"effects.{effect_index}.tracking.requirements: "
                        "not-required tracking must have no requirements"
                    )

            simulation = effect.get("simulation")
            if isinstance(simulation, Mapping):
                simulation_state = simulation.get("status")
                simulation_requirements = simulation.get("requirements")
                if (
                    simulation_state == "confirmed"
                    and isinstance(simulation_requirements, list)
                    and not simulation_requirements
                ):
                    errors.append(
                        f"effects.{effect_index}.simulation.requirements: "
                        "confirmed simulation needs requirements"
                    )
                if (
                    simulation_state == "not-required"
                    and isinstance(simulation_requirements, list)
                    and simulation_requirements
                ):
                    errors.append(
                        f"effects.{effect_index}.simulation.requirements: "
                        "not-required simulation must have no requirements"
                    )

            safety = effect.get("human_safety_handoff")
            if isinstance(safety, Mapping):
                review = safety.get("review")
                if isinstance(review, str):
                    safety_location = (
                        f"effects.{effect_index}.human_safety_handoff.review"
                    )
                    if safety.get("required") is True:
                        qualified_human_review = re.search(
                            r"\bqualified\s+human(?:-safety)?\s+review(?:er)?\b|"
                            r"\bqualified\s+human(?:\s+[a-z-]+){0,3}\s+"
                            r"reviews?\b",
                            review,
                            re.IGNORECASE,
                        )
                        if qualified_human_review is None:
                            errors.append(
                                f"{safety_location}: required safety handoff "
                                "must state qualified human review"
                            )
                        review_without_negated_guarantees = re.sub(
                            r"\b(?:does\s+not|cannot|can\s+not|never)\s+"
                            r"guarantee(?:s|d|ing)?\b",
                            "",
                            review,
                            flags=re.IGNORECASE,
                        )
                        if re.search(
                            r"\bguarantee(?:s|d|ing)?\b",
                            review_without_negated_guarantees,
                            re.IGNORECASE,
                        ):
                            errors.append(
                                f"{safety_location}: required safety handoff "
                                "cannot guarantee safety outcomes"
                            )
                        if re.search(
                            r"\brisk[-\s]?free\b",
                            review,
                            re.IGNORECASE,
                        ):
                            errors.append(
                                f"{safety_location}: required safety handoff "
                                "cannot claim risk-free method"
                            )
                        if re.search(
                            r"\b(?:needs?|requires?)\s+no\s+"
                            r"(?:(?:qualified\s+)?human|specialist)\s+review\b|"
                            r"\bno\s+(?:(?:qualified\s+)?human(?:\s+safety)?\s+|"
                            r"specialist\s+)?review\s+(?:is\s+)?"
                            r"(?:needed|necessary|required)\b|"
                            r"\breview\s+(?:is\s+)?not\s+"
                            r"(?:needed|necessary|required)\b|"
                            r"\bneed\s+not\s+review\b",
                            review,
                            re.IGNORECASE,
                        ):
                            errors.append(
                                f"{safety_location}: required safety handoff "
                                "cannot waive specialist review"
                            )
                    if re.search(
                        r"\b(?:the\s+)?(?:planner|plan|agent|artifact)\s+"
                        r"(?:has\s+)?(?:approves?|clears?|certifies?)\b",
                        review,
                        re.IGNORECASE,
                    ):
                        errors.append(
                            f"{safety_location}: planner cannot approve "
                            "safety method"
                        )
                    if re.search(
                        r"\bno\s+(?:qualified\s+)?human\s+review\s+"
                        r"(?:is\s+)?(?:necessary|required)\b",
                        review,
                        re.IGNORECASE,
                    ):
                        errors.append(
                            f"{safety_location}: human review cannot be waived"
                        )
                    if re.search(
                        r"\b(?:is|are|was|were|be(?:en)?|deemed|considered)\s+"
                        r"(?:safe|approved|cleared|certified)\b",
                        review,
                        re.IGNORECASE,
                    ):
                        errors.append(
                            f"{safety_location}: safety handoff cannot claim "
                            "approval"
                        )

            metadata = effect.get("camera_lens_lighting_metadata")
            metadata_counts = {
                (shot_id, category): 0
                for shot_id in declared_effect_shots
                for category in ("camera", "lens", "lighting")
            }
            if isinstance(metadata, list):
                for metadata_index, claim in enumerate(metadata):
                    if not isinstance(claim, Mapping):
                        continue
                    claim_shot_id = claim.get("shot_id")
                    category = claim.get("category")
                    value = claim.get("value")
                    source_reference = claim.get("source_reference")
                    if not (
                        isinstance(claim_shot_id, str)
                        and isinstance(category, str)
                        and isinstance(value, str)
                        and isinstance(source_reference, str)
                    ):
                        continue
                    if claim_shot_id not in declared_effect_shots:
                        errors.append(
                            f"effects.{effect_index}."
                            f"camera_lens_lighting_metadata.{metadata_index}."
                            f"shot_id: {claim_shot_id} is not assigned to "
                            f"effect {effect_id}"
                        )
                    elif category in {"camera", "lens", "lighting"}:
                        metadata_counts[(claim_shot_id, category)] += 1

                    provenance_status = claim.get("provenance_status")
                    if provenance_status == "supplied" and (
                        category,
                        value,
                        source_reference,
                    ) not in source_fact_records.get(claim_shot_id, set()):
                        errors.append(
                            f"effects.{effect_index}."
                            f"camera_lens_lighting_metadata.{metadata_index}: "
                            "supplied claim must exactly match category, value, "
                            "and source_reference declared for shot "
                            f"{claim_shot_id}"
                        )
                    if provenance_status == "approved":
                        approval_id = claim.get("approval_id")
                        if not isinstance(approval_id, str):
                            errors.append(
                                f"effects.{effect_index}."
                                f"camera_lens_lighting_metadata.{metadata_index}: "
                                "approved claim requires source-bound approval "
                                "evidence"
                            )
                            continue
                        approval = approval_records.get(approval_id)
                        if approval is None:
                            errors.append(
                                f"effects.{effect_index}."
                                f"camera_lens_lighting_metadata.{metadata_index}."
                                f"approval_id: unknown approval evidence "
                                f"{approval_id}"
                            )
                            continue
                        if not (
                            approval.get("kind") == "metadata"
                            and approval.get("effect_id") == effect_id
                            and approval.get("shot_id") == claim_shot_id
                            and approval.get("category") == category
                            and approval.get("value") == value
                            and approval.get("source_reference") == source_reference
                        ):
                            errors.append(
                                f"effects.{effect_index}."
                                f"camera_lens_lighting_metadata.{metadata_index}."
                                f"approval_id: approval evidence {approval_id} "
                                "does not exactly bind approved metadata claim"
                            )
                    elif claim.get("approval_id") is not None:
                        errors.append(
                            f"effects.{effect_index}."
                            f"camera_lens_lighting_metadata.{metadata_index}."
                            "approval_id: non-approved claim cannot retain "
                            "approval_id"
                        )
            for shot_id in sorted(declared_effect_shots):
                for category in ("camera", "lens", "lighting"):
                    if metadata_counts[(shot_id, category)] != 1:
                        errors.append(
                            f"effects.{effect_index}."
                            "camera_lens_lighting_metadata: must contain "
                            f"exactly one {category} claim for shot {shot_id}"
                        )

    if isinstance(supplied_boundary_evidence, list):
        for evidence_index, evidence in enumerate(supplied_boundary_evidence):
            if not isinstance(evidence, Mapping):
                continue
            effect_id = evidence.get("effect_id")
            if not isinstance(effect_id, str) or effect_id not in effect_shots:
                if isinstance(effect_id, str):
                    errors.append(
                        f"supplied_boundary_evidence.{evidence_index}.effect_id: "
                        f"unknown effect {effect_id}"
                    )
                continue
            supplied_shot_ids = evidence.get("shot_ids")
            supplied_shot_set = {
                shot_id
                for shot_id in supplied_shot_ids
                if isinstance(shot_id, str)
            } if isinstance(supplied_shot_ids, list) else set()
            if supplied_shot_set != effect_shots[effect_id]:
                errors.append(
                    f"supplied_boundary_evidence.{evidence_index}.shot_ids: must "
                    f"exactly match shots assigned to effect {effect_id}"
                )

    applicability = payload.get("applicability")
    applicability_by_shot: dict[str, tuple[int, Mapping[str, Any]]] = {}
    if isinstance(applicability, list):
        for record_index, record in enumerate(applicability):
            if not isinstance(record, Mapping):
                continue
            shot_id = record.get("shot_id")
            if isinstance(shot_id, str):
                if shot_id in applicability_by_shot:
                    errors.append(
                        f"applicability.{record_index}.shot_id: duplicate "
                        f"classification for {shot_id}"
                    )
                else:
                    applicability_by_shot[shot_id] = (record_index, record)
                if shot_id not in source_shots:
                    errors.append(
                        f"applicability.{record_index}.shot_id: unknown supplied "
                        f"shot {shot_id}"
                    )
            applicability_effect_ids = record.get("effect_ids")
            if (
                record.get("classification") == "effect"
                and isinstance(applicability_effect_ids, list)
                and not applicability_effect_ids
            ):
                errors.append(
                    f"applicability.{record_index}.effect_ids: effect "
                    "classification requires at least one effect"
                )
            if (
                record.get("classification") == "no-vfx"
                and isinstance(applicability_effect_ids, list)
                and applicability_effect_ids
            ):
                errors.append(
                    f"applicability.{record_index}.effect_ids: no-vfx shot "
                    "cannot reference effects"
                )
            if isinstance(applicability_effect_ids, list):
                for effect_ref_index, effect_ref in enumerate(applicability_effect_ids):
                    if isinstance(effect_ref, str) and effect_ref not in effect_shots:
                        errors.append(
                            f"applicability.{record_index}.effect_ids."
                            f"{effect_ref_index}: unknown effect {effect_ref}"
                        )
                    elif (
                        isinstance(effect_ref, str)
                        and isinstance(shot_id, str)
                        and shot_id not in effect_shots.get(effect_ref, set())
                    ):
                        errors.append(
                            f"applicability.{record_index}.effect_ids."
                            f"{effect_ref_index}: effect {effect_ref} is not "
                            f"assigned to shot {shot_id}"
                        )

    for shot_id in sorted(source_shots):
        if shot_id not in applicability_by_shot:
            errors.append(
                f"applicability: missing classification for supplied shot {shot_id}"
            )
    for effect_id, assigned_shots in sorted(effect_shots.items()):
        for shot_id in sorted(assigned_shots):
            applicability_record = applicability_by_shot.get(shot_id)
            if applicability_record is None:
                continue
            record_index, record = applicability_record
            referenced_effects = record.get("effect_ids")
            if isinstance(referenced_effects, list) and effect_id not in referenced_effects:
                errors.append(
                    f"applicability.{record_index}.effect_ids: must list effect "
                    f"{effect_id} assigned to {shot_id}"
                )

    if isinstance(uncertainties, list):
        for uncertainty_index, uncertainty in enumerate(uncertainties):
            if not isinstance(uncertainty, Mapping):
                continue
            uncertainty_id = uncertainty.get("uncertainty_id")
            for field, known, label in (
                ("effect_ids", declared_effect_ids, "effect"),
                ("shot_ids", set(source_shots), "shot"),
            ):
                references = uncertainty.get(field)
                if not isinstance(references, list):
                    continue
                for reference_index, reference in enumerate(references):
                    if isinstance(reference, str) and reference not in known:
                        errors.append(
                            f"uncertainties.{uncertainty_index}.{field}."
                            f"{reference_index}: unknown {label} {reference}"
                        )
            effect_ids = uncertainty.get("effect_ids")
            expected_shot_ids: set[str] = set()
            if isinstance(effect_ids, list):
                for effect_id in effect_ids:
                    if isinstance(effect_id, str):
                        expected_shot_ids.update(effect_shots.get(effect_id, set()))
                        effect_index = effect_indices.get(effect_id)
                        if (
                            isinstance(uncertainty_id, str)
                            and effect_index is not None
                            and uncertainty_id
                            not in effect_uncertainty_ids.get(effect_id, set())
                        ):
                            errors.append(
                                f"effects.{effect_index}.uncertainty_ids: must "
                                f"list {uncertainty_id} owned by effect "
                                f"{effect_id}"
                            )
            shot_ids = uncertainty.get("shot_ids")
            if isinstance(shot_ids, list):
                declared_shot_ids = {
                    shot_id for shot_id in shot_ids if isinstance(shot_id, str)
                }
                for shot_index, shot_id in enumerate(shot_ids):
                    if (
                        isinstance(shot_id, str)
                        and shot_id in source_shots
                        and shot_id not in expected_shot_ids
                    ):
                        errors.append(
                            f"uncertainties.{uncertainty_index}.shot_ids."
                            f"{shot_index}: {shot_id} is not assigned to its "
                            "effects"
                        )
                for shot_id in sorted(expected_shot_ids - declared_shot_ids):
                    errors.append(
                        f"uncertainties.{uncertainty_index}.shot_ids: must list "
                        f"shot {shot_id} assigned to its effects"
                    )

    for effect_id, linked_uncertainty_ids in sorted(effect_uncertainty_ids.items()):
        effect_index = effect_indices.get(effect_id)
        if effect_index is None:
            continue
        for uncertainty_index, uncertainty_id in enumerate(
            sorted(linked_uncertainty_ids)
        ):
            uncertainty = uncertainty_records.get(uncertainty_id)
            if uncertainty is None:
                continue
            owned_effect_ids = uncertainty.get("effect_ids")
            if not (
                isinstance(owned_effect_ids, list)
                and effect_id in owned_effect_ids
            ):
                errors.append(
                    f"effects.{effect_index}.uncertainty_ids.{uncertainty_index}: "
                    f"uncertainty {uncertainty_id} does not list effect "
                    f"{effect_id}"
                )

    if isinstance(approval_evidence, list):
        for approval_index, approval in enumerate(approval_evidence):
            if not isinstance(approval, Mapping):
                continue
            effect_id = approval.get("effect_id")
            if not isinstance(effect_id, str) or effect_id not in effect_shots:
                continue
            expected_shot_ids = effect_shots[effect_id]
            kind = approval.get("kind")
            if kind == "metadata":
                shot_id = approval.get("shot_id")
                if isinstance(shot_id, str) and shot_id not in expected_shot_ids:
                    errors.append(
                        f"approval_evidence.{approval_index}.shot_id: {shot_id} "
                        f"is not assigned to effect {effect_id}"
                    )
                continue
            approval_shot_ids = approval.get("shot_ids")
            if not isinstance(approval_shot_ids, list):
                continue
            declared_shot_ids = {
                shot_id for shot_id in approval_shot_ids if isinstance(shot_id, str)
            }
            if declared_shot_ids != expected_shot_ids:
                errors.append(
                    f"approval_evidence.{approval_index}.shot_ids: must exactly "
                    f"match shots assigned to effect {effect_id}"
                )

    forbidden_content = re.compile(
        r"https?://|data:[^\s,;]+(?:;base64)?,|"
        r"\b(?:api[_-]?(?:key|token)|access[_-]?token|secret(?:[_-]?key)?|"
        r"bearer)\b\s*[:=]?|"
        r"\b(?:after\s+effects|(?:adobe\s+)?premiere(?:\s+pro)?|"
        r"davinci\s+resolve|avid|final\s+cut\s+pro|nuke|"
        r"(?:(?:use|using|in|with|via)\s+blackmagic\s+fusion|"
        r"(?:use|using|in|with|via)\s+fusion"
        r"(?!\s+(?:energy|reaction|reactor)\b))|maya|houdini|blender|"
        r"cinema\s*4d|unreal\s+engine)\b|"
        r"\b(?:budget|schedule|call\s+sheet|casting|procurement|"
        r"rights?\s+clearance|legal\s+(?:approval|decision))\b|"
        r"(?:[$€£]\s*\d)",
        re.IGNORECASE,
    )
    for location, node in _iter_bounded_artifact_nodes(payload):
        if isinstance(node, str) and forbidden_content.search(node):
            errors.append(f"{location}: forbidden operational content")
    return errors


def _validate_animation_supplied_facts(
    shot_index: int,
    shot_id: str,
    shot_character_ids: set[str],
    facts: object,
) -> list[str]:
    """Validate exact source-ledger records without treating them as claims."""
    if not isinstance(facts, list):
        return []

    errors: list[str] = []
    seen_records: set[tuple[str, str | None, str, str]] = set()
    for fact_index, fact in enumerate(facts):
        if not isinstance(fact, Mapping):
            continue
        scope = fact.get("scope")
        character_id = fact.get("character_id")
        value = fact.get("value")
        source_reference = fact.get("source_reference")
        if scope == "shot-character" and isinstance(character_id, str):
            if character_id not in shot_character_ids:
                errors.append(
                    f"source_context.shots.{shot_index}.supplied_facts."
                    f"{fact_index}.character_id: {character_id} is not declared "
                    f"for supplied shot {shot_id}"
                )
        if not (
            scope in {"shot", "shot-character"}
            and (isinstance(character_id, str) or character_id is None)
            and isinstance(value, str)
            and isinstance(source_reference, str)
        ):
            continue
        record = (scope, character_id, value, source_reference)
        if record not in seen_records:
            seen_records.add(record)
            continue
        owner = (
            f"shot {shot_id}"
            if scope == "shot"
            else f"shot-character {shot_id} / {character_id}"
        )
        errors.append(
            f"source_context.shots.{shot_index}.supplied_facts.{fact_index}: "
            f"duplicate supplied fact for {owner}"
        )
    return errors


def _collect_animation_source_context(
    payload: Mapping[str, Any], project_id: str
) -> tuple[
    list[str],
    Mapping[str, Any] | None,
    set[str] | None,
    dict[str, Mapping[str, Any]],
    set[tuple[str, str]],
    dict[str, str],
]:
    """Collect the supplied animation graph while reporting source errors."""
    errors: list[str] = []
    context = payload.get("source_context")
    known_character_ids: set[str] | None = None
    known_scene_ids: set[str] | None = None
    source_shots: dict[str, Mapping[str, Any]] = {}
    required_pairs: set[tuple[str, str]] = set()
    shot_lineage: dict[str, str] = {}
    seen_shot_ids: set[str] = set()
    seen_camera_intent_ids: set[str] = set()
    seen_performance_intent_ids: set[str] = set()
    if isinstance(context, Mapping):
        known_character_ids = _string_set(context.get("character_ids"))
        known_scene_ids = _string_set(context.get("scene_ids"))
        positive_three = r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
        character_pattern = rf"{re.escape(project_id)}-CH{positive_three}"
        source_character_values = context.get("character_ids")
        if isinstance(source_character_values, list):
            for character_index, character_id in enumerate(source_character_values):
                if (
                    isinstance(character_id, str)
                    and re.fullmatch(character_pattern, character_id) is None
                ):
                    errors.append(
                        f"source_context.character_ids.{character_index}: "
                        f"{character_id!r} must match {project_id}-CH###"
                    )
        source_scene_values = context.get("scene_ids")
        if isinstance(source_scene_values, list):
            for scene_index, scene_id in enumerate(source_scene_values):
                if (
                    isinstance(scene_id, str)
                    and not scene_id.startswith(f"{project_id}-")
                ):
                    errors.append(
                        f"source_context.scene_ids.{scene_index}: {scene_id!r} "
                        f"must belong to project {project_id}"
                    )
        shots = context.get("shots")
        if isinstance(shots, list):
            for shot_index, shot in enumerate(shots):
                if not isinstance(shot, Mapping):
                    continue
                scene_id = shot.get("scene_id")
                shot_id = shot.get("shot_id")
                if not isinstance(shot_id, str):
                    continue
                if shot_id in seen_shot_ids:
                    errors.append(
                        f"source_context.shots.{shot_index}.shot_id: duplicate "
                        f"supplied shot ID {shot_id}"
                    )
                else:
                    seen_shot_ids.add(shot_id)
                    source_shots[shot_id] = shot
                if not shot_id.startswith(f"{project_id}-"):
                    errors.append(
                        f"source_context.shots.{shot_index}.shot_id: "
                        f"{shot_id!r} must belong to project {project_id}"
                    )
                if (
                    isinstance(scene_id, str)
                    and known_scene_ids is not None
                    and scene_id not in known_scene_ids
                ):
                    errors.append(
                        f"source_context.shots.{shot_index}.scene_id: unknown "
                        f"supplied scene {scene_id}"
                    )
                if known_scene_ids is not None:
                    matching_scenes = [
                        supplied_scene
                        for supplied_scene in known_scene_ids
                        if shot_id.startswith(f"{supplied_scene}-SH")
                    ]
                    if len(matching_scenes) == 1:
                        supplied_scene = matching_scenes[0]
                        shot_lineage[shot_id] = supplied_scene
                        if (
                            isinstance(scene_id, str)
                            and scene_id != supplied_scene
                        ):
                            errors.append(
                                f"source_context.shots.{shot_index}.scene_id: "
                                f"{scene_id} does not match scene {supplied_scene} "
                                f"encoded by shot {shot_id}"
                            )
                character_ids = shot.get("character_ids")
                if isinstance(character_ids, list):
                    supplied_shot_characters = {
                        character_id
                        for character_id in character_ids
                        if isinstance(character_id, str)
                    }
                    required_pairs.update(
                        (shot_id, character_id)
                        for character_id in supplied_shot_characters
                    )
                    for character_index, character_id in enumerate(character_ids):
                        if (
                            isinstance(character_id, str)
                            and known_character_ids is not None
                            and character_id not in known_character_ids
                        ):
                            errors.append(
                                f"source_context.shots.{shot_index}."
                                f"character_ids.{character_index}: unknown "
                                f"supplied character {character_id}"
                            )
                    camera_intent = shot.get("camera_intent")
                    if isinstance(camera_intent, Mapping):
                        camera_id = camera_intent.get("intent_id")
                        camera_pattern = (
                            rf"{re.escape(project_id)}-CI"
                            r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
                        )
                        if (
                            isinstance(camera_id, str)
                            and re.fullmatch(camera_pattern, camera_id) is None
                        ):
                            errors.append(
                                f"source_context.shots.{shot_index}."
                                f"camera_intent.intent_id: {camera_id!r} must "
                                f"match {project_id}-CI###"
                            )
                        if isinstance(camera_id, str):
                            if camera_id in seen_camera_intent_ids:
                                errors.append(
                                    f"source_context.shots.{shot_index}."
                                    "camera_intent.intent_id: duplicate supplied "
                                    f"camera intent ID {camera_id}"
                                )
                            else:
                                seen_camera_intent_ids.add(camera_id)
                    performance_characters: set[str] = set()
                    performance_intents = shot.get("performance_intents")
                    if isinstance(performance_intents, list):
                        for intent_index, intent in enumerate(performance_intents):
                            if not isinstance(intent, Mapping):
                                continue
                            performance_id = intent.get("intent_id")
                            performance_pattern = (
                                rf"{re.escape(project_id)}-PI"
                                r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
                            )
                            if (
                                isinstance(performance_id, str)
                                and re.fullmatch(
                                    performance_pattern, performance_id
                                )
                                is None
                            ):
                                errors.append(
                                    f"source_context.shots.{shot_index}."
                                    f"performance_intents.{intent_index}."
                                    f"intent_id: {performance_id!r} must match "
                                    f"{project_id}-PI###"
                                )
                            if isinstance(performance_id, str):
                                if performance_id in seen_performance_intent_ids:
                                    errors.append(
                                        f"source_context.shots.{shot_index}."
                                        f"performance_intents.{intent_index}."
                                        "intent_id: duplicate supplied "
                                        f"performance intent ID {performance_id}"
                                    )
                                else:
                                    seen_performance_intent_ids.add(performance_id)
                            intent_character = intent.get("character_id")
                            if isinstance(intent_character, str):
                                if intent_character in performance_characters:
                                    errors.append(
                                        f"source_context.shots.{shot_index}."
                                        f"performance_intents.{intent_index}."
                                        "character_id: duplicate supplied "
                                        "performance intent for "
                                        f"{intent_character}"
                                    )
                                else:
                                    performance_characters.add(intent_character)
                                if intent_character not in supplied_shot_characters:
                                    errors.append(
                                        f"source_context.shots.{shot_index}."
                                        f"performance_intents.{intent_index}."
                                        f"character_id: {intent_character} is "
                                        "not declared for supplied shot "
                                        f"{shot_id}"
                                    )
                    for character_id in sorted(
                        supplied_shot_characters - performance_characters
                    ):
                        errors.append(
                            f"source_context.shots.{shot_index}."
                            "performance_intents: missing supplied performance "
                            f"intent for {character_id}"
                        )
                    errors.extend(
                        _validate_animation_supplied_facts(
                            shot_index,
                            shot_id,
                            supplied_shot_characters,
                            shot.get("supplied_facts"),
                        )
                    )
                timing_context = context.get("timing")
                if (
                    isinstance(timing_context, Mapping)
                    and timing_context.get("unit") == "frames"
                ):
                    duration = shot.get("duration")
                    if (
                        isinstance(duration, (int, float))
                        and not isinstance(duration, bool)
                        and not isinstance(duration, int)
                    ):
                        errors.append(
                            f"source_context.shots.{shot_index}.duration: frame "
                            f"timing must be an integer, got {duration}"
                        )

    return (
        errors,
        context if isinstance(context, Mapping) else None,
        known_character_ids,
        source_shots,
        required_pairs,
        shot_lineage,
    )


def _collect_animation_reference_owners(
    plans: list[object],
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Index plan-owned references without assuming schema-valid records."""
    beat_owners: dict[str, str] = {}
    pose_owners: dict[str, str] = {}
    continuity_owners: dict[str, str] = {}
    for plan in plans:
        if not isinstance(plan, Mapping):
            continue
        declared_plan_id = plan.get("animation_plan_id")
        declared_character_id = plan.get("character_id")
        if not isinstance(declared_plan_id, str):
            continue
        for collection_name, id_name, owners in (
            ("acting_beats", "acting_beat_id", beat_owners),
            ("key_poses", "key_pose_id", pose_owners),
        ):
            records = plan.get(collection_name)
            if not isinstance(records, list):
                continue
            for record in records:
                if not isinstance(record, Mapping):
                    continue
                identifier = record.get(id_name)
                if isinstance(identifier, str):
                    owners.setdefault(identifier, declared_plan_id)
        continuity = plan.get("continuity")
        continuity_id = (
            continuity.get("continuity_id")
            if isinstance(continuity, Mapping)
            else None
        )
        if (
            isinstance(continuity_id, str)
            and isinstance(declared_character_id, str)
        ):
            continuity_owners.setdefault(continuity_id, declared_character_id)
    return beat_owners, pose_owners, continuity_owners


def _validate_animation_source_bindings(
    base: str,
    plan: Mapping[str, Any],
    source_shot: Mapping[str, Any] | None,
) -> list[str]:
    """Require a plan to bind the exact supplied camera and performance intent."""
    bindings = plan.get("source_bindings")
    if not isinstance(source_shot, Mapping) or not isinstance(bindings, Mapping):
        return []

    errors: list[str] = []
    camera_intent = source_shot.get("camera_intent")
    supplied_camera_id = (
        camera_intent.get("intent_id")
        if isinstance(camera_intent, Mapping)
        else None
    )
    bound_camera_id = bindings.get("camera_intent_id")
    if (
        isinstance(bound_camera_id, str)
        and isinstance(supplied_camera_id, str)
        and bound_camera_id != supplied_camera_id
    ):
        errors.append(
            f"{base}.source_bindings.camera_intent_id: {bound_camera_id} "
            f"does not bind the supplied camera intent {supplied_camera_id}"
        )

    character_id = plan.get("character_id")
    supplied_performance_id: str | None = None
    performance_intents = source_shot.get("performance_intents")
    if isinstance(performance_intents, list):
        for intent in performance_intents:
            if (
                isinstance(intent, Mapping)
                and intent.get("character_id") == character_id
                and isinstance(intent.get("intent_id"), str)
            ):
                supplied_performance_id = intent["intent_id"]
                break
    bound_performance_id = bindings.get("performance_intent_id")
    if (
        isinstance(bound_performance_id, str)
        and isinstance(supplied_performance_id, str)
        and bound_performance_id != supplied_performance_id
    ):
        errors.append(
            f"{base}.source_bindings.performance_intent_id: "
            f"{bound_performance_id} does not bind supplied performance "
            f"intent {supplied_performance_id} for {character_id}"
        )
    return errors


def _index_animation_supplied_facts(
    source_shot: Mapping[str, Any],
) -> tuple[set[tuple[str, str]], dict[str, set[tuple[str, str]]]]:
    """Index exact source-ledger pairs by their declared applicability."""
    shot_pairs: set[tuple[str, str]] = set()
    character_pairs: dict[str, set[tuple[str, str]]] = {}
    facts = source_shot.get("supplied_facts")
    if not isinstance(facts, list):
        return shot_pairs, character_pairs
    for fact in facts:
        if not isinstance(fact, Mapping):
            continue
        scope = fact.get("scope")
        character_id = fact.get("character_id")
        value = fact.get("value")
        source_reference = fact.get("source_reference")
        if not isinstance(value, str) or not isinstance(source_reference, str):
            continue
        pair = (value, source_reference)
        if scope == "shot" and character_id is None:
            shot_pairs.add(pair)
        elif scope == "shot-character" and isinstance(character_id, str):
            character_pairs.setdefault(character_id, set()).add(pair)
    return shot_pairs, character_pairs


_ANIMATION_SUPPLIED_CLAIM_FIELDS = (
    "value",
    "action",
    "performance",
    "pose",
    "readability",
    "intent",
    "entry_state",
    "exit_state",
)


def _validate_animation_supplied_claim_bindings(
    base: str,
    plan: Mapping[str, Any],
    source_shot: Mapping[str, Any] | None,
) -> list[str]:
    """Bind every downstream supplied claim to its exact scoped source pair."""
    shot_id = plan.get("shot_id")
    character_id = plan.get("character_id")
    if not (
        isinstance(source_shot, Mapping)
        and isinstance(shot_id, str)
        and isinstance(character_id, str)
    ):
        return []

    errors: list[str] = []
    shot_pairs, character_pairs = _index_animation_supplied_facts(source_shot)
    for location, node in _iter_bounded_artifact_nodes(plan):
        if not isinstance(node, Mapping):
            continue
        provenance = node.get("provenance")
        if not (
            isinstance(provenance, Mapping)
            and provenance.get("status") == "supplied"
        ):
            continue
        source_reference = provenance.get("source_reference")
        if not isinstance(source_reference, str):
            continue
        is_shot_claim = location == "camera_relationship"
        declared_pairs = (
            shot_pairs
            if is_shot_claim
            else character_pairs.get(character_id, set())
        )
        owner = (
            f"shot {shot_id}"
            if is_shot_claim
            else f"shot-character {shot_id} / {character_id}"
        )
        for field in _ANIMATION_SUPPLIED_CLAIM_FIELDS:
            value = node.get(field)
            if isinstance(value, str) and (value, source_reference) not in declared_pairs:
                errors.append(
                    f"{base}.{location}.{field}: supplied claim must exactly "
                    "match value and source_reference declared for "
                    f"{owner}"
                )
    return errors


def _validate_animation_time_range(
    location: str,
    timing: object,
    frame_timing: bool,
) -> tuple[list[str], tuple[int | float, int | float] | None]:
    """Validate one nonempty half-open animation range."""
    if not isinstance(timing, Mapping):
        return [], None
    errors: list[str] = []
    start = timing.get("start")
    end = timing.get("end")
    if frame_timing:
        for timing_name, timing_value in (("start", start), ("end", end)):
            if (
                isinstance(timing_value, (int, float))
                and not isinstance(timing_value, bool)
                and not isinstance(timing_value, int)
            ):
                errors.append(
                    f"{location}.{timing_name}: frame timing must be an integer, "
                    f"got {timing_value}"
                )
    if not (
        isinstance(start, (int, float))
        and not isinstance(start, bool)
        and isinstance(end, (int, float))
        and not isinstance(end, bool)
    ):
        return errors, None
    if start >= end:
        errors.append(
            f"{location}: start {start} must be less than end {end}"
        )
    return errors, (start, end)


def _validate_animation_continuity_chains(
    records_by_character: Mapping[
        str, list[tuple[str, str, int, str | None]]
    ],
) -> list[str]:
    """Validate character-owned continuity order and predecessor links."""
    errors: list[str] = []
    for character_id, records in sorted(records_by_character.items()):
        orders = [record[2] for record in records]
        if orders != list(range(1, len(records) + 1)):
            errors.append(
                f"shot_character_plans: {character_id} continuity order "
                f"must be ascending 1..{len(records)}"
            )
        for record_index, (base, continuity_id, _order, previous_id) in enumerate(
            records
        ):
            expected_previous = records[record_index - 1][1] if record_index else None
            if previous_id != expected_previous:
                errors.append(
                    f"{base}.continuity.previous_continuity_id: continuity "
                    f"{continuity_id} must follow {expected_previous}"
                )
    return errors


def _validate_animation_plan_contract(
    payload: Mapping[str, Any],
) -> list[str]:
    project_id = payload.get("project_id")
    if not isinstance(project_id, str):
        return []

    (
        errors,
        context,
        known_character_ids,
        source_shots,
        required_pairs,
        shot_lineage,
    ) = _collect_animation_source_context(payload, project_id)

    timing_context = context.get("timing") if isinstance(context, Mapping) else None
    frame_timing = (
        isinstance(timing_context, Mapping)
        and timing_context.get("unit") == "frames"
    )

    plans_value = payload.get("shot_character_plans")
    plans = plans_value if isinstance(plans_value, list) else []
    covered_pairs: set[tuple[str, str]] = set()
    plan_ids: set[str] = set()
    beat_owners, pose_owners, continuity_owners = (
        _collect_animation_reference_owners(plans)
    )
    plan_pattern = (
        rf"{re.escape(project_id)}-AP"
        r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
    )
    seen_nested_ids: dict[str, set[str]] = {
        "acting beat": set(),
        "key pose": set(),
        "hold": set(),
        "simulation": set(),
        "continuity": set(),
    }
    continuity_records: dict[
        str, list[tuple[str, str, int, str | None]]
    ] = {}
    for plan_index, plan in enumerate(plans):
        if not isinstance(plan, Mapping):
            continue
        base = f"shot_character_plans.{plan_index}"
        plan_id = plan.get("animation_plan_id")
        if isinstance(plan_id, str):
            if plan_id in plan_ids:
                errors.append(
                    f"{base}.animation_plan_id: duplicate animation plan ID "
                    f"{plan_id}"
                )
            else:
                plan_ids.add(plan_id)
            if re.fullmatch(plan_pattern, plan_id) is None:
                errors.append(
                    f"{base}.animation_plan_id: {plan_id!r} must match "
                    f"{project_id}-AP###"
                )
        character_id = plan.get("character_id")
        if (
            isinstance(character_id, str)
            and known_character_ids is not None
            and character_id not in known_character_ids
        ):
            errors.append(
                f"{base}.character_id: unknown supplied character {character_id}"
            )
        shot_id = plan.get("shot_id")
        if isinstance(shot_id, str) and shot_id not in source_shots:
            errors.append(f"{base}.shot_id: unknown supplied shot {shot_id}")
        if isinstance(shot_id, str) and isinstance(character_id, str):
            pair = (shot_id, character_id)
            if pair in covered_pairs:
                errors.append(
                    f"{base}: duplicate shot-character plan {shot_id} / "
                    f"{character_id}"
                )
            else:
                covered_pairs.add(pair)
        plan_scene_id = plan.get("scene_id")
        supplied_scene = shot_lineage.get(shot_id) if isinstance(shot_id, str) else None
        if (
            isinstance(plan_scene_id, str)
            and supplied_scene is not None
            and plan_scene_id != supplied_scene
        ):
            errors.append(
                f"{base}.scene_id: {plan_scene_id} does not match supplied "
                f"scene {supplied_scene} for shot {shot_id}"
            )

        source_shot = source_shots.get(shot_id) if isinstance(shot_id, str) else None
        source_shot_character_ids = (
            _string_set(source_shot.get("character_ids"))
            if isinstance(source_shot, Mapping)
            else None
        )
        if (
            isinstance(character_id, str)
            and isinstance(shot_id, str)
            and source_shot_character_ids is not None
            and character_id not in source_shot_character_ids
        ):
            errors.append(
                f"{base}.character_id: {character_id} is not declared for "
                f"supplied shot {shot_id}"
            )
        duration = (
            source_shot.get("duration")
            if isinstance(source_shot, Mapping)
            else None
        )
        errors.extend(_validate_animation_source_bindings(base, plan, source_shot))
        errors.extend(
            _validate_animation_supplied_claim_bindings(base, plan, source_shot)
        )

        beats = plan.get("acting_beats")
        beat_intervals: dict[str, tuple[int | float, int | float]] = {}
        previous_end: int | float | None = None
        last_end: int | float | None = None
        if isinstance(beats, list):
            for beat_index, beat in enumerate(beats):
                if not isinstance(beat, Mapping):
                    continue
                beat_id = beat.get("acting_beat_id")
                if isinstance(beat_id, str) and isinstance(plan_id, str):
                    if beat_id in seen_nested_ids["acting beat"]:
                        errors.append(
                            f"{base}.acting_beats.{beat_index}.acting_beat_id: "
                            f"duplicate acting beat ID {beat_id}"
                        )
                    else:
                        seen_nested_ids["acting beat"].add(beat_id)
                    nested_pattern = (
                        rf"{re.escape(plan_id)}-AB"
                        r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
                    )
                    if re.fullmatch(nested_pattern, beat_id) is None:
                        errors.append(
                            f"{base}.acting_beats.{beat_index}.acting_beat_id: "
                            f"{beat_id!r} must match {plan_id}-AB###"
                        )
                timing = beat.get("timing")
                timing_errors, beat_interval = _validate_animation_time_range(
                    f"{base}.acting_beats.{beat_index}.timing",
                    timing,
                    frame_timing,
                )
                errors.extend(timing_errors)
                if beat_interval is None:
                    continue
                start, end = beat_interval
                if isinstance(beat_id, str):
                    beat_intervals.setdefault(beat_id, beat_interval)
                if beat_index == 0 and start != 0:
                    errors.append(
                        f"{base}.acting_beats: timeline must start at 0, "
                        f"got {start}"
                    )
                if beat_index > 0 and previous_end is not None and start != previous_end:
                    errors.append(
                        f"{base}.acting_beats.{beat_index}.timing.start: "
                        f"{start} must equal previous end {previous_end}"
                    )
                if (
                    isinstance(duration, (int, float))
                    and not isinstance(duration, bool)
                    and end > duration
                ):
                    errors.append(
                        f"{base}.acting_beats.{beat_index}.timing.end: "
                        f"{end} exceeds supplied duration {duration}"
                    )
                previous_end = end
                last_end = end
            if (
                isinstance(duration, (int, float))
                and not isinstance(duration, bool)
                and last_end is not None
                and last_end != duration
                and last_end <= duration
            ):
                errors.append(
                    f"{base}.acting_beats: timeline must end at supplied "
                    f"duration {duration}, got {last_end}"
                )

        poses = plan.get("key_poses")
        pose_beats: dict[str, str] = {}
        if isinstance(poses, list):
            for pose_index, pose in enumerate(poses):
                if not isinstance(pose, Mapping):
                    continue
                pose_id = pose.get("key_pose_id")
                if isinstance(pose_id, str) and isinstance(plan_id, str):
                    if pose_id in seen_nested_ids["key pose"]:
                        errors.append(
                            f"{base}.key_poses.{pose_index}.key_pose_id: "
                            f"duplicate key pose ID {pose_id}"
                        )
                    else:
                        seen_nested_ids["key pose"].add(pose_id)
                    nested_pattern = (
                        rf"{re.escape(plan_id)}-KP"
                        r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
                    )
                    if re.fullmatch(nested_pattern, pose_id) is None:
                        errors.append(
                            f"{base}.key_poses.{pose_index}.key_pose_id: "
                            f"{pose_id!r} must match {plan_id}-KP###"
                        )
                beat_reference = pose.get("acting_beat_id")
                if isinstance(pose_id, str) and isinstance(beat_reference, str):
                    pose_beats.setdefault(pose_id, beat_reference)
                reference_owner = (
                    beat_owners.get(beat_reference)
                    if isinstance(beat_reference, str)
                    else None
                )
                if (
                    isinstance(beat_reference, str)
                    and isinstance(plan_id, str)
                    and reference_owner is None
                ):
                    errors.append(
                        f"{base}.key_poses.{pose_index}.acting_beat_id: "
                        f"unknown beat reference {beat_reference}"
                    )
                elif (
                    isinstance(beat_reference, str)
                    and isinstance(plan_id, str)
                    and reference_owner != plan_id
                ):
                    errors.append(
                        f"{base}.key_poses.{pose_index}.acting_beat_id: beat "
                        f"{beat_reference} belongs to plan {reference_owner}, "
                        f"not {plan_id}"
                    )
                at = pose.get("at")
                if (
                    frame_timing
                    and isinstance(at, (int, float))
                    and not isinstance(at, bool)
                    and not isinstance(at, int)
                ):
                    errors.append(
                        f"{base}.key_poses.{pose_index}.at: frame timing must "
                        f"be an integer, got {at}"
                    )
                interval = (
                    beat_intervals.get(beat_reference)
                    if isinstance(beat_reference, str)
                    else None
                )
                if (
                    interval is not None
                    and isinstance(at, (int, float))
                    and not isinstance(at, bool)
                    and not (interval[0] <= at < interval[1])
                ):
                    errors.append(
                        f"{base}.key_poses.{pose_index}.at: {at} must fall "
                        f"inside beat {beat_reference} interval "
                        f"[{interval[0]}, {interval[1]})"
                    )

        holds = plan.get("holds")
        if isinstance(holds, list):
            for hold_index, hold in enumerate(holds):
                if not isinstance(hold, Mapping):
                    continue
                hold_id = hold.get("hold_id")
                if isinstance(hold_id, str) and isinstance(plan_id, str):
                    if hold_id in seen_nested_ids["hold"]:
                        errors.append(
                            f"{base}.holds.{hold_index}.hold_id: duplicate "
                            f"hold ID {hold_id}"
                        )
                    else:
                        seen_nested_ids["hold"].add(hold_id)
                    nested_pattern = (
                        rf"{re.escape(plan_id)}-HD"
                        r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
                    )
                    if re.fullmatch(nested_pattern, hold_id) is None:
                        errors.append(
                            f"{base}.holds.{hold_index}.hold_id: {hold_id!r} "
                            f"must match {plan_id}-HD###"
                        )
                beat_reference = hold.get("acting_beat_id")
                reference_owner = (
                    beat_owners.get(beat_reference)
                    if isinstance(beat_reference, str)
                    else None
                )
                if (
                    isinstance(beat_reference, str)
                    and isinstance(plan_id, str)
                    and reference_owner is None
                ):
                    errors.append(
                        f"{base}.holds.{hold_index}.acting_beat_id: unknown "
                        f"beat reference {beat_reference}"
                    )
                elif (
                    isinstance(beat_reference, str)
                    and isinstance(plan_id, str)
                    and reference_owner != plan_id
                ):
                    errors.append(
                        f"{base}.holds.{hold_index}.acting_beat_id: beat "
                        f"{beat_reference} belongs to plan {reference_owner}, "
                        f"not {plan_id}"
                    )
                pose_reference = hold.get("key_pose_id")
                pose_owner = (
                    pose_owners.get(pose_reference)
                    if isinstance(pose_reference, str)
                    else None
                )
                if (
                    isinstance(pose_reference, str)
                    and isinstance(plan_id, str)
                    and pose_owner is None
                ):
                    errors.append(
                        f"{base}.holds.{hold_index}.key_pose_id: unknown pose "
                        f"reference {pose_reference}"
                    )
                elif (
                    isinstance(pose_reference, str)
                    and isinstance(plan_id, str)
                    and pose_owner != plan_id
                ):
                    errors.append(
                        f"{base}.holds.{hold_index}.key_pose_id: pose "
                        f"{pose_reference} belongs to plan {pose_owner}, not "
                        f"{plan_id}"
                    )
                pose_beat = (
                    pose_beats.get(pose_reference)
                    if isinstance(pose_reference, str)
                    else None
                )
                if (
                    isinstance(pose_reference, str)
                    and isinstance(beat_reference, str)
                    and pose_beat is not None
                    and pose_beat != beat_reference
                ):
                    errors.append(
                        f"{base}.holds.{hold_index}.key_pose_id: pose "
                        f"{pose_reference} belongs to beat {pose_beat}, not "
                        f"{beat_reference}"
                    )
                interval = (
                    beat_intervals.get(beat_reference)
                    if isinstance(beat_reference, str)
                    else None
                )
                hold_timing = hold.get("timing")
                timing_errors, hold_interval = _validate_animation_time_range(
                    f"{base}.holds.{hold_index}.timing",
                    hold_timing,
                    frame_timing,
                )
                errors.extend(timing_errors)
                if interval is not None and hold_interval is not None:
                    hold_start, hold_end = hold_interval
                    if not (
                        interval[0] <= hold_start and hold_end <= interval[1]
                    ):
                        errors.append(
                            f"{base}.holds.{hold_index}.timing: interval "
                            f"[{hold_start}, {hold_end}) must fall inside beat "
                            f"{beat_reference} interval "
                            f"[{interval[0]}, {interval[1]})"
                        )

        simulations = plan.get("simulations")
        if isinstance(simulations, list):
            for simulation_index, simulation in enumerate(simulations):
                if not isinstance(simulation, Mapping):
                    continue
                simulation_id = simulation.get("simulation_id")
                if isinstance(simulation_id, str) and isinstance(plan_id, str):
                    if simulation_id in seen_nested_ids["simulation"]:
                        errors.append(
                            f"{base}.simulations.{simulation_index}."
                            f"simulation_id: duplicate simulation ID "
                            f"{simulation_id}"
                        )
                    else:
                        seen_nested_ids["simulation"].add(simulation_id)
                    nested_pattern = (
                        rf"{re.escape(plan_id)}-SM"
                        r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
                    )
                    if re.fullmatch(nested_pattern, simulation_id) is None:
                        errors.append(
                            f"{base}.simulations.{simulation_index}."
                            f"simulation_id: {simulation_id!r} must match "
                            f"{plan_id}-SM###"
                        )
                certainty = simulation.get("certainty")
                if (
                    simulation.get("method_confirmation") == "confirmed"
                    and simulation.get("method") == "undetermined"
                ):
                    errors.append(
                        f"{base}.simulations.{simulation_index}.method: "
                        "undetermined method cannot be confirmed"
                    )
                if (
                    simulation.get("method_confirmation") == "unconfirmed"
                    and certainty in {"confirmed", "approved"}
                ):
                    errors.append(
                        f"{base}.simulations.{simulation_index}.certainty: "
                        "unconfirmed simulation method must remain assumption, "
                        f"not {certainty}"
                    )

        continuity = plan.get("continuity")
        if isinstance(continuity, Mapping):
            continuity_id = continuity.get("continuity_id")
            if isinstance(continuity_id, str) and isinstance(plan_id, str):
                if continuity_id in seen_nested_ids["continuity"]:
                    errors.append(
                        f"{base}.continuity.continuity_id: duplicate "
                        f"continuity ID {continuity_id}"
                    )
                else:
                    seen_nested_ids["continuity"].add(continuity_id)
                nested_pattern = (
                    rf"{re.escape(plan_id)}-CT"
                    r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
                )
                if re.fullmatch(nested_pattern, continuity_id) is None:
                    errors.append(
                        f"{base}.continuity.continuity_id: "
                        f"{continuity_id!r} must match {plan_id}-CT###"
                    )
            previous_id = continuity.get("previous_continuity_id")
            previous_owner = (
                continuity_owners.get(previous_id)
                if isinstance(previous_id, str)
                else None
            )
            if (
                isinstance(previous_id, str)
                and isinstance(character_id, str)
                and previous_owner is not None
                and previous_owner != character_id
            ):
                errors.append(
                    f"{base}.continuity.previous_continuity_id: continuity "
                    f"{previous_id} belongs to character {previous_owner}, not "
                    f"{character_id}"
                )
            order = continuity.get("order")
            if (
                isinstance(character_id, str)
                and isinstance(continuity_id, str)
                and isinstance(order, int)
                and not isinstance(order, bool)
            ):
                continuity_records.setdefault(character_id, []).append(
                    (base, continuity_id, order, previous_id)
                )

    errors.extend(_validate_animation_continuity_chains(continuity_records))

    for shot_id, character_id in sorted(required_pairs - covered_pairs):
        errors.append(
            "shot_character_plans: missing supplied shot-character plan "
            f"{shot_id} / {character_id}"
        )
    errors.extend(_validate_forbidden_artifact_content(payload))
    return errors


def _validate_character_look_bible_contract(
    payload: Mapping[str, Any],
) -> list[str]:
    project_id = payload.get("project_id")
    if not isinstance(project_id, str):
        return []

    errors: list[str] = []
    positive_three = r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
    character_pattern = rf"{re.escape(project_id)}-CH{positive_three}"
    anchor_pattern = rf"{character_pattern}-AN{positive_three}"
    state_pattern = rf"{character_pattern}-ST{positive_three}"
    reference_pattern = rf"{character_pattern}-RF{positive_three}"
    drift_pattern = rf"{character_pattern}-DR{positive_three}"
    context = payload.get("source_context")
    known_character_ids: set[str] | None = None
    known_scene_ids: set[str] | None = None
    known_shot_ids: set[str] | None = None
    shot_lineage: dict[str, str] = {}
    supplied_identity_text: dict[str, list[str]] = {}
    supplied_claim_pairs: dict[str, set[tuple[str, str]]] = {}
    if isinstance(context, Mapping):
        known_character_ids = _string_set(context.get("character_ids"))
        known_scene_ids = _string_set(context.get("scene_ids"))
        source_character_values = context.get("character_ids")
        if isinstance(source_character_values, list):
            for character_index, character_id in enumerate(
                source_character_values
            ):
                if (
                    isinstance(character_id, str)
                    and re.fullmatch(character_pattern, character_id) is None
                ):
                    errors.append(
                        f"source_context.character_ids.{character_index}: "
                        f"{character_id!r} must match {project_id}-CH###"
                    )
        source_scene_values = context.get("scene_ids")
        if isinstance(source_scene_values, list):
            for scene_index, scene_id in enumerate(source_scene_values):
                if (
                    isinstance(scene_id, str)
                    and not scene_id.startswith(f"{project_id}-")
                ):
                    errors.append(
                        f"source_context.scene_ids.{scene_index}: {scene_id!r} "
                        f"must belong to project {project_id}"
                    )
        identity_statements = context.get("identity_statements")
        if isinstance(identity_statements, list):
            for identity_index, identity_statement in enumerate(
                identity_statements
            ):
                if not isinstance(identity_statement, Mapping):
                    continue
                identity_character_id = identity_statement.get("character_id")
                if (
                    isinstance(identity_character_id, str)
                    and known_character_ids is not None
                    and identity_character_id not in known_character_ids
                ):
                    errors.append(
                        f"source_context.identity_statements.{identity_index}."
                        f"character_id: unknown supplied character "
                        f"{identity_character_id}"
                    )
                claim = identity_statement.get("claim")
                if (
                    isinstance(identity_character_id, str)
                    and isinstance(claim, Mapping)
                    and isinstance(claim.get("value"), str)
                ):
                    supplied_identity_text.setdefault(
                        identity_character_id, []
                    ).append(claim["value"])
                    provenance = claim.get("provenance")
                    source_reference = (
                        provenance.get("source_reference")
                        if isinstance(provenance, Mapping)
                        and provenance.get("status") == "supplied"
                        else None
                    )
                    if isinstance(source_reference, str):
                        pair = (claim["value"], source_reference)
                        declared_pairs = supplied_claim_pairs.setdefault(
                            identity_character_id, set()
                        )
                        if pair in declared_pairs:
                            errors.append(
                                "source_context.identity_statements."
                                f"{identity_index}.claim: duplicate supplied "
                                "claim pair for character "
                                f"{identity_character_id}"
                            )
                        else:
                            declared_pairs.add(pair)
        known_shot_ids = set()
        shots = context.get("shots")
        if isinstance(shots, list):
            for shot_index, shot in enumerate(shots):
                if not isinstance(shot, Mapping):
                    continue
                scene_id = shot.get("scene_id")
                shot_id = shot.get("shot_id")
                if not isinstance(shot_id, str):
                    continue
                known_shot_ids.add(shot_id)
                if not shot_id.startswith(f"{project_id}-"):
                    errors.append(
                        f"source_context.shots.{shot_index}.shot_id: "
                        f"{shot_id!r} must belong to project {project_id}"
                    )
                if known_scene_ids is None:
                    continue
                matching_scenes = [
                    supplied_scene
                    for supplied_scene in known_scene_ids
                    if shot_id.startswith(f"{supplied_scene}-SH")
                ]
                if len(matching_scenes) != 1:
                    errors.append(
                        f"source_context.shots.{shot_index}.shot_id: supplied "
                        f"shot {shot_id} does not belong to exactly one supplied scene"
                    )
                    continue
                supplied_scene = matching_scenes[0]
                shot_lineage[shot_id] = supplied_scene
                if isinstance(scene_id, str) and scene_id != supplied_scene:
                    errors.append(
                        f"source_context.shots.{shot_index}.scene_id: {scene_id} "
                        f"does not match scene {supplied_scene} encoded by shot "
                        f"{shot_id}"
                    )

    characters_value = payload.get("characters")
    characters = characters_value if isinstance(characters_value, list) else []
    character_ids: set[str] = set()
    anchor_ids: set[str] = set()
    anchor_owners: dict[str, str] = {}
    side_anchor_requirements: dict[str, set[str]] = {}
    drift_anchor_references: list[tuple[str, str, str | None]] = []
    for character_index, character in enumerate(characters):
        if not isinstance(character, Mapping):
            continue
        character_id = character.get("character_id")
        if isinstance(character_id, str):
            character_location = f"characters.{character_index}.character_id"
            if character_id in character_ids:
                errors.append(
                    f"{character_location}: duplicate character ID {character_id}"
                )
            else:
                character_ids.add(character_id)
            if re.fullmatch(character_pattern, character_id) is None:
                errors.append(
                    f"{character_location}: {character_id!r} must match "
                    f"{project_id}-CH###"
                )
            if (
                known_character_ids is not None
                and character_id not in known_character_ids
            ):
                errors.append(
                    f"{character_location}: unknown supplied character "
                    f"{character_id}"
                )
        visual_treatment = character.get("visual_treatment")
        if isinstance(visual_treatment, Mapping):
            provenance = visual_treatment.get("provenance")
            if (
                isinstance(provenance, Mapping)
                and provenance.get("status") != "proposed"
            ):
                errors.append(
                    f"characters.{character_index}.visual_treatment.provenance."
                    "status: visual treatment must be proposed, distinct from "
                    "supplied identity"
                )
        anchors = character.get("immutable_anchors")
        if isinstance(anchors, list):
            for anchor_index, anchor in enumerate(anchors):
                if not isinstance(anchor, Mapping):
                    continue
                anchor_id = anchor.get("anchor_id")
                if isinstance(anchor_id, str):
                    anchor_ids.add(anchor_id)
                    if isinstance(character_id, str):
                        anchor_owners.setdefault(anchor_id, character_id)
                    if re.fullmatch(anchor_pattern, anchor_id) is None:
                        errors.append(
                            f"characters.{character_index}.immutable_anchors."
                            f"{anchor_index}.anchor_id: {anchor_id!r} must match "
                            f"{project_id}-CH###-AN###"
                        )
                    if (
                        isinstance(character_id, str)
                        and not anchor_id.startswith(f"{character_id}-AN")
                    ):
                        errors.append(
                            f"characters.{character_index}.immutable_anchors."
                            f"{anchor_index}.anchor_id: {anchor_id} must belong "
                            f"to character {character_id}"
                        )
                if isinstance(character_id, str):
                    side_text_parts = [anchor.get("aspect")]
                    anchor_claim = anchor.get("claim")
                    if isinstance(anchor_claim, Mapping):
                        side_text_parts.append(anchor_claim.get("value"))
                    side_text = " ".join(
                        part.lower()
                        for part in side_text_parts
                        if isinstance(part, str)
                    )
                    for side in ("left", "right"):
                        if re.search(rf"\b{side}\b", side_text):
                            side_anchor_requirements.setdefault(
                                character_id, set()
                            ).add(side)
        drift_rules = character.get("prohibited_drift")
        if isinstance(drift_rules, list):
            for drift_index, drift_rule in enumerate(drift_rules):
                if not isinstance(drift_rule, Mapping):
                    continue
                drift_id = drift_rule.get("drift_id")
                if (
                    isinstance(drift_id, str)
                    and re.fullmatch(drift_pattern, drift_id) is None
                ):
                    errors.append(
                        f"characters.{character_index}.prohibited_drift."
                        f"{drift_index}.drift_id: {drift_id!r} must match "
                        f"{project_id}-CH###-DR###"
                    )
                if (
                    isinstance(drift_id, str)
                    and isinstance(character_id, str)
                    and not drift_id.startswith(f"{character_id}-DR")
                ):
                    errors.append(
                        f"characters.{character_index}.prohibited_drift."
                        f"{drift_index}.drift_id: {drift_id} must belong to "
                        f"character {character_id}"
                    )
                drift_anchor_ids = drift_rule.get("anchor_ids")
                if isinstance(drift_anchor_ids, list):
                    for anchor_reference_index, anchor_reference in enumerate(
                        drift_anchor_ids
                    ):
                        if isinstance(anchor_reference, str):
                            drift_anchor_references.append(
                                (
                                    f"characters.{character_index}."
                                    f"prohibited_drift.{drift_index}.anchor_ids."
                                    f"{anchor_reference_index}",
                                    anchor_reference,
                                    character_id
                                    if isinstance(character_id, str)
                                    else None,
                                )
                            )

    for location, anchor_reference, character_id in drift_anchor_references:
        if anchor_reference not in anchor_ids:
            errors.append(
                f"{location}: unknown anchor reference {anchor_reference}"
            )
        elif (
            character_id is not None
            and anchor_owners.get(anchor_reference) != character_id
        ):
            errors.append(
                f"{location}: anchor {anchor_reference} belongs to character "
                f"{anchor_owners[anchor_reference]}, not {character_id}"
            )

    states_value = payload.get("continuity_states")
    states = states_value if isinstance(states_value, list) else []
    state_ids: set[str] = set()
    state_owners: dict[str, str] = {}
    state_records_by_character: dict[
        str, list[tuple[int, str | None, int | None, object]]
    ] = {}
    for state_index, state in enumerate(states):
        if not isinstance(state, Mapping):
            continue
        state_id = state.get("state_id")
        if isinstance(state_id, str):
            location = f"continuity_states.{state_index}.state_id"
            if state_id in state_ids:
                errors.append(f"{location}: duplicate state ID {state_id}")
            else:
                state_ids.add(state_id)
            if re.fullmatch(state_pattern, state_id) is None:
                errors.append(
                    f"{location}: {state_id!r} must match "
                    f"{project_id}-CH###-ST###"
                )
        character_id = state.get("character_id")
        if isinstance(character_id, str):
            if isinstance(state_id, str):
                state_owners.setdefault(state_id, character_id)
            if character_id not in character_ids:
                errors.append(
                    f"continuity_states.{state_index}.character_id: unknown "
                    f"character reference {character_id}"
                )
            if (
                isinstance(state_id, str)
                and not state_id.startswith(f"{character_id}-ST")
            ):
                errors.append(
                    f"continuity_states.{state_index}.state_id: {state_id} "
                    f"must belong to character {character_id}"
                )
            state_records_by_character.setdefault(character_id, []).append(
                (
                    state_index,
                    state_id if isinstance(state_id, str) else None,
                    state.get("order")
                    if isinstance(state.get("order"), int)
                    and not isinstance(state.get("order"), bool)
                    else None,
                    state.get("previous_state_id"),
                )
            )
        scene_id = state.get("scene_id")
        if (
            isinstance(scene_id, str)
            and known_scene_ids is not None
            and scene_id not in known_scene_ids
        ):
            errors.append(
                f"continuity_states.{state_index}.scene_id: unknown scene "
                f"reference {scene_id}"
            )
        shot_ids = state.get("shot_ids")
        if isinstance(shot_ids, list):
            for shot_reference_index, shot_id in enumerate(shot_ids):
                if not isinstance(shot_id, str):
                    continue
                if known_shot_ids is not None and shot_id not in known_shot_ids:
                    errors.append(
                        f"continuity_states.{state_index}.shot_ids."
                        f"{shot_reference_index}: unknown shot reference {shot_id}"
                    )
                supplied_scene = shot_lineage.get(shot_id)
                if (
                    supplied_scene is not None
                    and isinstance(scene_id, str)
                    and scene_id != supplied_scene
                ):
                    errors.append(
                        f"continuity_states.{state_index}.scene_id: {scene_id} "
                        f"does not match supplied scene {supplied_scene} for shot "
                        f"{shot_id}"
                    )
        effects = state.get("anchor_effects")
        if not isinstance(effects, list):
            continue
        for effect_index, effect in enumerate(effects):
            if not isinstance(effect, Mapping):
                continue
            anchor_id = effect.get("anchor_id")
            if isinstance(anchor_id, str):
                if anchor_id not in anchor_ids:
                    errors.append(
                        f"continuity_states.{state_index}.anchor_effects."
                        f"{effect_index}.anchor_id: unknown anchor reference "
                        f"{anchor_id}"
                    )
                elif (
                    isinstance(character_id, str)
                    and anchor_owners.get(anchor_id) != character_id
                ):
                    errors.append(
                        f"continuity_states.{state_index}.anchor_effects."
                        f"{effect_index}.anchor_id: anchor {anchor_id} belongs "
                        f"to character {anchor_owners[anchor_id]}, not "
                        f"{character_id}"
                    )
                elif effect.get("effect") == "contradict":
                    errors.append(
                        f"continuity_states.{state_index}.anchor_effects."
                        f"{effect_index}.effect: immutable anchor {anchor_id} "
                        "cannot be contradicted"
                    )

    for character_id, character_states in state_records_by_character.items():
        orders = [record[2] for record in character_states]
        expected_orders = list(range(1, len(character_states) + 1))
        if all(order is not None for order in orders) and orders != expected_orders:
            errors.append(
                f"continuity_states: {character_id} state order must be "
                f"ascending 1..{len(character_states)}"
            )
        for local_index, (
            state_index,
            state_id,
            _order,
            previous_state_id,
        ) in enumerate(character_states):
            if (
                isinstance(previous_state_id, str)
                and previous_state_id not in state_ids
            ):
                errors.append(
                    f"continuity_states.{state_index}.previous_state_id: "
                    f"unknown state reference {previous_state_id}"
                )
            expected_previous = (
                None if local_index == 0 else character_states[local_index - 1][1]
            )
            if previous_state_id != expected_previous:
                if local_index == 0:
                    errors.append(
                        f"continuity_states.{state_index}.previous_state_id: "
                        f"first state {state_id} must use null"
                    )
                elif isinstance(expected_previous, str):
                    errors.append(
                        f"continuity_states.{state_index}.previous_state_id: "
                        f"state {state_id} must follow {expected_previous}"
                    )

    references_value = payload.get("reference_needs")
    references = references_value if isinstance(references_value, list) else []
    reference_ids: set[str] = set()
    reference_owners: dict[str, str] = {}
    reference_states: dict[str, set[str]] = {}
    front_turnaround_characters: set[str] = set()
    views_by_character: dict[str, set[str]] = {}
    for reference_index, reference in enumerate(references):
        if not isinstance(reference, Mapping):
            continue
        reference_id = reference.get("reference_id")
        if not isinstance(reference_id, str):
            continue
        location = f"reference_needs.{reference_index}.reference_id"
        if reference_id in reference_ids:
            errors.append(
                f"{location}: duplicate reference ID {reference_id}"
            )
        else:
            reference_ids.add(reference_id)
        if re.fullmatch(reference_pattern, reference_id) is None:
            errors.append(
                f"{location}: {reference_id!r} must match "
                f"{project_id}-CH###-RF###"
            )
        character_id = reference.get("character_id")
        if isinstance(character_id, str):
            reference_owners.setdefault(reference_id, character_id)
            if character_id not in character_ids:
                errors.append(
                    f"reference_needs.{reference_index}.character_id: unknown "
                    f"character reference {character_id}"
                )
            if not reference_id.startswith(f"{character_id}-RF"):
                errors.append(
                    f"reference_needs.{reference_index}.reference_id: "
                    f"{reference_id} must belong to character {character_id}"
                )
        if (
            isinstance(character_id, str)
            and reference.get("view") == "front-turnaround"
        ):
            front_turnaround_characters.add(character_id)
        if isinstance(character_id, str) and isinstance(
            reference.get("view"), str
        ):
            views_by_character.setdefault(character_id, set()).add(
                reference["view"]
            )
        declared_reference_states: set[str] = set()
        reference_state_ids = reference.get("state_ids")
        if isinstance(reference_state_ids, list):
            for state_reference_index, state_reference in enumerate(
                reference_state_ids
            ):
                if not isinstance(state_reference, str):
                    continue
                declared_reference_states.add(state_reference)
                if state_reference not in state_ids:
                    errors.append(
                        f"reference_needs.{reference_index}.state_ids."
                        f"{state_reference_index}: unknown state reference "
                        f"{state_reference}"
                    )
                elif (
                    isinstance(character_id, str)
                    and state_owners.get(state_reference) != character_id
                ):
                    errors.append(
                        f"reference_needs.{reference_index}.state_ids."
                        f"{state_reference_index}: state {state_reference} "
                        f"belongs to character {state_owners[state_reference]}, "
                        f"not {character_id}"
                    )
        reference_states.setdefault(reference_id, set()).update(
            declared_reference_states
        )

    for character_id in sorted(character_ids - front_turnaround_characters):
        errors.append(
            f"reference_needs: character {character_id} is missing required "
            "front-turnaround coverage"
        )
    for character_id in sorted(side_anchor_requirements):
        for side in sorted(side_anchor_requirements[character_id]):
            required_view = f"profile-{side}"
            if required_view not in views_by_character.get(character_id, set()):
                errors.append(
                    f"reference_needs: character {character_id} has a {side}-side "
                    f"immutable anchor but is missing required {required_view} "
                    "coverage"
                )

    coverage_value = payload.get("shot_coverage")
    coverage = coverage_value if isinstance(coverage_value, list) else []
    covered_shots: set[str] = set()
    covered_character_shots: set[tuple[str, str]] = set()
    for coverage_index, entry in enumerate(coverage):
        if not isinstance(entry, Mapping):
            continue
        scene_id = entry.get("scene_id")
        shot_id = entry.get("shot_id")
        if isinstance(shot_id, str):
            covered_shots.add(shot_id)
            entry_character_id = entry.get("character_id")
            coverage_key = (
                (shot_id, entry_character_id)
                if isinstance(entry_character_id, str)
                else None
            )
            if coverage_key is not None and coverage_key in covered_character_shots:
                errors.append(
                    f"shot_coverage.{coverage_index}.shot_id: duplicate shot "
                    f"coverage {shot_id}"
                )
            elif coverage_key is not None:
                covered_character_shots.add(coverage_key)
            if known_shot_ids is not None and shot_id not in known_shot_ids:
                errors.append(
                    f"shot_coverage.{coverage_index}.shot_id: unknown shot "
                    f"reference {shot_id}"
                )
            supplied_scene = shot_lineage.get(shot_id)
            if (
                supplied_scene is not None
                and isinstance(scene_id, str)
                and scene_id != supplied_scene
            ):
                errors.append(
                    f"shot_coverage.{coverage_index}.scene_id: {scene_id} does "
                    f"not match supplied scene {supplied_scene} for shot {shot_id}"
                )
        coverage_character_id = entry.get("character_id")
        if (
            isinstance(coverage_character_id, str)
            and coverage_character_id not in character_ids
        ):
            errors.append(
                f"shot_coverage.{coverage_index}.character_id: unknown character "
                f"reference {coverage_character_id}"
            )
        state_id = entry.get("state_id")
        if isinstance(state_id, str) and state_id not in state_ids:
            errors.append(
                f"shot_coverage.{coverage_index}.state_id: unknown state "
                f"reference {state_id}"
            )
        elif (
            isinstance(state_id, str)
            and isinstance(coverage_character_id, str)
            and state_owners.get(state_id) != coverage_character_id
        ):
            errors.append(
                f"shot_coverage.{coverage_index}.state_id: state {state_id} "
                f"belongs to character {state_owners[state_id]}, not "
                f"{coverage_character_id}"
            )
        entry_reference_ids = entry.get("reference_ids")
        if isinstance(entry_reference_ids, list):
            for reference_index, reference_id in enumerate(entry_reference_ids):
                if not isinstance(reference_id, str):
                    continue
                if reference_id not in reference_ids:
                    errors.append(
                        f"shot_coverage.{coverage_index}.reference_ids."
                        f"{reference_index}: unknown reference {reference_id}"
                    )
                elif (
                    isinstance(coverage_character_id, str)
                    and reference_owners.get(reference_id)
                    != coverage_character_id
                ):
                    errors.append(
                        f"shot_coverage.{coverage_index}.reference_ids."
                        f"{reference_index}: reference {reference_id} belongs "
                        f"to character {reference_owners[reference_id]}, not "
                        f"{coverage_character_id}"
                    )
                elif (
                    isinstance(state_id, str)
                    and state_id in state_ids
                    and state_id not in reference_states.get(reference_id, set())
                ):
                    errors.append(
                        f"shot_coverage.{coverage_index}.reference_ids."
                        f"{reference_index}: reference {reference_id} does not "
                        f"cover state {state_id}"
                    )

    if known_shot_ids is not None:
        for missing_shot in sorted(known_shot_ids - covered_shots):
            errors.append(f"shot_coverage: missing supplied shot {missing_shot}")

    errors.extend(
        _validate_supplied_character_claim_bindings(
            payload, supplied_claim_pairs
        )
    )

    errors.extend(_validate_forbidden_artifact_content(payload))

    sensitive_patterns = (
        ("ethnicity", re.compile(r"\b(?:ethnicity|ethnic|race|nationality)\b", re.I)),
        ("disability", re.compile(r"\b(?:disability|disabled)\b", re.I)),
        ("age", re.compile(r"\bage\b|\b\d+\s+years? old\b", re.I)),
        (
            "sex/gender",
            re.compile(
                r"\b(?:sex|gender|woman|man|female|male|nonbinary)\b", re.I
            ),
        ),
        ("diagnosis", re.compile(r"\b(?:diagnosis|diagnosed)\b", re.I)),
        ("body detail", re.compile(r"\bbody detail\b|\banatomy\b", re.I)),
    )
    for character_index, character in enumerate(characters):
        if not isinstance(character, Mapping):
            continue
        character_id = character.get("character_id")
        source_text = " ".join(
            supplied_identity_text.get(character_id, [])
            if isinstance(character_id, str)
            else []
        )
        for relative_location, node in _iter_character_look_nodes(character):
            if not isinstance(node, Mapping):
                continue
            value = node.get("value")
            provenance = node.get("provenance")
            if not isinstance(value, str) or not isinstance(provenance, Mapping):
                continue
            status = provenance.get("status")
            if status not in {"inferred", "proposed"}:
                continue
            for category, pattern in sensitive_patterns:
                if (
                    _has_unrestrained_sensitive_term(value, pattern)
                    and not pattern.search(source_text)
                ):
                    location = f"characters.{character_index}"
                    if relative_location:
                        location += f".{relative_location}"
                    errors.append(
                        f"{location}.value: unsupported {status} sensitive "
                        f"identity category {category!r} absent from "
                        "source_context.identity_statements"
                    )

    return errors


def _validate_supplied_character_claim_bindings(
    payload: Mapping[str, Any],
    supplied_claim_pairs: Mapping[str, set[tuple[str, str]]],
) -> list[str]:
    """Bind supplied appearance claims to exact, character-owned source pairs."""
    errors: list[str] = []
    for collection_name in (
        "characters",
        "continuity_states",
        "reference_needs",
    ):
        records = payload.get(collection_name)
        if not isinstance(records, list):
            continue
        for record_index, record in enumerate(records):
            if not isinstance(record, Mapping):
                continue
            character_id = record.get("character_id")
            if not isinstance(character_id, str):
                continue
            declared_pairs = supplied_claim_pairs.get(character_id, set())
            for relative_location, node in _iter_character_look_nodes(record):
                if not isinstance(node, Mapping):
                    continue
                value = node.get("value")
                provenance = node.get("provenance")
                if (
                    not isinstance(value, str)
                    or not isinstance(provenance, Mapping)
                    or provenance.get("status") != "supplied"
                ):
                    continue
                source_reference = provenance.get("source_reference")
                if (
                    isinstance(source_reference, str)
                    and (value, source_reference) in declared_pairs
                ):
                    continue
                location = f"{collection_name}.{record_index}"
                if relative_location != "$":
                    location += f".{relative_location}"
                errors.append(
                    f"{location}: supplied claim must exactly match a value "
                    "and source_reference declared for character "
                    f"{character_id} in source_context.identity_statements"
                )
    return errors


def _has_unrestrained_sensitive_term(
    value: str, sensitive_pattern: re.Pattern[str]
) -> bool:
    """Distinguish explicit restraint from an unsupported identity assertion."""
    restraint_pattern = re.compile(
        r"\bnot\s+(?:supplied|provided|established|specified|assigned|inferred|"
        r"applicable)\b|"
        r"\bno\b.*\b(?:supplied|provided|established|specified|assigned|"
        r"inferred|introduced)\b|"
        r"\b(?:none|neither)\b.*\b(?:assigned|inferred|specified|supplied|"
        r"introduced)\b|"
        r"\b(?:is|are|remains?)\s+(?:unknown|unspecified|unassigned|unresolved)\b",
        re.IGNORECASE,
    )
    positive_action_pattern = re.compile(
        r"\b(?:infer|invent|assign|set|choose|depict|portray|specify|establish|"
        r"introduce|add)\b",
        re.IGNORECASE,
    )
    for clause in re.split(r"[.;\n]+", value):
        if not sensitive_pattern.search(clause):
            continue
        if restraint_pattern.search(clause) and not positive_action_pattern.search(
            clause
        ):
            continue
        return True
    return False


def _iter_bounded_artifact_nodes(
    value: object,
) -> Iterator[tuple[str, object]]:
    """Yield bounded artifact paths without recursive traversal."""
    stack: list[tuple[object, str, int]] = [(value, "", 0)]
    visited = 0
    while stack and visited < 10_000:
        node, location, depth = stack.pop()
        visited += 1
        if depth > 100:
            continue
        yield location or "$", node
        if isinstance(node, Mapping):
            for key, child in reversed(list(node.items())):
                child_location = f"{location}.{key}" if location else str(key)
                stack.append((child, child_location, depth + 1))
        elif isinstance(node, list):
            for index in range(len(node) - 1, -1, -1):
                child_location = f"{location}.{index}" if location else str(index)
                stack.append((node[index], child_location, depth + 1))


def _iter_character_look_nodes(
    value: object,
) -> Iterator[tuple[str, object]]:
    """Retain the domain name for callers while sharing bounded traversal."""
    yield from _iter_bounded_artifact_nodes(value)


def _validate_forbidden_artifact_content(
    payload: Mapping[str, Any],
) -> list[str]:
    """Reject embedded transport, credential, and media payload strings."""
    errors: list[str] = []
    forbidden_content = re.compile(
        r"https?://|data:[^\s,;]+(?:;base64)?,|"
        r"\b(?:api[_-]?key|access[_-]?token|secret[_-]?key|bearer)\b\s*[:=]?",
        re.IGNORECASE,
    )
    for location, node in _iter_bounded_artifact_nodes(payload):
        if isinstance(node, str) and forbidden_content.search(node):
            errors.append(
                f"{location}: forbidden URL, credential, or encoded-media content"
            )
    return errors


def _validate_production_design_plan_contract(
    payload: Mapping[str, Any],
) -> list[str]:
    project_id = payload.get("project_id")
    if not isinstance(project_id, str):
        return []

    errors: list[str] = []
    assets_value = payload.get("assets")
    assets = assets_value if isinstance(assets_value, list) else []
    asset_ids: set[str] = set()
    asset_pattern = (
        rf"{re.escape(project_id)}-AS"
        rf"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{{2}})"
    )
    for asset_index, asset in enumerate(assets):
        if not isinstance(asset, Mapping):
            continue
        asset_id = asset.get("asset_id")
        if not isinstance(asset_id, str):
            continue
        location = f"assets.{asset_index}.asset_id"
        if asset_id in asset_ids:
            errors.append(f"{location}: duplicate asset ID {asset_id}")
        else:
            asset_ids.add(asset_id)
        if re.fullmatch(asset_pattern, asset_id) is None:
            errors.append(
                f"{location}: {asset_id!r} must match {project_id}-AS###"
            )

    context = payload.get("source_context")
    known_world_ids: set[str] | None = None
    known_scene_ids: set[str] | None = None
    known_shot_ids: set[str] | None = None
    shot_lineage: dict[str, str] = {}
    if isinstance(context, Mapping):
        known_world_ids = _string_set(context.get("world_ids"))
        known_scene_ids = _string_set(context.get("scene_ids"))
        known_shot_ids = _string_set(context.get("shot_ids"))
        for field, values in (
            ("world_ids", context.get("world_ids")),
            ("scene_ids", context.get("scene_ids")),
            ("shot_ids", context.get("shot_ids")),
        ):
            if not isinstance(values, list):
                continue
            for value_index, value in enumerate(values):
                if not isinstance(value, str):
                    continue
                if not value.startswith(f"{project_id}-"):
                    errors.append(
                        f"source_context.{field}.{value_index}: {value!r} "
                        f"must belong to project {project_id}"
                    )
        scene_values = context.get("scene_ids")
        shot_values = context.get("shot_ids")
        if isinstance(scene_values, list) and isinstance(shot_values, list):
            supplied_scenes = [
                scene_id for scene_id in scene_values if isinstance(scene_id, str)
            ]
            for shot_index, shot_id in enumerate(shot_values):
                if not isinstance(shot_id, str):
                    continue
                matching_scenes = [
                    scene_id
                    for scene_id in supplied_scenes
                    if shot_id.startswith(f"{scene_id}-SH")
                ]
                if len(matching_scenes) == 1:
                    shot_lineage[shot_id] = matching_scenes[0]
                else:
                    errors.append(
                        f"source_context.shot_ids.{shot_index}: supplied shot "
                        f"{shot_id} does not belong to a supplied scene"
                    )

    def validate_many(
        item: Mapping[str, Any],
        base: str,
        field: str,
        known: set[str] | None,
        kind: str,
    ) -> None:
        references = item.get(field)
        if not isinstance(references, list):
            return
        for reference_index, reference in enumerate(references):
            if (
                isinstance(reference, str)
                and known is not None
                and reference not in known
            ):
                errors.append(
                    f"{base}.{field}.{reference_index}: unknown {kind} "
                    f"reference {reference}"
                )

    def validate_asset_refs(
        item: Mapping[str, Any], base: str, field: str = "asset_ids"
    ) -> None:
        references = item.get(field)
        if not isinstance(references, list):
            return
        for reference_index, reference in enumerate(references):
            if isinstance(reference, str) and reference not in asset_ids:
                errors.append(
                    f"{base}.{field}.{reference_index}: unknown asset "
                    f"reference {reference}"
                )

    for asset_index, asset in enumerate(assets):
        if not isinstance(asset, Mapping):
            continue
        base = f"assets.{asset_index}"
        validate_many(asset, base, "world_ids", known_world_ids, "world")
        validate_many(asset, base, "scene_ids", known_scene_ids, "scene")
        validate_many(asset, base, "shot_ids", known_shot_ids, "shot")

    asset_shots: dict[str, set[str]] = {}
    asset_shot_locations: dict[tuple[str, str], str] = {}
    for asset_index, asset in enumerate(assets):
        if not isinstance(asset, Mapping):
            continue
        asset_id = asset.get("asset_id")
        shot_ids = asset.get("shot_ids")
        if not isinstance(asset_id, str) or not isinstance(shot_ids, list):
            continue
        declared_shots = asset_shots.setdefault(asset_id, set())
        for shot_index, shot_id in enumerate(shot_ids):
            if not isinstance(shot_id, str):
                continue
            declared_shots.add(shot_id)
            asset_shot_locations.setdefault(
                (asset_id, shot_id), f"assets.{asset_index}.shot_ids.{shot_index}"
            )

    coverage_value = payload.get("coverage")
    coverage = coverage_value if isinstance(coverage_value, list) else []
    covered_shots: set[str] = set()
    coverage_links: set[tuple[str, str]] = set()
    for coverage_index, entry in enumerate(coverage):
        if not isinstance(entry, Mapping):
            continue
        base = f"coverage.{coverage_index}"
        scene_id = entry.get("scene_id")
        if (
            isinstance(scene_id, str)
            and known_scene_ids is not None
            and scene_id not in known_scene_ids
        ):
            errors.append(f"{base}.scene_id: unknown scene reference {scene_id}")
        shot_id = entry.get("shot_id")
        if isinstance(shot_id, str):
            if known_shot_ids is not None and shot_id not in known_shot_ids:
                errors.append(f"{base}.shot_id: unknown shot reference {shot_id}")
            if shot_id in covered_shots:
                errors.append(f"{base}.shot_id: duplicate shot coverage {shot_id}")
            else:
                covered_shots.add(shot_id)
            supplied_scene = shot_lineage.get(shot_id)
            if isinstance(scene_id, str) and supplied_scene is not None:
                if scene_id != supplied_scene:
                    errors.append(
                        f"{base}.scene_id: {scene_id} does not match supplied "
                        f"scene {supplied_scene} for shot {shot_id}"
                    )
        validate_asset_refs(entry, base)
        coverage_asset_ids = entry.get("asset_ids")
        if isinstance(shot_id, str) and isinstance(coverage_asset_ids, list):
            for asset_reference_index, asset_reference in enumerate(
                coverage_asset_ids
            ):
                if not isinstance(asset_reference, str):
                    continue
                coverage_links.add((asset_reference, shot_id))
                declared_shots = asset_shots.get(asset_reference)
                if (
                    declared_shots is not None
                    and shot_id not in declared_shots
                ):
                    errors.append(
                        f"{base}.asset_ids.{asset_reference_index}: asset "
                        f"{asset_reference} does not declare shot {shot_id}"
                    )
    if known_shot_ids is not None:
        for missing_shot in sorted(known_shot_ids - covered_shots):
            errors.append(f"coverage: missing supplied shot coverage {missing_shot}")
    for asset_shot in sorted(asset_shot_locations):
        if asset_shot not in coverage_links:
            asset_id, shot_id = asset_shot
            location = asset_shot_locations[asset_shot]
            errors.append(
                f"{location}: declared asset-shot link {asset_id} -> {shot_id} "
                "is missing from coverage"
            )

    states_value = payload.get("continuity_states")
    states = states_value if isinstance(states_value, list) else []
    state_ids: set[str] = set()
    for state_index, state in enumerate(states):
        if not isinstance(state, Mapping):
            continue
        base = f"continuity_states.{state_index}"
        asset_id = state.get("asset_id")
        if isinstance(asset_id, str) and asset_id not in asset_ids:
            errors.append(f"{base}.asset_id: unknown asset reference {asset_id}")
        state_id = state.get("state_id")
        if isinstance(state_id, str):
            if state_id in state_ids:
                errors.append(f"{base}.state_id: duplicate state ID {state_id}")
            else:
                state_ids.add(state_id)
            if (
                not isinstance(asset_id, str)
                or re.fullmatch(
                    rf"{re.escape(asset_id)}-ST(?:0[1-9]|[1-9][0-9])", state_id
                )
                is None
            ):
                expected = (
                    f"{asset_id}-ST##"
                    if isinstance(asset_id, str)
                    else "<asset>-ST##"
                )
                errors.append(f"{base}.state_id: {state_id!r} must match {expected}")
        scene_id = state.get("scene_id")
        if (
            isinstance(scene_id, str)
            and known_scene_ids is not None
            and scene_id not in known_scene_ids
        ):
            errors.append(f"{base}.scene_id: unknown scene reference {scene_id}")
        validate_many(state, base, "shot_ids", known_shot_ids, "shot")

    dependencies_value = payload.get("cross_department_dependencies")
    dependencies = (
        dependencies_value if isinstance(dependencies_value, list) else []
    )
    for dependency_index, dependency in enumerate(dependencies):
        if not isinstance(dependency, Mapping):
            continue
        base = f"cross_department_dependencies.{dependency_index}"
        validate_asset_refs(dependency, base)
        validate_many(dependency, base, "scene_ids", known_scene_ids, "scene")
        validate_many(dependency, base, "shot_ids", known_shot_ids, "shot")

    return errors


def _string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


def _validate_story_concept_contract(payload: Mapping[str, Any]) -> list[str]:
    supplied_constraints = payload.get("supplied_constraints")
    assumptions = payload.get("assumptions")
    if not isinstance(supplied_constraints, list) or not isinstance(
        assumptions, list
    ):
        return []

    supplied_statements = {
        statement
        for item in supplied_constraints
        if isinstance(item, Mapping)
        and isinstance((statement := item.get("statement")), str)
    }
    return [
        f"assumptions.{index}: supplied constraint must not be relabeled as "
        "an assumption"
        for index, assumption in enumerate(assumptions)
        if isinstance(assumption, str) and assumption in supplied_statements
    ]


def _validate_script_revision_plan_contract(
    payload: Mapping[str, Any],
) -> list[str]:
    project_id = payload.get("project_id")
    unit_id = payload.get("unit_id")
    if not isinstance(project_id, str) or not isinstance(unit_id, str):
        return []

    errors: list[str] = []
    project_format = payload.get("project_format")
    expected_unit_suffix = "E" if project_format == "series" else "U"
    unit_pattern = (
        rf"{re.escape(project_id)}-{expected_unit_suffix}"
        rf"(?:0[1-9]|[1-9][0-9])"
    )
    if re.fullmatch(unit_pattern, unit_id) is None:
        errors.append(
            f"unit_id: {unit_id!r} must match "
            f"{project_id}-{expected_unit_suffix}##"
        )

    source_ids_value = payload.get("source_element_ids")
    source_ids = (
        {value for value in source_ids_value if isinstance(value, str)}
        if isinstance(source_ids_value, list)
        else set()
    )

    constraint_pattern = rf"{re.escape(project_id)}-(?:CON|AMB)[0-9]{{3,}}"
    constraints_value = payload.get("approved_constraints")
    constraints = constraints_value if isinstance(constraints_value, list) else []
    constraint_ids: set[str] = set()
    constraint_sources: dict[str, set[str]] = {}
    constraint_source_lists: dict[str, list[str]] = {}
    constraint_order: list[str] = []
    for constraint_index, constraint in enumerate(constraints):
        if not isinstance(constraint, Mapping):
            continue
        constraint_id = constraint.get("constraint_id")
        if isinstance(constraint_id, str):
            location = f"approved_constraints.{constraint_index}.constraint_id"
            if constraint_id in constraint_ids:
                errors.append(f"{location}: duplicate constraint ID {constraint_id}")
            else:
                constraint_ids.add(constraint_id)
                constraint_order.append(constraint_id)
            if re.fullmatch(constraint_pattern, constraint_id) is None:
                errors.append(
                    f"{location}: {constraint_id!r} must match "
                    f"{project_id}-CON### or {project_id}-AMB###"
                )
            constraint_type = constraint.get("constraint_type")
            if constraint_id.startswith(f"{project_id}-AMB"):
                if constraint_type != "approved-ambiguity":
                    errors.append(
                        f"approved_constraints.{constraint_index}.constraint_type: "
                        f"{constraint_id} requires approved-ambiguity"
                    )
            elif constraint_type == "approved-ambiguity":
                errors.append(
                    f"approved_constraints.{constraint_index}.constraint_type: "
                    f"approved ambiguity requires a {project_id}-AMB### ID"
                )

        protected_value = constraint.get("protected_source_ids")
        protected_ids: set[str] = set()
        if isinstance(protected_value, list):
            for protected_index, protected_id in enumerate(protected_value):
                if not isinstance(protected_id, str):
                    continue
                protected_ids.add(protected_id)
                if protected_id not in source_ids:
                    errors.append(
                        f"approved_constraints.{constraint_index}."
                        f"protected_source_ids.{protected_index}: unknown source "
                        f"element {protected_id}"
                    )
        if isinstance(constraint_id, str):
            constraint_sources.setdefault(constraint_id, set()).update(protected_ids)
            constraint_source_lists.setdefault(
                constraint_id,
                [
                    value
                    for value in protected_value
                    if isinstance(value, str)
                ]
                if isinstance(protected_value, list)
                else [],
            )

    items_value = payload.get("diagnosis_items")
    items = items_value if isinstance(items_value, list) else []
    diagnosis_ids: set[str] = set()
    priorities: set[int] = set()
    observed_priorities: list[int] = []
    dependency_order = {
        "upstream-story": 0,
        "scene-engine": 1,
        "line-craft": 2,
        "presentation-production": 3,
    }
    previous_dependency: str | None = None
    previous_dependency_rank = -1

    for item_index, item in enumerate(items):
        if not isinstance(item, Mapping):
            continue
        diagnosis_id = item.get("diagnosis_id")
        if isinstance(diagnosis_id, str):
            location = f"diagnosis_items.{item_index}.diagnosis_id"
            expected_diagnosis_id = f"{unit_id}-RV{item_index + 1:03d}"
            if diagnosis_id != expected_diagnosis_id:
                errors.append(
                    f"{location}: must equal {expected_diagnosis_id} "
                    f"for plan position {item_index + 1}"
                )
            if diagnosis_id in diagnosis_ids:
                errors.append(f"{location}: duplicate diagnosis ID {diagnosis_id}")
            else:
                diagnosis_ids.add(diagnosis_id)

        priority = item.get("priority")
        if isinstance(priority, int) and not isinstance(priority, bool):
            observed_priorities.append(priority)
            if priority in priorities:
                errors.append(
                    f"diagnosis_items.{item_index}.priority: "
                    f"duplicate priority {priority}"
                )
            else:
                priorities.add(priority)

        dependency = item.get("dependency_impact")
        if isinstance(dependency, str) and dependency in dependency_order:
            rank = dependency_order[dependency]
            if rank < previous_dependency_rank:
                errors.append(
                    f"diagnosis_items.{item_index}.dependency_impact: "
                    f"{dependency} must not follow lower-impact "
                    f"{previous_dependency}"
                )
            if rank > previous_dependency_rank:
                previous_dependency_rank = rank
                previous_dependency = dependency

        affected_value = item.get("affected_ids")
        affected_ids: set[str] = set()
        if isinstance(affected_value, list):
            for affected_index, affected_id in enumerate(affected_value):
                if not isinstance(affected_id, str):
                    continue
                affected_ids.add(affected_id)
                if affected_id not in source_ids:
                    errors.append(
                        f"diagnosis_items.{item_index}.affected_ids."
                        f"{affected_index}: unknown source element {affected_id}"
                    )

        evidence_value = item.get("evidence")
        evidenced_ids: set[str] = set()
        if isinstance(evidence_value, list):
            for evidence_index, evidence in enumerate(evidence_value):
                if not isinstance(evidence, Mapping):
                    continue
                evidence_id = evidence.get("source_id")
                if not isinstance(evidence_id, str):
                    continue
                location = (
                    f"diagnosis_items.{item_index}.evidence."
                    f"{evidence_index}.source_id"
                )
                if evidence_id in evidenced_ids:
                    errors.append(
                        f"{location}: duplicate evidence reference {evidence_id}"
                    )
                else:
                    evidenced_ids.add(evidence_id)
                if evidence_id not in source_ids:
                    errors.append(f"{location}: unknown source element {evidence_id}")
                if evidence_id not in affected_ids:
                    errors.append(
                        f"{location}: {evidence_id} is not listed in affected_ids"
                    )

        if isinstance(affected_value, list):
            for affected_index, affected_id in enumerate(affected_value):
                if isinstance(affected_id, str) and affected_id not in evidenced_ids:
                    errors.append(
                        f"diagnosis_items.{item_index}.affected_ids."
                        f"{affected_index}: {affected_id} has no evidence entry"
                    )

        change_targets_value = item.get("change_target_ids")
        change_target_ids: list[str] = []
        if isinstance(change_targets_value, list):
            for target_index, target_id in enumerate(change_targets_value):
                if not isinstance(target_id, str):
                    continue
                change_target_ids.append(target_id)
                location = (
                    f"diagnosis_items.{item_index}.change_target_ids.{target_index}"
                )
                if target_id not in source_ids:
                    errors.append(f"{location}: unknown source element {target_id}")
                if target_id not in affected_ids:
                    errors.append(
                        f"{location}: {target_id} is not listed in affected_ids"
                    )

        preserved_value = item.get("preserved_constraint_ids")
        preserved_ids: set[str] = set()
        if isinstance(preserved_value, list):
            for preserved_index, preserved_id in enumerate(preserved_value):
                if not isinstance(preserved_id, str):
                    continue
                preserved_ids.add(preserved_id)
                if preserved_id not in constraint_ids:
                    errors.append(
                        f"diagnosis_items.{item_index}.preserved_constraint_ids."
                        f"{preserved_index}: unknown approved constraint "
                        f"{preserved_id}"
                    )

        checks_value = item.get("preservation_checks")
        check_counts: dict[str, int] = {}
        if isinstance(checks_value, list):
            for check_index, check in enumerate(checks_value):
                if not isinstance(check, Mapping):
                    continue
                check_id = check.get("constraint_id")
                if not isinstance(check_id, str):
                    continue
                location = (
                    f"diagnosis_items.{item_index}.preservation_checks."
                    f"{check_index}.constraint_id"
                )
                check_counts[check_id] = check_counts.get(check_id, 0) + 1
                if check_counts[check_id] > 1:
                    errors.append(f"{location}: duplicate check for {check_id}")
                if check_id not in constraint_ids:
                    errors.append(f"{location}: unknown approved constraint {check_id}")
                elif check_id not in preserved_ids:
                    errors.append(
                        f"{location}: check constraint {check_id} is not listed "
                        "in preserved_constraint_ids"
                    )
                check_sources = check.get("protected_source_ids")
                if (
                    isinstance(check_sources, list)
                    and check_id in constraint_source_lists
                    and check_sources != constraint_source_lists[check_id]
                ):
                    errors.append(
                        f"diagnosis_items.{item_index}.preservation_checks."
                        f"{check_index}.protected_source_ids: must exactly match "
                        f"approved constraint {check_id} protected_source_ids"
                    )

        for preserved_id in preserved_ids:
            if check_counts.get(preserved_id, 0) == 0:
                errors.append(
                    f"diagnosis_items.{item_index}.preservation_checks: "
                    f"missing check for preserved constraint {preserved_id}"
                )

        for constraint_id, protected_ids in constraint_sources.items():
            if (
                affected_ids.intersection(protected_ids)
                and constraint_id not in preserved_ids
            ):
                errors.append(
                    f"diagnosis_items.{item_index}.preserved_constraint_ids: "
                    f"must preserve affected approved constraint {constraint_id}"
                )

        target_conflicts = [
            constraint_id
            for constraint_id in constraint_order
            if any(
                target_id in constraint_sources.get(constraint_id, set())
                for target_id in change_target_ids
            )
        ]
        execution_mode = item.get("execution_mode")
        if execution_mode == "executable-change":
            for target_index, target_id in enumerate(change_target_ids):
                for constraint_id in target_conflicts:
                    if target_id in constraint_sources.get(constraint_id, set()):
                        errors.append(
                            f"diagnosis_items.{item_index}.change_target_ids."
                            f"{target_index}: targets protected source {target_id} "
                            f"from {constraint_id}; requires "
                            "blocked-upstream-decision"
                        )
        elif execution_mode == "blocked-upstream-decision":
            decision = item.get("decision_request")
            conflicts_value = (
                decision.get("conflicting_constraint_ids")
                if isinstance(decision, Mapping)
                else None
            )
            if isinstance(conflicts_value, list):
                conflicts_match = all(
                    isinstance(conflict_id, str)
                    for conflict_id in conflicts_value
                ) and set(conflicts_value) == set(target_conflicts)
                if not conflicts_match:
                    expected = ", ".join(target_conflicts) or "none"
                    errors.append(
                        f"diagnosis_items.{item_index}.decision_request."
                        "conflicting_constraint_ids: must exactly match protected "
                        f"target conflicts: {expected}"
                    )
            if not target_conflicts:
                errors.append(
                    f"diagnosis_items.{item_index}.execution_mode: blocked mode "
                    "requires at least one protected change target"
                )

    if len(observed_priorities) == len(items):
        expected_priorities = list(range(1, len(items) + 1))
        if observed_priorities != expected_priorities:
            errors.append(
                "diagnosis_items: priorities must be ordered consecutive ranks "
                f"1..{len(items)}"
            )
    return errors


def _validate_unit_outline_contract(payload: Mapping[str, Any]) -> list[str]:
    project_id = payload.get("project_id")
    project_format = payload.get("project_format")
    unit_id = payload.get("unit_id")
    scenes = payload.get("scenes")
    if not isinstance(project_id, str) or not isinstance(unit_id, str):
        return []

    errors: list[str] = []
    unit_suffix = "E" if project_format == "series" else "U"
    unit_pattern = rf"{re.escape(project_id)}-{unit_suffix}(?:0[1-9]|[1-9][0-9])"
    if re.fullmatch(unit_pattern, unit_id) is None:
        errors.append(
            f"unit_id: {unit_id!r} must match {project_id}-{unit_suffix}##"
        )

    event_pattern = rf"{re.escape(project_id)}-EV(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{{2}})"
    plotline_pattern = rf"{re.escape(project_id)}-PL(?:0[1-9]|[1-9][0-9])"
    scene_pattern = rf"{re.escape(unit_id)}-SC(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{{2}})"

    def declared_ids(
        field: str,
        pattern: str,
        example: str,
        kind: str,
    ) -> set[str]:
        identifiers: set[str] = set()
        values = payload.get(field)
        if not isinstance(values, list):
            return identifiers
        for value_index, value in enumerate(values):
            if not isinstance(value, str):
                continue
            location = f"{field}.{value_index}"
            if value in identifiers:
                errors.append(f"{location}: duplicate {kind} ID {value}")
            else:
                identifiers.add(value)
            if re.fullmatch(pattern, value) is None:
                errors.append(f"{location}: {value!r} must match {example}")
        return identifiers

    event_ids = declared_ids(
        "source_event_ids", event_pattern, f"{project_id}-EV###", "event"
    )
    plotline_ids = declared_ids(
        "source_plotline_ids",
        plotline_pattern,
        f"{project_id}-PL##",
        "plotline",
    )

    scene_ids: set[str] = set()
    scene_indexes: list[int] = []
    if isinstance(scenes, list):
        for scene_index, scene in enumerate(scenes):
            if not isinstance(scene, Mapping):
                continue
            scene_id = scene.get("scene_id")
            declared_index = scene.get("scene_index")
            if isinstance(scene_id, str):
                location = f"scenes.{scene_index}.scene_id"
                if scene_id in scene_ids:
                    errors.append(f"{location}: duplicate scene ID {scene_id}")
                else:
                    scene_ids.add(scene_id)
                if re.fullmatch(scene_pattern, scene_id) is None:
                    errors.append(
                        f"{location}: {scene_id!r} must match {unit_id}-SC###"
                    )
                elif isinstance(declared_index, int):
                    expected_id = f"{unit_id}-SC{declared_index:03d}"
                    if scene_id != expected_id:
                        errors.append(
                            f"{location}: scene index {declared_index} must use {expected_id}"
                        )
            if isinstance(declared_index, int):
                scene_indexes.append(declared_index)

        expected_indexes = list(range(1, len(scenes) + 1))
        if len(scene_indexes) == len(scenes) and scene_indexes != expected_indexes:
            errors.append(
                f"scenes: scene indexes must be ascending order 1..{len(scenes)}"
            )

    def validate_reference(
        location: str,
        value: object,
        kind: str,
        known: set[str],
        pattern: str,
        example: str,
    ) -> None:
        if not isinstance(value, str):
            return
        if re.fullmatch(pattern, value) is None:
            errors.append(f"{location}: {value!r} must match {example}")
        elif value not in known:
            errors.append(f"{location}: unknown {kind} {value}")

    def validate_many(
        location: str,
        values: object,
        kind: str,
        known: set[str],
        pattern: str,
        example: str,
    ) -> None:
        if not isinstance(values, list):
            return
        for value_index, value in enumerate(values):
            validate_reference(
                f"{location}.{value_index}",
                value,
                kind,
                known,
                pattern,
                example,
            )

    assigned_event_ids: set[str] = set()
    scene_event_ids_by_scene: dict[str, set[str]] = {}
    scene_plotline_ids_by_scene: dict[str, set[str]] = {}
    scene_evidence_status_by_scene: dict[str, str] = {}
    previous_end: int | None = None
    runtime_seconds = payload.get("runtime_seconds")
    if isinstance(scenes, list):
        for scene_index, scene in enumerate(scenes):
            if not isinstance(scene, Mapping):
                continue
            start_seconds = scene.get("start_seconds")
            end_seconds = scene.get("end_seconds")
            if isinstance(start_seconds, int) and isinstance(end_seconds, int):
                if end_seconds <= start_seconds:
                    errors.append(
                        f"scenes.{scene_index}.end_seconds: end_seconds must be greater than start_seconds"
                    )
                if previous_end is not None and start_seconds < previous_end:
                    errors.append(
                        f"scenes.{scene_index}.start_seconds: scene must not overlap the prior scene"
                    )
                if isinstance(runtime_seconds, int) and end_seconds > runtime_seconds:
                    errors.append(
                        f"scenes.{scene_index}.end_seconds: {end_seconds} exceeds runtime_seconds {runtime_seconds}"
                    )
                previous_end = end_seconds
            validate_many(
                f"scenes.{scene_index}.event_ids",
                scene.get("event_ids"),
                "event",
                event_ids,
                event_pattern,
                f"{project_id}-EV###",
            )
            validate_many(
                f"scenes.{scene_index}.plotline_ids",
                scene.get("plotline_ids"),
                "plotline",
                plotline_ids,
                plotline_pattern,
                f"{project_id}-PL##",
            )
            scene_event_ids = scene.get("event_ids")
            if isinstance(scene_event_ids, list):
                assigned_event_ids.update(
                    event_id
                    for event_id in scene_event_ids
                    if isinstance(event_id, str) and event_id in event_ids
                )
            scene_id = scene.get("scene_id")
            if isinstance(scene_id, str) and scene_id in scene_ids:
                if isinstance(scene_event_ids, list):
                    scene_event_ids_by_scene[scene_id] = {
                        event_id
                        for event_id in scene_event_ids
                        if isinstance(event_id, str) and event_id in event_ids
                    }
                scene_plotline_ids = scene.get("plotline_ids")
                if isinstance(scene_plotline_ids, list):
                    scene_plotline_ids_by_scene[scene_id] = {
                        plotline_id
                        for plotline_id in scene_plotline_ids
                        if isinstance(plotline_id, str)
                        and plotline_id in plotline_ids
                    }
                evidence_status = scene.get("evidence_status")
                if isinstance(evidence_status, str):
                    scene_evidence_status_by_scene[scene_id] = evidence_status

    for event_id in sorted(event_ids - assigned_event_ids):
        errors.append(f"scenes: source event {event_id} is not assigned to a scene")

    covered_event_ids: set[str] = set()
    event_coverage_indexes: dict[str, int] = {}
    event_coverage_scenes: dict[str, set[str]] = {}
    event_coverage = payload.get("event_coverage")
    if isinstance(event_coverage, list):
        for coverage_index, coverage in enumerate(event_coverage):
            if not isinstance(coverage, Mapping):
                continue
            event_id = coverage.get("event_id")
            validate_reference(
                f"event_coverage.{coverage_index}.event_id",
                event_id,
                "event",
                event_ids,
                event_pattern,
                f"{project_id}-EV###",
            )
            if isinstance(event_id, str) and event_id in event_ids:
                if event_id in covered_event_ids:
                    errors.append(
                        f"event_coverage.{coverage_index}.event_id: duplicate event coverage {event_id}"
                    )
                covered_event_ids.add(event_id)
                event_coverage_indexes.setdefault(event_id, coverage_index)
                covered_scenes = event_coverage_scenes.setdefault(event_id, set())
                coverage_scene_ids = coverage.get("scene_ids")
                if isinstance(coverage_scene_ids, list):
                    for scene_reference_index, scene_reference in enumerate(
                        coverage_scene_ids
                    ):
                        if not isinstance(scene_reference, str):
                            continue
                        if scene_reference in scene_ids:
                            covered_scenes.add(scene_reference)
                            if event_id not in scene_event_ids_by_scene.get(
                                scene_reference, set()
                            ):
                                errors.append(
                                    f"event_coverage.{coverage_index}.scene_ids."
                                    f"{scene_reference_index}: scene {scene_reference} "
                                    f"does not carry event {event_id}"
                                )
            validate_many(
                f"event_coverage.{coverage_index}.scene_ids",
                coverage.get("scene_ids"),
                "scene",
                scene_ids,
                scene_pattern,
                f"{unit_id}-SC###",
            )
    for event_id in sorted(event_ids - covered_event_ids):
        errors.append(f"event_coverage: missing source event {event_id}")
    for event_id in sorted(covered_event_ids):
        actual_scenes = {
            scene_id
            for scene_id, assigned_ids in scene_event_ids_by_scene.items()
            if event_id in assigned_ids
        }
        missing_scenes = actual_scenes - event_coverage_scenes.get(event_id, set())
        coverage_index = event_coverage_indexes.get(event_id)
        if coverage_index is None:
            continue
        for scene_id in sorted(missing_scenes):
            errors.append(
                f"event_coverage.{coverage_index}.scene_ids: missing scene "
                f"{scene_id} carrying event {event_id}"
            )

    covered_plotline_ids: set[str] = set()
    plotline_coverage_indexes: dict[str, int] = {}
    plotline_coverage_scenes: dict[str, set[str]] = {}
    plotline_coverage = payload.get("plotline_coverage")
    if isinstance(plotline_coverage, list):
        for coverage_index, coverage in enumerate(plotline_coverage):
            if not isinstance(coverage, Mapping):
                continue
            plotline_id = coverage.get("plotline_id")
            validate_reference(
                f"plotline_coverage.{coverage_index}.plotline_id",
                plotline_id,
                "plotline",
                plotline_ids,
                plotline_pattern,
                f"{project_id}-PL##",
            )
            if isinstance(plotline_id, str) and plotline_id in plotline_ids:
                if plotline_id in covered_plotline_ids:
                    errors.append(
                        f"plotline_coverage.{coverage_index}.plotline_id: "
                        f"duplicate plotline coverage {plotline_id}"
                    )
                covered_plotline_ids.add(plotline_id)
                plotline_coverage_indexes.setdefault(plotline_id, coverage_index)
                covered_scenes = plotline_coverage_scenes.setdefault(
                    plotline_id, set()
                )
                coverage_scene_ids = coverage.get("scene_ids")
                if isinstance(coverage_scene_ids, list):
                    for scene_reference_index, scene_reference in enumerate(
                        coverage_scene_ids
                    ):
                        if not isinstance(scene_reference, str):
                            continue
                        if scene_reference in scene_ids:
                            covered_scenes.add(scene_reference)
                            if plotline_id not in scene_plotline_ids_by_scene.get(
                                scene_reference, set()
                            ):
                                errors.append(
                                    f"plotline_coverage.{coverage_index}.scene_ids."
                                    f"{scene_reference_index}: scene {scene_reference} "
                                    f"does not carry plotline {plotline_id}"
                                )
            validate_many(
                f"plotline_coverage.{coverage_index}.scene_ids",
                coverage.get("scene_ids"),
                "scene",
                scene_ids,
                scene_pattern,
                f"{unit_id}-SC###",
            )
    for plotline_id in sorted(plotline_ids - covered_plotline_ids):
        errors.append(f"plotline_coverage: missing source plotline {plotline_id}")
    for plotline_id in sorted(covered_plotline_ids):
        actual_scenes = {
            scene_id
            for scene_id, assigned_ids in scene_plotline_ids_by_scene.items()
            if plotline_id in assigned_ids
        }
        missing_scenes = actual_scenes - plotline_coverage_scenes.get(
            plotline_id, set()
        )
        coverage_index = plotline_coverage_indexes.get(plotline_id)
        if coverage_index is None:
            continue
        for scene_id in sorted(missing_scenes):
            errors.append(
                f"plotline_coverage.{coverage_index}.scene_ids: missing scene "
                f"{scene_id} carrying plotline {plotline_id}"
            )

    def validate_scene_pointer(location: str, container: object) -> None:
        if not isinstance(container, Mapping):
            return
        scene_id = container.get("scene_id")
        if scene_id is not None and not isinstance(scene_id, str):
            errors.append(f"{location}.scene_id: scene ID string required")
            return
        validate_reference(
            f"{location}.scene_id",
            scene_id,
            "scene",
            scene_ids,
            scene_pattern,
            f"{unit_id}-SC###",
        )

    validate_scene_pointer("opening_hook", payload.get("opening_hook"))
    opening_hook = payload.get("opening_hook")
    if (
        isinstance(scenes, list)
        and scenes
        and isinstance(scenes[0], Mapping)
        and isinstance(scenes[0].get("scene_id"), str)
        and isinstance(opening_hook, Mapping)
        and isinstance(opening_hook.get("scene_id"), str)
        and opening_hook.get("scene_id") != scenes[0].get("scene_id")
    ):
        errors.append(
            "opening_hook.scene_id: must target first scene "
            f"{scenes[0].get('scene_id')}"
        )
    for collection_name in ("emotional_turns", "act_outs"):
        collection = payload.get(collection_name)
        if not isinstance(collection, list):
            continue
        for item_index, item in enumerate(collection):
            validate_scene_pointer(f"{collection_name}.{item_index}", item)
    for field in ("midpoint", "climax", "resolution", "forward_hook"):
        validate_scene_pointer(field, payload.get(field))

    format_plan = payload.get("format_plan")
    if isinstance(format_plan, Mapping) and format_plan.get("mode") == "runtime-led":
        orientation = format_plan.get("orientation_by_seconds")
        payoff = format_plan.get("payoff_by_seconds")
        for field, value in (
            ("orientation_by_seconds", orientation),
            ("payoff_by_seconds", payoff),
        ):
            if (
                isinstance(value, int)
                and isinstance(runtime_seconds, int)
                and value > runtime_seconds
            ):
                errors.append(
                    f"format_plan.{field}: {value} exceeds runtime_seconds {runtime_seconds}"
                )
        if isinstance(orientation, int) and isinstance(payoff, int) and orientation > payoff:
            errors.append(
                "format_plan.orientation_by_seconds: orientation must not follow payoff_by_seconds"
            )
    if (
        isinstance(format_plan, Mapping)
        and format_plan.get("mode") == "documentary-evidence"
    ):
        evidence_event_ids: set[str] = set()
        evidence_items = format_plan.get("evidence_items")
        if isinstance(evidence_items, list):
            for item_index, item in enumerate(evidence_items):
                if not isinstance(item, Mapping):
                    continue
                event_id = item.get("event_id")
                validate_reference(
                    f"format_plan.evidence_items.{item_index}.event_id",
                    event_id,
                    "event",
                    event_ids,
                    event_pattern,
                    f"{project_id}-EV###",
                )
                if isinstance(event_id, str) and event_id in event_ids:
                    if event_id in evidence_event_ids:
                        errors.append(
                            f"format_plan.evidence_items.{item_index}.event_id: "
                            f"duplicate evidence item {event_id}"
                        )
                    evidence_event_ids.add(event_id)
                    evidence_status = item.get("status")
                    if isinstance(evidence_status, str):
                        for scene_id, assigned_ids in sorted(
                            scene_event_ids_by_scene.items()
                        ):
                            scene_status = scene_evidence_status_by_scene.get(scene_id)
                            if (
                                event_id in assigned_ids
                                and isinstance(scene_status, str)
                                and scene_status != evidence_status
                            ):
                                errors.append(
                                    f"format_plan.evidence_items.{item_index}.status: "
                                    f"status {evidence_status} disagrees: scene {scene_id} "
                                    f"has evidence_status {scene_status}"
                                )
        for event_id in sorted(event_ids - evidence_event_ids):
            errors.append(
                f"format_plan.evidence_items: missing source event {event_id}"
            )

    return errors


def _validate_season_arc_contract(payload: Mapping[str, Any]) -> list[str]:
    project_id = payload.get("project_id")
    episodes = payload.get("episodes")
    if not isinstance(project_id, str) or not isinstance(episodes, list):
        return []

    errors: list[str] = []
    patterns = {
        "episode": (
            rf"{re.escape(project_id)}-E(?:0[1-9]|[1-9][0-9])",
            f"{project_id}-E##",
        ),
        "plotline": (
            rf"{re.escape(project_id)}-PL(?:0[1-9]|[1-9][0-9])",
            f"{project_id}-PL##",
        ),
        "event": (
            rf"{re.escape(project_id)}-EV(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{{2}})",
            f"{project_id}-EV###",
        ),
        "character": (
            rf"{re.escape(project_id)}-CH(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{{2}})",
            f"{project_id}-CH###",
        ),
    }

    def declared_ids(field: str, kind: str) -> set[str]:
        identifiers: set[str] = set()
        values = payload.get(field)
        if not isinstance(values, list):
            return identifiers
        pattern, example = patterns[kind]
        for index, identifier in enumerate(values):
            if not isinstance(identifier, str):
                continue
            location = f"{field}.{index}"
            if identifier in identifiers:
                errors.append(f"{location}: duplicate {kind} ID {identifier}")
            else:
                identifiers.add(identifier)
            if re.fullmatch(pattern, identifier) is None:
                errors.append(f"{location}: {identifier!r} must match {example}")
        return identifiers

    plotline_ids = declared_ids("source_plotline_ids", "plotline")
    event_ids = declared_ids("source_event_ids", "event")
    character_ids = declared_ids("source_character_ids", "character")

    episode_ids: set[str] = set()
    episode_indexes: dict[str, int] = {}
    episode_numbers: list[int] = []
    episode_pattern, episode_example = patterns["episode"]
    for episode_index, episode in enumerate(episodes):
        if not isinstance(episode, Mapping):
            continue
        episode_id = episode.get("episode_id")
        episode_number = episode.get("episode_number")
        if isinstance(episode_id, str):
            location = f"episodes.{episode_index}.episode_id"
            if episode_id in episode_ids:
                errors.append(f"{location}: duplicate episode ID {episode_id}")
            else:
                episode_ids.add(episode_id)
                episode_indexes[episode_id] = episode_index
            if re.fullmatch(episode_pattern, episode_id) is None:
                errors.append(
                    f"{location}: {episode_id!r} must match {episode_example}"
                )
            elif isinstance(episode_number, int):
                expected_id = f"{project_id}-E{episode_number:02d}"
                if episode_id != expected_id:
                    errors.append(
                        f"{location}: episode {episode_number} must use {expected_id}"
                    )
        if isinstance(episode_number, int):
            episode_numbers.append(episode_number)

    expected_numbers = list(range(1, len(episodes) + 1))
    if len(episode_numbers) == len(episodes) and episode_numbers != expected_numbers:
        errors.append(
            f"episodes: episode numbers must be ascending order 1..{len(episodes)}"
        )

    def validate_reference(
        location: str,
        value: object,
        kind: str,
        known: set[str],
    ) -> None:
        if not isinstance(value, str):
            return
        pattern, example = patterns[kind]
        if re.fullmatch(pattern, value) is None:
            errors.append(f"{location}: {value!r} must match {example}")
        elif value not in known:
            errors.append(f"{location}: unknown {kind} {value}")

    def validate_many(
        location: str,
        values: object,
        kind: str,
        known: set[str],
    ) -> None:
        if not isinstance(values, list):
            return
        for value_index, value in enumerate(values):
            validate_reference(f"{location}.{value_index}", value, kind, known)

    for episode_index, episode in enumerate(episodes):
        if not isinstance(episode, Mapping):
            continue
        distribution = episode.get("plot_distribution")
        slots: set[str] = set()
        if isinstance(distribution, list):
            if not distribution:
                errors.append(
                    f"episodes.{episode_index}.plot_distribution: too short; "
                    "every episode must advance at least one plotline"
                )
            for plot_index, plot in enumerate(distribution):
                if not isinstance(plot, Mapping):
                    continue
                slot = plot.get("slot")
                if isinstance(slot, str):
                    location = (
                        f"episodes.{episode_index}.plot_distribution.{plot_index}.slot"
                    )
                    if slot in slots:
                        errors.append(f"{location}: duplicate plot slot {slot}")
                    slots.add(slot)
                plot_location = (
                    f"episodes.{episode_index}.plot_distribution.{plot_index}"
                )
                validate_reference(
                    f"{plot_location}.plotline_id",
                    plot.get("plotline_id"),
                    "plotline",
                    plotline_ids,
                )
                validate_many(
                    f"{plot_location}.event_ids",
                    plot.get("event_ids"),
                    "event",
                    event_ids,
                )
            if distribution and "A" not in slots:
                errors.append(
                    f"episodes.{episode_index}.plot_distribution: "
                    "every episode requires an A plot"
                )

        forward_hook = episode.get("forward_hook")
        if episode_index < len(episodes) - 1 and forward_hook is None:
            errors.append(
                f"episodes.{episode_index}.forward_hook: "
                "every nonfinal episode requires a forward hook"
            )
        if isinstance(forward_hook, Mapping):
            target_episode_id = forward_hook.get("target_episode_id")
            target_location = (
                f"episodes.{episode_index}.forward_hook.target_episode_id"
            )
            validate_reference(
                target_location,
                target_episode_id,
                "episode",
                episode_ids,
            )
            target_episode_index = (
                episode_indexes.get(target_episode_id)
                if isinstance(target_episode_id, str)
                else None
            )
            if (
                target_episode_index is not None
                and target_episode_index <= episode_index
            ):
                errors.append(
                    f"{target_location}: forward hook must target a strictly "
                    "later episode"
                )

    collection_contracts = (
        ("character_progression", "character_id", "character", character_ids, False),
        ("character_progression", "episode_ids", "episode", episode_ids, True),
        ("character_progression", "event_ids", "event", event_ids, True),
        ("relationship_progression", "character_ids", "character", character_ids, True),
        ("relationship_progression", "episode_ids", "episode", episode_ids, True),
        ("relationship_progression", "event_ids", "event", event_ids, True),
        ("reveal_schedule", "event_id", "event", event_ids, False),
        ("reveal_schedule", "episode_id", "episode", episode_ids, False),
        ("season_setups", "setup_event_id", "event", event_ids, False),
        ("season_setups", "episode_id", "episode", episode_ids, False),
        ("unresolved_threads", "plotline_id", "plotline", plotline_ids, False),
        ("next_season_seeds", "event_id", "event", event_ids, False),
    )
    for collection_name, field, kind, known, many in collection_contracts:
        items = payload.get(collection_name)
        if not isinstance(items, list):
            continue
        for item_index, item in enumerate(items):
            if not isinstance(item, Mapping):
                continue
            location = f"{collection_name}.{item_index}.{field}"
            if many:
                validate_many(location, item.get(field), kind, known)
            else:
                validate_reference(location, item.get(field), kind, known)

    finale_payoff = payload.get("finale_payoff")
    if isinstance(finale_payoff, Mapping):
        finale_episode_id = finale_payoff.get("episode_id")
        validate_reference(
            "finale_payoff.episode_id",
            finale_episode_id,
            "episode",
            episode_ids,
        )
        final_episode_id = None
        if episodes and isinstance(episodes[-1], Mapping):
            candidate = episodes[-1].get("episode_id")
            if isinstance(candidate, str):
                final_episode_id = candidate
        if (
            isinstance(finale_episode_id, str)
            and isinstance(final_episode_id, str)
            and finale_episode_id != final_episode_id
        ):
            errors.append(
                "finale_payoff.episode_id: finale payoff must target final episode "
                f"{final_episode_id}"
            )

        season_setups = payload.get("season_setups")
        declared_setups = {
            setup.get("setup_event_id")
            for setup in season_setups
            if isinstance(setup, Mapping)
            and isinstance(setup.get("setup_event_id"), str)
        } if isinstance(season_setups, list) else set()
        setup_references = finale_payoff.get("setup_event_ids")
        payoff_setup_ids: set[str] = set()
        if isinstance(setup_references, list):
            for setup_index, setup_event_id in enumerate(setup_references):
                location = f"finale_payoff.setup_event_ids.{setup_index}"
                validate_reference(location, setup_event_id, "event", event_ids)
                if isinstance(setup_event_id, str):
                    payoff_setup_ids.add(setup_event_id)
                if (
                    isinstance(setup_event_id, str)
                    and setup_event_id in event_ids
                    and setup_event_id not in declared_setups
                ):
                    errors.append(
                        f"{location}: undeclared setup event {setup_event_id}"
                    )
        payoff_episode_index = (
            episode_indexes.get(finale_episode_id)
            if isinstance(finale_episode_id, str)
            else None
        )
        if (
            isinstance(season_setups, list)
            and isinstance(finale_episode_id, str)
            and payoff_episode_index is not None
        ):
            for setup_index, setup in enumerate(season_setups):
                if not isinstance(setup, Mapping):
                    continue
                setup_event_id = setup.get("setup_event_id")
                if (
                    not isinstance(setup_event_id, str)
                    or setup_event_id not in payoff_setup_ids
                ):
                    continue
                setup_episode_id = setup.get("episode_id")
                setup_episode_index = (
                    episode_indexes.get(setup_episode_id)
                    if isinstance(setup_episode_id, str)
                    else None
                )
                if (
                    setup_episode_index is not None
                    and setup_episode_index >= payoff_episode_index
                ):
                    errors.append(
                        f"season_setups.{setup_index}.episode_id: setup used by "
                        "finale payoff must be scheduled strictly before finale "
                        f"episode {finale_episode_id}"
                    )
        validate_many(
            "finale_payoff.payoff_event_ids",
            finale_payoff.get("payoff_event_ids"),
            "event",
            event_ids,
        )

    return errors


def _validate_world_bible_contract(payload: Mapping[str, Any]) -> list[str]:
    project_id = payload.get("project_id")
    if not isinstance(project_id, str):
        return []

    errors: list[str] = []
    declared: dict[str, set[str]] = {}
    contracts = (
        ("locations", "location_id", "LO", "LO###"),
        ("rules", "rule_id", "WR", "WR###"),
        ("production_assets", "asset_id", "AS", "AS###"),
    )
    for collection_name, id_field, prefix, example in contracts:
        identifiers: set[str] = set()
        items = payload.get(collection_name)
        if not isinstance(items, list):
            declared[collection_name] = identifiers
            continue
        pattern = (
            rf"{re.escape(project_id)}-{prefix}"
            rf"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{{2}})"
        )
        for item_index, item in enumerate(items):
            if not isinstance(item, Mapping):
                continue
            identifier = item.get(id_field)
            if not isinstance(identifier, str):
                continue
            location = f"{collection_name}.{item_index}.{id_field}"
            if identifier in identifiers:
                errors.append(f"{location}: duplicate ID {identifier}")
            else:
                identifiers.add(identifier)
            if re.fullmatch(pattern, identifier) is None:
                errors.append(
                    f"{location}: {identifier!r} must match {project_id}-{example}"
                )
        declared[collection_name] = identifiers

    rule_ids = declared["rules"]
    systems = payload.get("systems")
    rule_pattern = (
        rf"{re.escape(project_id)}-WR"
        rf"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{{2}})"
    )
    if isinstance(systems, list):
        for system_index, system in enumerate(systems):
            if not isinstance(system, Mapping):
                continue
            references = system.get("rule_ids")
            if not isinstance(references, list):
                continue
            for reference_index, reference in enumerate(references):
                if not isinstance(reference, str):
                    continue
                location = f"systems.{system_index}.rule_ids.{reference_index}"
                if re.fullmatch(rule_pattern, reference) is None:
                    errors.append(
                        f"{location}: {reference!r} must match {project_id}-WR###"
                    )
                elif reference not in rule_ids:
                    errors.append(f"{location}: unknown rule {reference}")

    for collection_name in (
        "locations",
        "factions",
        "institutions",
        "history",
        "cultures",
        "systems",
        "rules",
        "terminology",
        "production_assets",
    ):
        items = payload.get(collection_name)
        if not isinstance(items, list):
            continue
        for item_index, item in enumerate(items):
            if not isinstance(item, Mapping):
                continue
            provenance = item.get("provenance")
            if (
                item.get("canon_status") == "canon"
                and isinstance(provenance, str)
                and provenance not in {"supplied", "approved"}
            ):
                errors.append(
                    f"{collection_name}.{item_index}.canon_status: "
                    "canon requires supplied or approved provenance"
                )
    return errors


def _validate_character_arc_identifiers(payload: Mapping[str, Any]) -> list[str]:
    project_id = payload.get("project_id")
    characters = payload.get("characters")
    if not isinstance(project_id, str) or not isinstance(characters, list):
        return []

    errors: list[str] = []
    character_ids: set[str] = set()
    character_pattern = rf"{re.escape(project_id)}-CH(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{{2}})"
    for character_index, character in enumerate(characters):
        if not isinstance(character, Mapping):
            continue
        character_id = character.get("character_id")
        if not isinstance(character_id, str):
            continue
        location = f"characters.{character_index}.character_id"
        if character_id in character_ids:
            errors.append(f"{location}: duplicate ID {character_id}")
        else:
            character_ids.add(character_id)
        if re.fullmatch(character_pattern, character_id) is None:
            errors.append(
                f"{location}: {character_id!r} must match {project_id}-CH###"
            )

    for character_index, character in enumerate(characters):
        if not isinstance(character, Mapping):
            continue
        relationships = character.get("relationships")
        if not isinstance(relationships, list):
            continue
        for relationship_index, relationship in enumerate(relationships):
            if not isinstance(relationship, Mapping):
                continue
            target = relationship.get("target_character_id")
            if not isinstance(target, str):
                continue
            location = (
                f"characters.{character_index}.relationships."
                f"{relationship_index}.target_character_id"
            )
            if re.fullmatch(character_pattern, target) is None:
                errors.append(f"{location}: {target!r} must match {project_id}-CH###")
            elif target not in character_ids:
                errors.append(f"{location}: unknown character {target}")
    return errors


def validate_character_arc_event_references(
    payload: Mapping[str, Any], declared_event_ids: Collection[str]
) -> list[str]:
    """Validate character turning events against a story structure event catalog."""
    project_id = payload.get("project_id")
    characters = payload.get("characters")
    if not isinstance(project_id, str) or not isinstance(characters, list):
        return []

    known_events = set(declared_event_ids)
    event_pattern = rf"{re.escape(project_id)}-EV(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{{2}})"
    errors: list[str] = []
    for character_index, character in enumerate(characters):
        if not isinstance(character, Mapping):
            continue
        turning_event_ids = character.get("turning_event_ids")
        if not isinstance(turning_event_ids, list):
            continue
        for event_index, event_id in enumerate(turning_event_ids):
            if not isinstance(event_id, str):
                continue
            location = (
                f"characters.{character_index}.turning_event_ids.{event_index}"
            )
            if re.fullmatch(event_pattern, event_id) is None:
                errors.append(
                    f"{location}: {event_id!r} must match {project_id}-EV###"
                )
            elif event_id not in known_events:
                errors.append(f"{location}: unknown event {event_id}")
    return errors


def _validate_story_structure_identifiers(payload: Mapping[str, Any]) -> list[str]:
    project_id = payload.get("project_id")
    if not isinstance(project_id, str):
        return []

    errors: list[str] = []
    declared: dict[str, set[str]] = {}
    contracts = (
        (
            "plotlines",
            "plotline_id",
            r"PL(?:0[1-9]|[1-9][0-9])",
            "PL##",
            "PL01",
        ),
        (
            "sequences",
            "sequence_id",
            r"SQ(?:0[1-9]|[1-9][0-9])",
            "SQ##",
            "SQ01",
        ),
        (
            "events",
            "event_id",
            r"EV(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})",
            "EV###",
            "EV001",
        ),
    )
    for collection_name, id_name, suffix, example, starting_suffix in contracts:
        identifiers: set[str] = set()
        items = payload.get(collection_name)
        if not isinstance(items, list):
            declared[collection_name] = identifiers
            continue
        for item_index, item in enumerate(items):
            if not isinstance(item, Mapping):
                continue
            identifier = item.get(id_name)
            if not isinstance(identifier, str):
                continue
            location = f"{collection_name}.{item_index}.{id_name}"
            if item_index == 0 and identifier != f"{project_id}-{starting_suffix}":
                errors.append(
                    f"{location}: first declared ID must start with "
                    f"{project_id}-{starting_suffix}"
                )
            if identifier in identifiers:
                errors.append(f"{location}: duplicate ID {identifier}")
            else:
                identifiers.add(identifier)
            if re.fullmatch(rf"{re.escape(project_id)}-{suffix}", identifier) is None:
                errors.append(
                    f"{location}: {identifier!r} must match {project_id}-{example}"
                )
        declared[collection_name] = identifiers

    plotline_ids = declared["plotlines"]
    sequence_ids = declared["sequences"]
    event_ids = declared["events"]
    sequence_indexes: dict[str, int] = {}
    event_sequence_ids: dict[str, tuple[int, str]] = {}
    event_orders_by_id: dict[str, int] = {}
    event_memberships: dict[str, list[tuple[int, int, str]]] = {}

    def validate_reference(
        location: str,
        value: object,
        suffix: str,
        example: str,
        known: set[str],
        kind: str,
    ) -> None:
        if not isinstance(value, str):
            return
        if re.fullmatch(rf"{re.escape(project_id)}-{suffix}", value) is None:
            errors.append(f"{location}: {value!r} must match {project_id}-{example}")
        elif value not in known:
            errors.append(f"{location}: unknown {kind} {value}")

    sequences = payload.get("sequences")
    if isinstance(sequences, list):
        for sequence_index, sequence in enumerate(sequences):
            if not isinstance(sequence, Mapping):
                continue
            sequence_id = sequence.get("sequence_id")
            if isinstance(sequence_id, str) and sequence_id not in sequence_indexes:
                sequence_indexes[sequence_id] = sequence_index
            for field, suffix, example, known, kind in (
                (
                    "plotline_ids",
                    r"PL(?:0[1-9]|[1-9][0-9])",
                    "PL##",
                    plotline_ids,
                    "plotline",
                ),
                (
                    "event_ids",
                    r"EV(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})",
                    "EV###",
                    event_ids,
                    "event",
                ),
            ):
                references = sequence.get(field)
                if not isinstance(references, list):
                    continue
                for reference_index, reference in enumerate(references):
                    validate_reference(
                        f"sequences.{sequence_index}.{field}.{reference_index}",
                        reference,
                        suffix,
                        example,
                        known,
                        kind,
                    )
                    if (
                        field == "event_ids"
                        and isinstance(reference, str)
                        and isinstance(sequence_id, str)
                    ):
                        event_memberships.setdefault(reference, []).append(
                            (sequence_index, reference_index, sequence_id)
                        )

    events = payload.get("events")
    if isinstance(events, list):
        seen_orders: set[int] = set()
        event_orders: list[int] = []
        for event_index, event in enumerate(events):
            if not isinstance(event, Mapping):
                continue
            order = event.get("order")
            if isinstance(order, int):
                event_orders.append(order)
                if order in seen_orders:
                    errors.append(f"events.{event_index}.order: duplicate order {order}")
                seen_orders.add(order)
            validate_reference(
                f"events.{event_index}.sequence_id",
                event.get("sequence_id"),
                r"SQ(?:0[1-9]|[1-9][0-9])",
                "SQ##",
                sequence_ids,
                "sequence",
            )
            event_id = event.get("event_id")
            event_sequence_id = event.get("sequence_id")
            if (
                isinstance(event_id, str)
                and isinstance(order, int)
                and not isinstance(order, bool)
                and event_id not in event_orders_by_id
            ):
                event_orders_by_id[event_id] = order
            if (
                isinstance(event_id, str)
                and isinstance(event_sequence_id, str)
                and event_id not in event_sequence_ids
            ):
                event_sequence_ids[event_id] = (event_index, event_sequence_id)
            references = event.get("plotline_ids")
            if isinstance(references, list):
                for reference_index, reference in enumerate(references):
                    validate_reference(
                        f"events.{event_index}.plotline_ids.{reference_index}",
                        reference,
                        r"PL(?:0[1-9]|[1-9][0-9])",
                        "PL##",
                        plotline_ids,
                        "plotline",
                    )
        expected_orders = list(range(1, len(events) + 1))
        if len(event_orders) == len(events) and event_orders != expected_orders:
            errors.append(
                f"events: event order must be ascending order 1..{len(events)}"
            )

    for event_id, memberships in event_memberships.items():
        for sequence_index, reference_index, sequence_id in memberships[1:]:
            errors.append(
                f"sequences.{sequence_index}.event_ids.{reference_index}: "
                f"duplicate sequence membership for {event_id}"
            )
        event_declaration = event_sequence_ids.get(event_id)
        if event_declaration is None:
            continue
        _, declared_sequence_id = event_declaration
        for sequence_index, reference_index, sequence_id in memberships:
            if declared_sequence_id != sequence_id:
                errors.append(
                    f"sequences.{sequence_index}.event_ids.{reference_index}: "
                    f"{event_id} points back to {declared_sequence_id}, "
                    f"not {sequence_id}"
                )

    for event_id, (event_index, declared_sequence_id) in event_sequence_ids.items():
        declared_sequence_index = sequence_indexes.get(declared_sequence_id)
        if declared_sequence_index is None:
            continue
        matching_memberships = [
            membership
            for membership in event_memberships.get(event_id, [])
            if membership[2] == declared_sequence_id
        ]
        if not matching_memberships:
            errors.append(
                f"events.{event_index}.sequence_id: {event_id} is missing from "
                f"sequences.{declared_sequence_index}.event_ids"
            )

    pairs = payload.get("setup_payoffs")
    if isinstance(pairs, list):
        for pair_index, pair in enumerate(pairs):
            if not isinstance(pair, Mapping):
                continue
            for field in ("setup_event_id", "payoff_event_id"):
                validate_reference(
                    f"setup_payoffs.{pair_index}.{field}",
                    pair.get(field),
                    r"EV(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})",
                    "EV###",
                    event_ids,
                    "event",
                )
            setup_event_id = pair.get("setup_event_id")
            payoff_event_id = pair.get("payoff_event_id")
            setup_order = event_orders_by_id.get(setup_event_id)
            payoff_order = event_orders_by_id.get(payoff_event_id)
            if (
                setup_order is not None
                and payoff_order is not None
                and setup_order >= payoff_order
            ):
                errors.append(
                    f"setup_payoffs.{pair_index}.payoff_event_id: payoff event "
                    f"{payoff_event_id} must occur strictly after setup event "
                    f"{setup_event_id} by declared event order"
                )

    candidate_models = payload.get("candidate_models")
    candidate_names: set[str] = set()
    if isinstance(candidate_models, list):
        for candidate_index, candidate in enumerate(candidate_models):
            if not isinstance(candidate, Mapping):
                continue
            name = candidate.get("name")
            if not isinstance(name, str):
                continue
            if name in candidate_names:
                errors.append(
                    f"candidate_models.{candidate_index}.name: duplicate candidate {name}"
                )
            candidate_names.add(name)
    selected_model = payload.get("selected_model")
    if isinstance(selected_model, str) and selected_model not in candidate_names:
        errors.append(f"selected_model: unknown candidate {selected_model}")
    components = payload.get("hybrid_components")
    if isinstance(components, list):
        for component_index, component in enumerate(components):
            if not isinstance(component, Mapping):
                continue
            source_model = component.get("source_model")
            if isinstance(source_model, str) and source_model not in candidate_names:
                errors.append(
                    f"hybrid_components.{component_index}.source_model: "
                    f"unknown candidate {source_model}"
                )
    return errors


def _validate_artifact_identifiers(
    schema_name: str, payload: Mapping[str, Any]
) -> list[str]:
    collection_name, id_name, id_suffix, id_example, reference_contracts = (
        _IDENTIFIER_CONTRACTS[schema_name]
    )
    scene_id = payload.get("scene_id")
    items = payload.get(collection_name)
    if not isinstance(scene_id, str) or not isinstance(items, list):
        return []

    errors: list[str] = []
    seen: set[str] = set()
    for item_index, item in enumerate(items):
        if not isinstance(item, Mapping):
            continue
        identifier = item.get(id_name)
        id_location = f"{collection_name}.{item_index}.{id_name}"
        if isinstance(identifier, str):
            if identifier in seen:
                errors.append(f"{id_location}: duplicate ID {identifier}")
            else:
                seen.add(identifier)
            if re.fullmatch(rf"{re.escape(scene_id)}-{id_suffix}", identifier) is None:
                errors.append(
                    f"{id_location}: {identifier!r} must match {scene_id}-{id_example}"
                )

        for reference_contract in reference_contracts:
            ref_name, ref_suffix, ref_example = reference_contract[:3]
            cardinality = (
                reference_contract[3] if len(reference_contract) == 4 else "many"
            )
            references = item.get(ref_name)
            if cardinality == "single":
                references_with_locations = [(ref_name, references)]
            elif isinstance(references, list):
                references_with_locations = [
                    (f"{ref_name}.{ref_index}", reference)
                    for ref_index, reference in enumerate(references)
                ]
            else:
                continue
            for ref_location, reference in references_with_locations:
                if not isinstance(reference, str):
                    continue
                if re.fullmatch(
                    rf"{re.escape(scene_id)}-{ref_suffix}", reference
                ) is None:
                    errors.append(
                        f"{collection_name}.{item_index}.{ref_location}: "
                        f"{reference!r} must match {scene_id}-{ref_example}"
                    )
    return errors


def validate_artifact_file(schema_name: str, json_path: Path, root: Path) -> list[str]:
    """Validate a JSON artifact file against a repository schema."""
    payload, errors = load_json_object(json_path)
    if errors:
        return errors
    assert payload is not None
    return validate_artifact(schema_name, payload, root)

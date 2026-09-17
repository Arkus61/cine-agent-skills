"""Validation for exact production-v2 package inventories."""

from __future__ import annotations

from collections.abc import Collection, Mapping
from pathlib import Path
from typing import Any

from .project_contracts import (
    PRODUCTION_MODES,
    PRODUCTION_PROFILE,
    ProjectIndex,
    required_production_artifacts,
)
from .project_validation import (
    inspect_exact_entries,
    load_validated_artifacts,
    validate_layer_manifest,
)


def _existing_contracts(directory: Path, contracts: Collection[Any]) -> tuple[Any, ...]:
    return tuple(contract for contract in contracts if (directory / contract.filename).is_file())


def _wrong_file_type_errors(directory: Path, contracts: Collection[Any]) -> list[str]:
    return [
        f"{contract.filename}: required file is missing"
        for contract in contracts
        if ((directory / contract.filename).exists() or (directory / contract.filename).is_symlink())
        and not (directory / contract.filename).is_file()
    ]


def _strings(value: Any) -> set[str]:
    return {item for item in value if isinstance(item, str)} if isinstance(value, list) else set()


def _records(value: Any) -> list[Mapping[str, Any]]:
    return [item for item in value if isinstance(item, Mapping)] if isinstance(value, list) else []


def _context_ids(payload: Mapping[str, Any], field: str) -> set[str]:
    context = payload.get("source_context")
    return _strings(context.get(field)) if isinstance(context, Mapping) else set()


def _reference_errors(
    errors: list[str], filename: str, location: str, values: Collection[str], known: Collection[str], label: str
) -> None:
    allowed = set(known)
    for value in sorted(set(values)):
        if value not in allowed:
            errors.append(f"{filename}: {location}: unknown upstream {label} {value}")


def _project_prefix_errors(
    errors: list[str], filename: str, location: str, values: Collection[str], project_id: str
) -> None:
    for value in sorted(set(values)):
        if not value.startswith(f"{project_id}-"):
            errors.append(f"{filename}: {location}: {value} must belong to project {project_id}")


def _coverage_errors(
    errors: list[str], filename: str, label: str, expected: Collection[str], actual: Collection[str]
) -> None:
    for shot_id in sorted(set(expected) - set(actual)):
        errors.append(f"{filename}: missing {label} for upstream shot {shot_id}")
    for shot_id in sorted(set(actual) - set(expected)):
        errors.append(f"{filename}: {label} names out-of-context shot {shot_id}")


def _exact_context_errors(
    errors: list[str],
    filename: str,
    location: str,
    actual: Collection[str],
    expected: Collection[str],
    label: str,
) -> None:
    for identifier in sorted(set(expected) - set(actual)):
        errors.append(
            f"{filename}: {location}: missing upstream {label} {identifier}"
        )
    for identifier in sorted(set(actual) - set(expected)):
        errors.append(
            f"{filename}: {location}: names out-of-context {label} {identifier}"
        )


def _production_design_errors(payload: Mapping[str, Any], upstream: ProjectIndex) -> list[str]:
    filename = "production-design-plan.json"
    errors: list[str] = []
    source_shots = _context_ids(payload, "shot_ids")
    _exact_context_errors(
        errors, filename, "source_context.shot_ids", source_shots,
        upstream.shot_ids, "shot",
    )
    _exact_context_errors(
        errors, filename, "source_context.scene_ids", _context_ids(payload, "scene_ids"),
        upstream.scene_ids, "scene",
    )
    _exact_context_errors(
        errors, filename, "source_context.world_ids", _context_ids(payload, "world_ids"),
        upstream.world_ids, "world",
    )
    _reference_errors(errors, filename, "source_context.shot_ids", source_shots, upstream.shot_ids, "shot")
    _reference_errors(errors, filename, "source_context.scene_ids", _context_ids(payload, "scene_ids"), upstream.scene_ids, "scene")
    _reference_errors(errors, filename, "source_context.world_ids", _context_ids(payload, "world_ids"), upstream.world_ids, "world")
    assets = _records(payload.get("assets"))
    asset_ids = {item["asset_id"] for item in assets if isinstance(item.get("asset_id"), str)}
    _project_prefix_errors(errors, filename, "assets.asset_id", asset_ids, upstream.project_id)
    for asset_id in sorted(set(upstream.asset_ids) - asset_ids):
        errors.append(f"{filename}: missing declared continuity asset {asset_id}")
    for index, asset in enumerate(assets):
        _reference_errors(errors, filename, f"assets.{index}.scene_ids", _strings(asset.get("scene_ids")), upstream.scene_ids, "scene")
        _reference_errors(errors, filename, f"assets.{index}.shot_ids", _strings(asset.get("shot_ids")), upstream.shot_ids, "shot")
        _reference_errors(errors, filename, f"assets.{index}.world_ids", _strings(asset.get("world_ids")), upstream.world_ids, "world")
    coverage = _records(payload.get("coverage"))
    coverage_shots = {item["shot_id"] for item in coverage if isinstance(item.get("shot_id"), str)}
    _coverage_errors(errors, filename, "coverage", upstream.shot_ids, coverage_shots)
    for index, record in enumerate(coverage):
        _reference_errors(errors, filename, f"coverage.{index}.shot_id", _strings([record.get("shot_id")]), upstream.shot_ids, "shot")
        _reference_errors(errors, filename, f"coverage.{index}.scene_id", _strings([record.get("scene_id")]), upstream.scene_ids, "scene")
        _reference_errors(errors, filename, f"coverage.{index}.asset_ids", _strings(record.get("asset_ids")), asset_ids, "asset")
    for index, state in enumerate(_records(payload.get("continuity_states"))):
        _reference_errors(errors, filename, f"continuity_states.{index}.asset_id", _strings([state.get("asset_id")]), asset_ids, "asset")
        _reference_errors(errors, filename, f"continuity_states.{index}.shot_ids", _strings(state.get("shot_ids")), upstream.shot_ids, "shot")
    for index, dependency in enumerate(_records(payload.get("cross_department_dependencies"))):
        _reference_errors(errors, filename, f"cross_department_dependencies.{index}.asset_ids", _strings(dependency.get("asset_ids")), asset_ids, "asset")
        _reference_errors(errors, filename, f"cross_department_dependencies.{index}.shot_ids", _strings(dependency.get("shot_ids")), upstream.shot_ids, "shot")
    return errors


def _character_look_errors(payload: Mapping[str, Any], upstream: ProjectIndex) -> list[str]:
    filename = "character-look-bible.json"
    errors: list[str] = []
    context = payload.get("source_context")
    source_shots = {
        item["shot_id"] for item in _records(context.get("shots") if isinstance(context, Mapping) else None)
        if isinstance(item.get("shot_id"), str)
    }
    _exact_context_errors(
        errors, filename, "source_context.character_ids", _context_ids(payload, "character_ids"),
        upstream.character_ids, "character",
    )
    _exact_context_errors(
        errors, filename, "source_context.scene_ids", _context_ids(payload, "scene_ids"),
        upstream.scene_ids, "scene",
    )
    _exact_context_errors(
        errors, filename, "source_context.shots", source_shots,
        upstream.shot_ids, "shot",
    )
    _reference_errors(errors, filename, "source_context.character_ids", _context_ids(payload, "character_ids"), upstream.character_ids, "character")
    _reference_errors(errors, filename, "source_context.scene_ids", _context_ids(payload, "scene_ids"), upstream.scene_ids, "scene")
    _reference_errors(errors, filename, "source_context.shots", source_shots, upstream.shot_ids, "shot")
    coverage = _records(payload.get("shot_coverage"))
    coverage_shots = {item["shot_id"] for item in coverage if isinstance(item.get("shot_id"), str)}
    _coverage_errors(errors, filename, "shot coverage", upstream.shot_ids, coverage_shots)
    for index, record in enumerate(coverage):
        _reference_errors(errors, filename, f"shot_coverage.{index}.shot_id", _strings([record.get("shot_id")]), upstream.shot_ids, "shot")
        _reference_errors(errors, filename, f"shot_coverage.{index}.character_id", _strings([record.get("character_id")]), upstream.character_ids, "character")
    return errors


def _animation_errors(payload: Mapping[str, Any], upstream: ProjectIndex) -> list[str]:
    filename = "animation-plan.json"
    errors: list[str] = []
    context = payload.get("source_context")
    source_shots = {
        item["shot_id"] for item in _records(context.get("shots") if isinstance(context, Mapping) else None)
        if isinstance(item.get("shot_id"), str)
    }
    _reference_errors(errors, filename, "source_context.character_ids", _context_ids(payload, "character_ids"), upstream.character_ids, "character")
    _reference_errors(errors, filename, "source_context.scene_ids", _context_ids(payload, "scene_ids"), upstream.scene_ids, "scene")
    _reference_errors(errors, filename, "source_context.shots", source_shots, upstream.shot_ids, "shot")
    plans = _records(payload.get("shot_character_plans"))
    plan_shots = {item["shot_id"] for item in plans if isinstance(item.get("shot_id"), str)}
    _coverage_errors(errors, filename, "shot-character plan", upstream.shot_ids, plan_shots)
    for index, plan in enumerate(plans):
        _reference_errors(errors, filename, f"shot_character_plans.{index}.shot_id", _strings([plan.get("shot_id")]), upstream.shot_ids, "shot")
        _reference_errors(errors, filename, f"shot_character_plans.{index}.character_id", _strings([plan.get("character_id")]), upstream.character_ids, "character")
    return errors


def _vfx_errors(payload: Mapping[str, Any], upstream: ProjectIndex) -> list[str]:
    filename = "vfx-plan.json"
    errors: list[str] = []
    context = payload.get("source_context")
    source_scenes = {item["scene_id"] for item in _records(context.get("scenes") if isinstance(context, Mapping) else None) if isinstance(item.get("scene_id"), str)}
    source_shots = {item["shot_id"] for item in _records(context.get("shots") if isinstance(context, Mapping) else None) if isinstance(item.get("shot_id"), str)}
    _reference_errors(errors, filename, "source_context.scenes", source_scenes, upstream.scene_ids, "scene")
    _reference_errors(errors, filename, "source_context.shots", source_shots, upstream.shot_ids, "shot")
    applicability = _records(payload.get("applicability"))
    applicability_shots = {item["shot_id"] for item in applicability if isinstance(item.get("shot_id"), str)}
    _coverage_errors(errors, filename, "applicability", upstream.shot_ids, applicability_shots)
    effect_ids = {item["effect_id"] for item in _records(payload.get("effects")) if isinstance(item.get("effect_id"), str)}
    _project_prefix_errors(errors, filename, "effects.effect_id", effect_ids, upstream.project_id)
    for index, record in enumerate(applicability):
        _reference_errors(errors, filename, f"applicability.{index}.effect_ids", _strings(record.get("effect_ids")), effect_ids, "effect")
    for index, effect in enumerate(_records(payload.get("effects"))):
        _reference_errors(errors, filename, f"effects.{index}.shot_ids", _strings(effect.get("shot_ids")), upstream.shot_ids, "shot")
    return errors


def _reference_pairs(value: Any) -> set[tuple[str, str]]:
    return {
        (item["kind"], item["id"])
        for item in _records(value)
        if isinstance(item.get("kind"), str) and isinstance(item.get("id"), str)
    }


def _check_pairs(errors: list[str], filename: str, location: str, pairs: Collection[tuple[str, str]], upstream: ProjectIndex, asset_ids: Collection[str]) -> None:
    registries = {
        "character": upstream.character_ids, "scene": upstream.scene_ids,
        "shot": upstream.shot_ids, "world": upstream.world_ids,
        "asset": set(upstream.asset_ids) | set(asset_ids), "beat": upstream.beat_ids,
        "sound": upstream.sound_ids,
    }
    for kind, identifier in sorted(set(pairs)):
        known = registries.get(kind)
        if known is None or identifier not in known:
            errors.append(f"{filename}: {location}: unknown upstream {kind} reference {identifier}")


def _prompt_errors(payload: Mapping[str, Any], upstream: ProjectIndex, asset_ids: Collection[str]) -> list[str]:
    filename = "media-prompt-package.json"
    errors: list[str] = []
    prompt_ids: set[str] = set()
    covered_shots: set[str] = set()
    for index, prompt in enumerate(_records(payload.get("prompts"))):
        prompt_id = prompt.get("prompt_id")
        if isinstance(prompt_id, str):
            prompt_ids.add(prompt_id)
        pairs = _reference_pairs(prompt.get("upstream_references"))
        _check_pairs(errors, filename, f"prompts.{index}.upstream_references", pairs, upstream, asset_ids)
        covered_shots.update(identifier for kind, identifier in pairs if kind == "shot")
    _project_prefix_errors(errors, filename, "prompts.prompt_id", prompt_ids, upstream.project_id)
    _coverage_errors(errors, filename, "prompt coverage", upstream.shot_ids, covered_shots)
    return errors


def _review_errors(payload: Mapping[str, Any], upstream: ProjectIndex, asset_ids: Collection[str], prompts: Mapping[str, Mapping[str, Any]], require_prompts: bool) -> list[str]:
    filename = "media-review-report.json"
    errors: list[str] = []
    context = payload.get("source_context")
    packages = _records(context.get("prompt_packages") if isinstance(context, Mapping) else None)
    if isinstance(context, Mapping):
        registries = context.get("registries")
        if isinstance(registries, Mapping):
            for field, kind, known in (
                ("character_ids", "character", upstream.character_ids),
                ("scene_ids", "scene", upstream.scene_ids),
                ("shot_ids", "shot", upstream.shot_ids),
                ("world_ids", "world", upstream.world_ids),
                ("asset_ids", "asset", set(upstream.asset_ids) | set(asset_ids)),
                ("beat_ids", "beat", upstream.beat_ids),
                ("sound_ids", "sound", upstream.sound_ids),
            ):
                _reference_errors(errors, filename, f"source_context.registries.{field}", _strings(registries.get(field)), known, kind)
    for index, record in enumerate(packages):
        prompt_id = record.get("prompt_id")
        if require_prompts and (not isinstance(prompt_id, str) or prompt_id not in prompts):
            errors.append(f"{filename}: source_context.prompt_packages.{index}.prompt_id: unknown in-package prompt {prompt_id}")
            continue
        if isinstance(prompt_id, str) and prompt_id in prompts:
            source_pairs = _reference_pairs(record.get("upstream_references"))
            actual_pairs = _reference_pairs(prompts[prompt_id].get("upstream_references"))
            if source_pairs != actual_pairs:
                errors.append(f"{filename}: source_context.prompt_packages.{index}.upstream_references: must exactly match in-package prompt {prompt_id}")
            criteria = record.get("acceptance_criteria")
            prompt_criteria = prompts[prompt_id].get("acceptance_criteria")
            if isinstance(criteria, list) and isinstance(prompt_criteria, list):
                expected_criteria = [
                    (
                        statement,
                        f"media-prompt-package.json#/prompts/{prompt_id}/acceptance_criteria/{criterion_index}",
                    )
                    for criterion_index, statement in enumerate(prompt_criteria)
                ]
                actual_criteria = [
                    (criterion.get("statement"), criterion.get("source_reference"))
                    if isinstance(criterion, Mapping) else (None, None)
                    for criterion in criteria
                ]
                if actual_criteria != expected_criteria:
                    errors.append(
                        f"{filename}: source_context.prompt_packages.{index}.acceptance_criteria: "
                        f"must exactly match in-package prompt {prompt_id}"
                    )
                for criterion_index, criterion in enumerate(criteria):
                    if not isinstance(criterion, Mapping):
                        continue
                    criterion_id = criterion.get("criterion_id")
                    if isinstance(criterion_id, str) and not criterion_id.startswith(f"{upstream.project_id}-"):
                        errors.append(f"{filename}: source_context.prompt_packages.{index}.acceptance_criteria.{criterion_index}.criterion_id: {criterion_id} must belong to project {upstream.project_id}")
                    if criterion_index >= len(prompt_criteria) or criterion.get("statement") != prompt_criteria[criterion_index]:
                        errors.append(f"{filename}: source_context.prompt_packages.{index}.acceptance_criteria.{criterion_index}: statement does not match in-package prompt {prompt_id}")
                    expected_reference = f"media-prompt-package.json#/prompts/{prompt_id}/acceptance_criteria/{criterion_index}"
                    if criterion.get("source_reference") != expected_reference:
                        errors.append(f"{filename}: source_context.prompt_packages.{index}.acceptance_criteria.{criterion_index}.source_reference: must bind {expected_reference}")
    reviewed_prompt_ids: set[str] = set()
    reviewed_shots: set[str] = set()
    for item_index, item in enumerate(_records(payload.get("items"))):
        _check_pairs(errors, filename, f"items.{item_index}.upstream_references", _reference_pairs(item.get("upstream_references")), upstream, asset_ids)
        item_pairs = _reference_pairs(item.get("upstream_references"))
        reviewed_shots.update(identifier for kind, identifier in item_pairs if kind == "shot")
        if item.get("status") == "approved" and not _records(item.get("inspection_evidence")):
            errors.append(f"{filename}: items.{item_index}: approved media requires non-empty inspection evidence")
        prompt_id = item.get("prompt_id")
        if isinstance(prompt_id, str):
            reviewed_prompt_ids.add(prompt_id)
        if require_prompts and (not isinstance(prompt_id, str) or prompt_id not in prompts):
            errors.append(f"{filename}: items.{item_index}.prompt_id: unknown in-package prompt {prompt_id}")
    if payload.get("package_status") == "awaiting-media" and _records(payload.get("items")):
        errors.append(f"{filename}: awaiting-media status cannot contain reviewed media items")
    if require_prompts and payload.get("package_status") == "reviewed":
        if reviewed_prompt_ids != set(prompts):
            errors.append(f"{filename}: reviewed media items must cover exactly the in-package prompt IDs")
        _coverage_errors(errors, filename, "reviewed media coverage", upstream.shot_ids, reviewed_shots)
    for index, item in enumerate(_records(payload.get("items"))):
        media_id = item.get("media_id")
        if isinstance(media_id, str) and not media_id.startswith(f"{upstream.project_id}-"):
            errors.append(f"{filename}: items.{index}.media_id: {media_id} must belong to project {upstream.project_id}")
    return errors


def validate_production_package(package_dir: Path, root: Path, production_modes: Collection[str], upstream: ProjectIndex, *, enforce_directory_name: bool = True) -> list[str]:
    """Validate an exact production-v2 package against an authoritative index."""
    package = Path(package_dir)
    try:
        contracts = required_production_artifacts(production_modes)
    except ValueError as exc:
        return [str(exc)]
    modes = tuple(production_modes)
    errors: list[str] = []
    if len(set(modes)) != len(modes):
        errors.append("production modes must not contain duplicates")
    if set(modes) != set(upstream.production_modes):
        errors.append("production modes must exactly match upstream project modes: " + ", ".join(sorted(upstream.production_modes)))
    expected = {contract.filename for contract in contracts}
    inventory_errors = inspect_exact_entries(package, expected, PRODUCTION_PROFILE)
    if any("unable to inspect" in error for error in inventory_errors):
        return inventory_errors
    payloads, load_errors = load_validated_artifacts(package, _existing_contracts(package, contracts), Path(root))
    errors.extend(inventory_errors)
    errors.extend(_wrong_file_type_errors(package, contracts))
    errors.extend(load_errors)
    if enforce_directory_name and package.name != upstream.project_id:
        errors.append(f"package directory {package.name} does not match project_id {upstream.project_id}")
    for filename, payload in payloads.items():
        if payload.get("project_id") != upstream.project_id:
            errors.append(f"{filename}: project_id {payload.get('project_id')} does not match {upstream.project_id}")
    manifest = payloads.get("production-manifest.json")
    if manifest is not None:
        if manifest.get("layer") != "production":
            errors.append(f"production-manifest.json: layer {manifest.get('layer')} does not match production")
        if manifest.get("profile") != PRODUCTION_PROFILE:
            errors.append(f"production-manifest.json: profile {manifest.get('profile')} does not match {PRODUCTION_PROFILE}")
        errors.extend(validate_layer_manifest(manifest, contracts, "production-manifest.json"))
    design = payloads.get("production-design-plan.json")
    if design is not None:
        errors.extend(_production_design_errors(design, upstream))
    look = payloads.get("character-look-bible.json")
    if look is not None:
        errors.extend(_character_look_errors(look, upstream))
    animation = payloads.get("animation-plan.json")
    if animation is not None:
        errors.extend(_animation_errors(animation, upstream))
    vfx = payloads.get("vfx-plan.json")
    if vfx is not None:
        errors.extend(_vfx_errors(vfx, upstream))
    asset_ids = {
        item["asset_id"] for item in _records(design.get("assets") if design is not None else None)
        if isinstance(item.get("asset_id"), str)
    }
    prompt_payload = payloads.get("media-prompt-package.json")
    prompts = {
        item["prompt_id"]: item for item in _records(prompt_payload.get("prompts") if prompt_payload is not None else None)
        if isinstance(item.get("prompt_id"), str)
    }
    if prompt_payload is not None:
        errors.extend(_prompt_errors(prompt_payload, upstream, asset_ids))
    review = payloads.get("media-review-report.json")
    if review is not None:
        errors.extend(_review_errors(review, upstream, asset_ids, prompts, "ai" in set(modes) or "hybrid" in set(modes)))
    return sorted(set(errors))


def _context_registry_ids(payload: Mapping[str, Any], field: str) -> set[str]:
    context = payload.get("source_context")
    registries = context.get("registries") if isinstance(context, Mapping) else None
    return _strings(registries.get(field)) if isinstance(registries, Mapping) else set()


def derive_production_index_at(package_dir: Path, root: Path, production_modes: Collection[str]) -> tuple[ProjectIndex | None, list[str]]:
    """Derive a CLI-only index from validated package context, never external proof.

    External story/script authenticity requires ``validate_production_package``
    with an independently built ``ProjectIndex``.
    """
    package = Path(package_dir)
    try:
        contracts = required_production_artifacts(production_modes)
    except ValueError as exc:
        return None, [str(exc)]
    payloads, errors = load_validated_artifacts(package, _existing_contracts(package, contracts), Path(root))
    if errors:
        return None, errors
    design = payloads.get("production-design-plan.json")
    look = payloads.get("character-look-bible.json")
    if design is None or look is None:
        return None, ["production package source contexts cannot be resolved without production-design-plan.json and character-look-bible.json"]
    project_id = design.get("project_id")
    context = design.get("source_context")
    look_context = look.get("source_context")
    if not isinstance(project_id, str) or not isinstance(context, Mapping) or not isinstance(look_context, Mapping):
        return None, ["production package source contexts cannot be resolved"]
    prompt = payloads.get("media-prompt-package.json")
    review = payloads.get("media-review-report.json")
    prompt_beats = _context_registry_ids(prompt, "beat_ids") if prompt is not None else set()
    review_beats = _context_registry_ids(review, "beat_ids") if review is not None else set()
    if prompt_beats and review_beats and prompt_beats != review_beats:
        return None, [
            "media prompt and review beat registries must exactly match for standalone CLI derivation"
        ]
    prompt_sounds = _context_registry_ids(prompt, "sound_ids") if prompt is not None else set()
    review_sounds = _context_registry_ids(review, "sound_ids") if review is not None else set()
    if prompt_sounds and review_sounds and prompt_sounds != review_sounds:
        return None, [
            "media prompt and review sound registries must exactly match for standalone CLI derivation"
        ]
    prompt_media = _context_registry_ids(prompt, "media_ids") if prompt is not None else set()
    review_media = _context_registry_ids(review, "media_ids") if review is not None else set()
    if prompt_media and review_media and prompt_media != review_media:
        return None, [
            "media prompt and review media registries must exactly match for standalone CLI derivation"
        ]
    return ProjectIndex(
        project_id=project_id, project_format="", production_modes=tuple(production_modes),
        scene_ids=frozenset(_strings(context.get("scene_ids"))), shot_ids=frozenset(_strings(context.get("shot_ids"))),
        character_ids=frozenset(_strings(look_context.get("character_ids"))), world_ids=frozenset(_strings(context.get("world_ids"))),
        asset_ids=frozenset(item["asset_id"] for item in _records(design.get("assets")) if isinstance(item.get("asset_id"), str)),
        beat_ids=frozenset(prompt_beats or review_beats),
        sound_ids=frozenset(prompt_sounds or review_sounds),
        media_ids=frozenset(prompt_media or review_media),
    ), []

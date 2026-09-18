"""Compact, literal production package fixtures."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from cine_skills.project_contracts import ProjectIndex, required_production_artifacts
from tests.test_artifacts import (
    valid_animation_plan,
    valid_character_look_bible,
    valid_media_prompt_package,
    valid_media_review_report,
    valid_production_design_plan,
    valid_vfx_plan,
)


PROJECT_ID = "NINEL"
SCENE_ID = "NINEL-U01-S01"
SHOT_IDS = tuple(f"{SCENE_ID}-SH{index:03d}" for index in range(1, 5))


def production_index(modes: tuple[str, ...]) -> ProjectIndex:
    return ProjectIndex(
        project_id=PROJECT_ID,
        project_format="short",
        production_modes=modes,
        unit_ids=frozenset({"NINEL-U01"}),
        scene_ids=frozenset({SCENE_ID}),
        beat_ids=frozenset({"NINEL-B001"}),
        shot_ids=frozenset(SHOT_IDS),
        character_ids=frozenset({"NINEL-CH001"}),
        world_ids=frozenset({"NINEL-LO001", "NINEL-WR001", "NINEL-WR002"}),
        asset_ids=frozenset({"NINEL-AS001", "NINEL-AS002", "NINEL-AS003", "NINEL-AS004"}),
    )


def _normalise(payload: dict[str, object]) -> dict[str, object]:
    """Map independently tested specialist fixtures onto one literal project."""
    encoded = json.dumps(payload)
    for source, target in (
        ("MORROW-U01-S01", SCENE_ID),
        ("ORBIT-S01", SCENE_ID),
        ("LANTERN-U01-S02", SCENE_ID),
        ("NINEL-E01-SC001", SCENE_ID),
        ("NINEL-E01-S01", SCENE_ID),
        ("MORROW", PROJECT_ID),
        ("ORBIT", PROJECT_ID),
        ("LANTERN", PROJECT_ID),
    ):
        encoded = encoded.replace(source, target)
    value = json.loads(encoded)
    assert isinstance(value, dict)
    return value


def _awaiting_media_report() -> dict[str, object]:
    report = _normalise(valid_media_review_report())
    report["package_status"] = "awaiting-media"
    report["items"] = []
    report["blockers"] = []
    report["missing_inputs"] = [
        {"kind": "media", "detail": "No inspectable media was supplied."},
        {"kind": "criterion", "detail": "Criteria cannot be assessed without media."},
    ]
    return report


def _bound_prompt_and_review() -> tuple[dict[str, object], dict[str, object]]:
    prompt = _normalise(valid_media_prompt_package())
    review = _normalise(valid_media_review_report())
    prompts = prompt["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    reviewed_packages = review["source_context"]
    assert isinstance(reviewed_packages, dict)
    packages = reviewed_packages["prompt_packages"]
    assert isinstance(packages, list) and isinstance(packages[0], dict)
    references = [
        {"kind": "character", "id": "NINEL-CH001"},
        {"kind": "scene", "id": SCENE_ID},
        *[{"kind": "shot", "id": shot_id} for shot_id in SHOT_IDS],
    ]
    prompt["prompts"] = [
        {
            **prompts[0],
            "upstream_references": references,
            "acceptance_criteria": [
                criterion["statement"]
                for criterion in packages[0]["acceptance_criteria"]
                if isinstance(criterion, dict)
            ],
        }
    ]
    prompt_context = prompt["source_context"]
    assert isinstance(prompt_context, dict)
    prompt_registries = prompt_context["registries"]
    assert isinstance(prompt_registries, dict)
    prompt_registries["shot_ids"] = list(SHOT_IDS)
    packages[0]["upstream_references"] = references
    items = review["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["upstream_references"] = references
    registries = reviewed_packages["registries"]
    assert isinstance(registries, dict)
    registries["character_ids"] = ["NINEL-CH001"]
    registries["shot_ids"] = list(SHOT_IDS)
    return prompt, review


def _expand_character_coverage(payload: dict[str, object]) -> None:
    context = payload["source_context"]
    assert isinstance(context, dict)
    shots = context["shots"]
    assert isinstance(shots, list)
    shots.extend({"scene_id": SCENE_ID, "shot_id": shot_id} for shot_id in SHOT_IDS[2:])
    states = payload["continuity_states"]
    assert isinstance(states, list) and isinstance(states[1], dict)
    state_shots = states[1]["shot_ids"]
    assert isinstance(state_shots, list)
    state_shots.extend(SHOT_IDS[2:])
    coverage = payload["shot_coverage"]
    assert isinstance(coverage, list) and isinstance(coverage[1], dict)
    for shot_id in SHOT_IDS[2:]:
        record = deepcopy(coverage[1])
        record["shot_id"] = shot_id
        coverage.append(record)


def _expand_vfx_coverage(payload: dict[str, object]) -> None:
    context = payload["source_context"]
    assert isinstance(context, dict)
    shots = context["shots"]
    applicability = payload["applicability"]
    assert isinstance(shots, list) and isinstance(shots[1], dict)
    assert isinstance(applicability, list) and isinstance(applicability[1], dict)
    for shot_id in SHOT_IDS[2:]:
        source = deepcopy(shots[1])
        source["shot_id"] = shot_id
        shots.append(source)
        record = deepcopy(applicability[1])
        record["shot_id"] = shot_id
        record["classification"] = "no-vfx"
        record["effect_ids"] = []
        applicability.append(record)


def _expand_animation_coverage(payload: dict[str, object]) -> None:
    context = payload["source_context"]
    plans = payload["shot_character_plans"]
    assert isinstance(context, dict) and isinstance(context["shots"], list)
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    source_shot = context["shots"][0]
    assert isinstance(source_shot, dict)
    for order, shot_id in enumerate(SHOT_IDS[1:], start=2):
        encoded_source = json.dumps(source_shot).replace(SHOT_IDS[0], shot_id)
        encoded_source = encoded_source.replace("NINEL-CI001", f"NINEL-CI{order:03d}")
        encoded_source = encoded_source.replace("NINEL-PI001", f"NINEL-PI{order:03d}")
        source = json.loads(encoded_source)
        assert isinstance(source, dict)
        context["shots"].append(source)
        encoded_plan = json.dumps(plans[0]).replace(SHOT_IDS[0], shot_id)
        encoded_plan = encoded_plan.replace("NINEL-AP001", f"NINEL-AP{order:03d}")
        encoded_plan = encoded_plan.replace("NINEL-CI001", f"NINEL-CI{order:03d}")
        encoded_plan = encoded_plan.replace("NINEL-PI001", f"NINEL-PI{order:03d}")
        plan = json.loads(encoded_plan)
        assert isinstance(plan, dict)
        continuity = plan["continuity"]
        assert isinstance(continuity, dict)
        continuity["order"] = order
        continuity["previous_continuity_id"] = f"NINEL-AP{order - 1:03d}-CT001"
        plans.append(plan)


def production_payloads(modes: tuple[str, ...]) -> dict[str, dict[str, object]]:
    """Return schema-valid payloads with the exact mode-specific inventory."""
    payloads = {
        "production-design-plan.json": _normalise(valid_production_design_plan()),
        "character-look-bible.json": _normalise(valid_character_look_bible()),
        "vfx-plan.json": _normalise(valid_vfx_plan()),
        "media-review-report.json": _awaiting_media_report(),
    }
    _expand_character_coverage(payloads["character-look-bible.json"])
    _expand_vfx_coverage(payloads["vfx-plan.json"])
    if {"animation", "hybrid"}.intersection(modes):
        payloads["animation-plan.json"] = _normalise(valid_animation_plan())
        _expand_animation_coverage(payloads["animation-plan.json"])
    if {"ai", "hybrid"}.intersection(modes):
        prompt, review = _bound_prompt_and_review()
        payloads["media-prompt-package.json"] = prompt
        payloads["media-review-report.json"] = review
    contracts = required_production_artifacts(modes)
    payloads["production-manifest.json"] = {
        "schema_version": "0.3.0",
        "release_version": "0.3.0",
        "project_id": PROJECT_ID,
        "layer": "production",
        "profile": "production",
        "artifacts": [
            {
                "filename": contract.filename,
                "schema_name": contract.schema_name,
                "schema_version": "0.3.0",
                "dependency_order": contract.dependency_order,
            }
            for contract in contracts
        ],
        "validation_status": "valid",
        "unresolved_questions": [],
    }
    return payloads


def write_production_package(package: Path, modes: tuple[str, ...]) -> ProjectIndex:
    package.mkdir(parents=True)
    for filename, payload in production_payloads(modes).items():
        (package / filename).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return production_index(modes)


def replace_payload(package: Path, filename: str, payload: dict[str, object]) -> None:
    (package / filename).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def read_payload(package: Path, filename: str) -> dict[str, Any]:
    value = json.loads((package / filename).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return deepcopy(value)

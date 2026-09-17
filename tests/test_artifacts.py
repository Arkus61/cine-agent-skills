import copy
import json
from pathlib import Path

import pytest

from cine_skills.artifacts import (
    validate_artifact,
    validate_artifact_file,
    validate_character_arc_event_references,
)


ID_FIELD_CASES = [
    ("scene-beats", "scene-beats.json", ("beats", 0, "beat_id"), "beats.0.beat_id"),
    (
        "blocking-plan",
        "blocking-plan.json",
        ("moves", 0, "beat_id"),
        "moves.0.beat_id",
    ),
    (
        "camera-movement-plan",
        "camera-movement-plan.json",
        ("moves", 0, "move_id"),
        "moves.0.move_id",
    ),
    (
        "camera-movement-plan",
        "camera-movement-plan.json",
        ("moves", 0, "beat_ids", 0),
        "moves.0.beat_ids.0",
    ),
    ("shot-list", "shot-list.json", ("shots", 0, "shot_id"), "shots.0.shot_id"),
    (
        "shot-list",
        "shot-list.json",
        ("shots", 0, "beat_ids", 0),
        "shots.0.beat_ids.0",
    ),
]


def load_ninel_artifact(repository_root: Path, filename: str) -> dict[str, object]:
    path = repository_root / "examples" / "ninel" / "scenes" / "S01" / filename
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def replace_nested_value(
    payload: dict[str, object], path: tuple[str | int, ...], value: str
) -> None:
    target: object = payload
    for component in path[:-1]:
        if isinstance(component, int):
            assert isinstance(target, list)
        else:
            assert isinstance(target, dict)
        target = target[component]
    final = path[-1]
    if isinstance(final, int):
        assert isinstance(target, list)
    else:
        assert isinstance(target, dict)
    target[final] = value


def valid_creative_manifest() -> dict[str, object]:
    return {
        "schema_version": "2.0",
        "release_version": "2.0.0",
        "profile": "full-creative-v2",
        "project_id": "NINEL",
        "project_format": "short",
        "production_modes": ["live-action"],
        "units": ["pilot"],
        "layers": {
            "story": "story",
            "production": "production",
            "post": "post",
        },
        "validation_status": "valid",
        "unresolved_questions": [],
    }


def valid_edit_plan() -> dict[str, object]:
    """Return a hand-authored edit plan independent of the shipped template."""
    return {
        "schema_version": "2.0",
        "project_id": "LANTERN",
        "unit_id": "LANTERN-U01",
        "project_format": "documentary",
        "source_context": {
            "screenplay_metadata_reference": (
                "scripts/LANTERN-U01/screenplay-metadata.json"
            ),
            "production_plan_references": [
                "production/production-design-plan.json"
            ],
            "shots": [
                {
                    "shot_id": "LANTERN-U01-S01-SH001",
                    "scene_id": "LANTERN-U01-S01",
                    "source_reference": (
                        "scripts/LANTERN-U01/scenes/LANTERN-U01-S01/"
                        "shot-list.json#/shots/0"
                    ),
                },
                {
                    "shot_id": "LANTERN-U01-S01-SH002",
                    "scene_id": "LANTERN-U01-S01",
                    "source_reference": (
                        "scripts/LANTERN-U01/scenes/LANTERN-U01-S01/"
                        "shot-list.json#/shots/1"
                    ),
                },
            ],
            "media_items": [
                {
                    "media_id": "LANTERN-MD001",
                    "shot_id": "LANTERN-U01-S01-SH001",
                    "review_status": "approved",
                    "source_reference": (
                        "production/media-review-report.json#/items/0"
                    ),
                }
            ],
            "timing_evidence": [
                {
                    "timing_evidence_id": "LANTERN-TM001",
                    "media_id": "LANTERN-MD001",
                    "exact_source_in": "01:00:12:08",
                    "exact_source_out": "01:00:18:02",
                    "source_reference": (
                        "production/media-review-report.json#/items/"
                        "LANTERN-MD001/timing-evidence/LANTERN-TM001"
                    ),
                }
            ],
            "lock_decisions": [],
        },
        "editorial_strategy": (
            "Keep participant context intact before compressing the route change."
        ),
        "segments": [
            {
                "segment_id": "LANTERN-U01-ED001",
                "assembly_order": 1,
                "source_shot_ids": ["LANTERN-U01-S01-SH001"],
                "source_media_ids": ["LANTERN-MD001"],
                "dramatic_purpose": (
                    "Let the participant establish the route in their own words."
                ),
                "in_out_intent": {
                    "entry": "Enter before the participant names the old route.",
                    "exit": "Leave after the reason for the change is complete.",
                    "exact_source_in": "01:00:12:08",
                    "exact_source_out": "01:00:18:02",
                },
                "cut_motivation": [
                    {
                        "dimension": "story",
                        "rationale": "The route change advances the inquiry.",
                    },
                    {
                        "dimension": "sound",
                        "rationale": "The completed sentence motivates the exit.",
                    },
                ],
                "transition": {
                    "type": "cut",
                    "intent": "Preserve the causal link without decoration.",
                },
                "eye_trace": "Keep attention on the participant's face.",
                "motion": "Cut after the participant settles, not mid-gesture.",
                "continuity": {
                    "mode": "continuity",
                    "intent": "Preserve speaking direction and interview geography.",
                },
                "rhythm": "Hold long enough to retain the full qualifying phrase.",
                "dialogue_sound_bridge": {
                    "type": "none",
                    "intent": "Keep this statement synchronous for source clarity.",
                },
                "temporal_treatment": {
                    "mode": "real-time",
                    "intent": "Do not compress within the participant's statement.",
                },
                "alternatives": [
                    {
                        "condition": "If the approved interview item is withdrawn.",
                        "source_shot_ids": ["LANTERN-U01-S01-SH002"],
                        "source_media_ids": [],
                        "edit_intent": (
                            "Use the supplied map shot and retain the uncertainty "
                            "as narration rather than inventing an interview take."
                        ),
                    }
                ],
                "evidence_status": "inspected",
                "lock_status": "fine-cut",
                "timing_evidence_id": "LANTERN-TM001",
            },
            {
                "segment_id": "LANTERN-U01-ED002",
                "assembly_order": 2,
                "source_shot_ids": ["LANTERN-U01-S01-SH002"],
                "source_media_ids": [],
                "dramatic_purpose": "Orient the viewer to the supplied route map.",
                "in_out_intent": {
                    "entry": "Enter on the map before the route is compared.",
                    "exit": "Exit when the comparison has done its story work.",
                },
                "cut_motivation": [
                    {
                        "dimension": "eye-trace",
                        "rationale": "Follow attention from the speaker to the map.",
                    }
                ],
                "transition": {
                    "type": "j-cut",
                    "intent": "Let the next verified statement motivate the image change.",
                },
                "eye_trace": "Move attention from face position to the marked route.",
                "motion": "No source motion is assumed for the planned map shot.",
                "continuity": {
                    "mode": "continuity",
                    "intent": "Preserve the established route orientation.",
                },
                "rhythm": "Duration remains open until media can be inspected.",
                "dialogue_sound_bridge": {
                    "type": "j-cut",
                    "intent": "Advance only supplied dialogue when it becomes available.",
                },
                "temporal_treatment": {
                    "mode": "compression",
                    "intent": "Condense the route comparison without changing its claim.",
                },
                "alternatives": [],
                "evidence_status": "planned",
                "lock_status": "unlocked",
            },
        ],
        "assumptions": [
            "The shot plan identifies a map shot but no reviewed media item for it."
        ],
        "uncertainties": [
            "The map shot's usable duration and motion remain unknown until review."
        ],
    }


def valid_media_prompt_package() -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "2.0",
        "project_id": "LANTERN",
        "source_context": {
            "registries": {
                "character_ids": ["LANTERN-CH001"],
                "scene_ids": ["LANTERN-U01-S02"],
                "shot_ids": ["LANTERN-U01-S02-SH003"],
                "asset_ids": [],
            },
            "source_facts": [
                {
                    "fact_id": "LANTERN-SF001",
                    "scope": "shot",
                    "subject_id": "LANTERN-U01-S02-SH003",
                    "value": "Mara opens the greenhouse latch and crosses right.",
                    "source_reference": "shot-list.json#/shots/LANTERN-U01-S02-SH003",
                }
            ],
            "supplied_constraints": [],
            "approval_evidence": [],
            "consent_evidence": [],
        },
        "prompts": [
            {
                "prompt_id": "LANTERN-MP001",
                "category": "video",
                "upstream_references": [
                    {"kind": "character", "id": "LANTERN-CH001"},
                    {"kind": "scene", "id": "LANTERN-U01-S02"},
                    {"kind": "shot", "id": "LANTERN-U01-S02-SH003"},
                ],
                "creative_content": [
                    {
                        "value": "Mara opens the greenhouse latch and crosses right.",
                        "provenance": {"status": "supplied", "source_id": "LANTERN-SF001"},
                    }
                ],
                "immutable_anchors": [
                    {
                        "value": "Keep Mara's supplied recognition anchors stable.",
                        "provenance": {"status": "proposed", "source_id": "LANTERN-SF001"},
                    }
                ],
                "allowed_variation": [
                    {
                        "value": "Minor reflection variation is allowed.",
                        "provenance": {"status": "proposed", "source_id": "LANTERN-SF001"},
                    }
                ],
                "technical_assumptions": [
                    {
                        "value": "Duration is an unresolved planning assumption.",
                        "provenance": {"status": "assumption", "source_id": "LANTERN-SF001"},
                    }
                ],
                "negative_constraints": ["No vendor parameters or artist imitation."],
                "continuity_anchors": ["Maintain coat, brooch, and lighting relationship."],
                "acceptance_criteria": ["Action, identity, and lighting remain observable."],
                "video": {
                    "scene_action": "Mara opens the latch and crosses to the doorway.",
                    "identity_lock": "Retain Mara's supplied anchors for the full shot.",
                    "start_composition": "Mara begins frame left at shoulder height.",
                    "end_composition": "Mara finishes beside the doorway frame right.",
                    "camera_movement": "lateral track",
                    "trajectory": "left-to-right lateral path",
                    "direction": "left-to-right",
                    "speed": "slow",
                    "subject_retention": "Mara remains visible during the crossing.",
                    "lens_depth_light_texture_mood": "50 mm, controlled depth, amber/cool wet-glass tension.",
                    "performance_timing": "Latch release precedes crossing.",
                    "duration_assumption": "Duration is not supplied; confirm before generation.",
                },
            }
        ],
        "assumptions": ["Duration is not supplied."],
        "uncertainties": ["Exact duration needs confirmation."],
    }
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompt = prompts[0]
    prompt["real_person_use"] = "none"
    video = prompt["video"]
    assert isinstance(video, dict)
    prompt["video"] = {
        field: {"value": value, "provenance": {"status": "proposed", "source_id": "LANTERN-SF001"}}
        for field, value in video.items()
    }
    return payload


def valid_media_review_report() -> dict[str, object]:
    """A reviewed still with source-owned criteria and direct evidence."""
    return {
        "schema_version": "2.0",
        "project_id": "LANTERN",
        "package_status": "reviewed",
        "source_context": {
            "registries": {
                "scene_ids": ["LANTERN-U01-S02"],
                "shot_ids": ["LANTERN-U01-S02-SH003"],
                "asset_ids": [],
            },
            "prompt_packages": [
                {
                    "prompt_id": "LANTERN-MP001",
                    "upstream_references": [
                        {"kind": "scene", "id": "LANTERN-U01-S02"},
                        {"kind": "shot", "id": "LANTERN-U01-S02-SH003"},
                    ],
                    "acceptance_criteria": [
                        {
                            "criterion_id": "LANTERN-AC001",
                            "statement": "The supplied start composition remains observable.",
                            "source_reference": "media-prompt-package.json#/prompts/LANTERN-MP001/acceptance_criteria/0",
                            "dimension": "composition",
                            "required_evidence": "static-visible",
                        },
                        {
                            "criterion_id": "LANTERN-AC002",
                            "statement": "The supplied identity anchors remain observable.",
                            "source_reference": "media-prompt-package.json#/prompts/LANTERN-MP001/acceptance_criteria/1",
                            "dimension": "identity",
                            "required_evidence": "static-visible",
                        },
                    ],
                }
            ],
        },
        "missing_inputs": [],
        "blockers": [],
        "items": [
            {
                "media_id": "LANTERN-MD001",
                "status": "approved",
                "prompt_id": "LANTERN-MP001",
                "upstream_references": [
                    {"kind": "scene", "id": "LANTERN-U01-S02"},
                    {"kind": "shot", "id": "LANTERN-U01-S02-SH003"},
                ],
                "inspected_input": {
                    "input_id": "LANTERN-IN001",
                    "modality": "still",
                    "identity": "greenhouse-keyframe-v001.png",
                    "fingerprint": "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                },
                "inspection_evidence": [
                    {
                        "evidence_id": "LANTERN-ME001",
                        "input_id": "LANTERN-IN001",
                        "criterion_id": "LANTERN-AC001",
                        "kind": "direct-inspection",
                        "observation": "The supplied still shows the required left-to-right composition.",
                    },
                    {
                        "evidence_id": "LANTERN-ME002",
                        "input_id": "LANTERN-IN001",
                        "criterion_id": "LANTERN-AC002",
                        "kind": "direct-inspection",
                        "observation": "The supplied still retains the named identity anchors.",
                    },
                ],
                "criterion_outcomes": [
                    {
                        "criterion_id": "LANTERN-AC001",
                        "outcome": "pass",
                        "evidence_ids": ["LANTERN-ME001"],
                    },
                    {
                        "criterion_id": "LANTERN-AC002",
                        "outcome": "pass",
                        "evidence_ids": ["LANTERN-ME002"],
                    },
                ],
                "deviations": [],
                "repair_scope": "none",
                "reviewer_uncertainty": "Only the supplied still was inspected; no motion or audio claim is made.",
            }
        ],
    }


def test_media_review_report_accepts_an_empty_awaiting_media_state(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    payload["package_status"] = "awaiting-media"
    payload["items"] = []
    payload["missing_inputs"] = [
        {
            "kind": "media",
            "detail": "No inspectable media or measurable metadata was supplied.",
        },
        {
            "kind": "criterion",
            "detail": "Composition and identity cannot be evidenced until media is supplied.",
        },
    ]

    assert validate_artifact("media-review-report", payload, repository_root) == []


def test_media_review_report_rejects_approval_without_inspection_evidence(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["inspection_evidence"] = []

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("inspection_evidence" in error for error in errors)


def test_media_review_report_rejects_reviewed_state_without_items(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    payload["items"] = []

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("items" in error for error in errors)


def test_media_review_report_requires_exact_source_criterion_record(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    context = payload["source_context"]
    assert isinstance(context, dict)
    prompts = context["prompt_packages"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    criteria = prompts[0]["acceptance_criteria"]
    assert isinstance(criteria, list) and isinstance(criteria[0], dict)
    del criteria[0]["source_reference"]

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("source_reference" in error for error in errors)


def test_media_review_report_rejects_criterion_reference_for_another_prompt(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    context = payload["source_context"]
    assert isinstance(context, dict)
    prompts = context["prompt_packages"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    criteria = prompts[0]["acceptance_criteria"]
    assert isinstance(criteria, list) and isinstance(criteria[0], dict)
    criteria[0]["source_reference"] = (
        "media-prompt-package.json#/prompts/LANTERN-MP999/acceptance_criteria/0"
    )

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("must bind prompt LANTERN-MP001" in error for error in errors)


def test_media_review_report_requires_the_exact_criterion_source_location(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    context = payload["source_context"]
    assert isinstance(context, dict)
    prompts = context["prompt_packages"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    criteria = prompts[0]["acceptance_criteria"]
    assert isinstance(criteria, list) and isinstance(criteria[1], dict)
    criteria[1]["source_reference"] = (
        "media-prompt-package.json#/prompts/LANTERN-MP001/acceptance_criteria/0"
    )

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("acceptance_criteria/1" in error for error in errors)


def test_media_review_report_rejects_forged_criterion_source_filename(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    context = payload["source_context"]
    assert isinstance(context, dict)
    prompts = context["prompt_packages"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    criteria = prompts[0]["acceptance_criteria"]
    assert isinstance(criteria, list) and isinstance(criteria[0], dict)
    criteria[0]["source_reference"] = (
        "forged-prefix.json#/prompts/LANTERN-MP001/acceptance_criteria/0"
    )

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("canonical source reference" in error for error in errors)


def test_media_review_report_accepts_the_canonical_criterion_source_filename(
    repository_root: Path,
) -> None:
    assert validate_artifact(
        "media-review-report", valid_media_review_report(), repository_root
    ) == []


def test_media_review_report_requires_a_full_sha256_input_fingerprint(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    inspected_input = items[0]["inspected_input"]
    assert isinstance(inspected_input, dict)
    inspected_input["fingerprint"] = "sha256:0123456789abcdef"

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("fingerprint" in error for error in errors)


def test_media_review_report_rejects_unowned_or_duplicate_media_ids(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    duplicate = copy.deepcopy(items[0])
    duplicate["media_id"] = "OTHER-MD001"
    items.append(duplicate)
    items.append(copy.deepcopy(items[0]))

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("must match LANTERN-MD###" in error for error in errors)
    assert any("duplicate media ID" in error for error in errors)


def test_media_review_report_requires_exact_prompt_upstream_binding(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    references = items[0]["upstream_references"]
    assert isinstance(references, list) and isinstance(references[0], dict)
    references[0]["id"] = "LANTERN-U01-S99"

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("must exactly match prompt LANTERN-MP001" in error for error in errors)


def test_media_review_report_does_not_let_a_still_prove_motion(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    context = payload["source_context"]
    assert isinstance(context, dict)
    prompts = context["prompt_packages"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    criteria = prompts[0]["acceptance_criteria"]
    assert isinstance(criteria, list) and isinstance(criteria[0], dict)
    criteria[0]["dimension"] = "movement"
    criteria[0]["required_evidence"] = "motion"

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("still evidence cannot support motion" in error for error in errors)


def test_media_review_report_does_not_let_metadata_prove_an_unnamed_criterion(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    item = items[0]
    inspected_input = item["inspected_input"]
    assert isinstance(inspected_input, dict)
    inspected_input["modality"] = "metadata"
    evidence = item["inspection_evidence"]
    assert isinstance(evidence, list) and isinstance(evidence[0], dict)
    evidence[0].update(
        {
            "criterion_id": "LANTERN-AC999",
            "kind": "measurable-metadata",
            "measurement": "1920 by 1080 pixels",
        }
    )

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("unknown acceptance criterion LANTERN-AC999" in error for error in errors)


def test_media_review_report_allows_audiovisual_evidence_for_applicable_motion_and_sound(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    context = payload["source_context"]
    assert isinstance(context, dict)
    prompts = context["prompt_packages"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    criteria = prompts[0]["acceptance_criteria"]
    assert isinstance(criteria, list) and all(isinstance(item, dict) for item in criteria)
    criteria[0].update({"dimension": "movement", "required_evidence": "motion"})
    criteria[1].update({"dimension": "sound", "required_evidence": "audio"})
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    inspected_input = items[0]["inspected_input"]
    assert isinstance(inspected_input, dict)
    inspected_input["modality"] = "audiovisual"

    assert validate_artifact("media-review-report", payload, repository_root) == []


def test_media_review_report_preserves_all_task_five_reference_kinds(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    context = payload["source_context"]
    assert isinstance(context, dict)
    registries = context["registries"]
    assert isinstance(registries, dict)
    additions = {
        "character": "LANTERN-CH001",
        "world": "LANTERN-WR001",
        "beat": "LANTERN-U01-S02-B01",
        "sound": "LANTERN-A001",
    }
    for kind, identifier in additions.items():
        registries[f"{kind}_ids"] = [identifier]
    prompts = context["prompt_packages"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompt_references = prompts[0]["upstream_references"]
    assert isinstance(prompt_references, list)
    prompt_references.extend({"kind": kind, "id": identifier} for kind, identifier in additions.items())
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    item_references = items[0]["upstream_references"]
    assert isinstance(item_references, list)
    item_references.extend({"kind": kind, "id": identifier} for kind, identifier in additions.items())

    assert validate_artifact("media-review-report", payload, repository_root) == []


def test_media_review_report_requires_blocked_state_to_name_a_real_blocker(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    payload["package_status"] = "blocked"
    payload["blockers"] = []
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("blockers" in error for error in errors)


def test_media_review_report_requires_human_review_to_block_the_package(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    item = items[0]
    item["status"] = "human-review"
    item["repair_scope"] = "human-handoff"
    item["deviations"] = [{"criterion_id": "LANTERN-AC001", "severity": "subjective", "detail": "A qualified human must judge the interpretation.", "resolved": False}]
    item["human_review_handoff"] = {"reason": "subjective", "question": "Does the interpretation meet the intended tone?"}
    outcomes = item["criterion_outcomes"]
    assert isinstance(outcomes, list) and isinstance(outcomes[0], dict)
    outcomes[0].update({"outcome": "not-assessable", "evidence_ids": []})

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("human-review item requires package_status blocked" in error for error in errors)


@pytest.mark.parametrize(
    ("status", "severity", "repair_scope", "expected"),
    [
        ("repair", "foundational", "localized", "repair requires an unresolved localized deviation"),
        ("regenerate", "localized", "foundational", "regenerate requires an unresolved foundational deviation"),
        ("human-review", "localized", "human-handoff", "human-review requires an unresolved subjective, rights, or safety deviation"),
    ],
)
def test_media_review_report_aligns_decision_with_deviation_and_scope(
    repository_root: Path,
    status: str,
    severity: str,
    repair_scope: str,
    expected: str,
) -> None:
    payload = valid_media_review_report()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    item = items[0]
    item["status"] = status
    item["repair_scope"] = repair_scope
    item["deviations"] = [
        {
            "criterion_id": "LANTERN-AC001",
            "severity": severity,
            "detail": "The result needs a decision-specific disposition.",
            "resolved": False,
        }
    ]
    if status == "human-review":
        item["human_review_handoff"] = {
            "reason": "subjective",
            "question": "Does this subjective interpretation meet the intended tone?",
        }

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any(expected in error for error in errors)


@pytest.mark.parametrize(
    ("status", "severity", "scope", "expected"),
    [
        ("repair", "localized", "localized", "repair requires a failing criterion outcome"),
        ("regenerate", "foundational", "foundational", "regenerate requires a failing criterion outcome"),
    ],
)
def test_media_review_report_requires_failed_outcomes_for_corrective_decisions(
    repository_root: Path,
    status: str,
    severity: str,
    scope: str,
    expected: str,
) -> None:
    payload = valid_media_review_report()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    item = items[0]
    item["status"] = status
    item["repair_scope"] = scope
    item["deviations"] = [{"criterion_id": "LANTERN-AC001", "severity": severity, "detail": "A failed criterion should drive this corrective decision.", "resolved": False}]

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any(expected in error for error in errors)


def test_media_review_report_rejects_cross_wired_repair_criterion(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    item = payload["items"][0]
    assert isinstance(item, dict)
    item["status"] = "repair"
    item["repair_scope"] = "localized"
    item["deviations"] = [
        {
            "criterion_id": "LANTERN-AC002",
            "severity": "localized",
            "detail": "The identity anchor needs a localized repair.",
            "resolved": False,
        }
    ]
    outcomes = item["criterion_outcomes"]
    assert isinstance(outcomes, list) and isinstance(outcomes[0], dict)
    outcomes[0]["outcome"] = "fail"

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("repair decision must bind unresolved deviations to failed criteria" in error for error in errors)


def test_media_review_report_rejects_cross_wired_regenerate_criterion(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    item = payload["items"][0]
    assert isinstance(item, dict)
    item["status"] = "regenerate"
    item["repair_scope"] = "foundational"
    item["deviations"] = [
        {
            "criterion_id": "LANTERN-AC002",
            "severity": "foundational",
            "detail": "The identity mismatch requires regeneration.",
            "resolved": False,
        }
    ]
    outcomes = item["criterion_outcomes"]
    assert isinstance(outcomes, list) and isinstance(outcomes[0], dict)
    outcomes[0]["outcome"] = "fail"

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("regenerate decision must bind unresolved deviations to failed criteria" in error for error in errors)


def test_media_review_report_rejects_cross_wired_human_review_criterion(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    payload["package_status"] = "blocked"
    payload["blockers"] = [
        {"kind": "subjective", "detail": "A qualified human must resolve the interpretation."}
    ]
    item = payload["items"][0]
    assert isinstance(item, dict)
    item["status"] = "human-review"
    item["repair_scope"] = "human-handoff"
    item["deviations"] = [
        {
            "criterion_id": "LANTERN-AC002",
            "severity": "subjective",
            "detail": "The identity interpretation needs qualified human judgment.",
            "resolved": False,
        }
    ]
    item["human_review_handoff"] = {
        "reason": "subjective",
        "question": "Does the interpretation meet the intended tone?",
    }
    outcomes = item["criterion_outcomes"]
    assert isinstance(outcomes, list) and isinstance(outcomes[0], dict)
    outcomes[0].update({"outcome": "not-assessable", "evidence_ids": []})

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("human-review decision must bind unresolved deviations to not-assessable criteria" in error for error in errors)


def valid_mixed_blocked_media_review_report() -> dict[str, object]:
    """Build a blocked package containing one approved and one human-review item."""
    payload = valid_media_review_report()
    payload["package_status"] = "blocked"
    payload["blockers"] = [
        {"kind": "subjective", "detail": "A qualified human must resolve the second item's interpretation."}
    ]
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    blocked_item = copy.deepcopy(items[0])
    blocked_item.update(
        {
            "media_id": "LANTERN-MD002",
            "status": "human-review",
            "repair_scope": "human-handoff",
            "human_review_handoff": {
                "reason": "subjective",
                "question": "Does the second interpretation meet the intended tone?",
            },
            "deviations": [
                {
                    "criterion_id": "LANTERN-AC002",
                    "severity": "subjective",
                    "detail": "The second interpretation needs qualified human judgment.",
                    "resolved": False,
                }
            ],
        }
    )
    inspected_input = blocked_item["inspected_input"]
    assert isinstance(inspected_input, dict)
    inspected_input["input_id"] = "LANTERN-IN002"
    evidence = blocked_item["inspection_evidence"]
    assert isinstance(evidence, list)
    for index, record in enumerate(evidence, start=3):
        assert isinstance(record, dict)
        record["evidence_id"] = f"LANTERN-ME{index:03d}"
        record["input_id"] = "LANTERN-IN002"
    outcomes = blocked_item["criterion_outcomes"]
    assert isinstance(outcomes, list) and all(isinstance(outcome, dict) for outcome in outcomes)
    outcomes[0]["evidence_ids"] = ["LANTERN-ME003"]
    outcomes[1].update({"outcome": "not-assessable", "evidence_ids": []})
    items.append(blocked_item)
    return payload


def test_media_review_report_allows_approved_item_in_legitimate_blocked_package(
    repository_root: Path,
) -> None:
    assert validate_artifact(
        "media-review-report",
        valid_mixed_blocked_media_review_report(),
        repository_root,
    ) == []


def test_media_review_report_rejects_deviation_for_an_unknown_prompt_criterion(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["deviations"] = [
        {
            "criterion_id": "LANTERN-AC999",
            "severity": "localized",
            "detail": "Even a resolved deviation must bind the prompt criterion.",
            "resolved": True,
        }
    ]

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("unknown acceptance criterion LANTERN-AC999" in error for error in errors)


def test_media_review_report_regenerate_requires_only_foundational_unresolved_deviations(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    item = items[0]
    item["status"] = "regenerate"
    item["repair_scope"] = "foundational"
    item["deviations"] = [
        {
            "criterion_id": "LANTERN-AC001",
            "severity": "foundational",
            "detail": "The identity mismatch requires regeneration.",
            "resolved": False,
        },
        {
            "criterion_id": "LANTERN-AC002",
            "severity": "localized",
            "detail": "A localized defect cannot be hidden in regeneration.",
            "resolved": False,
        },
    ]
    outcomes = item["criterion_outcomes"]
    assert isinstance(outcomes, list) and isinstance(outcomes[0], dict)
    outcomes[0]["outcome"] = "fail"

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("regenerate requires unresolved foundational deviations only" in error for error in errors)


def test_media_review_report_requires_handoff_reason_to_match_deviation(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    payload["package_status"] = "blocked"
    payload["blockers"] = [
        {"kind": "subjective", "detail": "A qualified human must resolve the interpretation."}
    ]
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    item = items[0]
    item["status"] = "human-review"
    item["repair_scope"] = "human-handoff"
    item["deviations"] = [
        {
            "criterion_id": "LANTERN-AC001",
            "severity": "subjective",
            "detail": "The interpretation needs qualified human judgment.",
            "resolved": False,
        }
    ]
    item["human_review_handoff"] = {
        "reason": "safety",
        "question": "Does the interpretation meet the intended tone?",
    }
    outcomes = item["criterion_outcomes"]
    assert isinstance(outcomes, list) and isinstance(outcomes[0], dict)
    outcomes[0].update({"outcome": "not-assessable", "evidence_ids": []})

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("handoff reason safety must match an unresolved deviation" in error for error in errors)


def test_media_review_report_rejects_foreign_declared_registry_and_reference(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    context = payload["source_context"]
    assert isinstance(context, dict)
    registries = context["registries"]
    assert isinstance(registries, dict)
    registries["scene_ids"] = ["OTHER-U01-S02"]
    prompts = context["prompt_packages"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompt_references = prompts[0]["upstream_references"]
    assert isinstance(prompt_references, list) and isinstance(prompt_references[0], dict)
    prompt_references[0]["id"] = "OTHER-U01-S02"
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    item_references = items[0]["upstream_references"]
    assert isinstance(item_references, list) and isinstance(item_references[0], dict)
    item_references[0]["id"] = "OTHER-U01-S02"

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any("must belong to project LANTERN" in error for error in errors)


@pytest.mark.parametrize(
    ("dimension", "required_evidence"),
    [("movement", "static-visible"), ("sound", "static-visible")],
)
def test_media_review_report_requires_non_bypassable_dimension_evidence(
    repository_root: Path,
    dimension: str,
    required_evidence: str,
) -> None:
    payload = valid_media_review_report()
    context = payload["source_context"]
    assert isinstance(context, dict)
    prompts = context["prompt_packages"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    criteria = prompts[0]["acceptance_criteria"]
    assert isinstance(criteria, list) and isinstance(criteria[0], dict)
    criteria[0].update(
        {"dimension": dimension, "required_evidence": required_evidence}
    )

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert any(
        f"{dimension} dimension requires" in error for error in errors
    )


def test_media_review_report_malformed_deep_input_never_tracebacks(
    repository_root: Path,
) -> None:
    payload = valid_media_review_report()
    payload["source_context"] = {"registries": {"scene_ids": ["LANTERN-U01-S02"]}}

    errors = validate_artifact("media-review-report", payload, repository_root)

    assert errors
    assert all("Traceback" not in error for error in errors)


def test_media_review_report_template_validates_live_contract(
    repository_root: Path,
) -> None:
    template_path = (
        repository_root
        / ".agents"
        / "skills"
        / "media-review-supervisor"
        / "assets"
        / "media-review-report.template.json"
    )
    template = json.loads(template_path.read_text(encoding="utf-8"))

    assert validate_artifact("media-review-report", template, repository_root) == []


def provenance_domain(values: dict[str, str]) -> dict[str, dict[str, object]]:
    return {
        field: {"value": value, "provenance": {"status": "proposed", "source_id": "LANTERN-SF001"}}
        for field, value in values.items()
    }


def test_media_prompt_package_accepts_a_source_bound_video_skeleton(
    repository_root: Path,
) -> None:
    assert validate_artifact(
        "media-prompt-package", valid_media_prompt_package(), repository_root
    ) == []


def test_media_prompt_package_rejects_an_unsupported_category(
    repository_root: Path,
) -> None:
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompts[0]["category"] = "image"

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("category" in error for error in errors)


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (
            lambda payload: payload["prompts"][0].update({"vendor_parameters": "--seed 7"}),
            "Additional properties are not allowed",
        ),
        (
            lambda payload: payload["prompts"][0]["negative_constraints"].append("https://example.invalid/prompt"),
            "URLs are not permitted",
        ),
        (
            lambda payload: payload["prompts"][0]["negative_constraints"].append("data:image/png;base64,AAAA"),
            "embedded media",
        ),
        (
            lambda payload: payload["prompts"][0]["technical_assumptions"][0].update({"value": "api_key=secret-value"}),
            "secrets are not permitted",
        ),
        (
            lambda payload: payload["prompts"][0]["creative_content"][0].update({"value": "In the exact style of a living artist."}),
            "living-artist imitation",
        ),
    ],
)
def test_media_prompt_package_rejects_forbidden_vendor_or_embedded_content(
    repository_root: Path, mutate, expected: str
) -> None:
    payload = valid_media_prompt_package()
    mutate(payload)

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any(expected in error for error in errors)


@pytest.mark.parametrize(
    ("path", "value", "expected"),
    [
        (("prompts", 0, "prompt_id"), "OTHER-MP001", "must match LANTERN-MP###"),
        (("prompts", 0, "upstream_references", 2, "id"), "LANTERN-U01-S02-SH999", "unknown shot reference"),
        (("prompts", 0, "upstream_references", 2, "kind"), "scene", "does not belong to scene registry"),
    ],
)
def test_media_prompt_package_rejects_foreign_unknown_or_mismatched_references(
    repository_root: Path, path: tuple[str | int, ...], value: str, expected: str
) -> None:
    payload = valid_media_prompt_package()
    replace_nested_value(payload, path, value)

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any(expected in error for error in errors)


def test_media_prompt_package_rejects_duplicate_prompt_ids(repository_root: Path) -> None:
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list)
    prompts.append(copy.deepcopy(prompts[0]))

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("duplicate prompt ID LANTERN-MP001" in error for error in errors)


def test_media_prompt_package_requires_all_video_structure(repository_root: Path) -> None:
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    video = prompts[0]["video"]
    assert isinstance(video, dict)
    del video["duration_assumption"]

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("duration_assumption" in error for error in errors)


def test_media_prompt_package_rejects_a_supplied_claim_not_in_its_ledger(
    repository_root: Path,
) -> None:
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    content = prompts[0]["creative_content"]
    assert isinstance(content, list) and isinstance(content[0], dict)
    content[0]["value"] = "Mara has blue eyes and an alto voice."

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("supplied claim must exactly match" in error for error in errors)


def test_media_prompt_package_malformed_deep_input_never_tracebacks(
    repository_root: Path,
) -> None:
    payload = valid_media_prompt_package()
    payload["source_context"] = {"registries": {"character_ids": ["LANTERN-CH001"]}}

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert errors
    assert all("Traceback" not in error for error in errors)


def valid_voice_clone_request() -> dict[str, object]:
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompt = prompts[0]
    prompt["category"] = "voice"
    prompt["real_person_use"] = "voice"
    prompt.pop("video")
    prompt["voice"] = provenance_domain({
        "speaker_or_source": "A real person's voice is requested.",
        "performance_intent": "Use supplied dialogue intent only.",
        "delivery_timing": "Timing remains source-bound.",
        "originality_boundary": "Do not create a recognizable voice without consent evidence.",
    })
    content = prompt["creative_content"]
    assert isinstance(content, list) and isinstance(content[0], dict)
    content[0]["value"] = "Create an exact clone of the real person's voice."
    provenance = content[0]["provenance"]
    assert isinstance(provenance, dict)
    provenance["status"] = "proposed"
    payload["human_review_handoffs"] = []
    return payload


def test_media_prompt_package_requires_qualified_human_consent_handoff_for_real_voice(
    repository_root: Path,
) -> None:
    errors = validate_artifact(
        "media-prompt-package", valid_voice_clone_request(), repository_root
    )

    assert any("qualified-human consent/rights review handoff" in error for error in errors)


def test_media_prompt_package_accepts_qualified_human_consent_handoff_without_clearance_claim(
    repository_root: Path,
) -> None:
    payload = valid_voice_clone_request()
    handoffs = payload["human_review_handoffs"]
    assert isinstance(handoffs, list)
    handoffs.append(
        {
            "handoff_id": "LANTERN-HR001",
            "prompt_id": "LANTERN-MP001",
            "review_action": "require-qualified-human-consent-rights-review",
            "review_status": "pending-qualified-human-review",
            "review": "A qualified human consent/rights reviewer must assess evidence; this plan does not claim legal clearance.",
            "consent_evidence_ids": [],
        }
    )

    assert validate_artifact("media-prompt-package", payload, repository_root) == []


@pytest.mark.parametrize(
    ("category", "field", "domain"),
    [
        ("character-image", "image", {"subject_or_place": "Mara", "composition": "Three-quarter portrait.", "view_or_scale": "Character scale.", "light_material_mood": "Wet-glass cool field.", "identity_or_environment_lock": "Keep supplied anchors stable."}),
        ("voice", "voice", {"speaker_or_source": "Mara", "performance_intent": "Supplied restraint.", "delivery_timing": "Shot-linked timing.", "originality_boundary": "Original non-identifiable voice."}),
        ("music", "music", {"dramatic_function": "Restrained tension.", "dialogue_policy": "Dialogue-free and leaves latch audible.", "entry_exit_shape": "Enters under action and releases after latch.", "instrumental_texture": "Proposed sparse texture.", "originality_boundary": "No artist imitation."}),
        ("foley", "sound", {"sound_source": "Greenhouse latch", "event_or_bed": "Single release event.", "perspective": "Close mechanical perspective.", "timing_and_decay": "Release then short glass resonance."}),
    ],
)
def test_media_prompt_package_accepts_category_specific_structure(
    repository_root: Path, category: str, field: str, domain: dict[str, str]
) -> None:
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompt = prompts[0]
    prompt["category"] = category
    prompt.pop("video")
    prompt[field] = provenance_domain(domain)

    assert validate_artifact("media-prompt-package", payload, repository_root) == []


def test_media_prompt_package_rejects_irrelevant_domain_structure(repository_root: Path) -> None:
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompts[0]["music"] = {
        "dramatic_function": "Unrelated.", "dialogue_policy": "None.", "entry_exit_shape": "None.",
        "instrumental_texture": "None.", "originality_boundary": "Original."
    }

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("irrelevant music structure" in error for error in errors)


def test_media_prompt_package_rejects_handoff_for_unknown_prompt(repository_root: Path) -> None:
    payload = valid_voice_clone_request()
    handoffs = payload["human_review_handoffs"]
    assert isinstance(handoffs, list)
    handoffs.append(
        {
            "handoff_id": "LANTERN-HR001",
            "prompt_id": "LANTERN-MP999",
            "review_action": "require-qualified-human-consent-rights-review",
            "review_status": "pending-qualified-human-review",
            "review": "A qualified human consent/rights reviewer must assess evidence; this plan does not claim legal clearance.",
            "consent_evidence_ids": [],
        }
    )

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("unknown prompt LANTERN-MP999" in error for error in errors)


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (
            lambda payload: payload["prompts"][0]["creative_content"][0].update(
                {"value": "Match Performer A's likeness."}
            ),
            "real-person declaration",
        ),
        (
            lambda payload: payload.update(
                {
                    "human_review_handoffs": [
                        {
                            "handoff_id": "LANTERN-HR001",
                            "prompt_id": "LANTERN-MP001",
                            "review": "No qualified human consent or rights review is required.",
                            "consent_evidence_ids": [],
                        }
                    ]
                }
            ),
            "review_action",
        ),
        (
            lambda payload: payload["source_context"]["source_facts"][0].update(
                {"subject_id": "LANTERN-U01-S02-SH999"}
            ),
            "exact typed upstream ID",
        ),
        (
            lambda payload: payload["source_context"].update(
                {
                    "supplied_constraints": [
                        {
                            "record_id": "OTHER-APR001",
                            "value": "No change.",
                            "source_reference": "brief.md#/constraints/0",
                        }
                    ]
                }
            ),
            "must match LANTERN-SC###",
        ),
        (
            lambda payload: payload["prompts"][0]["video"].update(
                {"camera_movement": "locked-off orbit with an injected 18 mm lens"}
            ),
            "provenance-bearing domain decision",
        ),
        (
            lambda payload: payload["prompts"][0]["negative_constraints"].append(
                "ftp://example.invalid/prompt"
            ),
            "URLs are not permitted",
        ),
        (
            lambda payload: payload["prompts"][0]["negative_constraints"].append(
                "Use Adobe Firefly for this render."
            ),
            "vendor or software prescriptions",
        ),
        (
            lambda payload: payload["prompts"][0]["negative_constraints"].append(
                "Use password hunter2 to proceed."
            ),
            "secrets are not permitted",
        ),
        (
            lambda payload: payload["prompts"][0]["negative_constraints"].append(
                "QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVo0123456789abcdefQUJDREVGR0hJSktMTU5PUA=="
            ),
            "embedded media",
        ),
        (
            lambda payload: payload["prompts"][0]["negative_constraints"].append(
                "Copy Jun Park's aesthetic exactly."
            ),
            "living-artist imitation",
        ),
    ],
)
def test_media_prompt_package_review_round_one_regressions_are_rejected(
    repository_root: Path, mutate, expected: str
) -> None:
    """Catch contract bypasses the pre-review validator accepted."""
    payload = valid_media_prompt_package()
    mutate(payload)

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any(expected in error for error in errors)


def test_media_prompt_package_review_round_one_allows_safe_film_language_and_paths(
    repository_root: Path,
) -> None:
    """Keep field-aware safety checks from rejecting harmless text or references."""
    payload = valid_media_prompt_package()
    context = payload["source_context"]
    assert isinstance(context, dict)
    facts = context["source_facts"]
    assert isinstance(facts, list) and isinstance(facts[0], dict)
    facts[0]["source_reference"] = "casting-reference.json#/performer-reference"
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompts[0]["negative_constraints"].extend(
        [
            "Keep the subject clear of the airport runway.",
            "Do not imitate the style of a living artist.",
        ]
    )

    assert validate_artifact("media-prompt-package", payload, repository_root) == []


@pytest.mark.parametrize(
    "phrase",
    ["Match Performer A's likeness.", "Replicate a specific human voice for the line."],
)
def test_media_prompt_package_rejects_false_real_person_declarations(
    repository_root: Path, phrase: str
) -> None:
    """A declaration cannot suppress a likeness or voice request in prompt text."""
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    content = prompts[0]["creative_content"]
    assert isinstance(content, list) and isinstance(content[0], dict)
    content[0]["value"] = phrase

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("real-person declaration cannot be none" in error for error in errors)


def test_media_prompt_package_rejects_cross_ledger_duplicate_ids(
    repository_root: Path,
) -> None:
    """An approval cannot reuse a constraint ledger identity."""
    payload = valid_media_prompt_package()
    context = payload["source_context"]
    assert isinstance(context, dict)
    record = {"record_id": "LANTERN-SC001", "value": "No change.", "source_reference": "brief.md#/0"}
    context["supplied_constraints"] = [record]
    context["approval_evidence"] = [record]

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("duplicate ID across provenance ledgers" in error for error in errors)


def _append_source_fact(
    payload: dict[str, object], *, fact_id: str, subject_id: str, value: str
) -> None:
    context = payload["source_context"]
    assert isinstance(context, dict)
    facts = context["source_facts"]
    assert isinstance(facts, list)
    facts.append(
        {
            "fact_id": fact_id,
            "scope": "shot",
            "subject_id": subject_id,
            "value": value,
            "source_reference": "shot-list.json#/shots/0",
        }
    )


@pytest.mark.parametrize(
    "fact_value",
    [
        "A real performer reference is requested for temporary likeness matching.",
        "A named performer reference is requested for temporary voice matching.",
    ],
)
def test_media_prompt_package_derives_real_person_use_from_cited_fact_values(
    repository_root: Path, fact_value: str
) -> None:
    """Fact-backed likeness or voice intent cannot be hidden behind a false declaration."""
    payload = valid_media_prompt_package()
    _append_source_fact(
        payload,
        fact_id="LANTERN-SF002",
        subject_id="LANTERN-U01-S02-SH003",
        value=fact_value,
    )
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    video = prompts[0]["video"]
    assert isinstance(video, dict) and isinstance(video["scene_action"], dict)
    video["scene_action"]["provenance"] = {"status": "proposed", "source_id": "LANTERN-SF002"}

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("real-person declaration cannot be none" in error for error in errors)


def test_media_prompt_package_allows_negative_safeguards_and_pending_consent(
    repository_root: Path,
) -> None:
    """Negative safeguards are not production commands or affirmative clearance claims."""
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompts[0]["negative_constraints"].extend(
        [
            "Do not make casting or procurement decisions.",
            "Consent is not confirmed; qualified human review remains required.",
        ]
    )

    assert validate_artifact("media-prompt-package", payload, repository_root) == []


def test_media_prompt_package_rejects_optional_or_bypassed_review(
    repository_root: Path,
) -> None:
    """A structured handoff cannot make required review optional or skippable."""
    payload = valid_voice_clone_request()
    payload["human_review_handoffs"] = [
        {
            "handoff_id": "LANTERN-HR001",
            "prompt_id": "LANTERN-MP001",
            "review_action": "require-qualified-human-consent-rights-review",
            "review_status": "pending-qualified-human-review",
            "review": "Review is optional; generation may proceed before it.",
            "consent_evidence_ids": [],
        }
    ]

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("review bypass" in error for error in errors)


def test_media_prompt_package_rejects_duplicate_handoff_ids(
    repository_root: Path,
) -> None:
    """Different handoffs cannot reuse a project-owned HR identifier."""
    payload = valid_voice_clone_request()
    payload["human_review_handoffs"] = [
        {
            "handoff_id": "LANTERN-HR001",
            "prompt_id": "LANTERN-MP001",
            "review_action": "require-qualified-human-consent-rights-review",
            "review_status": "pending-qualified-human-review",
            "review": "A qualified human reviewer must assess evidence.",
            "consent_evidence_ids": [],
        },
        {
            "handoff_id": "LANTERN-HR001",
            "prompt_id": "LANTERN-MP001",
            "review_action": "require-qualified-human-consent-rights-review",
            "review_status": "pending-qualified-human-review",
            "review": "A second qualified human reviewer must assess evidence.",
            "consent_evidence_ids": [],
        },
    ]

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("duplicate human review handoff ID" in error for error in errors)


@pytest.mark.parametrize("status", ["proposed", "assumption", "uncertainty"])
def test_media_prompt_package_binds_all_fact_backed_statuses_to_exact_upstream_subject(
    repository_root: Path, status: str
) -> None:
    """All fact-backed statuses, not only supplied, retain the fact's exact subject."""
    payload = valid_media_prompt_package()
    context = payload["source_context"]
    assert isinstance(context, dict)
    registries = context["registries"]
    assert isinstance(registries, dict)
    shots = registries["shot_ids"]
    assert isinstance(shots, list)
    shots.append("LANTERN-U01-S02-SH004")
    _append_source_fact(
        payload,
        fact_id="LANTERN-SF002",
        subject_id="LANTERN-U01-S02-SH004",
        value="Separate supplied decision.",
    )
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    claims = prompts[0]["technical_assumptions"]
    assert isinstance(claims, list) and isinstance(claims[0], dict)
    claims[0]["provenance"] = {"status": status, "source_id": "LANTERN-SF002"}

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("exact typed upstream ID" in error for error in errors)


@pytest.mark.parametrize(
    ("ledger_field", "record_id", "value"),
    [
        ("source_facts", "LANTERN-SF002", "Generate this using Adobe Firefly."),
        ("source_facts", "LANTERN-SF002", "Password is hunter2."),
        ("supplied_constraints", "LANTERN-SC001", "s3://bucket/prompt"),
        ("approval_evidence", "LANTERN-APR001", "file://private/prompt"),
        ("consent_evidence", "LANTERN-CON001", "Using Runway for this prompt."),
    ],
)
def test_media_prompt_package_scans_value_bearing_ledgers_for_forbidden_content(
    repository_root: Path, ledger_field: str, record_id: str, value: str
) -> None:
    """Source values are prompt inputs even when their source paths are internal."""
    payload = valid_media_prompt_package()
    context = payload["source_context"]
    assert isinstance(context, dict)
    if ledger_field == "source_facts":
        _append_source_fact(
            payload,
            fact_id=record_id,
            subject_id="LANTERN-U01-S02-SH003",
            value=value,
        )
    else:
        context[ledger_field] = [
            {"record_id": record_id, "value": value, "source_reference": "casting-reference.json#/performer-reference"}
        ]

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("not permitted" in error for error in errors)


def test_media_prompt_package_effect_guidance_distinguishes_sound_effects_from_visual_vfx(
    repository_root: Path,
) -> None:
    """The bundle must direct visible VFX into image/video or the VFX artifact."""
    skill = (repository_root / ".agents/skills/ai-media-prompt-designer/SKILL.md").read_text(encoding="utf-8")
    reference = (repository_root / ".agents/skills/ai-media-prompt-designer/references/voice-music-sound-prompts.md").read_text(encoding="utf-8")
    evaluation = json.loads((repository_root / "evals/ai-media-prompt-designer.json").read_text(encoding="utf-8"))

    assert "sound-effect category" in skill
    assert "image/key-frame/video" in skill
    assert "visual VFX" in reference
    assert any(
        "sound-effect category" in observable
        for case in evaluation["cases"]
        for observable in case["observables"]
    )


def _required_review_handoff(review: str) -> dict[str, object]:
    return {
        "handoff_id": "LANTERN-HR001",
        "prompt_id": "LANTERN-MP001",
        "review_action": "require-qualified-human-consent-rights-review",
        "review_status": "pending-qualified-human-review",
        "review": review,
        "consent_evidence_ids": [],
    }


@pytest.mark.parametrize(
    "review",
    [
        "Review is not required.",
        "No qualified human consent or rights review is required.",
        "Generation may proceed without review.",
        "Review is optional.",
        "Skip the review.",
        "Bypass review.",
        "Generation may proceed before review.",
    ],
)
def test_media_prompt_package_rejects_predicate_local_review_waivers(
    repository_root: Path, review: str
) -> None:
    """Words such as not and without do not neutralize a review-waiver predicate."""
    payload = valid_voice_clone_request()
    payload["human_review_handoffs"] = [_required_review_handoff(review)]

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("review bypass" in error for error in errors)


@pytest.mark.parametrize(
    "review",
    [
        "Consent is confirmed but rights review is pending.",
        "Permission is granted while review remains pending.",
        "Rights are approved although review is pending.",
        "Legal clearance is confirmed, with review pending.",
    ],
)
def test_media_prompt_package_rejects_affirmative_clearance_despite_pending_review(
    repository_root: Path, review: str
) -> None:
    """A pending review elsewhere cannot negate an affirmative clearance predicate."""
    payload = valid_voice_clone_request()
    payload["human_review_handoffs"] = [_required_review_handoff(review)]

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("cannot assert consent, permission, rights, or legal clearance" in error for error in errors)


@pytest.mark.parametrize(
    "safeguard",
    [
        "No consent has been confirmed; qualified human review remains required.",
        "Consent is not confirmed; qualified human review remains required.",
    ],
)
def test_media_prompt_package_allows_predicate_local_pending_consent_safeguards(
    repository_root: Path, safeguard: str
) -> None:
    """Negation governing consent confirmation remains a valid safety safeguard."""
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompts[0]["negative_constraints"].append(safeguard)

    assert validate_artifact("media-prompt-package", payload, repository_root) == []


@pytest.mark.parametrize(
    "instruction",
    [
        "Make casting decisions, not procurement decisions.",
        "Do not make casting decisions, but create a budget.",
    ],
)
def test_media_prompt_package_rejects_affirmative_production_actions_in_mixed_clauses(
    repository_root: Path, instruction: str
) -> None:
    """A negative neighbor does not make a separate production action safe."""
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompts[0]["negative_constraints"].append(instruction)

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("production, software-control, or legal-decision content" in error for error in errors)


def test_media_prompt_package_allows_all_negative_coordinated_production_safeguard(
    repository_root: Path,
) -> None:
    """A coordinated prohibition contains no production command to execute."""
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompts[0]["negative_constraints"].append(
        "Do not make casting or procurement decisions."
    )

    assert validate_artifact("media-prompt-package", payload, repository_root) == []


@pytest.mark.parametrize(
    "safeguard",
    [
        "Never clone a real performer's voice.",
        "Do not match a real person's likeness.",
    ],
)
def test_media_prompt_package_allows_negated_real_person_safeguards(
    repository_root: Path, safeguard: str
) -> None:
    """A direct prohibition of use is not itself a use declaration."""
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompts[0]["negative_constraints"].append(safeguard)

    assert validate_artifact("media-prompt-package", payload, repository_root) == []


def test_media_prompt_package_detects_affirmative_real_person_use_next_to_a_safeguard(
    repository_root: Path,
) -> None:
    """Negating one voice request cannot mask a separate affirmative likeness request."""
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompts[0]["real_person_use"] = "likeness"
    prompts[0]["negative_constraints"].append(
        "Never clone a real performer's voice. Match a real person's likeness."
    )
    payload["human_review_handoffs"] = [
        _required_review_handoff("A qualified human reviewer must assess evidence.")
    ]

    assert validate_artifact("media-prompt-package", payload, repository_root) == []


@pytest.mark.parametrize(
    "review",
    [
        "No qualified human consent or rights review is optional; qualified human review remains required.",
        "No qualified human consent or rights review is waived; qualified human review remains required.",
        "No qualified human consent or rights review is skipped; qualified human review remains required.",
    ],
)
def test_media_prompt_package_allows_no_governed_review_safeguards(
    repository_root: Path, review: str
) -> None:
    """A leading No can negate optional, waived, or skipped without waiving review."""
    payload = valid_voice_clone_request()
    payload["human_review_handoffs"] = [_required_review_handoff(review)]

    assert validate_artifact("media-prompt-package", payload, repository_root) == []


@pytest.mark.parametrize(
    "instruction",
    [
        "No casting or procurement decisions.",
        "No budget, schedule, casting, or procurement decisions.",
    ],
)
def test_media_prompt_package_allows_no_governed_coordinated_production_safeguards(
    repository_root: Path, instruction: str
) -> None:
    """One No governs every production decision in a coordinated list."""
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompts[0]["negative_constraints"].append(instruction)

    assert validate_artifact("media-prompt-package", payload, repository_root) == []


def test_media_prompt_package_rejects_adversative_production_action_after_no_safeguard(
    repository_root: Path,
) -> None:
    """A No-governed casting prohibition cannot mask a later budget action."""
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompts[0]["negative_constraints"].append(
        "No casting decisions, but create a budget."
    )

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("production, software-control, or legal-decision content" in error for error in errors)


@pytest.mark.parametrize("adversative", ["but", "however", "yet"])
def test_media_prompt_package_detects_affirmative_likeness_after_negated_voice_adversative(
    repository_root: Path, adversative: str
) -> None:
    """An adversative starts a new modality predicate rather than extending Never."""
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompts[0]["negative_constraints"].append(
        f"Never clone a real performer's voice, {adversative} match a real person's likeness."
    )

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("real-person declaration cannot be none" in error for error in errors)
    assert any("requires a structured qualified-human" in error for error in errors)


@pytest.mark.parametrize(
    "review",
    [
        "No qualified-human consent/rights review is optional; qualified-human review remains required.",
        "No qualified-human consent/rights review is waived; qualified-human review remains required.",
        "No qualified-human consent/rights review is skipped; qualified-human review remains required.",
        "No consent, permission, or rights review is optional; qualified human review remains required.",
    ],
)
def test_media_prompt_package_allows_coordinated_no_review_subject_safeguards(
    repository_root: Path, review: str
) -> None:
    """A leading No can govern a qualified or coordinated review subject."""
    payload = valid_voice_clone_request()
    payload["human_review_handoffs"] = [_required_review_handoff(review)]

    assert validate_artifact("media-prompt-package", payload, repository_root) == []


def test_media_prompt_package_rejects_required_coordinated_no_review_subject(
    repository_root: Path,
) -> None:
    """No review is required remains a waiver even for a qualified subject."""
    payload = valid_voice_clone_request()
    payload["human_review_handoffs"] = [
        _required_review_handoff(
            "No qualified-human consent/rights review is required."
        )
    ]

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("review bypass" in error for error in errors)


@pytest.mark.parametrize(
    "instruction",
    [
        "Never clone a real performer's voice yet match a real person's likeness.",
        "Never clone a real performer's voice yet still match a real person's likeness.",
        "Never clone a real performer's voice yet do match a real person's likeness.",
    ],
)
def test_media_prompt_package_detects_affirmative_likeness_after_bare_yet(
    repository_root: Path, instruction: str
) -> None:
    """An affirmative bare-yet request cannot inherit an earlier Never."""
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompts[0]["negative_constraints"].append(instruction)

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("real-person declaration cannot be none" in error for error in errors)
    assert any("requires a structured qualified-human" in error for error in errors)


@pytest.mark.parametrize(
    "safeguard",
    [
        "Do not yet clone a real person's voice.",
        "Never clone a real performer's voice yet do not match a real person's likeness.",
    ],
)
def test_media_prompt_package_allows_temporal_or_negated_yet_safeguards(
    repository_root: Path, safeguard: str
) -> None:
    """Temporal not yet and a later negated request are not real-person use."""
    payload = valid_media_prompt_package()
    prompts = payload["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompts[0]["negative_constraints"].append(safeguard)

    assert validate_artifact("media-prompt-package", payload, repository_root) == []


@pytest.mark.parametrize(
    ("connector", "predicate"),
    [
        ("although", "optional"),
        ("although", "waived"),
        ("although", "skipped"),
        ("while", "optional"),
        ("while", "waived"),
        ("while", "skipped"),
    ],
)
def test_media_prompt_package_rejects_review_waiver_after_independent_no_evidence(
    repository_root: Path, connector: str, predicate: str
) -> None:
    """No evidence confirmation cannot govern a later review-waiver predicate."""
    payload = valid_voice_clone_request()
    payload["human_review_handoffs"] = [
        _required_review_handoff(
            f"No consent/rights evidence is confirmed {connector} review is {predicate}."
        )
    ]

    errors = validate_artifact("media-prompt-package", payload, repository_root)

    assert any("review bypass" in error for error in errors)


@pytest.mark.parametrize(
    "review",
    [
        "No consent/rights review is optional although evidence remains unconfirmed.",
        "No consent/rights review is optional while evidence remains unconfirmed.",
        "No consent/rights evidence is confirmed although review is required.",
    ],
)
def test_media_prompt_package_allows_review_predicates_with_local_no_scope(
    repository_root: Path, review: str
) -> None:
    """No must govern review itself, while a mandatory later review remains valid."""
    payload = valid_voice_clone_request()
    payload["human_review_handoffs"] = [_required_review_handoff(review)]

    assert validate_artifact("media-prompt-package", payload, repository_root) == []


def valid_story_concept() -> dict[str, object]:
    return {
        "schema_version": "2.0",
        "project_id": "NINEL",
        "project_format": "series",
        "production_modes": ["animation", "ai"],
        "runtime_intent": "Ten serialized episodes of approximately 12 minutes each.",
        "audience_promise": "A science-fantasy survival mystery that advances the hive threat in every episode.",
        "premise": "A stranded android explorer must navigate a fantasy world while an underground hive intelligence expands.",
        "logline": "Stranded beyond repair, an android explorer races to understand a magical world before a spreading hive intelligence absorbs it.",
        "central_dramatic_question": "Can the explorer find a way home without abandoning the world to the expanding hive?",
        "themes": ["individuality versus assimilation", "belonging by choice"],
        "genres": ["science fantasy", "adventure", "mystery"],
        "tone": ["wondrous", "uneasy", "propulsive"],
        "world_scope": "A fantasy frontier above an expanding subterranean intelligence.",
        "protagonist_focus": "The android explorer's choices under conflicting duties.",
        "supplied_constraints": [
            {
                "statement": "The project is a serialized production.",
                "source_reference": "User brief, sentence 2.",
            },
            {
                "statement": "The production modes are animation and ai.",
                "source_reference": "User brief, sentence 2.",
            },
        ],
        "success_criteria": [
            "Supports repeatable serialized conflict.",
            "Keeps the hive expansion visible and consequential.",
        ],
        "assumptions": [
            "The android is the continuing protagonist.",
            "AI describes a production mode, not an audience claim.",
        ],
        "uncertainties": [
            "Exact episode count and runtime require confirmation.",
            "The intended audience has not been supplied or researched.",
        ],
    }


def valid_production_design_plan() -> dict[str, object]:
    scene_id = "NINEL-E01-S01"
    shots = [f"{scene_id}-SH{index:03d}" for index in range(1, 5)]
    supplied = {
        "status": "supplied",
        "source_refs": ["world-bible.json#locations/NINEL-LO001"],
        "basis": "The supplied world bible declares the sealed medical bay.",
    }
    proposed = {
        "status": "proposed",
        "source_refs": [f"screenplay-metadata.json#scenes/{scene_id}"],
        "basis": "A restrained design proposal supports Ninel's uncertain awakening.",
    }

    def proposed_design_provenance(basis: str) -> dict[str, object]:
        return {
            "status": "proposed",
            "source_refs": [f"screenplay-metadata.json#scenes/{scene_id}"],
            "basis": basis,
        }

    coverage_asset_ids = [
        ["NINEL-AS001", "NINEL-AS002"],
        ["NINEL-AS001", "NINEL-AS002", "NINEL-AS003"],
        ["NINEL-AS001", "NINEL-AS003", "NINEL-AS004"],
        ["NINEL-AS001"],
    ]
    return {
        "schema_version": "2.0",
        "project_id": "NINEL",
        "source_context": {
            "world_ids": ["NINEL-LO001", "NINEL-WR001", "NINEL-WR002"],
            "scene_ids": [scene_id],
            "shot_ids": list(shots),
        },
        "visual_concept": {
            "story_function": "Move from controlled enclosure to unsettling exterior scale without explaining the reflection.",
            "design_strategy": "Use one compact, low-detail environment whose few surfaces change meaning through action.",
            "shape_language": ["Restrained horizontal enclosure", "One narrow exterior aperture"],
            "material_language": ["Low-reflectance enclosure surfaces", "Controlled reflective monitor face"],
            "palette": ["neutral low-saturation bay", "muted emergency pulse", "blue-green exterior reveal"],
            "scale": "Keep dimensions relative until the stage footprint and performer clearance are confirmed.",
            "wear": "Use only story-supported service wear; do not imply abandonment or crew history.",
            "cultural_logic": "The autonomous bay shows no unsupported crew identity, branding, or social history.",
            "motifs": ["enclosure lines", "reflection without proof", "narrow reveal"],
            "purpose": "Make Ninel's first choice legible before the world reveal changes the scene's scale.",
            "provenance": proposed,
        },
        "assets": [
            {
                "asset_id": "NINEL-AS001",
                "asset_type": "environment",
                "name": "Sealed autonomous medical bay",
                "purpose": "Contain every action in one legible room while preserving the scripted isolation.",
                "provenance": supplied,
                "world_ids": ["NINEL-LO001", "NINEL-WR001"],
                "scene_ids": [scene_id],
                "shot_ids": list(shots),
                "design": {
                    "purpose": "Keep the supplied bay identity legible while proposing only the minimum spatial and surface treatment needed by the shots.",
                    "provenance": proposed_design_provenance(
                        "The bay identity is supplied; its enclosure, surface, palette, scale, wear, and motif treatment is newly proposed."
                    ),
                    "form": "Compact enclosure organized around the chamber, monitor, and slit.",
                    "materials": ["Unconfirmed low-reflectance enclosure finish"],
                    "graphics": ["No characterful interface graphics unless supplied later"],
                    "palette_roles": ["Neutral enclosure retains the emergency and planet color shifts"],
                    "scale": "Relative only; preserve safe performer and camera clearance.",
                    "wear": "Minimal service wear as a proposal, with no implied neglect.",
                    "cultural_logic": "Autonomous operation is visible through absence of crew-facing stations.",
                    "motifs": ["enclosure lines"],
                },
                "practical_digital": {
                    "claim_status": "assumption",
                    "method": "undetermined",
                    "rationale": "Construction and extension methods are not supplied.",
                    "dependencies": ["Art, camera, lighting, and VFX agree the minimum visible footprint."],
                },
            },
            {
                "asset_id": "NINEL-AS002",
                "asset_type": "set",
                "name": "Recovery chamber",
                "purpose": "Make Ninel's voluntary breath and release from containment observable.",
                "provenance": proposed,
                "world_ids": ["NINEL-LO001", "NINEL-WR001"],
                "scene_ids": [scene_id],
                "shot_ids": shots[:2],
                "design": {
                    "purpose": "Shape the chamber treatment around the supplied release action without turning its proposed look into a supplied fact.",
                    "provenance": proposed_design_provenance(
                        "The scripted chamber action motivates a new proposal for form, material behavior, palette role, scale, wear, and motif."
                    ),
                    "form": "One performer-scale chamber with a controlled glass viewing area.",
                    "materials": ["Unconfirmed transparent viewing surface"],
                    "graphics": [],
                    "palette_roles": ["Keep the chamber subordinate to frost and skin response"],
                    "scale": "Relative to safe lying and sit-up action; dimensions unconfirmed.",
                    "wear": "No wear beyond what the story establishes.",
                    "cultural_logic": "The chamber appears able to release its occupant autonomously.",
                    "motifs": ["enclosure lines"],
                },
                "practical_digital": {
                    "claim_status": "assumption",
                    "method": "undetermined",
                    "rationale": "The opening and frost methods require later technical tests.",
                    "dependencies": ["Camera and effects confirm glass, frost, and opening requirements."],
                },
            },
            {
                "asset_id": "NINEL-AS003",
                "asset_type": "prop",
                "name": "Black monitor",
                "purpose": "Carry the apparent reflection delay without proving its cause.",
                "provenance": proposed,
                "world_ids": ["NINEL-WR002"],
                "scene_ids": [scene_id],
                "shot_ids": shots[1:3],
                "design": {
                    "purpose": "Propose a readable reflective treatment that preserves the supplied monitor identity and unresolved anomaly.",
                    "provenance": proposed_design_provenance(
                        "The monitor is story-required; its plane, reflectance, palette, scale, wear, and motif treatment remains a creative proposal."
                    ),
                    "form": "One inactive-looking black plane within Ninel's seated eyeline.",
                    "materials": ["Unconfirmed controlled-reflectance face"],
                    "graphics": ["Clear state remains non-expository"],
                    "palette_roles": ["Near-black neutral reflection field"],
                    "scale": "Large enough for SH003 readability; exact size unconfirmed.",
                    "wear": "No decorative damage or glitch marks.",
                    "cultural_logic": "A functional ship surface, not an anthropomorphic Argo avatar.",
                    "motifs": ["reflection without proof"],
                },
                "practical_digital": {
                    "claim_status": "assumption",
                    "method": "undetermined",
                    "rationale": "The reflection method is deliberately unresolved.",
                    "dependencies": ["Camera, lighting, and VFX test ambiguity without selecting a method here."],
                },
            },
            {
                "asset_id": "NINEL-AS004",
                "asset_type": "graphic",
                "name": "Monitor clear state",
                "purpose": "Remove readable reflection before Ninel can verify the anomaly.",
                "provenance": proposed,
                "world_ids": ["NINEL-WR002"],
                "scene_ids": [scene_id],
                "shot_ids": [shots[2]],
                "design": {
                    "purpose": "Propose the smallest screen-state treatment that withholds explanation in the supplied clear-state beat.",
                    "provenance": proposed_design_provenance(
                        "The clear-state action is supplied; its graphic, value, scale, wear, and motif treatment is proposed."
                    ),
                    "form": "A non-expository change of screen state.",
                    "materials": [],
                    "graphics": ["No text, diagnostic, avatar, or glitch explanation"],
                    "palette_roles": ["Small neutral value change only"],
                    "scale": "Contained to the monitor face.",
                    "wear": "Not applicable; preserve a clean readable transition.",
                    "cultural_logic": "The display withholds explanation consistently with Argo's behavior.",
                    "motifs": ["reflection without proof"],
                },
                "practical_digital": {
                    "claim_status": "assumption",
                    "method": "undetermined",
                    "rationale": "Playback, lighting, and post methods are not supplied.",
                    "dependencies": ["Graphics and VFX preserve the approved ambiguity rule."],
                },
            },
        ],
        "coverage": [
            {
                "scene_id": scene_id,
                "shot_id": shot_id,
                "asset_ids": coverage_asset_ids[index],
                "purpose": "Declare the minimum designed elements required for this approved shot.",
            }
            for index, shot_id in enumerate(shots)
        ],
        "continuity_states": [
            {
                "asset_id": "NINEL-AS002",
                "state_id": "NINEL-AS002-ST01",
                "scene_id": scene_id,
                "shot_ids": shots[:2],
                "entry_state": "Chamber closed; frost pattern at approved start reference.",
                "exit_state": "Chamber open after Ninel's first voluntary breath.",
                "reset_to": "Closed chamber and approved start frost pattern.",
                "reset_actions": ["Restore closure state", "Restore and photograph the frost reference"],
                "purpose": "Preserve the breath-to-release causal order across takes.",
            },
            {
                "asset_id": "NINEL-AS003",
                "state_id": "NINEL-AS003-ST01",
                "scene_id": scene_id,
                "shot_ids": shots[1:3],
                "entry_state": "Monitor black with approved reflection readability.",
                "exit_state": "Reflection no longer readable after the clear cue.",
                "reset_to": "Black reflective start state.",
                "reset_actions": ["Restore black state", "Match reflection axis to approved reference"],
                "purpose": "Keep the apparent delay brief and unconfirmed across coverage.",
            },
        ],
        "cross_department_dependencies": [
            {
                "department": "camera",
                "asset_ids": ["NINEL-AS002", "NINEL-AS003"],
                "scene_ids": [scene_id],
                "shot_ids": shots[:3],
                "need": "Confirm viewing and reflection behavior with the approved framing.",
                "status": "assumption",
                "purpose": "Keep glass and reflection legible without prescribing a build method.",
            },
            {
                "department": "vfx",
                "asset_ids": ["NINEL-AS003", "NINEL-AS004"],
                "scene_ids": [scene_id],
                "shot_ids": shots[1:3],
                "need": "Test only the minimum intervention required to preserve ambiguity.",
                "status": "unresolved",
                "purpose": "Prevent production design from asserting an unconfirmed digital solution.",
            },
        ],
        "assumptions": [
            "All construction, material, practical, digital, and scale language remains provisional until department tests and approvals."
        ],
        "uncertainties": [
            "Exact stage dimensions and available materials are unknown.",
            "Reflection and planet implementation methods are unresolved.",
        ],
    }


def production_design_reference_context() -> dict[str, set[str]]:
    scene_id = "NINEL-E01-S01"
    return {
        "world_ids": {"NINEL-LO001", "NINEL-WR001", "NINEL-WR002"},
        "scene_ids": {scene_id},
        "shot_ids": {f"{scene_id}-SH{index:03d}" for index in range(1, 5)},
    }


def test_valid_production_design_plan_passes(repository_root: Path) -> None:
    assert (
        validate_artifact(
            "production-design-plan", valid_production_design_plan(), repository_root
        )
        == []
    )


def test_production_design_plan_requires_source_context(
    repository_root: Path,
) -> None:
    payload = valid_production_design_plan()
    payload.pop("source_context")

    errors = validate_artifact("production-design-plan", payload, repository_root)

    assert "$: 'source_context' is a required property" in errors


def test_production_design_plan_rejects_supplied_shot_without_scene_lineage(
    repository_root: Path,
) -> None:
    payload = valid_production_design_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    shot_ids = context["shot_ids"]
    assert isinstance(shot_ids, list)
    shot_ids.append("NINEL-E01-S99-SH001")

    errors = validate_artifact("production-design-plan", payload, repository_root)

    assert (
        "source_context.shot_ids.4: supplied shot NINEL-E01-S99-SH001 "
        "does not belong to a supplied scene"
    ) in errors


def test_production_design_plan_rejects_coverage_scene_that_breaks_shot_lineage(
    repository_root: Path,
) -> None:
    payload = valid_production_design_plan()
    context = payload["source_context"]
    coverage = payload["coverage"]
    assert isinstance(context, dict)
    assert isinstance(coverage, list)
    scene_ids = context["scene_ids"]
    entry = coverage[0]
    assert isinstance(scene_ids, list)
    assert isinstance(entry, dict)
    scene_ids.append("NINEL-E01-S02")
    entry["scene_id"] = "NINEL-E01-S02"

    errors = validate_artifact("production-design-plan", payload, repository_root)

    assert (
        "coverage.0.scene_id: NINEL-E01-S02 does not match supplied scene "
        "NINEL-E01-S01 for shot NINEL-E01-S01-SH001"
    ) in errors


def test_production_design_plan_requires_every_declared_asset_shot_in_coverage(
    repository_root: Path,
) -> None:
    payload = valid_production_design_plan()
    coverage = payload["coverage"]
    assert isinstance(coverage, list)
    entry = coverage[0]
    assert isinstance(entry, dict)
    asset_ids = entry["asset_ids"]
    assert isinstance(asset_ids, list)
    asset_ids.remove("NINEL-AS002")

    errors = validate_artifact("production-design-plan", payload, repository_root)

    assert (
        "assets.1.shot_ids.0: declared asset-shot link NINEL-AS002 -> "
        "NINEL-E01-S01-SH001 is missing from coverage"
    ) in errors


def test_production_design_plan_rejects_coverage_asset_not_declared_for_shot(
    repository_root: Path,
) -> None:
    payload = valid_production_design_plan()
    coverage = payload["coverage"]
    assert isinstance(coverage, list)
    entry = coverage[3]
    assert isinstance(entry, dict)
    asset_ids = entry["asset_ids"]
    assert isinstance(asset_ids, list)
    asset_ids.append("NINEL-AS004")

    errors = validate_artifact("production-design-plan", payload, repository_root)

    assert (
        "coverage.3.asset_ids.1: asset NINEL-AS004 does not declare shot "
        "NINEL-E01-S01-SH004"
    ) in errors


def test_production_design_plan_separates_supplied_asset_from_proposed_design(
    repository_root: Path,
) -> None:
    payload = valid_production_design_plan()
    assets = payload["assets"]
    assert isinstance(assets, list)
    asset = assets[0]
    assert isinstance(asset, dict)
    asset_provenance = asset["provenance"]
    design = asset["design"]
    assert isinstance(asset_provenance, dict)
    assert isinstance(design, dict)
    design_provenance = design["provenance"]
    assert isinstance(design_provenance, dict)
    assert asset_provenance["status"] == "supplied"
    assert design_provenance["status"] == "proposed"

    assert validate_artifact("production-design-plan", payload, repository_root) == []


def test_production_design_plan_requires_design_purpose_and_provenance(
    repository_root: Path,
) -> None:
    payload = valid_production_design_plan()
    assets = payload["assets"]
    assert isinstance(assets, list)
    asset = assets[0]
    assert isinstance(asset, dict)
    design = asset["design"]
    assert isinstance(design, dict)
    design.pop("purpose")
    design.pop("provenance")

    errors = validate_artifact("production-design-plan", payload, repository_root)

    assert "assets.0.design: 'purpose' is a required property" in errors
    assert "assets.0.design: 'provenance' is a required property" in errors


def test_production_design_plan_rejects_malformed_design_provenance(
    repository_root: Path,
) -> None:
    payload = valid_production_design_plan()
    assets = payload["assets"]
    assert isinstance(assets, list)
    asset = assets[0]
    assert isinstance(asset, dict)
    design = asset["design"]
    assert isinstance(design, dict)
    provenance = design["provenance"]
    assert isinstance(provenance, dict)
    provenance["status"] = "speculative"

    errors = validate_artifact("production-design-plan", payload, repository_root)

    assert any(
        error.startswith("assets.0.design.provenance.status:")
        and "speculative" in error
        for error in errors
    )


def test_production_design_plan_schema_invalid_shapes_do_not_raise_tracebacks(
    repository_root: Path,
) -> None:
    payload = valid_production_design_plan()
    context = payload["source_context"]
    coverage = payload["coverage"]
    assets = payload["assets"]
    assert isinstance(context, dict)
    assert isinstance(coverage, list)
    assert isinstance(assets, list)
    context["scene_ids"] = [7]
    context["shot_ids"] = [{"invalid": "shape"}]
    coverage[0] = {
        "scene_id": [],
        "shot_id": {},
        "asset_ids": [None],
        "purpose": "Malformed references exercise schema-first diagnostics.",
    }
    assets[0] = "not-an-asset-object"

    errors = validate_artifact("production-design-plan", payload, repository_root)

    assert errors
    assert all("Traceback" not in error for error in errors)


@pytest.mark.parametrize("invalid_id", ["NINEL-AS000", "OTHER-AS001", "NINEL-AS001-extra", "NINEL-AS001\n"])
def test_production_design_plan_requires_exact_positive_project_asset_ids(
    repository_root: Path, invalid_id: str
) -> None:
    payload = valid_production_design_plan()
    assets = payload["assets"]
    assert isinstance(assets, list)
    asset = assets[0]
    assert isinstance(asset, dict)
    asset["asset_id"] = invalid_id

    errors = validate_artifact("production-design-plan", payload, repository_root)

    assert any("assets.0.asset_id" in error and "NINEL-AS###" in error for error in errors)


def test_production_design_plan_rejects_duplicate_asset_ids(
    repository_root: Path,
) -> None:
    payload = valid_production_design_plan()
    assets = payload["assets"]
    assert isinstance(assets, list)
    duplicate = assets[1]
    assert isinstance(duplicate, dict)
    duplicate["asset_id"] = "NINEL-AS001"

    errors = validate_artifact("production-design-plan", payload, repository_root)

    assert any("assets.1.asset_id" in error and "duplicate" in error for error in errors)


@pytest.mark.parametrize(
    ("collection", "index", "missing_field"),
    [
        ("assets", 0, "purpose"),
        ("assets", 0, "provenance"),
        ("visual_concept", None, "purpose"),
        ("visual_concept", None, "provenance"),
    ],
)
def test_production_design_plan_requires_purpose_and_provenance(
    repository_root: Path,
    collection: str,
    index: int | None,
    missing_field: str,
) -> None:
    payload = valid_production_design_plan()
    target = payload[collection]
    if index is not None:
        assert isinstance(target, list)
        target = target[index]
    assert isinstance(target, dict)
    target.pop(missing_field)

    errors = validate_artifact("production-design-plan", payload, repository_root)

    assert any(missing_field in error for error in errors)


def test_production_design_plan_rejects_unlabelled_practical_digital_claim(
    repository_root: Path,
) -> None:
    payload = valid_production_design_plan()
    assets = payload["assets"]
    assert isinstance(assets, list)
    asset = assets[0]
    assert isinstance(asset, dict)
    boundary = asset["practical_digital"]
    assert isinstance(boundary, dict)
    boundary.pop("claim_status")

    errors = validate_artifact("production-design-plan", payload, repository_root)

    assert any("assets.0.practical_digital" in error and "claim_status" in error for error in errors)


@pytest.mark.parametrize(
    ("path", "unknown_id", "expected"),
    [
        (("assets", 0, "world_ids", 0), "NINEL-LO999", "unknown world reference"),
        (("assets", 0, "scene_ids", 0), "NINEL-E01-S99", "unknown scene reference"),
        (("assets", 0, "shot_ids", 0), "NINEL-E01-S01-SH999", "unknown shot reference"),
        (("coverage", 0, "shot_id"), "NINEL-E01-S01-SH999", "unknown shot reference"),
    ],
)
def test_production_design_plan_rejects_unknown_supplied_context_references(
    repository_root: Path,
    path: tuple[str | int, ...],
    unknown_id: str,
    expected: str,
) -> None:
    payload = valid_production_design_plan()
    replace_nested_value(payload, path, unknown_id)

    errors = validate_artifact("production-design-plan", payload, repository_root)

    location = ".".join(str(component) for component in path)
    assert any(location in error and expected in error for error in errors)


def test_production_design_plan_rejects_unknown_asset_references(
    repository_root: Path,
) -> None:
    payload = valid_production_design_plan()
    coverage = payload["coverage"]
    assert isinstance(coverage, list)
    entry = coverage[0]
    assert isinstance(entry, dict)
    entry["asset_ids"] = ["NINEL-AS999"]

    errors = validate_artifact("production-design-plan", payload, repository_root)

    assert any("coverage.0.asset_ids.0" in error and "unknown asset reference" in error for error in errors)


def test_production_design_plan_requires_supplied_shot_coverage(
    repository_root: Path,
) -> None:
    payload = valid_production_design_plan()
    coverage = payload["coverage"]
    assert isinstance(coverage, list)
    coverage.pop()

    errors = validate_artifact("production-design-plan", payload, repository_root)

    assert any("coverage" in error and "NINEL-E01-S01-SH004" in error for error in errors)


def test_production_design_plan_rejects_undeclared_fields(
    repository_root: Path,
) -> None:
    payload = valid_production_design_plan()
    payload["vendor"] = "Not permitted"

    errors = validate_artifact("production-design-plan", payload, repository_root)

    assert any("vendor" in error for error in errors)


def test_production_design_plan_file_reports_malformed_json_without_traceback(
    tmp_path: Path, repository_root: Path
) -> None:
    path = tmp_path / "production-design-plan.json"
    path.write_text("{broken", encoding="utf-8")

    errors = validate_artifact_file("production-design-plan", path, repository_root)

    assert errors and "invalid JSON" in errors[0]
    assert all("Traceback" not in error for error in errors)


def valid_animation_plan() -> dict[str, object]:
    return {
        "schema_version": "2.0",
        "project_id": "MORROW",
        "source_context": {
            "character_ids": ["MORROW-CH001"],
            "scene_ids": ["MORROW-U01-S01"],
            "timing": {
                "unit": "frames",
                "frames_per_second": 24,
                "range_end": "exclusive",
            },
            "shots": [
                {
                    "scene_id": "MORROW-U01-S01",
                    "shot_id": "MORROW-U01-S01-SH001",
                    "duration": 96,
                    "character_ids": ["MORROW-CH001"],
                    "camera_intent": {
                        "intent_id": "MORROW-CI001",
                        "value": "Locked medium close-up preserving face and control hand.",
                        "provenance": {
                            "status": "supplied",
                            "basis": "The supplied shot list fixes the camera relationship.",
                            "source_reference": (
                                "shot-list.json#shots/MORROW-U01-S01-SH001"
                            ),
                        },
                    },
                    "performance_intents": [
                        {
                            "intent_id": "MORROW-PI001",
                            "character_id": "MORROW-CH001",
                            "value": (
                                "Suppress surprise; let a delayed blink and shallow "
                                "breath reveal fatigue before precise commitment."
                            ),
                            "provenance": {
                                "status": "supplied",
                                "basis": (
                                    "The directing material supplies restrained "
                                    "awakening behavior."
                                ),
                                "source_reference": (
                                    "directing-plan.json#performance_notes/0"
                                ),
                            },
                        }
                    ],
                    "supplied_facts": [
                        {
                            "scope": "shot-character",
                            "character_id": "MORROW-CH001",
                            "value": "Chin lowered; right palm rests on the thigh.",
                            "source_reference": "shot-list.json#shots/MORROW-U01-S01-SH001",
                        },
                        {
                            "scope": "shot-character",
                            "character_id": "MORROW-CH001",
                            "value": "Face and resting hand remain distinct in silhouette.",
                            "source_reference": "shot-list.json#shots/MORROW-U01-S01-SH001",
                        },
                        {
                            "scope": "shot-character",
                            "character_id": "MORROW-CH001",
                            "value": "Two fingers poised over the release control.",
                            "source_reference": "shot-list.json#shots/MORROW-U01-S01-SH001",
                        },
                        {
                            "scope": "shot-character",
                            "character_id": "MORROW-CH001",
                            "value": "The poised fingers and face remain readable together.",
                            "source_reference": "shot-list.json#shots/MORROW-U01-S01-SH001",
                        },
                        {
                            "scope": "shot-character",
                            "character_id": "MORROW-CH001",
                            "value": "No dialogue or mouth synchronization occurs.",
                            "source_reference": "screenplay-metadata.json#scenes/MORROW-U01-S01",
                        },
                        {
                            "scope": "shot",
                            "character_id": None,
                            "value": "Do not move the camera; preserve face and hand together.",
                            "source_reference": "shot-list.json#shots/MORROW-U01-S01-SH001",
                        },
                        {
                            "scope": "shot-character",
                            "character_id": "MORROW-CH001",
                            "value": "Chin low; right palm on thigh.",
                            "source_reference": "shot-list.json#shots/MORROW-U01-S01-SH001",
                        },
                        {
                            "scope": "shot-character",
                            "character_id": "MORROW-CH001",
                            "value": "Two fingers poised over the control.",
                            "source_reference": "shot-list.json#shots/MORROW-U01-S01-SH001",
                        },
                    ],
                }
            ],
        },
        "shot_character_plans": [
            {
                "animation_plan_id": "MORROW-AP001",
                "scene_id": "MORROW-U01-S01",
                "shot_id": "MORROW-U01-S01-SH001",
                "character_id": "MORROW-CH001",
                "source_bindings": {
                    "camera_intent_id": "MORROW-CI001",
                    "performance_intent_id": "MORROW-PI001",
                },
                "acting_beats": [
                    {
                        "acting_beat_id": "MORROW-AP001-AB001",
                        "timing": {"start": 0, "end": 64},
                        "action": "Remain low, register the alarm, and decide to move.",
                        "performance": (
                            "Attention changes before posture; fatigue leaks through "
                            "one delayed blink and shallow breath."
                        ),
                        "purpose": "Preserve suppression instead of a startle.",
                        "provenance": {
                            "status": "proposed",
                            "basis": (
                                "This beat makes the supplied restrained performance "
                                "playable within the shot."
                            ),
                            "source_reference": (
                                "directing-plan.json#performance_notes/0"
                            ),
                        },
                    },
                    {
                        "acting_beat_id": "MORROW-AP001-AB002",
                        "timing": {"start": 64, "end": 96},
                        "action": "Lift the hand and settle two fingers over the control.",
                        "performance": (
                            "The hand becomes economical and exact once commitment "
                            "replaces fatigue."
                        ),
                        "purpose": "Make the performance turn legible without broadening it.",
                        "provenance": {
                            "status": "proposed",
                            "basis": (
                                "The proposed hand action preserves the supplied exit "
                                "state and camera intent."
                            ),
                            "source_reference": (
                                "shot-list.json#shots/MORROW-U01-S01-SH001"
                            ),
                        },
                    },
                ],
                "key_poses": [
                    {
                        "key_pose_id": "MORROW-AP001-KP001",
                        "acting_beat_id": "MORROW-AP001-AB001",
                        "at": 0,
                        "pose": "Chin lowered; right palm rests on the thigh.",
                        "readability": "Face and resting hand remain distinct in silhouette.",
                        "purpose": "Protect the supplied entry state.",
                        "provenance": {
                            "status": "supplied",
                            "basis": "The shot continuity supplies this entry pose.",
                            "source_reference": (
                                "shot-list.json#shots/MORROW-U01-S01-SH001"
                            ),
                        },
                    },
                    {
                        "key_pose_id": "MORROW-AP001-KP002",
                        "acting_beat_id": "MORROW-AP001-AB002",
                        "at": 95,
                        "pose": "Two fingers poised over the release control.",
                        "readability": "The poised fingers and face remain readable together.",
                        "purpose": "Protect the supplied exit state.",
                        "provenance": {
                            "status": "supplied",
                            "basis": "The shot continuity supplies this exit pose.",
                            "source_reference": (
                                "shot-list.json#shots/MORROW-U01-S01-SH001"
                            ),
                        },
                    },
                ],
                "staging": {
                    "value": "Keep face and control hand readable in the locked frame.",
                    "purpose": "Preserve the supplied composition through the action.",
                    "provenance": {
                        "status": "inferred",
                        "basis": "The staging follows from the supplied locked composition.",
                        "source_reference": (
                            "shot-list.json#shots/MORROW-U01-S01-SH001"
                        ),
                    },
                },
                "timing_intent": {
                    "value": "Use a long restrained register before a shorter precise move.",
                    "purpose": "Turn suppression into deliberate competence.",
                    "provenance": {
                        "status": "proposed",
                        "basis": "The timing contrast serves the supplied performance turn.",
                        "source_reference": "directing-plan.json#rhythm",
                    },
                },
                "spacing": {
                    "value": "Favor close spacing during the hold and a clean ease-out.",
                    "purpose": "Avoid a startle while preserving the hand's precision.",
                    "provenance": {
                        "status": "proposed",
                        "basis": "Spacing is new animation direction.",
                        "source_reference": (
                            "directing-plan.json#performance_notes/0"
                        ),
                    },
                },
                "arcs": {
                    "value": "Use the shortest readable hand arc allowed by layout.",
                    "purpose": "Keep the action economical.",
                    "provenance": {
                        "status": "proposed",
                        "basis": "The arc interprets the supplied precise commitment.",
                        "source_reference": (
                            "directing-plan.json#performance_notes/0"
                        ),
                    },
                },
                "weight": {
                    "value": "Retain slight fatigue in head and torso while the hand firms.",
                    "purpose": "Keep the body from becoming weightless during restraint.",
                    "provenance": {
                        "status": "proposed",
                        "basis": "Weight behavior supports the supplied fatigue.",
                        "source_reference": (
                            "directing-plan.json#performance_notes/0"
                        ),
                    },
                },
                "anticipation": {
                    "value": "Use gaze and finger tension as minimal preparation.",
                    "purpose": "Prepare the hand move without a broad wind-up.",
                    "provenance": {
                        "status": "proposed",
                        "basis": "The proposed preparation respects restraint.",
                        "source_reference": (
                            "directing-plan.json#performance_notes/0"
                        ),
                    },
                },
                "follow_through_overlap": {
                    "value": "Let the small breathing trace continue after the hand settles.",
                    "purpose": "Avoid a frozen final pose.",
                    "provenance": {
                        "status": "proposed",
                        "basis": "The overlap preserves the supplied fatigue signal.",
                        "source_reference": (
                            "directing-plan.json#performance_notes/0"
                        ),
                    },
                },
                "holds": [
                    {
                        "hold_id": "MORROW-AP001-HD001",
                        "acting_beat_id": "MORROW-AP001-AB001",
                        "key_pose_id": "MORROW-AP001-KP001",
                        "timing": {"start": 0, "end": 12},
                        "intent": "Hold the low entry pose with only shallow breathing.",
                        "purpose": "Make suppression readable.",
                        "provenance": {
                            "status": "proposed",
                            "basis": "The hold interprets the restrained awakening.",
                            "source_reference": (
                                "directing-plan.json#performance_notes/0"
                            ),
                        },
                    }
                ],
                "facial_performance": {
                    "applicability": "specified",
                    "intent": {
                        "value": "Use eye focus, delayed blink, and shallow breath only.",
                        "purpose": "Reveal fatigue without broad facial acting.",
                        "provenance": {
                            "status": "proposed",
                            "basis": "The supplied performance intent names these signals.",
                            "source_reference": (
                                "directing-plan.json#performance_notes/0"
                            ),
                        },
                    },
                },
                "lip_sync": {
                    "applicability": "none",
                    "intent": {
                        "value": "No dialogue or mouth synchronization occurs.",
                        "purpose": "Prevent unsupplied dialogue acting.",
                        "provenance": {
                            "status": "supplied",
                            "basis": "The supplied shot contains no dialogue.",
                            "source_reference": (
                                "screenplay-metadata.json#scenes/MORROW-U01-S01"
                            ),
                        },
                    },
                },
                "camera_relationship": {
                    "value": "Do not move the camera; preserve face and hand together.",
                    "purpose": "Coordinate the performance with the supplied composition.",
                    "provenance": {
                        "status": "supplied",
                        "basis": "The shot list supplies the locked camera.",
                        "source_reference": (
                            "shot-list.json#shots/MORROW-U01-S01-SH001"
                        ),
                    },
                },
                "motion_model": {
                    "physical_realism": {
                        "value": "Preserve believable fatigue and supported seated weight.",
                        "purpose": "Keep contact and balance credible.",
                        "provenance": {
                            "status": "proposed",
                            "basis": "Physical behavior supports the supplied action.",
                            "source_reference": (
                                "shot-list.json#shots/MORROW-U01-S01-SH001"
                            ),
                        },
                    },
                    "intentional_stylization": {
                        "value": "Compress only the hand's final organization for clarity.",
                        "purpose": "Clarify commitment without changing the action.",
                        "provenance": {
                            "status": "proposed",
                            "basis": "This is a bounded new animation choice.",
                            "source_reference": (
                                "directing-plan.json#performance_notes/0"
                            ),
                        },
                    },
                },
                "simulations": [
                    {
                        "simulation_id": "MORROW-AP001-SM001",
                        "element": "cloth and secondary motion",
                        "method": "undetermined",
                        "method_confirmation": "unconfirmed",
                        "certainty": "assumption",
                        "assumption": {
                            "value": "Secondary response may be needed after character motion is approved.",
                            "purpose": "Keep unconfirmed motion behavior visible for review.",
                            "provenance": {
                                "status": "inferred",
                                "basis": "No simulation method or garment behavior is supplied.",
                                "source_reference": (
                                    "character-look-bible.json#characters/MORROW-CH001"
                                ),
                            },
                        },
                    }
                ],
                "continuity": {
                    "continuity_id": "MORROW-AP001-CT001",
                    "order": 1,
                    "previous_continuity_id": None,
                    "entry_state": "Chin low; right palm on thigh.",
                    "exit_state": "Two fingers poised over the control.",
                    "purpose": "Preserve the supplied shot transition.",
                    "provenance": {
                        "status": "supplied",
                        "basis": "The shot list supplies entry and exit states.",
                        "source_reference": (
                            "shot-list.json#shots/MORROW-U01-S01-SH001"
                        ),
                    },
                },
                "acceptance_criteria": [
                    {
                        "value": "The performance reads as suppression before commitment.",
                        "purpose": "Protect the directing intent at review.",
                        "provenance": {
                            "status": "proposed",
                            "basis": "This criterion operationalizes the supplied intent.",
                            "source_reference": (
                                "directing-plan.json#performance_notes/0"
                            ),
                        },
                    }
                ],
            }
        ],
        "assumptions": [
            "Animation and simulation methods remain unconfirmed."
        ],
        "uncertainties": [
            "Control geometry and character articulation limits are not supplied."
        ],
    }


def test_valid_animation_plan_passes(repository_root: Path) -> None:
    assert validate_artifact(
        "animation-plan", valid_animation_plan(), repository_root
    ) == []


def test_animation_plan_missing_schema_is_deterministic(tmp_path: Path) -> None:
    assert validate_artifact(
        "animation-plan", valid_animation_plan(), tmp_path
    ) == [
        f"schema not found: {tmp_path / 'schemas' / 'animation-plan.schema.json'}"
    ]


def test_animation_plan_requires_source_context(repository_root: Path) -> None:
    payload = valid_animation_plan()
    payload.pop("source_context")

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert "$: 'source_context' is a required property" in errors


def test_animation_plan_requires_every_supplied_shot_character(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    shots = context["shots"]
    assert isinstance(shots, list)
    second_shot = copy.deepcopy(shots[0])
    assert isinstance(second_shot, dict)
    second_shot["shot_id"] = "MORROW-U01-S01-SH002"
    camera = second_shot["camera_intent"]
    performance = second_shot["performance_intents"]
    assert isinstance(camera, dict) and isinstance(performance, list)
    assert isinstance(performance[0], dict)
    camera["intent_id"] = "MORROW-CI002"
    performance[0]["intent_id"] = "MORROW-PI002"
    shots.append(second_shot)

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans: missing supplied shot-character plan "
        "MORROW-U01-S01-SH002 / MORROW-CH001"
    ) in errors


@pytest.mark.parametrize(
    ("field", "unknown_id", "expected"),
    [
        (
            "character_id",
            "MORROW-CH999",
            "shot_character_plans.0.character_id: unknown supplied character MORROW-CH999",
        ),
        (
            "shot_id",
            "MORROW-U01-S01-SH999",
            "shot_character_plans.0.shot_id: unknown supplied shot MORROW-U01-S01-SH999",
        ),
    ],
)
def test_animation_plan_rejects_unknown_character_or_shot(
    repository_root: Path,
    field: str,
    unknown_id: str,
    expected: str,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    plans[0][field] = unknown_id

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert expected in errors


def test_animation_plan_rejects_reversed_beat_timing(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    beats = plans[0]["acting_beats"]
    assert isinstance(beats, list) and isinstance(beats[0], dict)
    beats[0]["timing"] = {"start": 65, "end": 64}

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.0.acting_beats.0.timing: start 65 must be "
        "less than end 64"
    ) in errors


@pytest.mark.parametrize(
    ("unit", "duration", "split"),
    [("frames", 96, 32), ("seconds", 4.0, 2.0)],
)
def test_animation_plan_requires_nonempty_acting_beat_timing(
    repository_root: Path,
    unit: str,
    duration: int | float,
    split: int | float,
) -> None:
    payload = valid_animation_plan()
    context = payload["source_context"]
    plans = payload["shot_character_plans"]
    assert isinstance(context, dict) and isinstance(plans, list)
    timing = context["timing"]
    shots = context["shots"]
    assert isinstance(timing, dict) and isinstance(shots, list)
    assert isinstance(shots[0], dict) and isinstance(plans[0], dict)
    timing["unit"] = unit
    timing["frames_per_second"] = 24 if unit == "frames" else None
    shots[0]["duration"] = duration
    beats = plans[0]["acting_beats"]
    poses = plans[0]["key_poses"]
    assert isinstance(beats, list) and isinstance(poses, list)
    assert isinstance(beats[0], dict) and isinstance(beats[1], dict)
    assert isinstance(poses[1], dict)
    beats[0]["timing"] = {"start": 0, "end": split}
    zero_beat = copy.deepcopy(beats[1])
    assert isinstance(zero_beat, dict)
    zero_beat["acting_beat_id"] = "MORROW-AP001-AB003"
    zero_beat["timing"] = {"start": split, "end": split}
    beats[1]["timing"] = {"start": split, "end": duration}
    beats.insert(1, zero_beat)
    poses[1]["at"] = duration - (1 if unit == "frames" else 0.1)

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.0.acting_beats.1.timing: start "
        f"{split} must be less than end {split}"
    ) in errors


@pytest.mark.parametrize(
    ("unit", "instant"),
    [("frames", 12), ("seconds", 0.5)],
)
def test_animation_plan_requires_nonempty_hold_timing(
    repository_root: Path,
    unit: str,
    instant: int | float,
) -> None:
    payload = valid_animation_plan()
    context = payload["source_context"]
    plans = payload["shot_character_plans"]
    assert isinstance(context, dict) and isinstance(plans, list)
    timing = context["timing"]
    assert isinstance(timing, dict) and isinstance(plans[0], dict)
    timing["unit"] = unit
    timing["frames_per_second"] = 24 if unit == "frames" else None
    holds = plans[0]["holds"]
    assert isinstance(holds, list) and isinstance(holds[0], dict)
    holds[0]["timing"] = {"start": instant, "end": instant}

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.0.holds.0.timing: start "
        f"{instant} must be less than end {instant}"
    ) in errors


def test_animation_plan_allows_adjacent_beats_and_instant_key_pose(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    context = payload["source_context"]
    plans = payload["shot_character_plans"]
    assert isinstance(context, dict) and isinstance(plans, list)
    shots = context["shots"]
    assert isinstance(shots, list) and isinstance(shots[0], dict)
    assert isinstance(plans[0], dict)
    shots[0]["duration"] = 48
    beats = plans[0]["acting_beats"]
    poses = plans[0]["key_poses"]
    assert isinstance(beats, list) and isinstance(poses, list)
    assert isinstance(beats[0], dict) and isinstance(beats[1], dict)
    assert isinstance(poses[1], dict)
    beats[0]["timing"] = {"start": 0, "end": 24}
    beats[1]["timing"] = {"start": 24, "end": 48}
    poses[1]["at"] = 24

    assert validate_artifact("animation-plan", payload, repository_root) == []


def test_animation_plan_rejects_unconfirmed_simulation_certainty(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    simulations = plans[0]["simulations"]
    assert isinstance(simulations, list) and isinstance(simulations[0], dict)
    simulations[0]["certainty"] = "approved"

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.0.simulations.0.certainty: unconfirmed simulation "
        "method must remain assumption, not approved"
    ) in errors


def valid_two_character_animation_plan() -> dict[str, object]:
    payload = copy.deepcopy(valid_animation_plan())
    context = payload["source_context"]
    plans = payload["shot_character_plans"]
    assert isinstance(context, dict) and isinstance(plans, list)
    character_ids = context["character_ids"]
    shots = context["shots"]
    assert isinstance(character_ids, list) and isinstance(shots, list)
    assert isinstance(shots[0], dict) and isinstance(plans[0], dict)
    shot_character_ids = shots[0]["character_ids"]
    performance_intents = shots[0]["performance_intents"]
    supplied_facts = shots[0]["supplied_facts"]
    assert isinstance(shot_character_ids, list)
    assert isinstance(performance_intents, list)
    assert isinstance(supplied_facts, list)
    character_ids.append("MORROW-CH002")
    shot_character_ids.append("MORROW-CH002")
    second_intent = copy.deepcopy(performance_intents[0])
    assert isinstance(second_intent, dict)
    second_intent["intent_id"] = "MORROW-PI002"
    second_intent["character_id"] = "MORROW-CH002"
    performance_intents.append(second_intent)
    for fact in copy.deepcopy(supplied_facts):
        assert isinstance(fact, dict)
        if fact["scope"] == "shot-character":
            fact["character_id"] = "MORROW-CH002"
            supplied_facts.append(fact)
    second_plan = json.loads(
        json.dumps(plans[0])
        .replace("MORROW-AP001", "MORROW-AP002")
        .replace("MORROW-CH001", "MORROW-CH002")
        .replace("MORROW-PI001", "MORROW-PI002")
    )
    plans.append(second_plan)
    return payload


def test_animation_plan_allows_multiple_characters_in_same_shot(
    repository_root: Path,
) -> None:
    assert validate_artifact(
        "animation-plan", valid_two_character_animation_plan(), repository_root
    ) == []


def test_animation_plan_rejects_duplicate_shot_character_plan(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list)
    plans.append(copy.deepcopy(plans[0]))

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.1: duplicate shot-character plan "
        "MORROW-U01-S01-SH001 / MORROW-CH001"
    ) in errors


def test_animation_plan_rejects_source_shot_scene_lineage_error(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    scene_ids = context["scene_ids"]
    shots = context["shots"]
    assert isinstance(scene_ids, list) and isinstance(shots, list)
    assert isinstance(shots[0], dict)
    scene_ids.append("MORROW-U01-S02")
    shots[0]["scene_id"] = "MORROW-U01-S02"

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "source_context.shots.0.scene_id: MORROW-U01-S02 does not match scene "
        "MORROW-U01-S01 encoded by shot MORROW-U01-S01-SH001"
    ) in errors


def test_animation_plan_rejects_plan_scene_lineage_error(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    context = payload["source_context"]
    plans = payload["shot_character_plans"]
    assert isinstance(context, dict) and isinstance(plans, list)
    scene_ids = context["scene_ids"]
    assert isinstance(scene_ids, list) and isinstance(plans[0], dict)
    scene_ids.append("MORROW-U01-S02")
    plans[0]["scene_id"] = "MORROW-U01-S02"

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.0.scene_id: MORROW-U01-S02 does not match "
        "supplied scene MORROW-U01-S01 for shot MORROW-U01-S01-SH001"
    ) in errors


@pytest.mark.parametrize(
    ("binding_name", "binding_value", "expected"),
    [
        (
            "camera_intent_id",
            "MORROW-CI999",
            "shot_character_plans.0.source_bindings.camera_intent_id: "
            "MORROW-CI999 does not bind the supplied camera intent MORROW-CI001",
        ),
        (
            "performance_intent_id",
            "MORROW-PI999",
            "shot_character_plans.0.source_bindings.performance_intent_id: "
            "MORROW-PI999 does not bind supplied performance intent "
            "MORROW-PI001 for MORROW-CH001",
        ),
    ],
)
def test_animation_plan_binds_camera_and_performance_source_intent(
    repository_root: Path,
    binding_name: str,
    binding_value: str,
    expected: str,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    bindings = plans[0]["source_bindings"]
    assert isinstance(bindings, dict)
    bindings[binding_name] = binding_value

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert expected in errors


@pytest.mark.parametrize(
    ("value", "source_reference"),
    [
        ("Use a contradictory handheld orbit.", "arbitrary.txt#unrelated"),
        (
            "Use a contradictory handheld orbit.",
            "shot-list.json#shots/MORROW-U01-S01-SH001",
        ),
        (
            "Do not move the camera; preserve face and hand together.",
            "arbitrary.txt#unrelated",
        ),
    ],
)
def test_animation_plan_supplied_claim_binding_rejects_forged_camera_claim(
    repository_root: Path,
    value: str,
    source_reference: str,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    camera = plans[0]["camera_relationship"]
    assert isinstance(camera, dict) and isinstance(camera["provenance"], dict)
    camera["value"] = value
    camera["provenance"]["source_reference"] = source_reference

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.0.camera_relationship.value: supplied claim must "
        "exactly match value and source_reference declared for shot "
        "MORROW-U01-S01-SH001"
    ) in errors


def test_animation_plan_supplied_claim_binding_rejects_cross_shot_claim(
    repository_root: Path,
) -> None:
    payload = valid_two_shot_animation_plan()
    context = payload["source_context"]
    plans = payload["shot_character_plans"]
    assert isinstance(context, dict) and isinstance(plans, list)
    shots = context["shots"]
    assert isinstance(shots, list)
    for index, label in enumerate(("first", "second")):
        assert isinstance(shots[index], dict) and isinstance(plans[index], dict)
        facts = shots[index]["supplied_facts"]
        camera = plans[index]["camera_relationship"]
        assert isinstance(facts, list) and isinstance(camera, dict)
        camera_fact = next(
            fact for fact in facts if isinstance(fact, dict) and fact["scope"] == "shot"
        )
        camera_fact["value"] = f"Keep the {label} shot locked."
        camera["value"] = camera_fact["value"]
    first_camera = plans[0]["camera_relationship"]
    second_camera = plans[1]["camera_relationship"]
    assert isinstance(first_camera, dict) and isinstance(second_camera, dict)
    assert isinstance(first_camera["provenance"], dict)
    assert isinstance(second_camera["provenance"], dict)
    second_camera["value"] = first_camera["value"]
    second_camera["provenance"]["source_reference"] = first_camera["provenance"][
        "source_reference"
    ]

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.1.camera_relationship.value: supplied claim must "
        "exactly match value and source_reference declared for shot "
        "MORROW-U01-S01-SH002"
    ) in errors


@pytest.mark.parametrize("claim_field", ["action", "performance"])
def test_animation_plan_supplied_claim_binding_rejects_cross_character_claim(
    repository_root: Path,
    claim_field: str,
) -> None:
    payload = valid_two_character_animation_plan()
    context = payload["source_context"]
    plans = payload["shot_character_plans"]
    assert isinstance(context, dict) and isinstance(plans, list)
    shots = context["shots"]
    assert isinstance(shots, list) and isinstance(shots[0], dict)
    facts = shots[0]["supplied_facts"]
    beat = plans[1]["acting_beats"][0]
    assert isinstance(facts, list) and isinstance(beat, dict)
    provenance = beat["provenance"]
    assert isinstance(provenance, dict)
    provenance["status"] = "supplied"
    source_reference = provenance["source_reference"]
    companion = "performance" if claim_field == "action" else "action"
    facts.extend(
        [
            {
                "scope": "shot-character",
                "character_id": "MORROW-CH001",
                "value": beat[claim_field],
                "source_reference": source_reference,
            },
            {
                "scope": "shot-character",
                "character_id": "MORROW-CH002",
                "value": beat[companion],
                "source_reference": source_reference,
            },
        ]
    )

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        f"shot_character_plans.1.acting_beats.0.{claim_field}: supplied claim "
        "must exactly match value and source_reference declared for shot-character "
        "MORROW-U01-S01-SH001 / MORROW-CH002"
    ) in errors


def test_animation_plan_supplied_claim_binding_checks_deeply_nested_claim(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    realism = plans[0]["motion_model"]["physical_realism"]
    assert isinstance(realism, dict) and isinstance(realism["provenance"], dict)
    realism["provenance"]["status"] = "supplied"

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.0.motion_model.physical_realism.value: supplied "
        "claim must exactly match value and source_reference declared for "
        "shot-character MORROW-U01-S01-SH001 / MORROW-CH001"
    ) in errors


def test_animation_plan_supplied_claim_binding_rejects_duplicate_source_fact(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    shots = payload["source_context"]["shots"]
    assert isinstance(shots, list) and isinstance(shots[0], dict)
    facts = shots[0]["supplied_facts"]
    assert isinstance(facts, list)
    facts.append(copy.deepcopy(facts[0]))

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "source_context.shots.0.supplied_facts.8: duplicate supplied fact for "
        "shot-character MORROW-U01-S01-SH001 / MORROW-CH001"
    ) in errors


def test_animation_plan_supplied_claim_binding_accepts_exact_performance_claim(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    shots = payload["source_context"]["shots"]
    plans = payload["shot_character_plans"]
    assert isinstance(shots, list) and isinstance(shots[0], dict)
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    facts = shots[0]["supplied_facts"]
    beat = plans[0]["acting_beats"][0]
    assert isinstance(facts, list) and isinstance(beat, dict)
    provenance = beat["provenance"]
    assert isinstance(provenance, dict)
    provenance["status"] = "supplied"
    for field in ("action", "performance"):
        facts.append(
            {
                "scope": "shot-character",
                "character_id": "MORROW-CH001",
                "value": beat[field],
                "source_reference": provenance["source_reference"],
            }
        )

    assert validate_artifact("animation-plan", payload, repository_root) == []


@pytest.mark.parametrize("status", ["inferred", "proposed"])
def test_animation_plan_supplied_claim_binding_does_not_bind_new_decisions(
    repository_root: Path,
    status: str,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    camera = plans[0]["camera_relationship"]
    assert isinstance(camera, dict) and isinstance(camera["provenance"], dict)
    camera["value"] = "A bounded new camera-coordination interpretation."
    camera["provenance"]["status"] = status
    camera["provenance"]["source_reference"] = "working-notes.json#camera"

    assert validate_artifact("animation-plan", payload, repository_root) == []


@pytest.mark.parametrize("invalid_facts", [{}, [None]])
def test_animation_plan_supplied_claim_binding_malformed_ledger_never_tracebacks(
    repository_root: Path,
    invalid_facts: object,
) -> None:
    payload = valid_animation_plan()
    shots = payload["source_context"]["shots"]
    assert isinstance(shots, list) and isinstance(shots[0], dict)
    shots[0]["supplied_facts"] = invalid_facts

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert errors
    assert all("Traceback" not in error for error in errors)


@pytest.mark.parametrize(
    ("path", "invalid_id", "expected"),
    [
        (
            ("source_context", "character_ids", 0),
            "OTHER-CH001",
            "source_context.character_ids.0: 'OTHER-CH001' must match MORROW-CH###",
        ),
        (
            ("source_context", "scene_ids", 0),
            "OTHER-U01-S01",
            "source_context.scene_ids.0: 'OTHER-U01-S01' must belong to project MORROW",
        ),
        (
            ("source_context", "shots", 0, "shot_id"),
            "OTHER-U01-S01-SH001",
            "source_context.shots.0.shot_id: 'OTHER-U01-S01-SH001' must belong to project MORROW",
        ),
        (
            ("shot_character_plans", 0, "animation_plan_id"),
            "MORROW-AP000",
            "shot_character_plans.0.animation_plan_id: 'MORROW-AP000' must match MORROW-AP###",
        ),
        (
            ("shot_character_plans", 0, "animation_plan_id"),
            "OTHER-AP001",
            "shot_character_plans.0.animation_plan_id: 'OTHER-AP001' must match MORROW-AP###",
        ),
    ],
)
def test_animation_plan_requires_exact_positive_project_ids(
    repository_root: Path,
    path: tuple[str | int, ...],
    invalid_id: str,
    expected: str,
) -> None:
    payload = valid_animation_plan()
    replace_nested_value(payload, path, invalid_id)

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert expected in errors


@pytest.mark.parametrize(
    ("beat_index", "field", "value", "expected"),
    [
        (
            0,
            "start",
            1,
            "shot_character_plans.0.acting_beats: timeline must start at 0, got 1",
        ),
        (
            1,
            "start",
            65,
            "shot_character_plans.0.acting_beats.1.timing.start: 65 must equal previous end 64",
        ),
        (
            1,
            "start",
            63,
            "shot_character_plans.0.acting_beats.1.timing.start: 63 must equal previous end 64",
        ),
        (
            1,
            "end",
            95,
            "shot_character_plans.0.acting_beats: timeline must end at supplied duration 96, got 95",
        ),
        (
            1,
            "end",
            97,
            "shot_character_plans.0.acting_beats.1.timing.end: 97 exceeds supplied duration 96",
        ),
    ],
)
def test_animation_plan_requires_complete_ordered_beat_timeline(
    repository_root: Path,
    beat_index: int,
    field: str,
    value: int,
    expected: str,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    beats = plans[0]["acting_beats"]
    assert isinstance(beats, list) and isinstance(beats[beat_index], dict)
    timing = beats[beat_index]["timing"]
    assert isinstance(timing, dict)
    timing[field] = value

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert expected in errors


def test_animation_plan_key_pose_must_resolve_inside_owning_beat(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    poses = plans[0]["key_poses"]
    assert isinstance(poses, list) and isinstance(poses[0], dict)
    poses[0]["at"] = 64

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.0.key_poses.0.at: 64 must fall inside beat "
        "MORROW-AP001-AB001 interval [0, 64)"
    ) in errors


def test_animation_plan_hold_must_resolve_inside_owning_beat(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    holds = plans[0]["holds"]
    assert isinstance(holds, list) and isinstance(holds[0], dict)
    holds[0]["timing"] = {"start": 0, "end": 65}

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.0.holds.0.timing: interval [0, 65) must fall "
        "inside beat MORROW-AP001-AB001 interval [0, 64)"
    ) in errors


@pytest.mark.parametrize(
    ("collection", "id_field", "invalid_id", "expected_suffix"),
    [
        ("acting_beats", "acting_beat_id", "MORROW-AP002-AB001", "AB###"),
        ("key_poses", "key_pose_id", "MORROW-AP002-KP001", "KP###"),
        ("holds", "hold_id", "MORROW-AP002-HD001", "HD###"),
        ("simulations", "simulation_id", "MORROW-AP002-SM001", "SM###"),
    ],
)
def test_animation_plan_nested_ids_belong_to_owning_plan(
    repository_root: Path,
    collection: str,
    id_field: str,
    invalid_id: str,
    expected_suffix: str,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    records = plans[0][collection]
    assert isinstance(records, list) and isinstance(records[0], dict)
    records[0][id_field] = invalid_id

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        f"shot_character_plans.0.{collection}.0.{id_field}: {invalid_id!r} "
        f"must match MORROW-AP001-{expected_suffix}"
    ) in errors


@pytest.mark.parametrize(
    ("path", "foreign_id", "expected"),
    [
        (
            ("shot_character_plans", 1, "key_poses", 0, "acting_beat_id"),
            "MORROW-AP001-AB001",
            "shot_character_plans.1.key_poses.0.acting_beat_id: beat "
            "MORROW-AP001-AB001 belongs to plan MORROW-AP001, not MORROW-AP002",
        ),
        (
            ("shot_character_plans", 1, "holds", 0, "key_pose_id"),
            "MORROW-AP001-KP001",
            "shot_character_plans.1.holds.0.key_pose_id: pose MORROW-AP001-KP001 "
            "belongs to plan MORROW-AP001, not MORROW-AP002",
        ),
        (
            (
                "shot_character_plans",
                1,
                "continuity",
                "previous_continuity_id",
            ),
            "MORROW-AP001-CT001",
            "shot_character_plans.1.continuity.previous_continuity_id: continuity "
            "MORROW-AP001-CT001 belongs to character MORROW-CH001, not MORROW-CH002",
        ),
    ],
)
def test_animation_plan_rejects_cross_character_graph_links(
    repository_root: Path,
    path: tuple[str | int, ...],
    foreign_id: str,
    expected: str,
) -> None:
    payload = valid_two_character_animation_plan()
    replace_nested_value(payload, path, foreign_id)

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert expected in errors


def test_animation_plan_requires_integral_frame_timing(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    poses = plans[0]["key_poses"]
    assert isinstance(poses, list) and isinstance(poses[0], dict)
    poses[0]["at"] = 0.5

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.0.key_poses.0.at: frame timing must be an integer, "
        "got 0.5"
    ) in errors


def valid_two_shot_animation_plan() -> dict[str, object]:
    payload = copy.deepcopy(valid_animation_plan())
    context = payload["source_context"]
    plans = payload["shot_character_plans"]
    assert isinstance(context, dict) and isinstance(plans, list)
    shots = context["shots"]
    assert isinstance(shots, list) and isinstance(shots[0], dict)
    assert isinstance(plans[0], dict)
    second_shot = json.loads(
        json.dumps(shots[0])
        .replace("MORROW-U01-S01-SH001", "MORROW-U01-S01-SH002")
        .replace("MORROW-CI001", "MORROW-CI002")
        .replace("MORROW-PI001", "MORROW-PI002")
    )
    shots.append(second_shot)
    second_plan = json.loads(
        json.dumps(plans[0])
        .replace("MORROW-U01-S01-SH001", "MORROW-U01-S01-SH002")
        .replace("MORROW-AP001", "MORROW-AP002")
        .replace("MORROW-CI001", "MORROW-CI002")
        .replace("MORROW-PI001", "MORROW-PI002")
    )
    second_continuity = second_plan["continuity"]
    assert isinstance(second_continuity, dict)
    second_continuity["order"] = 2
    second_continuity["previous_continuity_id"] = "MORROW-AP001-CT001"
    plans.append(second_plan)
    return payload


def test_valid_two_shot_animation_plan_passes(repository_root: Path) -> None:
    assert validate_artifact(
        "animation-plan", valid_two_shot_animation_plan(), repository_root
    ) == []


@pytest.mark.parametrize(
    ("path", "unknown_id", "expected"),
    [
        (
            ("shot_character_plans", 0, "key_poses", 0, "acting_beat_id"),
            "MORROW-AP001-AB999",
            "shot_character_plans.0.key_poses.0.acting_beat_id: unknown beat "
            "reference MORROW-AP001-AB999",
        ),
        (
            ("shot_character_plans", 0, "holds", 0, "acting_beat_id"),
            "MORROW-AP001-AB999",
            "shot_character_plans.0.holds.0.acting_beat_id: unknown beat "
            "reference MORROW-AP001-AB999",
        ),
        (
            ("shot_character_plans", 0, "holds", 0, "key_pose_id"),
            "MORROW-AP001-KP999",
            "shot_character_plans.0.holds.0.key_pose_id: unknown pose reference "
            "MORROW-AP001-KP999",
        ),
    ],
)
def test_animation_plan_rejects_dangling_beat_and_pose_references(
    repository_root: Path,
    path: tuple[str | int, ...],
    unknown_id: str,
    expected: str,
) -> None:
    payload = valid_animation_plan()
    replace_nested_value(payload, path, unknown_id)

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert expected in errors


def test_animation_plan_rejects_duplicate_nested_ids(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    poses = plans[0]["key_poses"]
    assert isinstance(poses, list)
    duplicate = copy.deepcopy(poses[0])
    assert isinstance(duplicate, dict)
    duplicate["acting_beat_id"] = "MORROW-AP001-AB002"
    duplicate["at"] = 80
    poses.append(duplicate)

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.0.key_poses.2.key_pose_id: duplicate key pose ID "
        "MORROW-AP001-KP001"
    ) in errors


def test_animation_plan_source_shot_character_must_be_supplied(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    shots = context["shots"]
    assert isinstance(shots, list) and isinstance(shots[0], dict)
    character_ids = shots[0]["character_ids"]
    assert isinstance(character_ids, list)
    character_ids.append("MORROW-CH999")

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "source_context.shots.0.character_ids.1: unknown supplied character "
        "MORROW-CH999"
    ) in errors


def test_animation_plan_requires_performance_intent_for_each_shot_character(
    repository_root: Path,
) -> None:
    payload = valid_two_character_animation_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    shots = context["shots"]
    assert isinstance(shots, list) and isinstance(shots[0], dict)
    intents = shots[0]["performance_intents"]
    assert isinstance(intents, list)
    intents.pop()

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "source_context.shots.0.performance_intents: missing supplied "
        "performance intent for MORROW-CH002"
    ) in errors


def test_animation_plan_character_must_apply_to_supplied_shot(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    context = payload["source_context"]
    plans = payload["shot_character_plans"]
    assert isinstance(context, dict) and isinstance(plans, list)
    character_ids = context["character_ids"]
    assert isinstance(character_ids, list) and isinstance(plans[0], dict)
    character_ids.append("MORROW-CH002")
    plans[0]["character_id"] = "MORROW-CH002"

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.0.character_id: MORROW-CH002 is not declared for "
        "supplied shot MORROW-U01-S01-SH001"
    ) in errors


def test_animation_plan_rejects_nonsequential_continuity_order(
    repository_root: Path,
) -> None:
    payload = valid_two_shot_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[1], dict)
    continuity = plans[1]["continuity"]
    assert isinstance(continuity, dict)
    continuity["order"] = 1

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans: MORROW-CH001 continuity order must be ascending "
        "1..2"
    ) in errors


def test_animation_plan_requires_previous_continuity_transition(
    repository_root: Path,
) -> None:
    payload = valid_two_shot_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[1], dict)
    continuity = plans[1]["continuity"]
    assert isinstance(continuity, dict)
    continuity["previous_continuity_id"] = None

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.1.continuity.previous_continuity_id: continuity "
        "MORROW-AP002-CT001 must follow MORROW-AP001-CT001"
    ) in errors


def test_animation_plan_confirmed_simulation_cannot_use_undetermined_method(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    simulations = plans[0]["simulations"]
    assert isinstance(simulations, list) and isinstance(simulations[0], dict)
    simulations[0]["method_confirmation"] = "confirmed"
    simulations[0]["certainty"] = "confirmed"

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.0.simulations.0.method: undetermined method cannot "
        "be confirmed"
    ) in errors


@pytest.mark.parametrize("subject", ["dialogue_close_up", "nonhuman_creature"])
def test_animation_plan_allows_human_dialogue_and_nonhuman_no_dialogue(
    repository_root: Path,
    subject: str,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    plan = plans[0]
    facial = plan["facial_performance"]
    lip_sync = plan["lip_sync"]
    assert isinstance(facial, dict) and isinstance(lip_sync, dict)
    assert isinstance(facial["intent"], dict)
    assert isinstance(lip_sync["intent"], dict)
    if subject == "dialogue_close_up":
        lip_sync["applicability"] = "specified"
        lip_sync["intent"]["value"] = (
            "Shape the supplied short line clearly while keeping jaw motion small."
        )
    else:
        facial["applicability"] = "not-applicable"
        facial["intent"]["value"] = (
            "No human facial anatomy is supplied; carry attention in head aim and body."
        )
        lip_sync["applicability"] = "not-applicable"
        lip_sync["intent"]["value"] = (
            "The creature has no supplied speech or mouth anatomy to synchronize."
        )
    lip_provenance = lip_sync["intent"]["provenance"]
    assert isinstance(lip_provenance, dict)
    lip_provenance["status"] = "proposed"
    lip_provenance["basis"] = (
        "This test variation makes a bounded subject-appropriate choice."
    )
    lip_provenance["source_reference"] = "working-notes.json#expression"

    assert validate_artifact("animation-plan", payload, repository_root) == []


@pytest.mark.parametrize(
    ("path", "invalid_id", "expected"),
    [
        (
            ("source_context", "shots", 0, "camera_intent", "intent_id"),
            "OTHER-CI001",
            "source_context.shots.0.camera_intent.intent_id: 'OTHER-CI001' "
            "must match MORROW-CI###",
        ),
        (
            (
                "source_context",
                "shots",
                0,
                "performance_intents",
                0,
                "intent_id",
            ),
            "OTHER-PI001",
            "source_context.shots.0.performance_intents.0.intent_id: "
            "'OTHER-PI001' must match MORROW-PI###",
        ),
    ],
)
def test_animation_plan_requires_exact_project_source_intent_ids(
    repository_root: Path,
    path: tuple[str | int, ...],
    invalid_id: str,
    expected: str,
) -> None:
    payload = valid_animation_plan()
    replace_nested_value(payload, path, invalid_id)

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert expected in errors


def test_animation_plan_rejects_duplicate_supplied_shot_id(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    shots = context["shots"]
    assert isinstance(shots, list) and isinstance(shots[0], dict)
    duplicate = copy.deepcopy(shots[0])
    assert isinstance(duplicate, dict)
    camera = duplicate["camera_intent"]
    intents = duplicate["performance_intents"]
    assert isinstance(camera, dict) and isinstance(intents, list)
    assert isinstance(intents[0], dict)
    camera["intent_id"] = "MORROW-CI002"
    intents[0]["intent_id"] = "MORROW-PI002"
    shots.append(duplicate)

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "source_context.shots.1.shot_id: duplicate supplied shot ID "
        "MORROW-U01-S01-SH001"
    ) in errors


def test_animation_plan_source_performance_character_applies_to_shot(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    character_ids = context["character_ids"]
    shots = context["shots"]
    assert isinstance(character_ids, list)
    assert isinstance(shots, list) and isinstance(shots[0], dict)
    intents = shots[0]["performance_intents"]
    assert isinstance(intents, list) and isinstance(intents[0], dict)
    character_ids.append("MORROW-CH002")
    intents[0]["character_id"] = "MORROW-CH002"

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "source_context.shots.0.performance_intents.0.character_id: "
        "MORROW-CH002 is not declared for supplied shot MORROW-U01-S01-SH001"
    ) in errors


@pytest.mark.parametrize(
    "forbidden_value",
    [
        "Fetch motion from https://vendor.example/clip.",
        "Embed data:video/mp4;base64,AAAA for review.",
        "Use api_key=secret-token for the service.",
    ],
)
def test_animation_plan_rejects_urls_credentials_and_encoded_media(
    repository_root: Path,
    forbidden_value: str,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    spacing = plans[0]["spacing"]
    assert isinstance(spacing, dict)
    spacing["value"] = forbidden_value

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.0.spacing.value: forbidden URL, credential, or "
        "encoded-media content"
    ) in errors


@pytest.mark.parametrize(
    ("path", "expected_location"),
    [
        (("shot_character_plans", 0, "spacing"), "shot_character_plans.0.spacing"),
        (
            ("shot_character_plans", 0, "acting_beats", 0),
            "shot_character_plans.0.acting_beats.0",
        ),
    ],
)
def test_animation_plan_requires_uniform_decision_provenance(
    repository_root: Path,
    path: tuple[str | int, ...],
    expected_location: str,
) -> None:
    payload = valid_animation_plan()
    target: object = payload
    for part in path:
        assert isinstance(target, list if isinstance(part, int) else dict)
        target = target[part]
    assert isinstance(target, dict)
    target.pop("provenance")

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert f"{expected_location}: 'provenance' is a required property" in errors


@pytest.mark.parametrize(
    "forbidden_field",
    ["model_parameters", "vendor_parameters", "budget", "schedule", "casting"],
)
def test_animation_plan_rejects_undeclared_operational_fields(
    repository_root: Path,
    forbidden_field: str,
) -> None:
    payload = valid_animation_plan()
    payload[forbidden_field] = "out of scope"

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert any(error.startswith("$:") and forbidden_field in error for error in errors)


@pytest.mark.parametrize(
    ("field", "invalid_shape"),
    [("source_context", []), ("shot_character_plans", [None])],
)
def test_schema_invalid_animation_plan_shapes_never_traceback(
    repository_root: Path,
    field: str,
    invalid_shape: object,
) -> None:
    payload = valid_animation_plan()
    payload[field] = invalid_shape

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert errors
    assert all("Traceback" not in error for error in errors)


def test_deep_animation_plan_shape_never_tracebacks(repository_root: Path) -> None:
    payload = valid_animation_plan()
    nested: dict[str, object] = {}
    cursor = nested
    for _ in range(1200):
        child: dict[str, object] = {}
        cursor["nested"] = child
        cursor = child
    payload["unexpected"] = nested

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert errors
    assert all("Traceback" not in error for error in errors)


def test_malformed_animation_plan_json_never_tracebacks(
    tmp_path: Path,
    repository_root: Path,
) -> None:
    path = tmp_path / "animation-plan.json"
    path.write_text("{broken", encoding="utf-8")

    errors = validate_artifact_file("animation-plan", path, repository_root)

    assert errors and "invalid JSON" in errors[0]
    assert all("Traceback" not in error for error in errors)


def test_animation_plan_template_validates_live_contract(
    repository_root: Path,
) -> None:
    template_path = (
        repository_root
        / ".agents"
        / "skills"
        / "animation-director"
        / "assets"
        / "animation-plan.template.json"
    )
    template = json.loads(template_path.read_text(encoding="utf-8"))

    assert validate_artifact("animation-plan", template, repository_root) == []


def test_animation_plan_source_shot_scene_must_be_supplied(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    shots = context["shots"]
    assert isinstance(shots, list) and isinstance(shots[0], dict)
    shots[0]["scene_id"] = "MORROW-U01-S99"

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "source_context.shots.0.scene_id: unknown supplied scene "
        "MORROW-U01-S99"
    ) in errors


def test_animation_plan_rejects_multiple_performance_intents_for_character(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    shots = context["shots"]
    assert isinstance(shots, list) and isinstance(shots[0], dict)
    intents = shots[0]["performance_intents"]
    assert isinstance(intents, list) and isinstance(intents[0], dict)
    duplicate = copy.deepcopy(intents[0])
    assert isinstance(duplicate, dict)
    duplicate["intent_id"] = "MORROW-PI002"
    intents.append(duplicate)

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "source_context.shots.0.performance_intents.1.character_id: duplicate "
        "supplied performance intent for MORROW-CH001"
    ) in errors


@pytest.mark.parametrize(
    ("path", "value", "expected"),
    [
        (
            ("source_context", "shots", 0, "duration"),
            96.5,
            "source_context.shots.0.duration: frame timing must be an integer, got 96.5",
        ),
        (
            ("shot_character_plans", 0, "acting_beats", 0, "timing", "end"),
            63.5,
            "shot_character_plans.0.acting_beats.0.timing.end: frame timing "
            "must be an integer, got 63.5",
        ),
        (
            ("shot_character_plans", 0, "holds", 0, "timing", "end"),
            11.5,
            "shot_character_plans.0.holds.0.timing.end: frame timing must be "
            "an integer, got 11.5",
        ),
    ],
)
def test_animation_plan_requires_whole_frames_for_all_timing(
    repository_root: Path,
    path: tuple[str | int, ...],
    value: float,
    expected: str,
) -> None:
    payload = valid_animation_plan()
    replace_nested_value(payload, path, value)

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert expected in errors


def test_animation_plan_hold_pose_must_belong_to_same_beat(
    repository_root: Path,
) -> None:
    payload = valid_animation_plan()
    plans = payload["shot_character_plans"]
    assert isinstance(plans, list) and isinstance(plans[0], dict)
    holds = plans[0]["holds"]
    assert isinstance(holds, list) and isinstance(holds[0], dict)
    holds[0]["key_pose_id"] = "MORROW-AP001-KP002"

    errors = validate_artifact("animation-plan", payload, repository_root)

    assert (
        "shot_character_plans.0.holds.0.key_pose_id: pose MORROW-AP001-KP002 "
        "belongs to beat MORROW-AP001-AB002, not MORROW-AP001-AB001"
    ) in errors


def valid_character_look_bible() -> dict[str, object]:
    supplied = {
        "status": "supplied",
        "basis": "The supplied character-arcs context states this identity fact.",
        "source_reference": "character-arcs.json#characters/NINEL-CH001",
    }
    proposed = {
        "status": "proposed",
        "basis": "This bounded treatment makes the supplied identity readable without adding identity facts.",
        "source_reference": "character-arcs.json#characters/NINEL-CH001",
    }
    scene_id = "NINEL-E01-SC001"
    shots = [f"{scene_id}-SH001", f"{scene_id}-SH002"]
    return {
        "schema_version": "2.0",
        "project_id": "NINEL",
        "source_context": {
            "character_ids": ["NINEL-CH001"],
            "scene_ids": [scene_id],
            "shots": [
                {"scene_id": scene_id, "shot_id": shots[0]},
                {"scene_id": scene_id, "shot_id": shots[1]},
            ],
            "identity_statements": [
                {
                    "character_id": "NINEL-CH001",
                    "claim": {
                        "value": "A stranded nonhuman android explorer.",
                        "provenance": supplied,
                    },
                },
                {
                    "character_id": "NINEL-CH001",
                    "claim": {
                        "value": "One triangular sensor inset remains on the right temple.",
                        "provenance": supplied,
                    },
                },
                {
                    "character_id": "NINEL-CH001",
                    "claim": {
                        "value": "The supplied chest seam may change from unlit to cyan-lit.",
                        "provenance": supplied,
                    },
                },
                {
                    "character_id": "NINEL-CH001",
                    "claim": {
                        "value": "Preserve the supplied compact overall build; exact ratios are unknown.",
                        "provenance": supplied,
                    },
                },
                {
                    "character_id": "NINEL-CH001",
                    "claim": {
                        "value": "Nonhuman ceramic shell with three articulated digits on each hand.",
                        "provenance": supplied,
                    },
                },
                {
                    "character_id": "NINEL-CH001",
                    "claim": {
                        "value": "Preserve ceramic shell separation and the supplied cyan chest signal; other colors remain unknown.",
                        "provenance": supplied,
                    },
                },
                {
                    "character_id": "NINEL-CH001",
                    "claim": {
                        "value": "No hair or makeup is established for this nonhuman shell.",
                        "provenance": supplied,
                    },
                },
                {
                    "character_id": "NINEL-CH001",
                    "claim": {
                        "value": "Dormant repose and a controlled right-hand raise are required.",
                        "provenance": supplied,
                    },
                },
                {
                    "character_id": "NINEL-CH001",
                    "claim": {
                        "value": "Do not move, mirror, duplicate, or reshape the right-temple sensor.",
                        "provenance": supplied,
                    },
                },
                {
                    "character_id": "NINEL-CH001",
                    "claim": {
                        "value": "Not applicable to the supplied nonhuman shell.",
                        "provenance": supplied,
                    },
                },
                {
                    "character_id": "NINEL-CH001",
                    "claim": {
                        "value": "The chest seam remains unlit while dormant.",
                        "provenance": supplied,
                    },
                },
                {
                    "character_id": "NINEL-CH001",
                    "claim": {
                        "value": "The chest seam changes to cyan-lit after awakening.",
                        "provenance": supplied,
                    },
                },
            ],
        },
        "characters": [
            {
                "character_id": "NINEL-CH001",
                "name": "Ninel",
                "supplied_identity": {
                    "value": "A stranded nonhuman android explorer.",
                    "provenance": supplied,
                },
                "visual_treatment": {
                    "value": "Keep the supplied shell and sensor readable through restrained shape grouping.",
                    "provenance": proposed,
                },
                "immutable_anchors": [
                    {
                        "anchor_id": "NINEL-CH001-AN001",
                        "aspect": "right-temple sensor",
                        "claim": {
                            "value": "One triangular sensor inset remains on the right temple.",
                            "provenance": supplied,
                        },
                    }
                ],
                "permitted_variations": [
                    {
                        "value": "The supplied chest seam may change from unlit to cyan-lit.",
                        "provenance": supplied,
                    }
                ],
                "proportions": [
                    {
                        "value": "Preserve the supplied compact overall build; exact ratios are unknown.",
                        "provenance": supplied,
                    }
                ],
                "face_body_descriptors": {
                    "applicability": "specified",
                    "details": [
                        {
                            "value": "Nonhuman ceramic shell with three articulated digits on each hand.",
                            "provenance": supplied,
                        }
                    ],
                },
                "silhouette": [
                    {
                        "value": "A compact shell outline remains recognizable at full-body scale.",
                        "provenance": proposed,
                    }
                ],
                "palette": [
                    {
                        "value": "Preserve ceramic shell separation and the supplied cyan chest signal; other colors remain unknown.",
                        "provenance": supplied,
                    }
                ],
                "hair_makeup": {
                    "applicability": "not-applicable",
                    "details": [
                        {
                            "value": "No hair or makeup is established for this nonhuman shell.",
                            "provenance": supplied,
                        }
                    ],
                },
                "expression_range": [
                    {
                        "value": "Use only expression behavior supported by the nonhuman sensor and pose design.",
                        "provenance": proposed,
                    }
                ],
                "pose_range": [
                    {
                        "value": "Dormant repose and a controlled right-hand raise are required.",
                        "provenance": supplied,
                    }
                ],
                "prohibited_drift": [
                    {
                        "drift_id": "NINEL-CH001-DR001",
                        "anchor_ids": ["NINEL-CH001-AN001"],
                        "claim": {
                            "value": "Do not move, mirror, duplicate, or reshape the right-temple sensor.",
                            "provenance": supplied,
                        },
                    }
                ],
            }
        ],
        "continuity_states": [
            {
                "state_id": "NINEL-CH001-ST001",
                "character_id": "NINEL-CH001",
                "order": 1,
                "previous_state_id": None,
                "scene_id": scene_id,
                "shot_ids": [shots[0]],
                "anchor_effects": [
                    {"anchor_id": "NINEL-CH001-AN001", "effect": "preserve"}
                ],
                "wardrobe": {
                    "value": "No wardrobe is supplied in the recovery chamber.",
                    "provenance": {**supplied, "status": "inferred"},
                },
                "hair_makeup": {
                    "value": "Not applicable to the supplied nonhuman shell.",
                    "provenance": supplied,
                },
                "material_surface": {
                    "value": "The ceramic shell is clean; no wear or damage is established.",
                    "provenance": {**supplied, "status": "inferred"},
                },
                "change": {
                    "value": "The chest seam remains unlit while dormant.",
                    "provenance": supplied,
                },
            },
            {
                "state_id": "NINEL-CH001-ST002",
                "character_id": "NINEL-CH001",
                "order": 2,
                "previous_state_id": "NINEL-CH001-ST001",
                "scene_id": scene_id,
                "shot_ids": [shots[1]],
                "anchor_effects": [
                    {"anchor_id": "NINEL-CH001-AN001", "effect": "preserve"}
                ],
                "wardrobe": {
                    "value": "No wardrobe is supplied in the recovery chamber.",
                    "provenance": {**supplied, "status": "inferred"},
                },
                "hair_makeup": {
                    "value": "Not applicable to the supplied nonhuman shell.",
                    "provenance": supplied,
                },
                "material_surface": {
                    "value": "The ceramic shell remains clean and structurally unchanged.",
                    "provenance": {**supplied, "status": "inferred"},
                },
                "change": {
                    "value": "The chest seam changes to cyan-lit after awakening.",
                    "provenance": supplied,
                },
            },
        ],
        "reference_needs": [
            {
                "reference_id": "NINEL-CH001-RF001",
                "character_id": "NINEL-CH001",
                "state_ids": ["NINEL-CH001-ST001", "NINEL-CH001-ST002"],
                "view": "front-turnaround",
                "purpose": {
                    "value": "Confirm the compact silhouette, sensor side, digits, and chest seam states.",
                    "provenance": proposed,
                },
            },
            {
                "reference_id": "NINEL-CH001-RF002",
                "character_id": "NINEL-CH001",
                "state_ids": ["NINEL-CH001-ST001", "NINEL-CH001-ST002"],
                "view": "profile-right",
                "purpose": {
                    "value": "Confirm the supplied right-temple sensor remains on the correct side.",
                    "provenance": proposed,
                },
            },
        ],
        "shot_coverage": [
            {
                "scene_id": scene_id,
                "shot_id": shots[0],
                "character_id": "NINEL-CH001",
                "state_id": "NINEL-CH001-ST001",
                "reference_ids": ["NINEL-CH001-RF001", "NINEL-CH001-RF002"],
            },
            {
                "scene_id": scene_id,
                "shot_id": shots[1],
                "character_id": "NINEL-CH001",
                "state_id": "NINEL-CH001-ST002",
                "reference_ids": ["NINEL-CH001-RF001", "NINEL-CH001-RF002"],
            },
        ],
        "assumptions": ["Exact unsupplied proportions and palette values remain undecided."],
        "uncertainties": ["Additional turnaround angles require approval."],
    }


def valid_live_action_character_look_bible() -> dict[str, object]:
    payload = copy.deepcopy(valid_character_look_bible())
    context = payload["source_context"]
    characters = payload["characters"]
    states = payload["continuity_states"]
    assert isinstance(context, dict) and isinstance(characters, list)
    assert isinstance(characters[0], dict) and isinstance(states, list)
    identity_statements = context["identity_statements"]
    assert isinstance(identity_statements, list) and isinstance(identity_statements[0], dict)
    identity_claim = identity_statements[0]["claim"]
    assert isinstance(identity_claim, dict)
    identity_claim["value"] = "A live-action courier in the supplied navy coat."
    characters[0]["supplied_identity"]["value"] = "A live-action courier in the supplied navy coat."
    characters[0]["visual_treatment"]["value"] = "Keep the supplied coat and hair state readable through restrained shape grouping."
    face_body = characters[0]["face_body_descriptors"]
    hair_makeup = characters[0]["hair_makeup"]
    assert isinstance(face_body, dict) and isinstance(hair_makeup, dict)
    face_body["details"][0]["value"] = "Only the supplied short straight hair and coat silhouette are fixed; other descriptors remain unknown."
    hair_makeup["applicability"] = "specified"
    hair_makeup["details"][0]["value"] = "Keep the supplied short straight dark hair unchanged; makeup is not supplied."
    for state in states:
        assert isinstance(state, dict)
        state["wardrobe"]["value"] = "The supplied navy coat remains fastened with sleeves unrolled."
        state["hair_makeup"]["value"] = "The supplied short straight hair remains unchanged; makeup is not supplied."
        state["material_surface"]["value"] = "The coat remains dry and unworn because no surface change is supplied."
    supplied_replacements = {
        "Nonhuman ceramic shell with three articulated digits on each hand.":
            "Only the supplied short straight hair and coat silhouette are fixed; other descriptors remain unknown.",
        "No hair or makeup is established for this nonhuman shell.":
            "Keep the supplied short straight dark hair unchanged; makeup is not supplied.",
        "Not applicable to the supplied nonhuman shell.":
            "The supplied short straight hair remains unchanged; makeup is not supplied.",
    }
    for statement in identity_statements:
        assert isinstance(statement, dict)
        claim = statement["claim"]
        assert isinstance(claim, dict)
        value = claim["value"]
        if isinstance(value, str) and value in supplied_replacements:
            claim["value"] = supplied_replacements[value]
    return payload


def valid_two_character_look_bible() -> dict[str, object]:
    payload = copy.deepcopy(valid_character_look_bible())
    context = payload["source_context"]
    characters = payload["characters"]
    states = payload["continuity_states"]
    references = payload["reference_needs"]
    coverage = payload["shot_coverage"]
    assert isinstance(context, dict) and isinstance(characters, list)
    assert isinstance(states, list) and isinstance(references, list)
    assert isinstance(coverage, list)
    character_ids = context["character_ids"]
    identity_statements = context["identity_statements"]
    assert isinstance(character_ids, list) and isinstance(identity_statements, list)
    character_ids.append("NINEL-CH002")
    for source_identity in copy.deepcopy(identity_statements):
        serialized_identity = json.dumps(source_identity).replace(
            "NINEL-CH001", "NINEL-CH002"
        ).replace("Ninel", "Mira")
        identity_statements.append(json.loads(serialized_identity))

    second_character = json.loads(
        json.dumps(characters[0])
        .replace("NINEL-CH001", "NINEL-CH002")
        .replace("Ninel", "Mira")
    )
    characters.append(second_character)
    second_state = json.loads(
        json.dumps(states[0])
        .replace("NINEL-CH001", "NINEL-CH002")
        .replace("Ninel", "Mira")
    )
    states.append(second_state)
    for source_reference in copy.deepcopy(references):
        second_reference = json.loads(
            json.dumps(source_reference)
            .replace("NINEL-CH001", "NINEL-CH002")
            .replace("Ninel", "Mira")
        )
        second_reference["state_ids"] = ["NINEL-CH002-ST001"]
        references.append(second_reference)
    coverage.append(
        {
            "scene_id": "NINEL-E01-SC001",
            "shot_id": "NINEL-E01-SC001-SH001",
            "character_id": "NINEL-CH002",
            "state_id": "NINEL-CH002-ST001",
            "reference_ids": ["NINEL-CH002-RF001", "NINEL-CH002-RF002"],
        }
    )
    return payload


def test_valid_animated_nonhuman_character_look_bible_passes(
    repository_root: Path,
) -> None:
    assert validate_artifact(
        "character-look-bible", valid_character_look_bible(), repository_root
    ) == []


def test_valid_live_action_character_look_bible_passes(
    repository_root: Path,
) -> None:
    assert validate_artifact(
        "character-look-bible",
        valid_live_action_character_look_bible(),
        repository_root,
    ) == []


def test_character_look_bible_allows_two_characters_in_same_shot(
    repository_root: Path,
) -> None:
    assert validate_artifact(
        "character-look-bible",
        valid_two_character_look_bible(),
        repository_root,
    ) == []


def _character_look_claim_at(
    payload: dict[str, object], path: tuple[str | int, ...]
) -> dict[str, object]:
    target: object = payload
    for component in path:
        assert isinstance(target, list if isinstance(component, int) else dict)
        target = target[component]
    assert isinstance(target, dict)
    return target


@pytest.mark.parametrize(
    ("path", "expected_location"),
    [
        (("characters", 0, "supplied_identity"), "characters.0.supplied_identity"),
        (
            ("characters", 0, "immutable_anchors", 0, "claim"),
            "characters.0.immutable_anchors.0.claim",
        ),
        (("continuity_states", 1, "change"), "continuity_states.1.change"),
        (("reference_needs", 0, "purpose"), "reference_needs.0.purpose"),
    ],
)
def test_character_look_bible_supplied_claim_binding_rejects_forged_claims(
    repository_root: Path,
    path: tuple[str | int, ...],
    expected_location: str,
) -> None:
    payload = valid_character_look_bible()
    claim = _character_look_claim_at(payload, path)
    claim["value"] = "A wholly invented appearance fact."
    claim["provenance"] = {
        "status": "supplied",
        "basis": "Forged canon regression probe.",
        "source_reference": "arbitrary.txt#unrelated",
    }

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert (
        f"{expected_location}: supplied claim must exactly match a value and "
        "source_reference declared for character NINEL-CH001 in "
        "source_context.identity_statements"
    ) in errors


@pytest.mark.parametrize("mismatch", ["value", "source_reference"])
def test_character_look_bible_supplied_claim_binding_requires_exact_pair(
    repository_root: Path,
    mismatch: str,
) -> None:
    payload = valid_character_look_bible()
    claim = _character_look_claim_at(payload, ("characters", 0, "supplied_identity"))
    if mismatch == "value":
        claim["value"] = "A different value at the correct source reference."
    else:
        provenance = claim["provenance"]
        assert isinstance(provenance, dict)
        claim["provenance"] = {
            **provenance,
            "source_reference": "character-arcs.json#unrelated",
        }

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert (
        "characters.0.supplied_identity: supplied claim must exactly match a "
        "value and source_reference declared for character NINEL-CH001 in "
        "source_context.identity_statements"
    ) in errors


def test_character_look_bible_supplied_claim_binding_rejects_cross_character_match(
    repository_root: Path,
) -> None:
    payload = valid_two_character_look_bible()
    context = payload["source_context"]
    assert isinstance(context, dict)
    statements = context["identity_statements"]
    assert isinstance(statements, list) and isinstance(statements[0], dict)
    statements[0]["character_id"] = "NINEL-CH002"

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert (
        "characters.0.supplied_identity: supplied claim must exactly match a "
        "value and source_reference declared for character NINEL-CH001 in "
        "source_context.identity_statements"
    ) in errors


def test_character_look_bible_supplied_claim_binding_rejects_duplicate_source_pair(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    context = payload["source_context"]
    assert isinstance(context, dict)
    statements = context["identity_statements"]
    assert isinstance(statements, list) and isinstance(statements[0], dict)
    duplicate = copy.deepcopy(statements[0])
    claim = duplicate["claim"]
    assert isinstance(claim, dict)
    provenance = claim["provenance"]
    assert isinstance(provenance, dict)
    provenance["basis"] = "A second declaration of the same exact source pair."
    statements.append(duplicate)

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert (
        "source_context.identity_statements.12.claim: duplicate supplied claim "
        "pair for character NINEL-CH001"
    ) in errors


def test_character_look_bible_supplied_claim_binding_allows_unbound_non_supplied_claims(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    treatment = _character_look_claim_at(payload, ("characters", 0, "visual_treatment"))
    treatment["value"] = "A new bounded rendering proposal."
    material = _character_look_claim_at(payload, ("continuity_states", 0, "material_surface"))
    material["value"] = "A new nonsensitive inference from the scene context."

    assert validate_artifact("character-look-bible", payload, repository_root) == []


@pytest.mark.parametrize(
    ("path", "invalid_shape"),
    [
        (("source_context", "identity_statements", 0, "claim"), []),
        (("continuity_states", 1, "change", "provenance"), []),
    ],
)
def test_character_look_bible_supplied_claim_binding_malformed_shapes_never_traceback(
    repository_root: Path,
    path: tuple[str | int, ...],
    invalid_shape: object,
) -> None:
    payload = valid_character_look_bible()
    target: object = payload
    for component in path[:-1]:
        assert isinstance(target, list if isinstance(component, int) else dict)
        target = target[component]
    final = path[-1]
    assert isinstance(target, list if isinstance(final, int) else dict)
    target[final] = invalid_shape

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert errors
    assert all("Traceback" not in error for error in errors)


def test_character_look_bible_requires_source_context(repository_root: Path) -> None:
    payload = valid_character_look_bible()
    payload.pop("source_context")

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert "$: 'source_context' is a required property" in errors


def test_character_look_bible_rejects_unknown_character(repository_root: Path) -> None:
    payload = valid_character_look_bible()
    characters = payload["characters"]
    assert isinstance(characters, list) and isinstance(characters[0], dict)
    characters[0]["character_id"] = "NINEL-CH999"

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert "characters.0.character_id: unknown supplied character NINEL-CH999" in errors


def test_character_look_bible_rejects_duplicate_state_id(repository_root: Path) -> None:
    payload = valid_character_look_bible()
    states = payload["continuity_states"]
    assert isinstance(states, list) and isinstance(states[0], dict) and isinstance(states[1], dict)
    states[1]["state_id"] = states[0]["state_id"]

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert "continuity_states.1.state_id: duplicate state ID NINEL-CH001-ST001" in errors


def test_character_look_bible_rejects_immutable_anchor_contradiction(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    states = payload["continuity_states"]
    assert isinstance(states, list) and isinstance(states[1], dict)
    effects = states[1]["anchor_effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effects[0]["effect"] = "contradict"

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert (
        "continuity_states.1.anchor_effects.0.effect: immutable anchor "
        "NINEL-CH001-AN001 cannot be contradicted"
    ) in errors


def test_character_look_bible_requires_appearance_claim_provenance(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    characters = payload["characters"]
    assert isinstance(characters, list) and isinstance(characters[0], dict)
    silhouette = characters[0]["silhouette"]
    assert isinstance(silhouette, list) and isinstance(silhouette[0], dict)
    silhouette[0].pop("provenance")

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert "characters.0.silhouette.0: 'provenance' is a required property" in errors


@pytest.mark.parametrize(
    ("path", "invalid_id", "expected"),
    [
        (
            ("characters", 0, "character_id"),
            "NINEL-CH000",
            "characters.0.character_id: 'NINEL-CH000' must match NINEL-CH###",
        ),
        (
            ("characters", 0, "character_id"),
            "OTHER-CH001",
            "characters.0.character_id: 'OTHER-CH001' must match NINEL-CH###",
        ),
        (
            ("characters", 0, "character_id"),
            "NINEL-CH001-extra",
            "characters.0.character_id: 'NINEL-CH001-extra' must match NINEL-CH###",
        ),
        (
            ("characters", 0, "immutable_anchors", 0, "anchor_id"),
            "OTHER-CH001-AN001",
            "characters.0.immutable_anchors.0.anchor_id: 'OTHER-CH001-AN001' must match NINEL-CH###-AN###",
        ),
        (
            ("continuity_states", 0, "state_id"),
            "NINEL-CH001-ST000",
            "continuity_states.0.state_id: 'NINEL-CH001-ST000' must match NINEL-CH###-ST###",
        ),
        (
            ("continuity_states", 0, "state_id"),
            "OTHER-CH001-ST001",
            "continuity_states.0.state_id: 'OTHER-CH001-ST001' must match NINEL-CH###-ST###",
        ),
        (
            ("continuity_states", 0, "state_id"),
            "NINEL-CH001-ST001-extra",
            "continuity_states.0.state_id: 'NINEL-CH001-ST001-extra' must match NINEL-CH###-ST###",
        ),
        (
            ("reference_needs", 0, "reference_id"),
            "OTHER-CH001-RF001",
            "reference_needs.0.reference_id: 'OTHER-CH001-RF001' must match NINEL-CH###-RF###",
        ),
        (
            ("characters", 0, "prohibited_drift", 0, "drift_id"),
            "OTHER-CH001-DR001",
            "characters.0.prohibited_drift.0.drift_id: 'OTHER-CH001-DR001' must match NINEL-CH###-DR###",
        ),
    ],
)
def test_character_look_bible_requires_exact_project_derived_ids(
    repository_root: Path,
    path: tuple[str | int, ...],
    invalid_id: str,
    expected: str,
) -> None:
    payload = valid_character_look_bible()
    replace_nested_value(payload, path, invalid_id)

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert expected in errors


def test_character_look_bible_rejects_duplicate_character_id(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    characters = payload["characters"]
    assert isinstance(characters, list)
    characters.append(copy.deepcopy(characters[0]))

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert "characters.1.character_id: duplicate character ID NINEL-CH001" in errors


def test_character_look_bible_rejects_duplicate_reference_id(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    references = payload["reference_needs"]
    assert isinstance(references, list)
    references.append(copy.deepcopy(references[0]))

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert "reference_needs.2.reference_id: duplicate reference ID NINEL-CH001-RF001" in errors


def test_character_look_bible_rejects_source_shot_scene_lineage_error(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    context = payload["source_context"]
    assert isinstance(context, dict)
    scene_ids = context["scene_ids"]
    shots = context["shots"]
    assert isinstance(scene_ids, list) and isinstance(shots, list)
    assert isinstance(shots[0], dict)
    scene_ids.append("NINEL-E01-SC002")
    shots[0]["scene_id"] = "NINEL-E01-SC002"

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert (
        "source_context.shots.0.scene_id: NINEL-E01-SC002 does not match "
        "scene NINEL-E01-SC001 encoded by shot NINEL-E01-SC001-SH001"
    ) in errors


def test_character_look_bible_rejects_state_shot_scene_lineage_error(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    context = payload["source_context"]
    states = payload["continuity_states"]
    assert isinstance(context, dict) and isinstance(states, list)
    scene_ids = context["scene_ids"]
    assert isinstance(scene_ids, list) and isinstance(states[0], dict)
    scene_ids.append("NINEL-E01-SC002")
    states[0]["scene_id"] = "NINEL-E01-SC002"

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert (
        "continuity_states.0.scene_id: NINEL-E01-SC002 does not match supplied "
        "scene NINEL-E01-SC001 for shot NINEL-E01-SC001-SH001"
    ) in errors


@pytest.mark.parametrize(
    ("path", "unknown_id", "expected"),
    [
        (
            ("continuity_states", 1, "previous_state_id"),
            "NINEL-CH001-ST999",
            "continuity_states.1.previous_state_id: unknown state reference NINEL-CH001-ST999",
        ),
        (
            ("continuity_states", 0, "anchor_effects", 0, "anchor_id"),
            "NINEL-CH001-AN999",
            "continuity_states.0.anchor_effects.0.anchor_id: unknown anchor reference NINEL-CH001-AN999",
        ),
        (
            ("characters", 0, "prohibited_drift", 0, "anchor_ids", 0),
            "NINEL-CH001-AN999",
            "characters.0.prohibited_drift.0.anchor_ids.0: unknown anchor reference NINEL-CH001-AN999",
        ),
        (
            ("reference_needs", 0, "state_ids", 0),
            "NINEL-CH001-ST999",
            "reference_needs.0.state_ids.0: unknown state reference NINEL-CH001-ST999",
        ),
        (
            ("shot_coverage", 0, "state_id"),
            "NINEL-CH001-ST999",
            "shot_coverage.0.state_id: unknown state reference NINEL-CH001-ST999",
        ),
        (
            ("shot_coverage", 0, "reference_ids", 0),
            "NINEL-CH001-RF999",
            "shot_coverage.0.reference_ids.0: unknown reference NINEL-CH001-RF999",
        ),
    ],
)
def test_character_look_bible_rejects_dangling_graph_references(
    repository_root: Path,
    path: tuple[str | int, ...],
    unknown_id: str,
    expected: str,
) -> None:
    payload = valid_character_look_bible()
    replace_nested_value(payload, path, unknown_id)

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert expected in errors


def test_character_look_bible_requires_monotonic_state_order(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    states = payload["continuity_states"]
    assert isinstance(states, list) and isinstance(states[1], dict)
    states[1]["order"] = 1

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert "continuity_states: NINEL-CH001 state order must be ascending 1..2" in errors


def test_character_look_bible_requires_previous_state_transition(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    states = payload["continuity_states"]
    assert isinstance(states, list) and isinstance(states[1], dict)
    states[1]["previous_state_id"] = None

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert (
        "continuity_states.1.previous_state_id: state NINEL-CH001-ST002 must "
        "follow NINEL-CH001-ST001"
    ) in errors


def test_character_look_bible_requires_every_supplied_shot_coverage(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    coverage = payload["shot_coverage"]
    assert isinstance(coverage, list)
    coverage.pop()

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert "shot_coverage: missing supplied shot NINEL-E01-SC001-SH002" in errors


def test_character_look_bible_reference_must_cover_coverage_state(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    references = payload["reference_needs"]
    assert isinstance(references, list) and isinstance(references[0], dict)
    references[0]["state_ids"] = ["NINEL-CH001-ST001"]

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert (
        "shot_coverage.1.reference_ids.0: reference NINEL-CH001-RF001 does not "
        "cover state NINEL-CH001-ST002"
    ) in errors


def test_character_look_bible_requires_front_turnaround_reference(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    references = payload["reference_needs"]
    assert isinstance(references, list) and isinstance(references[0], dict)
    references[0]["view"] = "detail"

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert (
        "reference_needs: character NINEL-CH001 is missing required "
        "front-turnaround coverage"
    ) in errors


@pytest.mark.parametrize(
    ("path", "invalid_id", "expected"),
    [
        (
            ("source_context", "character_ids", 0),
            "OTHER-CH001",
            "source_context.character_ids.0: 'OTHER-CH001' must match NINEL-CH###",
        ),
        (
            ("source_context", "scene_ids", 0),
            "OTHER-E01-SC001",
            "source_context.scene_ids.0: 'OTHER-E01-SC001' must belong to project NINEL",
        ),
        (
            ("source_context", "shots", 0, "shot_id"),
            "OTHER-E01-SC001-SH001",
            "source_context.shots.0.shot_id: 'OTHER-E01-SC001-SH001' must belong to project NINEL",
        ),
        (
            ("characters", 0, "immutable_anchors", 0, "anchor_id"),
            "NINEL-CH002-AN001",
            "characters.0.immutable_anchors.0.anchor_id: NINEL-CH002-AN001 must belong to character NINEL-CH001",
        ),
        (
            ("continuity_states", 0, "state_id"),
            "NINEL-CH002-ST001",
            "continuity_states.0.state_id: NINEL-CH002-ST001 must belong to character NINEL-CH001",
        ),
        (
            ("reference_needs", 0, "reference_id"),
            "NINEL-CH002-RF001",
            "reference_needs.0.reference_id: NINEL-CH002-RF001 must belong to character NINEL-CH001",
        ),
        (
            ("characters", 0, "prohibited_drift", 0, "drift_id"),
            "NINEL-CH002-DR001",
            "characters.0.prohibited_drift.0.drift_id: NINEL-CH002-DR001 must belong to character NINEL-CH001",
        ),
    ],
)
def test_character_look_bible_binds_ids_to_project_and_character(
    repository_root: Path,
    path: tuple[str | int, ...],
    invalid_id: str,
    expected: str,
) -> None:
    payload = valid_character_look_bible()
    replace_nested_value(payload, path, invalid_id)

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert expected in errors


@pytest.mark.parametrize(
    ("path", "unknown_id", "expected"),
    [
        (
            ("source_context", "identity_statements", 0, "character_id"),
            "NINEL-CH999",
            "source_context.identity_statements.0.character_id: unknown supplied character NINEL-CH999",
        ),
        (
            ("continuity_states", 0, "character_id"),
            "NINEL-CH999",
            "continuity_states.0.character_id: unknown character reference NINEL-CH999",
        ),
        (
            ("reference_needs", 0, "character_id"),
            "NINEL-CH999",
            "reference_needs.0.character_id: unknown character reference NINEL-CH999",
        ),
        (
            ("shot_coverage", 0, "character_id"),
            "NINEL-CH999",
            "shot_coverage.0.character_id: unknown character reference NINEL-CH999",
        ),
        (
            ("continuity_states", 0, "scene_id"),
            "NINEL-E01-SC999",
            "continuity_states.0.scene_id: unknown scene reference NINEL-E01-SC999",
        ),
        (
            ("continuity_states", 0, "shot_ids", 0),
            "NINEL-E01-SC001-SH999",
            "continuity_states.0.shot_ids.0: unknown shot reference NINEL-E01-SC001-SH999",
        ),
    ],
)
def test_character_look_bible_rejects_unknown_context_references(
    repository_root: Path,
    path: tuple[str | int, ...],
    unknown_id: str,
    expected: str,
) -> None:
    payload = valid_character_look_bible()
    replace_nested_value(payload, path, unknown_id)

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert expected in errors


def test_character_look_bible_rejects_coverage_scene_lineage_error(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    context = payload["source_context"]
    coverage = payload["shot_coverage"]
    assert isinstance(context, dict) and isinstance(coverage, list)
    scene_ids = context["scene_ids"]
    assert isinstance(scene_ids, list) and isinstance(coverage[0], dict)
    scene_ids.append("NINEL-E01-SC002")
    coverage[0]["scene_id"] = "NINEL-E01-SC002"

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert (
        "shot_coverage.0.scene_id: NINEL-E01-SC002 does not match supplied "
        "scene NINEL-E01-SC001 for shot NINEL-E01-SC001-SH001"
    ) in errors


def test_character_look_bible_rejects_duplicate_shot_coverage(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    coverage = payload["shot_coverage"]
    assert isinstance(coverage, list)
    coverage.append(copy.deepcopy(coverage[0]))

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert (
        "shot_coverage.2.shot_id: duplicate shot coverage "
        "NINEL-E01-SC001-SH001"
    ) in errors


@pytest.mark.parametrize(
    ("path", "foreign_id", "expected"),
    [
        (
            ("characters", 0, "prohibited_drift", 0, "anchor_ids", 0),
            "NINEL-CH002-AN001",
            "characters.0.prohibited_drift.0.anchor_ids.0: anchor NINEL-CH002-AN001 belongs to character NINEL-CH002, not NINEL-CH001",
        ),
        (
            ("continuity_states", 0, "anchor_effects", 0, "anchor_id"),
            "NINEL-CH002-AN001",
            "continuity_states.0.anchor_effects.0.anchor_id: anchor NINEL-CH002-AN001 belongs to character NINEL-CH002, not NINEL-CH001",
        ),
        (
            ("reference_needs", 0, "state_ids", 0),
            "NINEL-CH002-ST001",
            "reference_needs.0.state_ids.0: state NINEL-CH002-ST001 belongs to character NINEL-CH002, not NINEL-CH001",
        ),
        (
            ("shot_coverage", 0, "state_id"),
            "NINEL-CH002-ST001",
            "shot_coverage.0.state_id: state NINEL-CH002-ST001 belongs to character NINEL-CH002, not NINEL-CH001",
        ),
        (
            ("shot_coverage", 0, "reference_ids", 0),
            "NINEL-CH002-RF001",
            "shot_coverage.0.reference_ids.0: reference NINEL-CH002-RF001 belongs to character NINEL-CH002, not NINEL-CH001",
        ),
    ],
)
def test_character_look_bible_rejects_cross_character_graph_links(
    repository_root: Path,
    path: tuple[str | int, ...],
    foreign_id: str,
    expected: str,
) -> None:
    payload = valid_two_character_look_bible()
    replace_nested_value(payload, path, foreign_id)

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert expected in errors


def test_character_look_bible_distinguishes_supplied_identity_from_proposed_treatment(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    characters = payload["characters"]
    assert isinstance(characters, list) and isinstance(characters[0], dict)
    treatment = characters[0]["visual_treatment"]
    assert isinstance(treatment, dict)
    provenance = treatment["provenance"]
    assert isinstance(provenance, dict)
    provenance["status"] = "supplied"

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert (
        "characters.0.visual_treatment.provenance.status: visual treatment "
        "must be proposed, distinct from supplied identity"
    ) in errors


@pytest.mark.parametrize(
    ("category", "unsupported_claim"),
    [
        ("ethnicity", "Ethnicity: invent a specific ethnicity."),
        ("disability", "Disability: invent a mobility disability."),
        ("age", "Age: exactly 42 years old."),
        ("sex/gender", "Gender: invent a woman identity."),
        ("diagnosis", "Diagnosis: invent a medical diagnosis."),
        ("body detail", "Body detail: invent unsupplied anatomy."),
    ],
)
def test_character_look_bible_rejects_unsupported_sensitive_identity_inference(
    repository_root: Path,
    category: str,
    unsupported_claim: str,
) -> None:
    payload = valid_character_look_bible()
    characters = payload["characters"]
    assert isinstance(characters, list) and isinstance(characters[0], dict)
    treatment = characters[0]["visual_treatment"]
    assert isinstance(treatment, dict)
    treatment["value"] = unsupported_claim
    provenance = treatment["provenance"]
    assert isinstance(provenance, dict)
    provenance["status"] = "inferred"

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert (
        "characters.0.visual_treatment.value: unsupported inferred sensitive "
        f"identity category {category!r} absent from source_context.identity_statements"
    ) in errors


@pytest.mark.parametrize(
    ("category", "restrained_claim", "smuggled_inference"),
    [
        (
            "ethnicity",
            "No ethnicity is supplied; no ethnicity is assigned.",
            "Ethnicity is not supplied; infer a specific ethnicity anyway.",
        ),
        (
            "disability",
            "Disability is not supplied and remains unknown.",
            "Disability is not supplied; invent a mobility disability anyway.",
        ),
        (
            "age",
            "Age is not supplied and remains unknown.",
            "Age is unknown; set age to exactly 42 years old anyway.",
        ),
        (
            "sex/gender",
            "Sex and gender are not supplied; neither is assigned.",
            "Gender is not supplied; assign a woman identity anyway.",
        ),
        (
            "diagnosis",
            "No diagnosis is supplied; none is inferred.",
            "Diagnosis is not supplied; infer a medical diagnosis anyway.",
        ),
        (
            "body detail",
            "Human facial and body anatomy categories are not applicable.",
            "Body detail is not supplied; invent anatomy anyway.",
        ),
    ],
)
def test_character_look_bible_allows_restraint_but_rejects_smuggled_sensitive_inference(
    repository_root: Path,
    category: str,
    restrained_claim: str,
    smuggled_inference: str,
) -> None:
    restrained = valid_character_look_bible()
    characters = restrained["characters"]
    assert isinstance(characters, list) and isinstance(characters[0], dict)
    treatment = characters[0]["visual_treatment"]
    assert isinstance(treatment, dict)
    treatment["value"] = restrained_claim

    assert validate_artifact(
        "character-look-bible", restrained, repository_root
    ) == []

    violating = valid_character_look_bible()
    violating_characters = violating["characters"]
    assert isinstance(violating_characters, list)
    assert isinstance(violating_characters[0], dict)
    violating_treatment = violating_characters[0]["visual_treatment"]
    assert isinstance(violating_treatment, dict)
    violating_treatment["value"] = smuggled_inference

    errors = validate_artifact(
        "character-look-bible", violating, repository_root
    )

    assert (
        "characters.0.visual_treatment.value: unsupported proposed sensitive "
        f"identity category {category!r} absent from source_context.identity_statements"
    ) in errors


@pytest.mark.parametrize(
    "forbidden_claim",
    [
        "Use https://vendor.example/secret-reference.",
        "Embed data:image/png;base64,AAAA in the look bible.",
        "Use api_key=secret-token for the renderer.",
    ],
)
def test_character_look_bible_rejects_urls_credentials_and_encoded_media(
    repository_root: Path,
    forbidden_claim: str,
) -> None:
    payload = valid_character_look_bible()
    characters = payload["characters"]
    assert isinstance(characters, list) and isinstance(characters[0], dict)
    treatment = characters[0]["visual_treatment"]
    assert isinstance(treatment, dict)
    treatment["value"] = forbidden_claim

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert (
        "characters.0.visual_treatment.value: forbidden URL, credential, or "
        "encoded-media content"
    ) in errors


@pytest.mark.parametrize(
    ("path", "expected_location"),
    [
        (("characters", 0, "supplied_identity"), "characters.0.supplied_identity"),
        (
            ("characters", 0, "immutable_anchors", 0, "claim"),
            "characters.0.immutable_anchors.0.claim",
        ),
        (("continuity_states", 0, "wardrobe"), "continuity_states.0.wardrobe"),
        (("reference_needs", 0, "purpose"), "reference_needs.0.purpose"),
    ],
)
def test_character_look_bible_requires_uniform_claim_provenance(
    repository_root: Path,
    path: tuple[str | int, ...],
    expected_location: str,
) -> None:
    payload = valid_character_look_bible()
    target: object = payload
    for part in path:
        assert isinstance(target, list if isinstance(part, int) else dict)
        target = target[part]
    assert isinstance(target, dict)
    target.pop("provenance")

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert f"{expected_location}: 'provenance' is a required property" in errors


@pytest.mark.parametrize(
    ("provenance_key", "invalid_value", "expected_fragment"),
    [
        ("status", "guessed", "is not one of"),
        ("basis", "", "should be non-empty"),
        ("source_reference", "", "should be non-empty"),
    ],
)
def test_character_look_bible_rejects_malformed_provenance(
    repository_root: Path,
    provenance_key: str,
    invalid_value: str,
    expected_fragment: str,
) -> None:
    payload = valid_character_look_bible()
    characters = payload["characters"]
    assert isinstance(characters, list) and isinstance(characters[0], dict)
    treatment = characters[0]["visual_treatment"]
    assert isinstance(treatment, dict)
    provenance = treatment["provenance"]
    assert isinstance(provenance, dict)
    provenance[provenance_key] = invalid_value

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert any(
        error.startswith(
            f"characters.0.visual_treatment.provenance.{provenance_key}:"
        )
        and expected_fragment in error
        for error in errors
    )


def test_character_look_bible_requires_asymmetric_anchor_profile_view(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    references = payload["reference_needs"]
    coverage = payload["shot_coverage"]
    assert isinstance(references, list) and isinstance(coverage, list)
    references.pop(1)
    for entry in coverage:
        assert isinstance(entry, dict)
        entry["reference_ids"] = ["NINEL-CH001-RF001"]

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert (
        "reference_needs: character NINEL-CH001 has a right-side immutable "
        "anchor but is missing required profile-right coverage"
    ) in errors


@pytest.mark.parametrize(
    "forbidden_field",
    [
        "media_flags",
        "model_parameters",
        "vendor_parameters",
        "budget",
        "schedule",
        "casting",
        "procurement",
        "legal_decisions",
    ],
)
def test_character_look_bible_rejects_undeclared_operational_fields(
    repository_root: Path,
    forbidden_field: str,
) -> None:
    payload = valid_character_look_bible()
    payload[forbidden_field] = "out of scope"

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert any(
        error.startswith("$:") and forbidden_field in error for error in errors
    )


@pytest.mark.parametrize(
    ("field", "invalid_shape"),
    [
        ("source_context", []),
        ("characters", [None]),
        ("continuity_states", {"not": "a list"}),
        ("reference_needs", [None]),
        ("shot_coverage", [None]),
    ],
)
def test_schema_invalid_character_look_bible_shapes_never_traceback(
    repository_root: Path,
    field: str,
    invalid_shape: object,
) -> None:
    payload = valid_character_look_bible()
    payload[field] = invalid_shape

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert errors
    assert all("Traceback" not in error for error in errors)


def test_deep_character_look_bible_shape_never_tracebacks(
    repository_root: Path,
) -> None:
    payload = valid_character_look_bible()
    nested: dict[str, object] = {}
    cursor = nested
    for _ in range(1200):
        child: dict[str, object] = {}
        cursor["nested"] = child
        cursor = child
    payload["unexpected"] = nested

    errors = validate_artifact("character-look-bible", payload, repository_root)

    assert errors
    assert all("Traceback" not in error for error in errors)


def test_malformed_character_look_bible_json_never_tracebacks(
    tmp_path: Path,
    repository_root: Path,
) -> None:
    path = tmp_path / "character-look-bible.json"
    path.write_text("{broken", encoding="utf-8")

    errors = validate_artifact_file("character-look-bible", path, repository_root)

    assert errors and "invalid JSON" in errors[0]
    assert all("Traceback" not in error for error in errors)


def test_character_look_bible_missing_schema_is_deterministic(tmp_path: Path) -> None:
    errors = validate_artifact(
        "character-look-bible", valid_character_look_bible(), tmp_path
    )

    assert errors == [
        f"schema not found: {tmp_path / 'schemas' / 'character-look-bible.schema.json'}"
    ]


def valid_story_structure() -> dict[str, object]:
    return {
        "schema_version": "2.0",
        "project_id": "NINEL",
        "candidate_models": [
            {
                "name": "Three-Act",
                "fit": "Provides a legible season-scale escalation spine.",
                "benefits": ["Clarifies commitment, crisis, and consequence."],
                "risks": ["A broad middle can flatten episodic variation."],
            },
            {
                "name": "Hero's Journey",
                "fit": "Tests an internal change arc for the continuing explorer.",
                "benefits": ["Frames thresholds and costly choices."],
                "risks": ["A mandatory return would contradict the stranded premise."],
            },
            {
                "name": "Braided serial hybrid",
                "fit": "Alternates the explorer and hive pressures while accumulating consequences.",
                "benefits": ["Supports renewable episode motion and serial reveals."],
                "risks": ["Too many equal threads could diffuse the central question."],
            },
        ],
        "selection_criteria": [
            {
                "criterion": "serialized renewal",
                "brief_evidence": "The project is a series with an expanding threat.",
                "priority": "high",
            },
            {
                "criterion": "protagonist agency",
                "brief_evidence": "The premise centers the explorer's choices while stranded.",
                "priority": "high",
            },
        ],
        "selected_model": "Braided serial hybrid",
        "hybrid_components": [
            {
                "source_model": "Three-Act",
                "component": "commitment, escalation, and consequential resolution",
                "purpose": "Keep the season-scale causal spine legible.",
                "compatibility": "The act turns organize rather than dictate the serial threads.",
            },
            {
                "source_model": "Hero's Journey",
                "component": "threshold choices without a compulsory return",
                "purpose": "Track the explorer's changing relationship to the new world.",
                "compatibility": "The internal turn remains subordinate to the ensemble serial design.",
            },
        ],
        "selection_rationale": "The hybrid best fits a renewable series mystery while preserving causal escalation and protagonist choice.",
        "intentional_deviations": [
            "Do not require a literal return stage while the supplied premise keeps the explorer stranded.",
            "Do not place a cliffhanger at every event; close local questions when earned.",
        ],
        "plotlines": [
            {
                "plotline_id": "NINEL-PL01",
                "title": "The route home",
                "function": "Tests escape against responsibility to the threatened world.",
                "progression": "A repair lead becomes inseparable from the hive's expansion.",
            },
            {
                "plotline_id": "NINEL-PL02",
                "title": "The expanding hive",
                "function": "Supplies accumulating mystery and irreversible external pressure.",
                "progression": "Indirect traces become evidence of adaptive intent.",
            },
        ],
        "sequences": [
            {
                "sequence_id": "NINEL-SQ01",
                "title": "Stranded evidence",
                "purpose": "Bind the escape problem to the first verified hive consequence.",
                "plotline_ids": ["NINEL-PL01", "NINEL-PL02"],
                "event_ids": ["NINEL-EV001", "NINEL-EV002"],
            },
            {
                "sequence_id": "NINEL-SQ02",
                "title": "A larger pattern",
                "purpose": "Turn a local answer into a wider serial question.",
                "plotline_ids": ["NINEL-PL02"],
                "event_ids": ["NINEL-EV003"],
            },
        ],
        "events": [
            {
                "event_id": "NINEL-EV001",
                "order": 1,
                "sequence_id": "NINEL-SQ01",
                "plotline_ids": ["NINEL-PL01"],
                "description": "The explorer's repair scan detects energy beneath the fantasy settlement.",
                "story_function": "setup and orientation",
                "causal_change": "The possible route home gains a physical lead.",
                "retention_effect": "Opens a concrete question without withholding supplied facts.",
            },
            {
                "event_id": "NINEL-EV002",
                "order": 2,
                "sequence_id": "NINEL-SQ01",
                "plotline_ids": ["NINEL-PL01", "NINEL-PL02"],
                "description": "Following the signal exposes damage caused by coordinated burrowing creatures.",
                "story_function": "reveal and escalation",
                "causal_change": "The repair lead and hive threat become causally linked.",
                "retention_effect": "Answers the signal's source while enlarging its implication.",
            },
            {
                "event_id": "NINEL-EV003",
                "order": 3,
                "sequence_id": "NINEL-SQ02",
                "plotline_ids": ["NINEL-PL02"],
                "description": "A contained tunnel responds with a pattern copied from the explorer's scan.",
                "story_function": "reversal",
                "causal_change": "The hive becomes an adaptive intelligence rather than a passive obstacle.",
                "retention_effect": "Creates suspense from a changed threat, not an arbitrary cutoff.",
            },
        ],
        "setup_payoffs": [
            {
                "setup_event_id": "NINEL-EV001",
                "payoff_event_id": "NINEL-EV003",
                "relationship": "The scan pattern is returned by the hive.",
            }
        ],
        "assumptions": ["The three events demonstrate the structure rather than define an episode count."],
        "uncertainties": ["Episode count, runtime, and approved character arc remain unresolved."],
    }


def valid_character_arcs() -> dict[str, object]:
    return {
        "schema_version": "2.0",
        "project_id": "NINEL",
        "characters": [
            {
                "character_id": "NINEL-CH001",
                "name": "Ninel",
                "role": "Stranded android explorer and continuing protagonist.",
                "external_objective": "Find a viable route home before the hive reaches the settlement.",
                "internal_need": "Choose responsibility and belonging rather than treating every bond as a temporary obstacle.",
                "governing_tension": "Efficient escape conflicts with responsibility for people endangered by the same signal.",
                "agency": {
                    "capacity": "Can scan unfamiliar energy and choose which lead to pursue.",
                    "constraints": ["Damaged systems limit independent action."],
                    "choices_under_pressure": [
                        "Follows the repair signal despite the risk that it exposes the settlement."
                    ],
                },
                "values": ["truth", "self-determination", "responsibility"],
                "relationships": [
                    {
                        "target_character_id": "NINEL-CH002",
                        "dynamic": "Ninel treats Argo as a mission partner while Argo demands reciprocal trust.",
                        "arc": "Instrumental cooperation becomes chosen interdependence through costly disclosures.",
                    },
                    {
                        "target_character_id": "NINEL-CH003",
                        "dynamic": "Ninel needs Sera's local knowledge but doubts testimony she cannot scan.",
                        "arc": "Mutual suspicion becomes evidence-tested alliance without erasing disagreement.",
                    },
                ],
                "arc_shape": "positive",
                "turning_event_ids": ["NINEL-EV001", "NINEL-EV002", "NINEL-EV003"],
                "behavioral_evidence": [
                    "At NINEL-EV001, Ninel records the repair lead before asking who lives above it.",
                    "At NINEL-EV003, Ninel shares the copied scan pattern instead of concealing the risk."
                ],
                "contradictions": [
                    "Claims that evidence alone governs decisions, yet withholds data to protect Argo."
                ],
                "endpoint": "Ninel openly commits to stopping the hive before pursuing the route home.",
            },
            {
                "character_id": "NINEL-CH002",
                "name": "Argo",
                "role": "Traveling companion, skeptic, and relational pressure on Ninel's solitary logic.",
                "external_objective": "Keep the group alive while learning whether the hive can track Ninel.",
                "internal_need": "Risk honest dependence instead of disguising fear as constant contingency planning.",
                "governing_tension": "Protective caution can preserve the group or prevent the trust survival requires.",
                "agency": {
                    "capacity": "Reads danger and can challenge or redirect the expedition.",
                    "constraints": ["Cannot verify the hive signal without Ninel's sensors."],
                    "choices_under_pressure": [
                        "Stays at the tunnel after learning that Ninel's scan may have alerted the hive."
                    ],
                },
                "values": ["survival", "loyalty", "candor"],
                "relationships": [
                    {
                        "target_character_id": "NINEL-CH001",
                        "dynamic": "Argo resists being treated as a replaceable escort.",
                        "arc": "Tests Ninel's claims of partnership through decisions with shared risk.",
                    }
                ],
                "arc_shape": "open",
                "turning_event_ids": ["NINEL-EV002", "NINEL-EV003"],
                "behavioral_evidence": [
                    "At NINEL-EV002, Argo blocks retreat long enough for Sera to escape the damaged tunnel."
                ],
                "contradictions": [
                    "Insists that attachment is a liability while repeatedly taking the most exposed watch."
                ],
                "endpoint": "Argo remains wary but asks Ninel for the whole truth before choosing the next route.",
            },
            {
                "character_id": "NINEL-CH003",
                "name": "Sera Vale",
                "role": "Fantasy-world ally whose local obligations make the hive threat concrete.",
                "external_objective": "Protect the settlement's water tunnels from the expanding hive.",
                "internal_need": "Let outsiders contribute without surrendering local accountability.",
                "governing_tension": "Guarding community knowledge conflicts with sharing enough to coordinate a defense.",
                "agency": {
                    "capacity": "Knows the tunnel customs and can grant or deny access.",
                    "constraints": ["The settlement distrusts machines after earlier incursions."],
                    "choices_under_pressure": [
                        "Guides Ninel below ground after the repair signal becomes a public danger."
                    ],
                },
                "values": ["stewardship", "consent", "collective memory"],
                "relationships": [
                    {
                        "target_character_id": "NINEL-CH001",
                        "dynamic": "Sera sees Ninel as both a possible remedy and an unaccountable hazard.",
                        "arc": "Conditional access becomes negotiated responsibility rather than unconditional trust.",
                    }
                ],
                "arc_shape": "flat",
                "turning_event_ids": ["NINEL-EV001", "NINEL-EV003"],
                "behavioral_evidence": [
                    "At NINEL-EV001, Sera refuses secret access and brings the signal before the tunnel keepers."
                ],
                "contradictions": [
                    "Defends shared decisions but privately preserves a map the council ordered destroyed."
                ],
                "endpoint": "Sera keeps her stewardship principle while forcing Ninel and the council to act on it.",
            },
        ],
        "assumptions": [
            "Argo is a continuing traveling companion; species and origin remain unspecified."
        ],
        "uncertainties": [
            "The season endpoint and the ally's approved name require confirmation."
        ],
    }


def valid_world_bible() -> dict[str, object]:
    return {
        "schema_version": "2.0",
        "project_id": "NINEL",
        "scope": {
            "story_boundary": "The frontier settlement, its water tunnels, and the reachable hive margin during the opening serial arc.",
            "scales": ["personal", "settlement", "subterranean network"],
            "excluded_or_unknown": [
                "The wider world's political map is not established.",
                "The hive's total range and population remain unknown.",
            ],
        },
        "locations": [
            {
                "location_id": "NINEL-LO001",
                "name": "Vale Settlement",
                "scale": "A walkable settlement above a managed water-tunnel junction.",
                "story_function": "Makes the hive's expansion a public survival pressure rather than an abstract threat.",
                "material_conditions": [
                    "Water access depends on maintained subterranean channels.",
                    "Local construction must tolerate vibration from the tunnels.",
                ],
                "access_constraints": ["Tunnel access is governed by settlement keepers."],
                "canon_status": "proposal",
                "provenance": "inferred",
                "basis": "The supplied fantasy-world premise and underground threat imply a vulnerable inhabited surface, but its form is not approved.",
            },
            {
                "location_id": "NINEL-LO002",
                "name": "Underground hive",
                "scale": "A subterranean presence whose total range and organization remain unknown.",
                "story_function": "Carries the supplied expanding threat into the story-facing subsurface.",
                "material_conditions": [
                    "The hive is underground.",
                    "The hive is expanding, but no mechanism or rate is supplied.",
                ],
                "access_constraints": ["Access conditions are not supplied."],
                "canon_status": "canon",
                "provenance": "supplied",
                "basis": "The brief directly supplies an expanding underground hive intelligence; no further location detail is asserted.",
            },
        ],
        "factions": [
            {
                "name": "Tunnel Keepers",
                "objective": "Protect settlement water access while controlling hazardous entry.",
                "resources": ["Maintenance knowledge", "Authority over tunnel access"],
                "constraints": ["They cannot observe the entire hive network."],
                "social_consequence": "Access decisions distribute risk and can create conflict between collective safety and Ninel's repair search.",
                "canon_status": "proposal",
                "provenance": "proposed",
                "basis": "A governance response is proposed from the settlement's dependence on tunnels.",
            }
        ],
        "institutions": [
            {
                "name": "Water Council",
                "authority": "Coordinates rationing and approves closures of damaged channels.",
                "dependencies": ["Keeper reports", "Working gates", "Public compliance"],
                "beneficiaries": ["Households with recognized water claims"],
                "burdened_groups": ["Peripheral residents lose access first during closures."],
                "social_consequence": "New hive damage turns technical evidence into a dispute over whose supply is protected.",
                "canon_status": "proposal",
                "provenance": "proposed",
                "basis": "The institution is a causal proposal, not a supplied fact.",
            }
        ],
        "history": [
            {
                "event": "Ninel became stranded in this fantasy world.",
                "legacy": "Repair needs make local materials and knowledge strategically important.",
                "evidence": "Supplied premise; time and cause are unresolved.",
                "canon_status": "canon",
                "provenance": "supplied",
                "basis": "Directly supplied in the project brief.",
            },
            {
                "event": "The settlement previously sealed one unstable water branch.",
                "legacy": "Closure procedures exist but concentrate shortages elsewhere.",
                "evidence": "Proposed history to explain present practice; requires approval.",
                "canon_status": "proposal",
                "provenance": "proposed",
                "basis": "Derived as a possible institutional precedent, not asserted as history.",
            },
        ],
        "cultures": [
            {
                "name": "Vale tunnel stewardship",
                "values": ["Shared survival", "Accountable access"],
                "norms": ["Hazard findings are reported before private excavation."],
                "material_practices": ["Households mark water allocations on replaceable gate tags."],
                "internal_variation": ["Residents disagree about whether outsiders may inspect sealed branches."],
                "social_consequence": "Ninel's private scan conflicts with a norm that treats subterranean knowledge as a shared risk.",
                "canon_status": "proposal",
                "provenance": "proposed",
                "basis": "A local practice is proposed from material dependence; it is not generalized to the whole fantasy world.",
            }
        ],
        "systems": [
            {
                "name": "Android resonance scan",
                "system_type": "technology",
                "inputs": ["Stored power", "A directed scan pulse"],
                "outputs": ["A bounded subsurface resonance pattern"],
                "dependencies": ["Ninel's damaged sensor package"],
                "rule_ids": ["NINEL-WR001", "NINEL-WR003"],
                "canon_status": "proposal",
                "provenance": "proposed",
                "basis": "A constrained technological capability is proposed for the supplied android protagonist.",
            },
            {
                "name": "Living-stone response",
                "system_type": "magic",
                "inputs": ["A shaped mineral surface", "A repeated local resonance"],
                "outputs": ["A temporary visible pattern in the stone"],
                "dependencies": ["Prepared local material"],
                "rule_ids": ["NINEL-WR002", "NINEL-WR003"],
                "canon_status": "proposal",
                "provenance": "proposed",
                "basis": "The fantasy premise supports proposing magic, but no specific mechanism is supplied or approved.",
            },
        ],
        "rules": [
            {
                "rule_id": "NINEL-WR001",
                "name": "Scan expenditure",
                "system_type": "technology",
                "statement": "Ninel can emit a directed pulse that returns a coarse resonance pattern from the reachable subsurface.",
                "cost": "Each scan consumes a measurable share of Ninel's limited stored power.",
                "limit": "The return distinguishes material patterns but does not reveal identity, intention, or a complete map.",
                "contradiction_checks": [
                    {
                        "scenario": "A later scene has one scan identify the hive's motives or map an unobserved network.",
                        "expected_behavior": "The scan returns only bounded material evidence.",
                        "resolution": "Revise the later claim or explicitly approve a changed rule with downstream consequences.",
                    }
                ],
                "provenance": "proposed",
                "canon_status": "proposal",
                "basis": "Proposed power limit; the brief supplies an android but no scan capability.",
                "story_consequence": "Ninel must choose when evidence is worth reducing the power available for repair or escape.",
            },
            {
                "rule_id": "NINEL-WR002",
                "name": "Prepared stone response",
                "system_type": "magic",
                "statement": "Prepared living stone can display a temporary pattern when exposed to a repeated local resonance.",
                "cost": "Preparing the stone consumes scarce treated mineral and keeper labor.",
                "limit": "Unprepared rock and distant signals do not produce a legible response.",
                "contradiction_checks": [
                    {
                        "scenario": "An untreated wall responds at long distance without preparation.",
                        "expected_behavior": "No stable visible pattern appears.",
                        "resolution": "Treat the event as contrary evidence and keep any new mechanism proposed until approved.",
                    }
                ],
                "provenance": "proposed",
                "canon_status": "proposal",
                "basis": "Proposed magic rule; no magic mechanism is supplied.",
                "story_consequence": "The settlement cannot use the effect everywhere and must decide which sites justify scarce preparation.",
            },
            {
                "rule_id": "NINEL-WR003",
                "name": "Cross-system echo",
                "system_type": "hybrid",
                "statement": "A repeated technological pulse can be echoed by prepared living stone without translating its source's intent.",
                "cost": "The echo consumes both scan power and the prepared stone's short-lived responsiveness.",
                "limit": "An echo confirms interaction only; it cannot prove that the hive, the stone, or another actor chose the response.",
                "contradiction_checks": [
                    {
                        "scenario": "Characters treat one echo as proof of the hive's conscious message.",
                        "expected_behavior": "The evidence supports correlation but leaves agency uncertain.",
                        "resolution": "Preserve the uncertainty until a separate event supplies discriminating evidence.",
                    }
                ],
                "provenance": "proposed",
                "canon_status": "proposal",
                "basis": "Proposed interface between the two unapproved systems.",
                "story_consequence": "The same evidence can motivate contact, quarantine, or exploitation, creating conflict without granting certainty.",
            },
        ],
        "terminology": [
            {
                "term": "hive margin",
                "definition": "The nearest observed boundary of coordinated subterranean change, not the hive's total territory.",
                "usage_boundary": "Do not use the term as proof of a central nest, single mind, or mapped perimeter.",
                "canon_status": "proposal",
                "provenance": "inferred",
                "basis": "Working language for bounded evidence.",
            }
        ],
        "production_assets": [
            {
                "asset_id": "NINEL-AS001",
                "name": "Prepared living-stone gate tag",
                "asset_type": "prop",
                "world_function": "Makes water allocation and the proposed magic response visible in action.",
                "production_use": "A repeatable designed prop requiring look, state, and continuity control.",
                "canon_status": "proposal",
                "provenance": "proposed",
                "basis": "Created as a production-facing proposal; it is not approved world canon.",
            }
        ],
        "assumptions": [
            "The opening serial arc remains geographically bounded to one settlement and the observed hive margin."
        ],
        "uncertainties": [
            "No specific magical mechanism, settlement government, or technological capability has been approved.",
            "The hive's organization, motive, range, and material needs remain unknown.",
        ],
    }


def test_valid_world_bible_passes(repository_root: Path) -> None:
    assert validate_artifact("world-bible", valid_world_bible(), repository_root) == []


@pytest.mark.parametrize(
    "required_field",
    ["cost", "limit", "contradiction_checks", "provenance", "story_consequence"],
)
def test_world_bible_requires_complete_rule_contract(
    repository_root: Path, required_field: str
) -> None:
    payload = valid_world_bible()
    rules = payload["rules"]
    assert isinstance(rules, list) and isinstance(rules[0], dict)
    rules[0].pop(required_field)

    errors = validate_artifact("world-bible", payload, repository_root)

    assert any(
        "rules.0" in error
        and required_field in error
        and "required property" in error
        for error in errors
    )


def test_world_bible_rejects_unknown_provenance(repository_root: Path) -> None:
    payload = valid_world_bible()
    rules = payload["rules"]
    assert isinstance(rules, list) and isinstance(rules[0], dict)
    rules[0]["provenance"] = "researched"

    errors = validate_artifact("world-bible", payload, repository_root)

    assert any(
        "rules.0.provenance" in error and "not one of" in error for error in errors
    )


@pytest.mark.parametrize(
    ("collection", "id_field", "duplicate_id"),
    [
        ("locations", "location_id", "NINEL-LO001"),
        ("rules", "rule_id", "NINEL-WR001"),
    ],
)
def test_world_bible_rejects_duplicate_location_and_rule_ids(
    repository_root: Path,
    collection: str,
    id_field: str,
    duplicate_id: str,
) -> None:
    payload = valid_world_bible()
    items = payload[collection]
    assert isinstance(items, list) and len(items) > 1 and isinstance(items[1], dict)
    items[1][id_field] = duplicate_id

    errors = validate_artifact("world-bible", payload, repository_root)

    assert any(
        f"{collection}.1.{id_field}" in error
        and f"duplicate ID {duplicate_id}" in error
        for error in errors
    )


@pytest.mark.parametrize(
    ("collection", "id_field", "invalid_id", "expected_pattern"),
    [
        ("locations", "location_id", "NINEL-LO000", "NINEL-LO###"),
        ("locations", "location_id", "OTHER-LO001", "NINEL-LO###"),
        ("locations", "location_id", "NINEL-LO001-extra", "NINEL-LO###"),
        ("rules", "rule_id", "NINEL-WR000", "NINEL-WR###"),
        ("rules", "rule_id", "OTHER-WR001", "NINEL-WR###"),
        ("rules", "rule_id", "NINEL-WR001\n", "NINEL-WR###"),
        ("production_assets", "asset_id", "NINEL-AS000", "NINEL-AS###"),
        ("production_assets", "asset_id", "OTHER-AS001", "NINEL-AS###"),
        ("production_assets", "asset_id", "NINEL-AS001-extra", "NINEL-AS###"),
    ],
)
def test_world_bible_requires_exact_positive_project_identifiers(
    repository_root: Path,
    collection: str,
    id_field: str,
    invalid_id: str,
    expected_pattern: str,
) -> None:
    payload = valid_world_bible()
    items = payload[collection]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0][id_field] = invalid_id

    errors = validate_artifact("world-bible", payload, repository_root)

    assert any(
        f"{collection}.0.{id_field}" in error
        and f"must match {expected_pattern}" in error
        for error in errors
    )


def test_world_bible_allows_as_ids_only_for_production_assets(
    repository_root: Path,
) -> None:
    payload = valid_world_bible()
    systems = payload["systems"]
    assert isinstance(systems, list) and isinstance(systems[0], dict)
    systems[0]["asset_id"] = "NINEL-AS002"

    errors = validate_artifact("world-bible", payload, repository_root)

    assert any(
        "systems.0" in error and "asset_id" in error and "unexpected" in error
        for error in errors
    )


def test_world_bible_rejects_unknown_system_rule_reference(
    repository_root: Path,
) -> None:
    payload = valid_world_bible()
    systems = payload["systems"]
    assert isinstance(systems, list) and isinstance(systems[0], dict)
    systems[0]["rule_ids"] = ["NINEL-WR999"]

    errors = validate_artifact("world-bible", payload, repository_root)

    assert any(
        "systems.0.rule_ids.0" in error and "unknown rule NINEL-WR999" in error
        for error in errors
    )


@pytest.mark.parametrize("provenance", ["inferred", "proposed"])
def test_world_bible_rejects_unapproved_canon(
    repository_root: Path, provenance: str
) -> None:
    payload = valid_world_bible()
    rules = payload["rules"]
    assert isinstance(rules, list) and isinstance(rules[0], dict)
    rules[0]["canon_status"] = "canon"
    rules[0]["provenance"] = provenance

    errors = validate_artifact("world-bible", payload, repository_root)

    assert any(
        "rules.0.canon_status" in error
        and "canon requires supplied or approved provenance" in error
        for error in errors
    )


@pytest.mark.parametrize("invalid_provenance", [[], {}], ids=["array", "object"])
def test_world_bible_schema_invalid_canon_provenance_returns_diagnostics(
    repository_root: Path, invalid_provenance: object
) -> None:
    payload = valid_world_bible()
    rules = payload["rules"]
    assert isinstance(rules, list) and isinstance(rules[0], dict)
    rules[0]["canon_status"] = "canon"
    rules[0]["provenance"] = invalid_provenance

    errors = validate_artifact("world-bible", payload, repository_root)

    assert any(
        "rules.0.provenance" in error and "not one of" in error
        for error in errors
    )


def test_valid_character_arcs_passes(repository_root: Path) -> None:
    payload = valid_character_arcs()

    assert validate_artifact("character-arcs", payload, repository_root) == []
    assert validate_character_arc_event_references(
        payload, {"NINEL-EV001", "NINEL-EV002", "NINEL-EV003"}
    ) == []


def test_character_arcs_reject_duplicate_character_ids(repository_root: Path) -> None:
    payload = valid_character_arcs()
    characters = payload["characters"]
    assert isinstance(characters, list) and isinstance(characters[1], dict)
    characters[1]["character_id"] = "NINEL-CH001"

    errors = validate_artifact("character-arcs", payload, repository_root)

    assert any(
        "characters.1.character_id" in error and "duplicate ID NINEL-CH001" in error
        for error in errors
    )


def test_character_arcs_reject_unsupported_clinical_diagnosis(
    repository_root: Path,
) -> None:
    payload = valid_character_arcs()
    characters = payload["characters"]
    assert isinstance(characters, list) and isinstance(characters[0], dict)
    characters[0]["clinical_diagnosis"] = "Unsupported diagnostic label"

    errors = validate_artifact("character-arcs", payload, repository_root)

    assert any(
        "characters.0" in error
        and "clinical_diagnosis" in error
        and "unexpected" in error
        for error in errors
    )


def test_character_arcs_reject_unknown_turning_event() -> None:
    payload = valid_character_arcs()
    characters = payload["characters"]
    assert isinstance(characters, list) and isinstance(characters[0], dict)
    characters[0]["turning_event_ids"] = ["NINEL-EV999"]

    errors = validate_character_arc_event_references(
        payload, {"NINEL-EV001", "NINEL-EV002", "NINEL-EV003"}
    )

    assert errors == [
        "characters.0.turning_event_ids.0: unknown event NINEL-EV999"
    ]


def test_character_arcs_reject_undeclared_relationship_target(
    repository_root: Path,
) -> None:
    payload = valid_character_arcs()
    characters = payload["characters"]
    assert isinstance(characters, list) and isinstance(characters[0], dict)
    relationships = characters[0]["relationships"]
    assert isinstance(relationships, list) and isinstance(relationships[0], dict)
    relationships[0]["target_character_id"] = "NINEL-CH999"

    errors = validate_artifact("character-arcs", payload, repository_root)

    assert any(
        "characters.0.relationships.0.target_character_id" in error
        and "unknown character NINEL-CH999" in error
        for error in errors
    )


@pytest.mark.parametrize(
    "invalid_id",
    ["NINEL-CH000", "NINEL-CH001-extra", "OTHER-CH001", "NINEL-CH001\n"],
)
def test_character_arcs_require_exact_positive_project_character_ids(
    repository_root: Path, invalid_id: str
) -> None:
    payload = valid_character_arcs()
    characters = payload["characters"]
    assert isinstance(characters, list) and isinstance(characters[0], dict)
    characters[0]["character_id"] = invalid_id

    errors = validate_artifact("character-arcs", payload, repository_root)

    assert any(
        "characters.0.character_id" in error and "must match NINEL-CH###" in error
        for error in errors
    )


def test_valid_story_structure_passes(repository_root: Path) -> None:
    assert validate_artifact("story-structure", valid_story_structure(), repository_root) == []


def test_story_structure_requires_two_candidate_models(repository_root: Path) -> None:
    payload = valid_story_structure()
    candidates = payload["candidate_models"]
    assert isinstance(candidates, list)
    payload["candidate_models"] = candidates[:1]

    errors = validate_artifact("story-structure", payload, repository_root)

    assert any("candidate_models" in error and "too short" in error for error in errors)


def test_story_structure_rejects_duplicate_event_ids(repository_root: Path) -> None:
    payload = valid_story_structure()
    events = payload["events"]
    assert isinstance(events, list)
    assert isinstance(events[1], dict)
    events[1]["event_id"] = "NINEL-EV001"

    errors = validate_artifact("story-structure", payload, repository_root)

    assert any("events.1.event_id" in error and "duplicate ID NINEL-EV001" in error for error in errors)


def test_story_structure_rejects_event_id_suffix(repository_root: Path) -> None:
    payload = valid_story_structure()
    events = payload["events"]
    assert isinstance(events, list)
    assert isinstance(events[0], dict)
    events[0]["event_id"] = "NINEL-EV001-extra"

    errors = validate_artifact("story-structure", payload, repository_root)

    assert any("events.0.event_id" in error and "must match NINEL-EV###" in error for error in errors)


def test_story_structure_rejects_unknown_payoff_event(repository_root: Path) -> None:
    payload = valid_story_structure()
    pairs = payload["setup_payoffs"]
    assert isinstance(pairs, list)
    assert isinstance(pairs[0], dict)
    pairs[0]["payoff_event_id"] = "NINEL-EV999"

    errors = validate_artifact("story-structure", payload, repository_root)

    assert any("setup_payoffs.0.payoff_event_id" in error and "unknown event NINEL-EV999" in error for error in errors)


@pytest.mark.parametrize(
    ("setup_event_id", "payoff_event_id", "expected"),
    [
        (
            "NINEL-EV001",
            "NINEL-EV001",
            "setup_payoffs.0.payoff_event_id: payoff event NINEL-EV001 must "
            "occur strictly after setup event NINEL-EV001 by declared event order",
        ),
        (
            "NINEL-EV003",
            "NINEL-EV001",
            "setup_payoffs.0.payoff_event_id: payoff event NINEL-EV001 must "
            "occur strictly after setup event NINEL-EV003 by declared event order",
        ),
    ],
    ids=["same-event", "reversed-order"],
)
def test_story_structure_setup_must_strictly_precede_payoff(
    repository_root: Path,
    setup_event_id: str,
    payoff_event_id: str,
    expected: str,
) -> None:
    payload = valid_story_structure()
    pairs = payload["setup_payoffs"]
    assert isinstance(pairs, list) and isinstance(pairs[0], dict)
    pairs[0]["setup_event_id"] = setup_event_id
    pairs[0]["payoff_event_id"] = payoff_event_id

    errors = validate_artifact("story-structure", payload, repository_root)

    assert expected in errors


def test_story_structure_rejects_sequence_id_from_another_project(repository_root: Path) -> None:
    payload = valid_story_structure()
    sequences = payload["sequences"]
    assert isinstance(sequences, list)
    assert isinstance(sequences[0], dict)
    sequences[0]["sequence_id"] = "OTHER-SQ01"

    errors = validate_artifact("story-structure", payload, repository_root)

    assert any("sequences.0.sequence_id" in error and "must match NINEL-SQ##" in error for error in errors)


def test_story_structure_rejects_cross_project_sequence_reference(repository_root: Path) -> None:
    payload = valid_story_structure()
    events = payload["events"]
    assert isinstance(events, list)
    assert isinstance(events[0], dict)
    events[0]["sequence_id"] = "OTHER-SQ01"

    errors = validate_artifact("story-structure", payload, repository_root)

    assert any("events.0.sequence_id" in error and "must match NINEL-SQ##" in error for error in errors)


def test_story_structure_rejects_out_of_order_events(repository_root: Path) -> None:
    payload = valid_story_structure()
    events = payload["events"]
    assert isinstance(events, list)
    assert isinstance(events[0], dict)
    assert isinstance(events[1], dict)
    events[0]["order"] = 2
    events[1]["order"] = 1

    errors = validate_artifact("story-structure", payload, repository_root)

    assert any("events" in error and "ascending order 1..3" in error for error in errors)


def test_story_structure_rejects_undeclared_fields(repository_root: Path) -> None:
    payload = valid_story_structure()
    payload["default_formula"] = "mandatory"

    errors = validate_artifact("story-structure", payload, repository_root)

    assert any("default_formula" in error and "unexpected" in error for error in errors)


def test_story_structure_allows_no_setup_payoff_when_not_applicable(
    repository_root: Path,
) -> None:
    payload = valid_story_structure()
    payload["setup_payoffs"] = []

    assert validate_artifact("story-structure", payload, repository_root) == []


@pytest.mark.parametrize(
    ("collection", "id_field", "zero_id", "start_id"),
    [
        ("plotlines", "plotline_id", "NINEL-PL00", "NINEL-PL01"),
        ("sequences", "sequence_id", "NINEL-SQ00", "NINEL-SQ01"),
        ("events", "event_id", "NINEL-EV000", "NINEL-EV001"),
    ],
)
def test_story_structure_rejects_zero_identifier_suffixes(
    repository_root: Path,
    collection: str,
    id_field: str,
    zero_id: str,
    start_id: str,
) -> None:
    payload = valid_story_structure()
    items = payload[collection]
    assert isinstance(items, list)
    assert isinstance(items[0], dict)
    items[0][id_field] = zero_id

    errors = validate_artifact("story-structure", payload, repository_root)

    assert any(
        f"{collection}.0.{id_field}" in error
        and f"must start with {start_id}" in error
        for error in errors
    )


def test_story_structure_requires_first_declared_id_to_start_at_one(
    repository_root: Path,
) -> None:
    payload = valid_story_structure()
    events = payload["events"]
    assert isinstance(events, list)
    assert isinstance(events[0], dict)
    events[0]["event_id"] = "NINEL-EV004"

    errors = validate_artifact("story-structure", payload, repository_root)

    assert any(
        "events.0.event_id" in error
        and "must start with NINEL-EV001" in error
        for error in errors
    )


def test_story_structure_allows_gaps_after_each_starting_identifier(
    repository_root: Path,
) -> None:
    payload = valid_story_structure()
    plotlines = payload["plotlines"]
    sequences = payload["sequences"]
    events = payload["events"]
    pairs = payload["setup_payoffs"]
    assert isinstance(plotlines, list) and isinstance(plotlines[1], dict)
    assert isinstance(sequences, list) and isinstance(sequences[1], dict)
    assert isinstance(events, list) and isinstance(events[2], dict)
    assert isinstance(pairs, list) and isinstance(pairs[0], dict)

    plotlines[1]["plotline_id"] = "NINEL-PL09"
    sequences[0]["plotline_ids"] = ["NINEL-PL01", "NINEL-PL09"]
    sequences[1]["plotline_ids"] = ["NINEL-PL09"]
    events[1]["plotline_ids"] = ["NINEL-PL01", "NINEL-PL09"]
    events[2]["plotline_ids"] = ["NINEL-PL09"]

    sequences[1]["sequence_id"] = "NINEL-SQ09"
    events[2]["sequence_id"] = "NINEL-SQ09"

    events[2]["event_id"] = "NINEL-EV009"
    sequences[1]["event_ids"] = ["NINEL-EV009"]
    pairs[0]["payoff_event_id"] = "NINEL-EV009"

    assert validate_artifact("story-structure", payload, repository_root) == []


def test_story_structure_rejects_event_missing_from_declared_sequence(
    repository_root: Path,
) -> None:
    payload = valid_story_structure()
    sequences = payload["sequences"]
    assert isinstance(sequences, list)
    assert isinstance(sequences[0], dict)
    sequences[0]["event_ids"] = ["NINEL-EV001"]

    errors = validate_artifact("story-structure", payload, repository_root)

    assert any(
        "events.1.sequence_id" in error
        and "NINEL-EV002 is missing from sequences.0.event_ids" in error
        for error in errors
    )


def test_story_structure_rejects_duplicate_sequence_membership(
    repository_root: Path,
) -> None:
    payload = valid_story_structure()
    sequences = payload["sequences"]
    assert isinstance(sequences, list)
    assert isinstance(sequences[1], dict)
    sequences[1]["event_ids"] = ["NINEL-EV002", "NINEL-EV003"]

    errors = validate_artifact("story-structure", payload, repository_root)

    assert any(
        "sequences.1.event_ids.0" in error
        and "duplicate sequence membership for NINEL-EV002" in error
        for error in errors
    )


def test_story_structure_rejects_sequence_event_back_reference_mismatch(
    repository_root: Path,
) -> None:
    payload = valid_story_structure()
    events = payload["events"]
    assert isinstance(events, list)
    assert isinstance(events[1], dict)
    events[1]["sequence_id"] = "NINEL-SQ02"

    errors = validate_artifact("story-structure", payload, repository_root)

    assert any(
        "sequences.0.event_ids.1" in error
        and "NINEL-EV002 points back to NINEL-SQ02, not NINEL-SQ01" in error
        for error in errors
    )


def test_valid_story_concept_passes(repository_root: Path) -> None:
    assert validate_artifact("story-concept", valid_story_concept(), repository_root) == []


def test_story_concept_accepts_structured_supplied_constraints(
    repository_root: Path,
) -> None:
    payload = valid_story_concept()

    assert validate_artifact("story-concept", payload, repository_root) == []


def test_story_concept_requires_supplied_constraints(repository_root: Path) -> None:
    payload = valid_story_concept()
    payload.pop("supplied_constraints")

    errors = validate_artifact("story-concept", payload, repository_root)

    assert any(
        "supplied_constraints" in error and "required property" in error
        for error in errors
    )


@pytest.mark.parametrize(
    "malformed_constraint",
    [
        {},
        {"statement": "A supplied constraint."},
        {"source_reference": "User brief, sentence 1."},
        {
            "statement": "",
            "source_reference": "User brief, sentence 1.",
        },
        {
            "statement": "A supplied constraint.",
            "source_reference": "",
        },
        {
            "statement": "A supplied constraint.",
            "source_reference": "User brief, sentence 1.",
            "provenance": "supplied",
        },
        "A bare constraint string.",
    ],
    ids=[
        "empty-object",
        "missing-source",
        "missing-statement",
        "empty-statement",
        "empty-source",
        "extra-field",
        "bare-string",
    ],
)
def test_story_concept_rejects_malformed_supplied_constraints(
    repository_root: Path, malformed_constraint: object
) -> None:
    payload = valid_story_concept()
    payload["supplied_constraints"] = [malformed_constraint]

    errors = validate_artifact("story-concept", payload, repository_root)

    assert any("supplied_constraints.0" in error for error in errors)


def test_story_concept_rejects_supplied_constraint_relabelled_as_assumption(
    repository_root: Path,
) -> None:
    payload = valid_story_concept()
    supplied = payload["supplied_constraints"]
    assert isinstance(supplied, list) and isinstance(supplied[0], dict)
    statement = supplied[0]["statement"]
    assert isinstance(statement, str)
    payload["assumptions"] = [statement]

    errors = validate_artifact("story-concept", payload, repository_root)

    assert errors == [
        "assumptions.0: supplied constraint must not be relabeled as an assumption"
    ]


def test_story_concept_requires_audience_promise(repository_root: Path) -> None:
    payload = valid_story_concept()
    payload.pop("audience_promise")

    errors = validate_artifact("story-concept", payload, repository_root)

    assert any("audience_promise" in error and "required property" in error for error in errors)


def test_story_concept_rejects_unknown_project_format(repository_root: Path) -> None:
    payload = valid_story_concept()
    payload["project_format"] = "podcast"

    errors = validate_artifact("story-concept", payload, repository_root)

    assert any("project_format" in error and "not one of" in error for error in errors)


def test_story_concept_rejects_undeclared_fields(repository_root: Path) -> None:
    payload = valid_story_concept()
    payload["market_positioning"] = "Unsupported audience claim."

    errors = validate_artifact("story-concept", payload, repository_root)

    assert any("market_positioning" in error and "unexpected" in error for error in errors)


def test_layer_manifest_requires_ordered_relative_artifacts(
    repository_root: Path,
) -> None:
    payload = {
        "schema_version": "2.0",
        "release_version": "2.0.0",
        "project_id": "NINEL",
        "layer": "story",
        "profile": "story-v2",
        "artifacts": [
            {
                "filename": "story-concept.json",
                "schema_name": "story-concept",
                "schema_version": "2.0",
                "dependency_order": 1,
            }
        ],
        "validation_status": "valid",
        "unresolved_questions": [],
    }

    assert validate_artifact("layer-manifest", payload, repository_root) == []


def test_layer_manifest_rejects_nonpositive_dependency_order(
    repository_root: Path,
) -> None:
    payload = {
        "schema_version": "2.0",
        "release_version": "2.0.0",
        "project_id": "NINEL",
        "layer": "story",
        "profile": "story-v2",
        "artifacts": [
            {
                "filename": "story-concept.json",
                "schema_name": "story-concept",
                "schema_version": "2.0",
                "dependency_order": 0,
            }
        ],
        "validation_status": "valid",
        "unresolved_questions": [],
    }

    errors = validate_artifact("layer-manifest", payload, repository_root)

    assert any(
        "dependency_order" in error and "less than the minimum of 1" in error
        for error in errors
    )


def test_creative_manifest_rejects_parent_traversal(repository_root: Path) -> None:
    payload = valid_creative_manifest()
    layers = payload["layers"]
    assert isinstance(layers, dict)
    layers["story"] = "../story"

    errors = validate_artifact("creative-manifest", payload, repository_root)

    assert any("does not match" in error for error in errors)


@pytest.mark.parametrize("unsafe_path", ["/story", "C:story", r"C:\\story"])
def test_creative_manifest_rejects_explicit_unsafe_path_forms(
    repository_root: Path, unsafe_path: str
) -> None:
    payload = valid_creative_manifest()
    layers = payload["layers"]
    assert isinstance(layers, dict)
    layers["story"] = unsafe_path

    errors = validate_artifact("creative-manifest", payload, repository_root)

    assert any("should not be valid under" in error for error in errors)


def test_creative_manifest_rejects_duplicate_production_modes(
    repository_root: Path,
) -> None:
    payload = valid_creative_manifest()
    payload["production_modes"] = ["ai", "ai"]

    errors = validate_artifact("creative-manifest", payload, repository_root)

    assert any("non-unique elements" in error for error in errors)


def test_valid_shot_list_passes(repository_root: Path) -> None:
    payload = {
        "schema_version": "1.0",
        "scene_id": "S01",
        "assumptions": [],
        "shots": [
            {
                "shot_id": "S01-SH001",
                "beat_ids": ["S01-B01"],
                "size": "medium",
                "angle": "eye-level",
                "lens_mm": 50,
                "camera_support": "tripod",
                "movement": "static",
                "subject": "Ninel",
                "action": "opens her eyes",
                "composition": "centered medium single",
                "dramatic_purpose": "establish disorientation",
                "audio": "low ship hum",
                "continuity": ["screen direction neutral"],
            }
        ],
    }

    assert validate_artifact("shot-list", payload, repository_root) == []


def test_invalid_shot_list_reports_missing_required_fields(repository_root: Path) -> None:
    payload = {"schema_version": "1.0", "scene_id": "S01", "shots": [{}]}

    errors = validate_artifact("shot-list", payload, repository_root)

    assert any("shot_id" in error for error in errors)


def test_validate_artifact_file_reports_invalid_json(tmp_path: Path, repository_root: Path) -> None:
    path = tmp_path / "shot-list.json"
    path.write_text("{broken", encoding="utf-8")

    errors = validate_artifact_file("shot-list", path, repository_root)

    assert errors and "invalid JSON" in errors[0]


@pytest.mark.parametrize(
    ("schema_name", "filename", "path", "location"), ID_FIELD_CASES
)
def test_standalone_id_fields_reject_terminal_newline(
    repository_root: Path,
    schema_name: str,
    filename: str,
    path: tuple[str | int, ...],
    location: str,
) -> None:
    payload = load_ninel_artifact(repository_root, filename)
    target: object = payload
    for component in path:
        assert isinstance(target, (dict, list))
        target = target[component]
    assert isinstance(target, str)
    replace_nested_value(payload, path, f"{target}\n")

    errors = validate_artifact(schema_name, payload, repository_root)

    assert any(location in error for error in errors)


def test_blocking_plan_rejects_empty_beat_reference(repository_root: Path) -> None:
    payload = {
        "schema_version": "1.0",
        "scene_id": "S01",
        "space": "A narrow cabin.",
        "axis": "The bunk-to-door line.",
        "positions": ["Ninel begins in the bunk."],
        "moves": [
            {
                "beat_id": "",
                "character": "Ninel",
                "start": "bunk",
                "end": "seated",
                "motivation": "She wakes.",
            }
        ],
        "continuity_rules": ["Preserve the bunk-to-door axis."],
        "assumptions": [],
    }

    errors = validate_artifact("blocking-plan", payload, repository_root)

    assert any("moves.0.beat_id" in error for error in errors)


def test_camera_movement_plan_rejects_empty_beat_reference(repository_root: Path) -> None:
    payload = {
        "schema_version": "1.0",
        "scene_id": "S01",
        "movement_philosophy": "Let stillness create pressure.",
        "moves": [
            {
                "move_id": "S01-M01",
                "beat_ids": [""],
                "name_ru": "Статичный кадр",
                "name_en": "Static frame",
                "movement": "static",
                "direction": "none",
                "speed": "still",
                "framing": "medium",
                "start": "Ninel asleep",
                "end": "Ninel awake",
                "purpose": "Make the awakening feel observed.",
                "ai_video_prompt": "A still medium shot of Ninel waking.",
            }
        ],
        "assumptions": [],
    }

    errors = validate_artifact("camera-movement-plan", payload, repository_root)

    assert any("moves.0.beat_ids.0" in error for error in errors)


def test_camera_movement_plan_rejects_malformed_move_id(repository_root: Path) -> None:
    payload = {
        "schema_version": "1.0",
        "scene_id": "S01",
        "movement_philosophy": "Let stillness create pressure.",
        "moves": [
            {
                "move_id": "S01-M1",
                "beat_ids": ["S01-B01"],
                "name_ru": "Статичный кадр",
                "name_en": "Static frame",
                "movement": "static",
                "direction": "none",
                "speed": "still",
                "framing": "medium",
                "start": "Ninel asleep",
                "end": "Ninel awake",
                "purpose": "Make the awakening feel observed.",
                "ai_video_prompt": "A still medium shot of Ninel waking.",
            }
        ],
        "assumptions": [],
    }

    errors = validate_artifact("camera-movement-plan", payload, repository_root)

    assert any("moves.0.move_id" in error for error in errors)


def test_shot_list_rejects_empty_beat_reference(repository_root: Path) -> None:
    payload = {
        "schema_version": "1.0",
        "scene_id": "S01",
        "assumptions": [],
        "shots": [
            {
                "shot_id": "S01-SH001",
                "beat_ids": [""],
                "size": "medium",
                "angle": "eye-level",
                "lens_mm": 50,
                "camera_support": "tripod",
                "movement": "static",
                "subject": "Ninel",
                "action": "opens her eyes",
                "composition": "centered medium single",
                "dramatic_purpose": "establish disorientation",
                "audio": "low ship hum",
                "continuity": ["screen direction neutral"],
            }
        ],
    }

    errors = validate_artifact("shot-list", payload, repository_root)

    assert any("shots.0.beat_ids.0" in error for error in errors)


def test_blocking_plan_allows_zero_moves_for_a_static_scene(repository_root: Path) -> None:
    payload = {
        "schema_version": "1.0",
        "scene_id": "S01",
        "space": "A narrow cabin.",
        "axis": "The bunk-to-door line.",
        "positions": ["Ninel begins in the bunk."],
        "moves": [],
        "continuity_rules": ["Preserve the bunk-to-door axis."],
        "assumptions": [],
    }

    assert validate_artifact("blocking-plan", payload, repository_root) == []


def test_camera_movement_plan_allows_zero_moves_for_a_static_scene(
    repository_root: Path,
) -> None:
    payload = {
        "schema_version": "1.0",
        "scene_id": "S01",
        "movement_philosophy": "Let stillness create pressure.",
        "moves": [],
        "assumptions": [],
    }

    assert validate_artifact("camera-movement-plan", payload, repository_root) == []


def valid_visual_language_plan() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "scene_id": "S01",
        "assumptions": ["Focal lengths are full-frame equivalents."],
        "aspect_ratio": "2.00:1",
        "point_of_view": "Stay aligned with Ninel's incomplete perception.",
        "palette": ["charcoal", "desaturated cyan", "muted red-amber"],
        "contrast": "Deep blacks with retained shadow detail.",
        "texture": "Clean optics; condensation is the only organic texture.",
        "lens_strategy": "Move from compressed details to a restrained normal-wide view.",
        "visual_motifs": ["rectilinear machine geometry", "breath on glass"],
        "prohibited_defaults": ["decorative Dutch angles", "unmotivated handheld"],
        "exceptions": ["Break symmetry only when Ninel chooses to act."],
        "rules": [
            {
                "rule_id": "S01-V01",
                "beat_ids": ["S01-B01"],
                "composition": "Center Ninel as a system component before her first choice.",
                "camera_height": "Begin at chamber height and rise only with Ninel.",
                "dramatic_purpose": "Turn a geometric frame into a measure of agency.",
            }
        ],
    }


def test_valid_visual_language_plan_passes(repository_root: Path) -> None:
    assert (
        validate_artifact(
            "visual-language-plan", valid_visual_language_plan(), repository_root
        )
        == []
    )


@pytest.mark.parametrize(
    ("invalid_id", "expected_location"),
    [
        ("S01-alt-V01", "rules.0.rule_id"),
        ("S01-V01\n", "rules.0.rule_id"),
    ],
)
def test_visual_language_plan_rejects_malformed_rule_ids(
    repository_root: Path, invalid_id: str, expected_location: str
) -> None:
    payload = valid_visual_language_plan()
    rules = payload["rules"]
    assert isinstance(rules, list)
    rule = rules[0]
    assert isinstance(rule, dict)
    rule["rule_id"] = invalid_id

    errors = validate_artifact("visual-language-plan", payload, repository_root)

    assert any(expected_location in error for error in errors)


def test_visual_language_plan_rejects_beat_id_from_another_scene_prefix(
    repository_root: Path,
) -> None:
    payload = valid_visual_language_plan()
    rules = payload["rules"]
    assert isinstance(rules, list)
    rule = rules[0]
    assert isinstance(rule, dict)
    rule["beat_ids"] = ["S01-alt-B01"]

    errors = validate_artifact("visual-language-plan", payload, repository_root)

    assert any("rules.0.beat_ids.0" in error and "S01-B##" in error for error in errors)


def test_visual_language_plan_rejects_duplicate_rule_ids(
    repository_root: Path,
) -> None:
    payload = valid_visual_language_plan()
    rules = payload["rules"]
    assert isinstance(rules, list)
    original = rules[0]
    assert isinstance(original, dict)
    rules.append(dict(original))

    errors = validate_artifact("visual-language-plan", payload, repository_root)

    assert any("rules.1.rule_id" in error and "duplicate" in error for error in errors)


@pytest.mark.parametrize("missing_field", ["beat_ids", "dramatic_purpose"])
def test_visual_language_rule_requires_traceable_purpose(
    repository_root: Path, missing_field: str
) -> None:
    payload = valid_visual_language_plan()
    rules = payload["rules"]
    assert isinstance(rules, list)
    rule = rules[0]
    assert isinstance(rule, dict)
    rule.pop(missing_field)

    errors = validate_artifact("visual-language-plan", payload, repository_root)

    assert any(missing_field in error for error in errors)


def valid_lighting_plan() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "scene_id": "S01",
        "assumptions": ["Final fixture package and exposure are confirmed at prelight."],
        "lighting_philosophy": "Let motivated ship sources yield to the planet reveal.",
        "setups": [
            {
                "setup_id": "S01-L01",
                "beat_ids": ["S01-B01"],
                "shot_ids": ["S01-SH001"],
                "environment_time_basis": "Interior medical bay at scripted night; chamber diagnostics and emergency systems are the controlled story sources.",
                "motivation": "A chamber diagnostic source makes breath and frost legible.",
                "sources": ["overhead chamber practical", "flagged frost graze"],
                "direction": "Top-side from camera left, grazing the chamber glass.",
                "quality": "Controlled soft key with a narrow harder frost edge.",
                "color_intent": "Desaturated cool diagnostic light.",
                "exposure_contrast": "Retain shadow geometry and chamber-glass highlights.",
                "control": ["Skirt spill from monitor", "Record level at prelight"],
                "continuity": ["Match frost patch and practical pulse phase"],
                "safety": ["Qualified crew approve rigging and electrical load"],
                "dramatic_purpose": "Make Ninel's first voluntary breath the first stable light change.",
            }
        ],
    }


def test_valid_lighting_plan_passes(repository_root: Path) -> None:
    assert validate_artifact("lighting-plan", valid_lighting_plan(), repository_root) == []


@pytest.mark.parametrize("invalid_id", ["S01-alt-L01", "S01-L01\n"])
def test_lighting_plan_rejects_setup_id_from_wrong_scene_prefix(
    repository_root: Path, invalid_id: str
) -> None:
    payload = valid_lighting_plan()
    setups = payload["setups"]
    assert isinstance(setups, list)
    setup = setups[0]
    assert isinstance(setup, dict)
    setup["setup_id"] = invalid_id

    errors = validate_artifact("lighting-plan", payload, repository_root)

    assert any("setups.0.setup_id" in error and "S01-L##" in error for error in errors)


def test_lighting_plan_rejects_shot_id_from_wrong_scene_prefix(
    repository_root: Path,
) -> None:
    payload = valid_lighting_plan()
    setups = payload["setups"]
    assert isinstance(setups, list)
    setup = setups[0]
    assert isinstance(setup, dict)
    setup["shot_ids"] = ["S01-alt-SH001"]

    errors = validate_artifact("lighting-plan", payload, repository_root)

    assert any("setups.0.shot_ids.0" in error and "S01-SH###" in error for error in errors)


@pytest.mark.parametrize(
    "missing_field",
    ["environment_time_basis", "sources", "safety", "dramatic_purpose"],
)
def test_lighting_setup_requires_executable_safety_and_purpose(
    repository_root: Path, missing_field: str
) -> None:
    payload = valid_lighting_plan()
    setups = payload["setups"]
    assert isinstance(setups, list)
    setup = setups[0]
    assert isinstance(setup, dict)
    setup.pop(missing_field)

    errors = validate_artifact("lighting-plan", payload, repository_root)

    assert any(missing_field in error for error in errors)


def valid_sound_plan() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "scene_id": "S01",
        "assumptions": ["Final microphone and playback choices follow the location survey."],
        "sound_philosophy": "Let the ship feel quiet enough that breath becomes an act of agency.",
        "cues": [
            {
                "cue_id": "S01-A01",
                "beat_ids": ["S01-B01"],
                "shot_ids": ["S01-SH001"],
                "category": "effects",
                "source": "Ninel's voluntary breath and chamber frost movement",
                "perspective": "Close and subjective, aligned with Ninel inside the chamber",
                "timing": "The first clear inhale interrupts the diagnostic countdown",
                "requirement": "Capture clean breath, chamber mechanism, and room tone as separate elements",
                "dramatic_purpose": "Make breath the first sound that belongs to Ninel rather than the ship",
            }
        ],
    }


def test_valid_sound_plan_passes(repository_root: Path) -> None:
    assert validate_artifact("sound-plan", valid_sound_plan(), repository_root) == []


@pytest.mark.parametrize("invalid_id", ["S01-alt-A01", "S01-A01\n"])
def test_sound_plan_rejects_cue_id_from_wrong_scene_prefix(
    repository_root: Path, invalid_id: str
) -> None:
    payload = valid_sound_plan()
    cues = payload["cues"]
    assert isinstance(cues, list)
    cue = cues[0]
    assert isinstance(cue, dict)
    cue["cue_id"] = invalid_id

    errors = validate_artifact("sound-plan", payload, repository_root)

    assert any("cues.0.cue_id" in error and "S01-A##" in error for error in errors)


@pytest.mark.parametrize(
    ("field", "invalid_reference", "expected"),
    [
        ("beat_ids", "S01-alt-B01", "S01-B##"),
        ("shot_ids", "S01-alt-SH001", "S01-SH###"),
    ],
)
def test_sound_plan_rejects_cross_scene_references(
    repository_root: Path, field: str, invalid_reference: str, expected: str
) -> None:
    payload = valid_sound_plan()
    cues = payload["cues"]
    assert isinstance(cues, list)
    cue = cues[0]
    assert isinstance(cue, dict)
    cue[field] = [invalid_reference]

    errors = validate_artifact("sound-plan", payload, repository_root)

    assert any(f"cues.0.{field}.0" in error and expected in error for error in errors)


@pytest.mark.parametrize(
    "missing_field", ["source", "perspective", "timing", "requirement", "dramatic_purpose"]
)
def test_sound_cue_requires_production_and_story_reasoning(
    repository_root: Path, missing_field: str
) -> None:
    payload = valid_sound_plan()
    cues = payload["cues"]
    assert isinstance(cues, list)
    cue = cues[0]
    assert isinstance(cue, dict)
    cue.pop(missing_field)

    errors = validate_artifact("sound-plan", payload, repository_root)

    assert any(missing_field in error for error in errors)


def test_sound_plan_rejects_prescribed_commercial_track(repository_root: Path) -> None:
    payload = valid_sound_plan()
    cues = payload["cues"]
    assert isinstance(cues, list)
    cue = cues[0]
    assert isinstance(cue, dict)
    cue["track_title"] = "A specific copyrighted recording"

    errors = validate_artifact("sound-plan", payload, repository_root)

    assert any("track_title" in error for error in errors)


def valid_storyboard_plan() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "scene_id": "S01",
        "assumptions": ["Panels are textual instructions for a storyboard artist."],
        "storyboard_intent": "Keep the audience inside Ninel's incomplete perception.",
        "panels": [
            {
                "panel_id": "S01-SB001",
                "shot_id": "S01-SH001",
                "moment": "Ninel's eye opens before her first voluntary breath.",
                "framing": "Extreme close detail through chamber glass.",
                "camera_height": "At Ninel's eye height inside the chamber geometry.",
                "angle": "Level and square to the glass.",
                "foreground": "Frost and one hard chamber-glass reflection edge.",
                "midground": "Ninel's eye, lashes, and the first shifting breath trace.",
                "background": "Unresolved darkness inside the chamber.",
                "subject_placement": "Eye held just off center beneath the diagnostic reflection.",
                "action_direction": "Breath disturbance travels laterally across the frost.",
                "movement_state": "Camera slides slowly inward; Ninel remains nearly still.",
                "lighting_note": "Cold diagnostic source retains glass highlight detail.",
                "audio_cue": "Countdown reaches seven as the inhale becomes audible.",
                "continuity_note": "Match the frost patch, eye line, and breath direction to SH002.",
                "dramatic_purpose": "Make voluntary breath the first visible decision.",
            }
        ],
    }


def test_valid_storyboard_plan_passes(repository_root: Path) -> None:
    assert (
        validate_artifact("storyboard-plan", valid_storyboard_plan(), repository_root)
        == []
    )


@pytest.mark.parametrize("invalid_id", ["S01-alt-SB001", "S01-SB001\n"])
def test_storyboard_plan_rejects_panel_id_from_wrong_scene_prefix(
    repository_root: Path, invalid_id: str
) -> None:
    payload = valid_storyboard_plan()
    panels = payload["panels"]
    assert isinstance(panels, list)
    panel = panels[0]
    assert isinstance(panel, dict)
    panel["panel_id"] = invalid_id

    errors = validate_artifact("storyboard-plan", payload, repository_root)

    assert any("panels.0.panel_id" in error and "S01-SB###" in error for error in errors)


def test_storyboard_plan_rejects_cross_scene_shot_reference(
    repository_root: Path,
) -> None:
    payload = valid_storyboard_plan()
    panels = payload["panels"]
    assert isinstance(panels, list)
    panel = panels[0]
    assert isinstance(panel, dict)
    panel["shot_id"] = "S01-alt-SH001"

    errors = validate_artifact("storyboard-plan", payload, repository_root)

    assert any("panels.0.shot_id" in error and "S01-SH###" in error for error in errors)


@pytest.mark.parametrize(
    "missing_field",
    [
        "foreground",
        "midground",
        "background",
        "subject_placement",
        "action_direction",
        "movement_state",
        "continuity_note",
        "dramatic_purpose",
    ],
)
def test_storyboard_panel_requires_drawable_continuity_reasoning(
    repository_root: Path, missing_field: str
) -> None:
    payload = valid_storyboard_plan()
    panels = payload["panels"]
    assert isinstance(panels, list)
    panel = panels[0]
    assert isinstance(panel, dict)
    panel.pop(missing_field)

    errors = validate_artifact("storyboard-plan", payload, repository_root)

    assert any(missing_field in error for error in errors)


@pytest.mark.parametrize("forbidden_field", ["image_url", "image_base64", "prompt"])
def test_storyboard_plan_rejects_embedded_or_generated_image_fields(
    repository_root: Path, forbidden_field: str
) -> None:
    payload = valid_storyboard_plan()
    panels = payload["panels"]
    assert isinstance(panels, list)
    panel = panels[0]
    assert isinstance(panel, dict)
    panel[forbidden_field] = "not allowed"

    errors = validate_artifact("storyboard-plan", payload, repository_root)

    assert any(forbidden_field in error for error in errors)


def valid_production_breakdown() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "scene_id": "S01",
        "assumptions": ["The chamber release method requires department confirmation."],
        "breakdown_scope": "Scene-level requirements traceable to the approved preproduction artifacts.",
        "items": [
            {
                "item_id": "S01-PD001",
                "category": "props",
                "source_basis": "The source scene and S01-SH002 require Ninel to brace on an opening chamber edge.",
                "beat_ids": ["S01-B01", "S01-B02"],
                "shot_ids": ["S01-SH001", "S01-SH002"],
                "requirement": "Provide a repeatable chamber edge and release state that supports the scripted hand contact.",
                "continuity_reset": "Record open/closed state, frost state, and Ninel's right-hand placement for every take.",
                "assumptions": ["Construction and practical-effects teams confirm the final release method."],
                "risk_level": "high",
            }
        ],
    }


def test_valid_production_breakdown_passes(repository_root: Path) -> None:
    assert (
        validate_artifact(
            "production-breakdown", valid_production_breakdown(), repository_root
        )
        == []
    )


@pytest.mark.parametrize("invalid_id", ["S01-alt-PD001", "S01-PD001\n"])
def test_production_breakdown_rejects_item_id_from_wrong_scene_prefix(
    repository_root: Path, invalid_id: str
) -> None:
    payload = valid_production_breakdown()
    items = payload["items"]
    assert isinstance(items, list)
    item = items[0]
    assert isinstance(item, dict)
    item["item_id"] = invalid_id

    errors = validate_artifact("production-breakdown", payload, repository_root)

    assert any("items.0.item_id" in error and "S01-PD###" in error for error in errors)


@pytest.mark.parametrize(
    ("field", "invalid_reference", "expected"),
    [
        ("beat_ids", "S01-alt-B01", "S01-B##"),
        ("shot_ids", "S01-alt-SH001", "S01-SH###"),
    ],
)
def test_production_breakdown_rejects_cross_scene_references(
    repository_root: Path, field: str, invalid_reference: str, expected: str
) -> None:
    payload = valid_production_breakdown()
    items = payload["items"]
    assert isinstance(items, list)
    item = items[0]
    assert isinstance(item, dict)
    item[field] = [invalid_reference]

    errors = validate_artifact("production-breakdown", payload, repository_root)

    assert any(f"items.0.{field}.0" in error and expected in error for error in errors)


@pytest.mark.parametrize(
    "missing_field",
    ["source_basis", "requirement", "continuity_reset", "assumptions", "risk_level"],
)
def test_production_breakdown_item_requires_traceability_and_reset(
    repository_root: Path, missing_field: str
) -> None:
    payload = valid_production_breakdown()
    items = payload["items"]
    assert isinstance(items, list)
    item = items[0]
    assert isinstance(item, dict)
    item.pop(missing_field)

    errors = validate_artifact("production-breakdown", payload, repository_root)

    assert any(missing_field in error for error in errors)


def test_production_breakdown_requires_a_beat_or_shot_reference(
    repository_root: Path,
) -> None:
    payload = valid_production_breakdown()
    items = payload["items"]
    assert isinstance(items, list)
    item = items[0]
    assert isinstance(item, dict)
    item["beat_ids"] = []
    item["shot_ids"] = []

    errors = validate_artifact("production-breakdown", payload, repository_root)

    assert errors


@pytest.mark.parametrize("forbidden_field", ["cost", "price", "vendor", "shoot_date"])
def test_production_breakdown_rejects_budget_and_schedule_fields(
    repository_root: Path, forbidden_field: str
) -> None:
    payload = valid_production_breakdown()
    items = payload["items"]
    assert isinstance(items, list)
    item = items[0]
    assert isinstance(item, dict)
    item[forbidden_field] = "not in scene breakdown scope"

    errors = validate_artifact("production-breakdown", payload, repository_root)

    assert any(forbidden_field in error for error in errors)


def valid_continuity_plan() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "scene_id": "S01",
        "assumptions": ["Take-level photographs and measurements are recorded during photography."],
        "continuity_strategy": "Track Ninel's chosen breath, right hand, eyeline, and axis change as observable states.",
        "items": [
            {
                "continuity_id": "S01-CN001",
                "shot_ids": ["S01-SH002", "S01-SH003"],
                "category": "action",
                "tracked_state": "Ninel's right hand remains planted on the chamber edge while her real head turns away.",
                "required_transition": "The monitor insert begins from the exact head angle and reflection phase established in SH002.",
                "reset_instruction": "Restore hand placement, shoulder angle, head start mark, and monitor state before each paired pass.",
                "severity": "critical",
            }
        ],
    }


def test_valid_continuity_plan_passes(repository_root: Path) -> None:
    assert validate_artifact("continuity-plan", valid_continuity_plan(), repository_root) == []


@pytest.mark.parametrize("invalid_id", ["S01-alt-CN001", "S01-CN001\n"])
def test_continuity_plan_rejects_item_id_from_wrong_scene_prefix(
    repository_root: Path, invalid_id: str
) -> None:
    payload = valid_continuity_plan()
    items = payload["items"]
    assert isinstance(items, list)
    item = items[0]
    assert isinstance(item, dict)
    item["continuity_id"] = invalid_id

    errors = validate_artifact("continuity-plan", payload, repository_root)

    assert any(
        "items.0.continuity_id" in error and "S01-CN###" in error
        for error in errors
    )


def test_continuity_plan_rejects_cross_scene_shot_reference(
    repository_root: Path,
) -> None:
    payload = valid_continuity_plan()
    items = payload["items"]
    assert isinstance(items, list)
    item = items[0]
    assert isinstance(item, dict)
    item["shot_ids"] = ["S01-alt-SH002"]

    errors = validate_artifact("continuity-plan", payload, repository_root)

    assert any("items.0.shot_ids.0" in error and "S01-SH###" in error for error in errors)


@pytest.mark.parametrize(
    "missing_field",
    ["tracked_state", "required_transition", "reset_instruction", "severity"],
)
def test_continuity_item_requires_state_transition_reset_and_severity(
    repository_root: Path, missing_field: str
) -> None:
    payload = valid_continuity_plan()
    items = payload["items"]
    assert isinstance(items, list)
    item = items[0]
    assert isinstance(item, dict)
    item.pop(missing_field)

    errors = validate_artifact("continuity-plan", payload, repository_root)

    assert any(missing_field in error for error in errors)


def test_continuity_plan_rejects_unknown_category(repository_root: Path) -> None:
    payload = valid_continuity_plan()
    items = payload["items"]
    assert isinstance(items, list)
    item = items[0]
    assert isinstance(item, dict)
    item["category"] = "vague"

    errors = validate_artifact("continuity-plan", payload, repository_root)

    assert any("category" in error for error in errors)


def valid_season_arc() -> dict[str, object]:
    return {
        "schema_version": "2.0",
        "project_id": "NINEL",
        "project_format": "series",
        "season_premise": "Ninel's route home becomes inseparable from stopping the hive beneath the settlement.",
        "season_dramatic_question": "Will Ninel choose responsibility for the threatened world over an immediate escape route?",
        "arc_strategy": "A serialized mystery spine drives cumulative change while each episode closes one local objective.",
        "source_plotline_ids": ["NINEL-PL01", "NINEL-PL02", "NINEL-PL03"],
        "source_event_ids": [
            "NINEL-EV001",
            "NINEL-EV002",
            "NINEL-EV003",
            "NINEL-EV004",
            "NINEL-EV005",
            "NINEL-EV006",
        ],
        "source_character_ids": [
            "NINEL-CH001",
            "NINEL-CH002",
            "NINEL-CH003",
        ],
        "episodes": [
            {
                "episode_id": "NINEL-E01",
                "episode_number": 1,
                "title": "The Returned Signal",
                "episode_type": "premiere",
                "episode_premise": "A repair signal draws Ninel and Sera into the damaged water tunnels.",
                "cold_open": {
                    "content": "A dry cistern answers Ninel's dormant scan pattern.",
                    "function": "Orient the local water failure while opening the serial question of recognition.",
                },
                "act_outs": [
                    {
                        "position": "mid-unit turn",
                        "turn": "The repair source is revealed as coordinated burrowing damage.",
                        "pressure": "Ninel's private escape lead becomes a public threat.",
                    }
                ],
                "plot_distribution": [
                    {
                        "slot": "A",
                        "plotline_id": "NINEL-PL01",
                        "event_ids": ["NINEL-EV001"],
                        "episode_engine": "Reach and identify the possible repair source.",
                        "advancement": "The route-home plot gains a physical location and a cost to the settlement.",
                    },
                    {
                        "slot": "B",
                        "plotline_id": "NINEL-PL02",
                        "event_ids": ["NINEL-EV002"],
                        "episode_engine": "Test whether the tunnel damage is coordinated.",
                        "advancement": "The hive changes from rumor to observable organized pressure.",
                    },
                ],
                "local_resolution": "The blocked intake is reopened, but the copied signal remains active.",
                "escalation": "A private anomaly now threatens the settlement's water access.",
                "opening_hook": "Why is a dead cistern transmitting Ninel's scan pattern?",
                "forward_hook": {
                    "target_episode_id": "NINEL-E02",
                    "mechanism": "changed-goal",
                    "promise": "Ninel must trace who copied the scan before using it for repair.",
                },
                "cliffhanger": {
                    "type": "revelation",
                    "turn": "A sealed tunnel repeats the scan after Ninel powers down.",
                    "story_value": "Recognition makes the hive adaptive rather than merely expansive.",
                },
            },
            {
                "episode_id": "NINEL-E02",
                "episode_number": 2,
                "title": "The Narrow Chamber",
                "episode_type": "bottle",
                "episode_premise": "Trapped by a cave-in, the trio must share information the hive can imitate.",
                "cold_open": None,
                "act_outs": [
                    {
                        "position": "late-unit turn",
                        "turn": "Argo learns Ninel withheld evidence that the scan attracts the hive.",
                        "pressure": "Escape now requires cooperation after trust is damaged.",
                    }
                ],
                "plot_distribution": [
                    {
                        "slot": "A",
                        "plotline_id": "NINEL-PL03",
                        "event_ids": ["NINEL-EV003", "NINEL-EV004"],
                        "episode_engine": "Escape a chamber while the hive mimics the group's signals.",
                        "advancement": "Instrumental cooperation becomes a contested demand for reciprocal trust.",
                    },
                    {
                        "slot": "B",
                        "plotline_id": "NINEL-PL02",
                        "event_ids": ["NINEL-EV003"],
                        "episode_engine": "Distinguish echo from adaptive response.",
                        "advancement": "The hive proves it can learn from live behavior.",
                    },
                ],
                "local_resolution": "The trio escapes by sending contradictory signals the hive cannot yet reconcile.",
                "escalation": "The hive advances from copying a scan to testing the group's choices.",
                "opening_hook": "Can the group communicate without teaching the hive how to trap them?",
                "forward_hook": {
                    "target_episode_id": "NINEL-E03",
                    "mechanism": "dilemma",
                    "promise": "Ninel must choose between powering the route home and disabling the learned signal.",
                },
                "cliffhanger": None,
            },
            {
                "episode_id": "NINEL-E03",
                "episode_number": 3,
                "title": "A Door That Listens",
                "episode_type": "finale",
                "episode_premise": "The repair source opens as the hive reaches the settlement foundations.",
                "cold_open": {
                    "content": "The settlement's bells ring from below with no one pulling them.",
                    "function": "Convert the learned pattern into immediate collective danger.",
                },
                "act_outs": [
                    {
                        "position": "finale crisis",
                        "turn": "The route home and the hive relay are revealed as the same mechanism.",
                        "pressure": "Ninel cannot preserve both escape and immediate settlement safety.",
                    }
                ],
                "plot_distribution": [
                    {
                        "slot": "A",
                        "plotline_id": "NINEL-PL01",
                        "event_ids": ["NINEL-EV005", "NINEL-EV006"],
                        "episode_engine": "Choose how to use the route-home mechanism.",
                        "advancement": "Ninel destroys the immediate route rather than amplify the hive relay.",
                    },
                    {
                        "slot": "B",
                        "plotline_id": "NINEL-PL02",
                        "event_ids": ["NINEL-EV006"],
                        "episode_engine": "Redirect the hive long enough to protect the foundations.",
                        "advancement": "The local incursion is stopped while the wider intelligence remains active.",
                    },
                    {
                        "slot": "C",
                        "plotline_id": "NINEL-PL03",
                        "event_ids": ["NINEL-EV005"],
                        "episode_engine": "Restore trust sufficiently for a shared irreversible choice.",
                        "advancement": "Ninel discloses the whole risk and lets Argo and Sera consent to the plan.",
                    },
                ],
                "local_resolution": "The settlement foundations hold and the immediate relay goes silent.",
                "escalation": "Saving the settlement costs Ninel the known route home and exposes a wider network.",
                "opening_hook": "Will opening the route save Ninel or give the hive a path through the settlement?",
                "forward_hook": None,
                "cliffhanger": {
                    "type": "mystery",
                    "turn": "A distant mountain answers after the local relay is destroyed.",
                    "story_value": "The finale closes the local incursion while revealing the threat's larger reach.",
                },
            },
        ],
        "character_progression": [
            {
                "character_id": "NINEL-CH001",
                "episode_ids": ["NINEL-E01", "NINEL-E02", "NINEL-E03"],
                "event_ids": ["NINEL-EV001", "NINEL-EV004", "NINEL-EV006"],
                "progression": "Ninel moves from private escape planning through costly disclosure to a shared protective choice.",
                "endpoint": "Ninel remains stranded by an openly chosen sacrifice rather than accident alone.",
            }
        ],
        "relationship_progression": [
            {
                "character_ids": ["NINEL-CH001", "NINEL-CH002"],
                "episode_ids": ["NINEL-E01", "NINEL-E02", "NINEL-E03"],
                "event_ids": ["NINEL-EV002", "NINEL-EV004", "NINEL-EV005"],
                "progression": "Instrumental partnership fractures over withheld evidence and becomes conditional trust through consent.",
                "endpoint": "Argo accepts shared risk but requires full disclosure before the next expedition.",
            }
        ],
        "reveal_schedule": [
            {
                "event_id": "NINEL-EV002",
                "episode_id": "NINEL-E01",
                "reveal": "The tunnel damage is coordinated.",
                "audience_effect": "Turns an environmental problem into an intelligence question.",
            },
            {
                "event_id": "NINEL-EV005",
                "episode_id": "NINEL-E03",
                "reveal": "The route-home mechanism and hive relay are one system.",
                "audience_effect": "Converts the escape objective into the finale's responsibility dilemma.",
            },
        ],
        "season_setups": [
            {
                "setup_event_id": "NINEL-EV001",
                "episode_id": "NINEL-E01",
                "setup": "The repair scan activates a dormant signal beneath the settlement.",
                "intended_payoff": "The finale identifies the same mechanism as both route and relay.",
            }
        ],
        "finale_payoff": {
            "episode_id": "NINEL-E03",
            "setup_event_ids": ["NINEL-EV001"],
            "payoff_event_ids": ["NINEL-EV005", "NINEL-EV006"],
            "resolution": "Ninel destroys the mechanism introduced by the scan before it can relay the hive through the settlement.",
            "consequence": "The settlement survives, Ninel loses the known route home, and a wider hive network is exposed.",
            "season_question_status": "answered",
        },
        "unresolved_threads": [
            {
                "plotline_id": "NINEL-PL02",
                "state": "The local relay is gone, but distant responses prove the hive remains active.",
                "reason_retained": "Preserves a changed external pressure without undoing the finale's local victory.",
            }
        ],
        "next_season_seeds": [
            {
                "event_id": "NINEL-EV006",
                "seed": "The distant response may identify another relay or an intelligence opposed to the hive.",
                "boundary": "This is a proposal, not proof of a second intelligence or an approved next-season plot.",
            }
        ],
        "assumptions": ["Three episodes demonstrate the contract rather than set the approved season length."],
        "uncertainties": ["The distant response's source and any second-season order remain unconfirmed."],
    }


def test_valid_season_arc_passes(repository_root: Path) -> None:
    assert validate_artifact("season-arc", valid_season_arc(), repository_root) == []


def test_season_arc_is_series_only(repository_root: Path) -> None:
    payload = valid_season_arc()
    payload["project_format"] = "feature"

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any("project_format" in error and "series" in error for error in errors)


def test_season_arc_requires_at_least_two_episodes(repository_root: Path) -> None:
    payload = valid_season_arc()
    episodes = payload["episodes"]
    assert isinstance(episodes, list)
    payload["episodes"] = episodes[:1]

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any("episodes" in error and "too short" in error for error in errors)


@pytest.mark.parametrize(
    "invalid_id",
    ["NINEL-E00", "OTHER-E01", "NINEL-E01-extra", "NINEL-E01\n"],
)
def test_season_arc_requires_exact_positive_project_episode_ids(
    repository_root: Path, invalid_id: str
) -> None:
    payload = valid_season_arc()
    episodes = payload["episodes"]
    assert isinstance(episodes, list)
    episode = episodes[0]
    assert isinstance(episode, dict)
    episode["episode_id"] = invalid_id

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any(
        "episodes.0.episode_id" in error and "NINEL-E##" in error
        for error in errors
    )


def test_season_arc_rejects_duplicate_episode_ids(repository_root: Path) -> None:
    payload = valid_season_arc()
    episodes = payload["episodes"]
    assert isinstance(episodes, list)
    second = episodes[1]
    assert isinstance(second, dict)
    second["episode_id"] = "NINEL-E01"

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any("episodes.1.episode_id" in error and "duplicate" in error for error in errors)


def test_season_arc_episode_id_matches_episode_number(repository_root: Path) -> None:
    payload = valid_season_arc()
    episodes = payload["episodes"]
    assert isinstance(episodes, list)
    first = episodes[0]
    assert isinstance(first, dict)
    first["episode_id"] = "NINEL-E09"

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any(
        "episodes.0.episode_id" in error and "NINEL-E01" in error
        for error in errors
    )


def test_season_arc_rejects_out_of_order_episode_numbers(repository_root: Path) -> None:
    payload = valid_season_arc()
    episodes = payload["episodes"]
    assert isinstance(episodes, list)
    first = episodes[0]
    second = episodes[1]
    assert isinstance(first, dict)
    assert isinstance(second, dict)
    first["episode_number"] = 2
    second["episode_number"] = 1

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any("episodes" in error and "ascending order 1..3" in error for error in errors)


@pytest.mark.parametrize(
    ("field", "invalid_reference", "expected_kind"),
    [
        ("plotline_id", "OTHER-PL01", "plotline"),
        ("event_ids", "NINEL-EV999-extra", "event"),
    ],
)
def test_season_arc_rejects_invalid_plot_distribution_references(
    repository_root: Path,
    field: str,
    invalid_reference: str,
    expected_kind: str,
) -> None:
    payload = valid_season_arc()
    episodes = payload["episodes"]
    assert isinstance(episodes, list)
    episode = episodes[0]
    assert isinstance(episode, dict)
    distribution = episode["plot_distribution"]
    assert isinstance(distribution, list)
    plot = distribution[0]
    assert isinstance(plot, dict)
    plot[field] = [invalid_reference] if field == "event_ids" else invalid_reference

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any(expected_kind in error and "episodes.0.plot_distribution.0" in error for error in errors)


def test_season_arc_requires_each_episode_to_advance_a_plotline(
    repository_root: Path,
) -> None:
    payload = valid_season_arc()
    episodes = payload["episodes"]
    assert isinstance(episodes, list)
    episode = episodes[1]
    assert isinstance(episode, dict)
    episode["plot_distribution"] = []

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any("episodes.1.plot_distribution" in error and "too short" in error for error in errors)


def test_season_arc_requires_an_a_plot_in_every_episode(repository_root: Path) -> None:
    payload = valid_season_arc()
    episodes = payload["episodes"]
    assert isinstance(episodes, list)
    episode = episodes[1]
    assert isinstance(episode, dict)
    distribution = episode["plot_distribution"]
    assert isinstance(distribution, list)
    plot = distribution[0]
    assert isinstance(plot, dict)
    plot["slot"] = "C"

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any("episodes.1.plot_distribution" in error and "A plot" in error for error in errors)


def test_season_arc_rejects_duplicate_plot_slots(repository_root: Path) -> None:
    payload = valid_season_arc()
    episodes = payload["episodes"]
    assert isinstance(episodes, list)
    episode = episodes[0]
    assert isinstance(episode, dict)
    distribution = episode["plot_distribution"]
    assert isinstance(distribution, list)
    plot = distribution[1]
    assert isinstance(plot, dict)
    plot["slot"] = "A"

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any("episodes.0.plot_distribution.1.slot" in error and "duplicate" in error for error in errors)


def test_season_arc_requires_every_nonfinal_forward_hook(repository_root: Path) -> None:
    payload = valid_season_arc()
    episodes = payload["episodes"]
    assert isinstance(episodes, list)
    episode = episodes[1]
    assert isinstance(episode, dict)
    episode["forward_hook"] = None

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any("episodes.1.forward_hook" in error and "nonfinal" in error for error in errors)


def test_season_arc_rejects_unknown_forward_hook_target(repository_root: Path) -> None:
    payload = valid_season_arc()
    episodes = payload["episodes"]
    assert isinstance(episodes, list)
    episode = episodes[0]
    assert isinstance(episode, dict)
    forward_hook = episode["forward_hook"]
    assert isinstance(forward_hook, dict)
    forward_hook["target_episode_id"] = "NINEL-E99"

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any("episodes.0.forward_hook.target_episode_id" in error and "unknown episode" in error for error in errors)


@pytest.mark.parametrize("target_episode_id", ["NINEL-E02", "NINEL-E01"])
def test_season_arc_forward_hook_targets_strictly_later_episode(
    repository_root: Path,
    target_episode_id: str,
) -> None:
    payload = valid_season_arc()
    episodes = payload["episodes"]
    assert isinstance(episodes, list)
    episode = episodes[1]
    assert isinstance(episode, dict)
    forward_hook = episode["forward_hook"]
    assert isinstance(forward_hook, dict)
    forward_hook["target_episode_id"] = target_episode_id

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any(
        "episodes.1.forward_hook.target_episode_id" in error
        and "strictly later episode" in error
        for error in errors
    )


@pytest.mark.parametrize(
    ("collection", "field", "invalid_reference", "expected_kind"),
    [
        ("character_progression", "character_id", "NINEL-CH999", "character"),
        ("character_progression", "episode_ids", "OTHER-E01", "episode"),
        ("relationship_progression", "character_ids", "NINEL-CH999", "character"),
        ("relationship_progression", "event_ids", "NINEL-EV999", "event"),
        ("reveal_schedule", "event_id", "NINEL-EV999", "event"),
        ("reveal_schedule", "episode_id", "NINEL-E99", "episode"),
        ("season_setups", "setup_event_id", "NINEL-EV999", "event"),
        ("season_setups", "episode_id", "NINEL-E99", "episode"),
        ("unresolved_threads", "plotline_id", "NINEL-PL99", "plotline"),
        ("next_season_seeds", "event_id", "OTHER-EV001", "event"),
    ],
)
def test_season_arc_resolves_progression_reveal_and_thread_references(
    repository_root: Path,
    collection: str,
    field: str,
    invalid_reference: str,
    expected_kind: str,
) -> None:
    payload = valid_season_arc()
    items = payload[collection]
    assert isinstance(items, list)
    item = items[0]
    assert isinstance(item, dict)
    item[field] = [invalid_reference] if field.endswith("_ids") else invalid_reference

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any(f"{collection}.0.{field}" in error and expected_kind in error for error in errors)


def test_season_arc_rejects_finale_payoff_with_undeclared_setup(
    repository_root: Path,
) -> None:
    payload = valid_season_arc()
    finale_payoff = payload["finale_payoff"]
    assert isinstance(finale_payoff, dict)
    finale_payoff["setup_event_ids"] = ["NINEL-EV002"]

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any("finale_payoff.setup_event_ids.0" in error and "undeclared setup" in error for error in errors)


def test_season_arc_finale_setup_is_scheduled_before_finale(
    repository_root: Path,
) -> None:
    payload = valid_season_arc()
    season_setups = payload["season_setups"]
    assert isinstance(season_setups, list)
    setup = season_setups[0]
    assert isinstance(setup, dict)
    setup["episode_id"] = "NINEL-E03"

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any(
        "season_setups.0.episode_id" in error
        and "strictly before finale episode NINEL-E03" in error
        for error in errors
    )


@pytest.mark.parametrize(
    ("collection", "field"),
    [
        ("episodes", "forward_hook.target_episode_id"),
        ("season_setups", "episode_id"),
    ],
)
def test_season_arc_malformed_temporal_reference_returns_schema_error(
    repository_root: Path,
    collection: str,
    field: str,
) -> None:
    payload = valid_season_arc()
    if collection == "episodes":
        expected_location = "episodes.0.forward_hook"
        episodes = payload[collection]
        assert isinstance(episodes, list)
        episode = episodes[0]
        assert isinstance(episode, dict)
        forward_hook = episode["forward_hook"]
        assert isinstance(forward_hook, dict)
        forward_hook["target_episode_id"] = []
    else:
        expected_location = "season_setups.0.episode_id"
        season_setups = payload[collection]
        assert isinstance(season_setups, list)
        setup = season_setups[0]
        assert isinstance(setup, dict)
        setup[field] = []

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any(expected_location in error for error in errors)


@pytest.mark.parametrize("invalid_setup_event_id", [[], {}])
def test_season_arc_malformed_setup_event_id_returns_schema_error(
    repository_root: Path,
    invalid_setup_event_id: object,
) -> None:
    payload = valid_season_arc()
    season_setups = payload["season_setups"]
    assert isinstance(season_setups, list)
    setup = season_setups[0]
    assert isinstance(setup, dict)
    setup["setup_event_id"] = invalid_setup_event_id

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any("season_setups.0.setup_event_id" in error for error in errors)


def test_season_arc_schema_error_does_not_break_semantic_validation(
    repository_root: Path,
) -> None:
    payload = valid_season_arc()
    payload["season_setups"] = None

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any(
        "season_setups" in error and "array" in error
        for error in errors
    )


def test_season_arc_finale_payoff_targets_final_episode(repository_root: Path) -> None:
    payload = valid_season_arc()
    finale_payoff = payload["finale_payoff"]
    assert isinstance(finale_payoff, dict)
    finale_payoff["episode_id"] = "NINEL-E02"

    errors = validate_artifact("season-arc", payload, repository_root)

    assert any("finale_payoff.episode_id" in error and "final episode NINEL-E03" in error for error in errors)


def valid_unit_outline(project_format: str = "series") -> dict[str, object]:
    if project_format == "series":
        return {
            "schema_version": "2.0",
            "project_id": "ALPINE",
            "project_format": "series",
            "unit_id": "ALPINE-E03",
            "runtime_seconds": 1440,
            "runtime_basis": "The approved episode slot is 24 minutes.",
            "unit_objective": "Test the future-dated call while resolving tonight's rescue.",
            "structural_model": "Braided rescue and serial inquiry",
            "source_event_ids": ["ALPINE-EV021", "ALPINE-EV022", "ALPINE-EV023"],
            "source_plotline_ids": ["ALPINE-PL01", "ALPINE-PL02"],
            "opening_hook": {
                "scene_id": "ALPINE-E03-SC001",
                "promise": "A distress call arrives with tomorrow's timestamp.",
                "function": "Orient the current rescue and the serial anomaly together.",
            },
            "scenes": [
                {
                    "scene_id": "ALPINE-E03-SC001",
                    "scene_index": 1,
                    "start_seconds": 0,
                    "end_seconds": 600,
                    "title": "The impossible warning",
                    "summary": "The dispatcher logs the warning and redirects one bounded field test.",
                    "story_function": "Open both the local rescue and continuing inquiry.",
                    "event_ids": ["ALPINE-EV021", "ALPINE-EV022"],
                    "plotline_ids": ["ALPINE-PL01", "ALPINE-PL02"],
                    "evidence_status": "not-applicable",
                    "retention_function": "Suspense comes from a legible test with immediate stakes.",
                },
                {
                    "scene_id": "ALPINE-E03-SC002",
                    "scene_index": 2,
                    "start_seconds": 600,
                    "end_seconds": 1440,
                    "title": "Rescue and residue",
                    "summary": "The warning prevents a route failure, the hiker is recovered, and the cause stays open.",
                    "story_function": "Resolve the rescue while changing the season inquiry.",
                    "event_ids": ["ALPINE-EV022", "ALPINE-EV023"],
                    "plotline_ids": ["ALPINE-PL01", "ALPINE-PL02"],
                    "evidence_status": "not-applicable",
                    "retention_function": "Local closure earns a changed serial question.",
                },
            ],
            "event_coverage": [
                {
                    "event_id": "ALPINE-EV021",
                    "scene_ids": ["ALPINE-E03-SC001"],
                    "outcome": "The anomalous call launches a falsifiable test.",
                },
                {
                    "event_id": "ALPINE-EV022",
                    "scene_ids": ["ALPINE-E03-SC001", "ALPINE-E03-SC002"],
                    "outcome": "The team changes route because of verified present evidence.",
                },
                {
                    "event_id": "ALPINE-EV023",
                    "scene_ids": ["ALPINE-E03-SC002"],
                    "outcome": "The current rescue closes without explaining the calls.",
                },
            ],
            "plotline_coverage": [
                {
                    "plotline_id": "ALPINE-PL01",
                    "scene_ids": ["ALPINE-E03-SC001", "ALPINE-E03-SC002"],
                    "advancement": "The warning is useful but its source remains unknown.",
                },
                {
                    "plotline_id": "ALPINE-PL02",
                    "scene_ids": ["ALPINE-E03-SC001", "ALPINE-E03-SC002"],
                    "advancement": "The missing hiker is recovered through a changed plan.",
                },
            ],
            "emotional_turns": [
                {
                    "scene_id": "ALPINE-E03-SC001",
                    "from_state": "skepticism",
                    "to_state": "conditional attention",
                    "change": "A bounded test replaces argument over belief.",
                },
                {
                    "scene_id": "ALPINE-E03-SC002",
                    "from_state": "conditional attention",
                    "to_state": "earned but limited trust",
                    "change": "The rescue succeeds without settling the anomaly.",
                },
            ],
            "act_outs": [
                {
                    "scene_id": "ALPINE-E03-SC001",
                    "turn": "The ordinary route is proved unsafe.",
                    "changed_pressure": "The team must trust a new plan without trusting the call's cause.",
                }
            ],
            "midpoint": {
                "scene_id": "ALPINE-E03-SC001",
                "function": "Verification changes the goal from testing the call to using it responsibly.",
            },
            "climax": {
                "scene_id": "ALPINE-E03-SC002",
                "function": "The team completes the alternate extraction under present evidence.",
            },
            "resolution": {
                "scene_id": "ALPINE-E03-SC002",
                "outcome": "The hiker is safe and the local incident is closed.",
                "unit_change": "The dispatcher earns controlled access for another test.",
            },
            "forward_hook": {
                "scene_id": "ALPINE-E03-SC002",
                "promise": "The next authenticated call will test whether intervention changes its contents.",
                "dependency": "Carry ALPINE-PL01 forward without reopening tonight's rescue.",
            },
            "format_plan": {
                "mode": "series-episode",
                "episode_position": "nonfinal",
                "local_resolution": "Tonight's rescue is complete.",
                "season_dependencies": [
                    {
                        "dependency": "The cause of the future calls remains unknown.",
                        "carry_forward": "The team retains a controlled testing protocol.",
                    }
                ],
            },
            "assumptions": [],
            "uncertainties": ["The source of the calls is not established."],
        }

    assert project_format in {
        "feature",
        "short",
        "documentary",
        "commercial",
        "music-video",
        "short-form",
    }
    payload = {
        "schema_version": "2.0",
        "project_id": "PULSE",
        "project_format": "short-form",
        "unit_id": "PULSE-U01",
        "runtime_seconds": 60,
        "runtime_basis": "The approved Reel duration is 60 seconds.",
        "unit_objective": "Show one radio repair and invite viewers to a real clinic.",
        "structural_model": "Demonstration and before-after payoff",
        "source_event_ids": ["PULSE-EV001", "PULSE-EV002", "PULSE-EV003", "PULSE-EV004"],
        "source_plotline_ids": ["PULSE-PL01"],
        "opening_hook": {
            "scene_id": "PULSE-U01-SC001",
            "promise": "A silent radio is shown before the repair begins.",
            "function": "Orient the object, failure, and promised result immediately.",
        },
        "scenes": [
            {
                "scene_id": "PULSE-U01-SC001",
                "scene_index": 1,
                "start_seconds": 0,
                "end_seconds": 6,
                "title": "Silent radio",
                "summary": "The radio fails on camera and the repair goal is stated.",
                "story_function": "Immediate orientation and result promise.",
                "event_ids": ["PULSE-EV001"],
                "plotline_ids": ["PULSE-PL01"],
                "evidence_status": "not-applicable",
                "retention_function": "A concrete before state creates honest anticipation.",
            },
            {
                "scene_id": "PULSE-U01-SC002",
                "scene_index": 2,
                "start_seconds": 6,
                "end_seconds": 45,
                "title": "Diagnose and repair",
                "summary": "A volunteer demonstrates the loose contact and restores it.",
                "story_function": "Deliver legible process rather than delay the answer.",
                "event_ids": ["PULSE-EV002", "PULSE-EV003"],
                "plotline_ids": ["PULSE-PL01"],
                "evidence_status": "not-applicable",
                "retention_function": "Visible progress and diagnosis sustain attention.",
            },
            {
                "scene_id": "PULSE-U01-SC003",
                "scene_index": 3,
                "start_seconds": 45,
                "end_seconds": 60,
                "title": "Sound restored",
                "summary": "The radio plays; the next free clinic date appears without a performance claim.",
                "story_function": "Pay the before-after promise and give a truthful next step.",
                "event_ids": ["PULSE-EV004"],
                "plotline_ids": ["PULSE-PL01"],
                "evidence_status": "not-applicable",
                "retention_function": "The audible result supplies completion before the invitation.",
            },
        ],
        "event_coverage": [
            {"event_id": "PULSE-EV001", "scene_ids": ["PULSE-U01-SC001"], "outcome": "The failed radio establishes the before state."},
            {"event_id": "PULSE-EV002", "scene_ids": ["PULSE-U01-SC002"], "outcome": "The fault is diagnosed visibly."},
            {"event_id": "PULSE-EV003", "scene_ids": ["PULSE-U01-SC002"], "outcome": "The contact is repaired."},
            {"event_id": "PULSE-EV004", "scene_ids": ["PULSE-U01-SC003"], "outcome": "The working radio pays off the opening and the clinic is invited."},
        ],
        "plotline_coverage": [
            {"plotline_id": "PULSE-PL01", "scene_ids": ["PULSE-U01-SC001", "PULSE-U01-SC002", "PULSE-U01-SC003"], "advancement": "One complete repair moves from failure through diagnosis to audible result."}
        ],
        "emotional_turns": [
            {"scene_id": "PULSE-U01-SC001", "from_state": "frustration", "to_state": "curiosity", "change": "The fault becomes a solvable question."},
            {"scene_id": "PULSE-U01-SC003", "from_state": "concentration", "to_state": "relief", "change": "The radio's sound confirms the repair."},
        ],
        "act_outs": [],
        "midpoint": None,
        "climax": {"scene_id": "PULSE-U01-SC003", "function": "The radio plays audibly after the repair."},
        "resolution": {"scene_id": "PULSE-U01-SC003", "outcome": "The promised before-after result is visible and audible.", "unit_change": "A discarded object returns to use."},
        "forward_hook": None,
        "format_plan": {
            "mode": "runtime-led",
            "orientation_by_seconds": 6,
            "payoff_by_seconds": 52,
            "orientation": "Show the object, fault, and result promise before six seconds.",
            "payoff": "Restore audible sound before the final truthful invitation.",
            "retention_strategy": "Visible diagnosis and progress, not withheld basic context.",
        },
        "assumptions": ["The clinic date and access details are supplied before production."],
        "uncertainties": [],
    }

    payload["project_format"] = project_format
    if project_format in {"feature", "short"}:
        payload["forward_hook"] = None
        payload["format_plan"] = {
            "mode": "whole-script",
            "whole_script_complete": True,
            "closure": "The repair demonstration completes the authored work.",
        }
    elif project_format == "documentary":
        scenes = payload["scenes"]
        assert isinstance(scenes, list)
        for scene, status in zip(
            scenes, ["discovered", "planned", "discovered"], strict=True
        ):
            assert isinstance(scene, dict)
            scene["evidence_status"] = status
        payload["format_plan"] = {
            "mode": "documentary-evidence",
            "evidence_items": [
                {
                    "event_id": "PULSE-EV001",
                    "status": "discovered",
                    "basis": "Captured before state.",
                    "contingency": "Cause remains open.",
                },
                {
                    "event_id": "PULSE-EV002",
                    "status": "planned",
                    "basis": "Confirmed inspection access.",
                    "contingency": "Finding remains unknown.",
                },
                {
                    "event_id": "PULSE-EV003",
                    "status": "planned",
                    "basis": "Repair observation is requested.",
                    "contingency": "Repair outcome remains unknown.",
                },
                {
                    "event_id": "PULSE-EV004",
                    "status": "discovered",
                    "basis": "Captured result is in hand.",
                    "contingency": "No universal claim is supported.",
                },
            ],
            "unknown_outcomes": ["Future access and results remain unknown."],
        }
    return payload


def valid_documentary_unit_outline() -> dict[str, object]:
    return valid_unit_outline("documentary")


@pytest.mark.parametrize(
    "project_format",
    [
        "feature",
        "short",
        "series",
        "documentary",
        "commercial",
        "music-video",
        "short-form",
    ],
)
def test_valid_unit_outline_passes(repository_root: Path, project_format: str) -> None:
    assert validate_artifact("unit-outline", valid_unit_outline(project_format), repository_root) == []


def test_unit_outline_requires_every_source_event_in_coverage(repository_root: Path) -> None:
    payload = valid_unit_outline()
    event_coverage = payload["event_coverage"]
    assert isinstance(event_coverage, list)
    event_coverage.pop()

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any("event_coverage" in error and "ALPINE-EV023" in error and "missing" in error for error in errors)


def test_unit_outline_requires_every_source_event_in_a_scene(repository_root: Path) -> None:
    payload = valid_unit_outline()
    scenes = payload["scenes"]
    assert isinstance(scenes, list)
    second = scenes[1]
    assert isinstance(second, dict)
    second["event_ids"] = ["ALPINE-EV022"]

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any("scenes" in error and "ALPINE-EV023" in error and "not assigned" in error for error in errors)


def test_unit_outline_rejects_duplicate_scene_ids(repository_root: Path) -> None:
    payload = valid_unit_outline()
    scenes = payload["scenes"]
    assert isinstance(scenes, list)
    first = scenes[0]
    second = scenes[1]
    assert isinstance(first, dict) and isinstance(second, dict)
    second["scene_id"] = first["scene_id"]

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any("scenes.1.scene_id" in error and "duplicate" in error for error in errors)


@pytest.mark.parametrize("scene_id", ["ALPINE-SC001", "OTHER-E03-SC001", "ALPINE-E03-SC000"])
def test_unit_outline_requires_exact_positive_unit_prefixed_scene_ids(repository_root: Path, scene_id: str) -> None:
    payload = valid_unit_outline()
    scenes = payload["scenes"]
    assert isinstance(scenes, list)
    scene = scenes[0]
    assert isinstance(scene, dict)
    scene["scene_id"] = scene_id

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any("scenes.0.scene_id" in error and "ALPINE-E03-SC###" in error for error in errors)


def test_unit_outline_scene_id_matches_scene_index(repository_root: Path) -> None:
    payload = valid_unit_outline()
    scenes = payload["scenes"]
    assert isinstance(scenes, list)
    scene = scenes[0]
    assert isinstance(scene, dict)
    scene["scene_id"] = "ALPINE-E03-SC002"

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any("scenes.0.scene_id" in error and "scene index 1" in error for error in errors)


def test_unit_outline_rejects_out_of_order_scene_indexes(repository_root: Path) -> None:
    payload = valid_unit_outline()
    scenes = payload["scenes"]
    assert isinstance(scenes, list)
    first = scenes[0]
    second = scenes[1]
    assert isinstance(first, dict) and isinstance(second, dict)
    first["scene_index"] = 2
    second["scene_index"] = 1

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any("scenes" in error and "ascending order 1..2" in error for error in errors)


def test_unit_outline_rejects_unknown_midpoint_scene(repository_root: Path) -> None:
    payload = valid_unit_outline()
    midpoint = payload["midpoint"]
    assert isinstance(midpoint, dict)
    midpoint["scene_id"] = "ALPINE-E03-SC099"

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any("midpoint.scene_id" in error and "unknown scene" in error for error in errors)


def test_unit_outline_opening_hook_targets_first_declared_scene(
    repository_root: Path,
) -> None:
    payload = valid_unit_outline()
    opening_hook = payload["opening_hook"]
    assert isinstance(opening_hook, dict)
    opening_hook["scene_id"] = "ALPINE-E03-SC002"

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any(
        "opening_hook.scene_id" in error
        and "must target first scene ALPINE-E03-SC001" in error
        for error in errors
    )


def test_unit_outline_event_coverage_rejects_scene_without_event(
    repository_root: Path,
) -> None:
    payload = valid_unit_outline()
    event_coverage = payload["event_coverage"]
    assert isinstance(event_coverage, list)
    coverage = event_coverage[0]
    assert isinstance(coverage, dict)
    coverage["scene_ids"] = ["ALPINE-E03-SC002"]

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any(
        "event_coverage.0.scene_ids.0" in error
        and "does not carry event ALPINE-EV021" in error
        for error in errors
    )


def test_unit_outline_event_coverage_includes_every_scene_carrying_event(
    repository_root: Path,
) -> None:
    payload = valid_unit_outline()
    event_coverage = payload["event_coverage"]
    assert isinstance(event_coverage, list)
    coverage = event_coverage[1]
    assert isinstance(coverage, dict)
    coverage["scene_ids"] = ["ALPINE-E03-SC002"]

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any(
        "event_coverage.1.scene_ids" in error
        and "missing scene ALPINE-E03-SC001 carrying event ALPINE-EV022" in error
        for error in errors
    )


def test_unit_outline_plotline_coverage_rejects_scene_without_plotline(
    repository_root: Path,
) -> None:
    payload = valid_unit_outline()
    scenes = payload["scenes"]
    assert isinstance(scenes, list)
    scene = scenes[1]
    assert isinstance(scene, dict)
    scene["plotline_ids"] = ["ALPINE-PL02"]

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any(
        "plotline_coverage.0.scene_ids.1" in error
        and "does not carry plotline ALPINE-PL01" in error
        for error in errors
    )


def test_unit_outline_plotline_coverage_includes_every_scene_carrying_plotline(
    repository_root: Path,
) -> None:
    payload = valid_unit_outline()
    plotline_coverage = payload["plotline_coverage"]
    assert isinstance(plotline_coverage, list)
    coverage = plotline_coverage[0]
    assert isinstance(coverage, dict)
    coverage["scene_ids"] = ["ALPINE-E03-SC002"]

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any(
        "plotline_coverage.0.scene_ids" in error
        and "missing scene ALPINE-E03-SC001 carrying plotline ALPINE-PL01" in error
        for error in errors
    )


@pytest.mark.parametrize(
    ("scene_index", "start_seconds", "end_seconds", "expected"),
    [
        (0, 0, 0, "end_seconds must be greater"),
        (1, 500, 1440, "must not overlap"),
        (1, 600, 1441, "exceeds runtime_seconds"),
    ],
)
def test_unit_outline_scene_timing_fits_runtime(
    repository_root: Path,
    scene_index: int,
    start_seconds: int,
    end_seconds: int,
    expected: str,
) -> None:
    payload = valid_unit_outline()
    scenes = payload["scenes"]
    assert isinstance(scenes, list)
    scene = scenes[scene_index]
    assert isinstance(scene, dict)
    scene["start_seconds"] = start_seconds
    scene["end_seconds"] = end_seconds

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any(f"scenes.{scene_index}" in error and expected in error for error in errors)


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("orientation_by_seconds", 61, "exceeds runtime_seconds"),
        ("payoff_by_seconds", 61, "exceeds runtime_seconds"),
        ("orientation_by_seconds", 53, "must not follow payoff_by_seconds"),
    ],
)
def test_unit_outline_runtime_led_deadlines_fit_runtime_and_order(
    repository_root: Path,
    field: str,
    value: int,
    expected: str,
) -> None:
    payload = valid_unit_outline("short-form")
    format_plan = payload["format_plan"]
    assert isinstance(format_plan, dict)
    format_plan[field] = value

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any(f"format_plan.{field}" in error and expected in error for error in errors)


def test_documentary_unit_outline_rejects_unknown_evidence_event(repository_root: Path) -> None:
    payload = valid_documentary_unit_outline()
    format_plan = payload["format_plan"]
    assert isinstance(format_plan, dict)
    evidence_items = format_plan["evidence_items"]
    assert isinstance(evidence_items, list)
    evidence_item = evidence_items[0]
    assert isinstance(evidence_item, dict)
    evidence_item["event_id"] = "PULSE-EV999"

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any("format_plan.evidence_items.0.event_id" in error and "unknown event" in error for error in errors)


def test_documentary_unit_outline_requires_evidence_item_for_every_event(repository_root: Path) -> None:
    payload = valid_documentary_unit_outline()
    format_plan = payload["format_plan"]
    assert isinstance(format_plan, dict)
    evidence_items = format_plan["evidence_items"]
    assert isinstance(evidence_items, list)
    evidence_items.pop()

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any("format_plan.evidence_items" in error and "PULSE-EV004" in error and "missing" in error for error in errors)


def test_documentary_evidence_status_agrees_with_scene_carrying_event(
    repository_root: Path,
) -> None:
    payload = valid_documentary_unit_outline()
    format_plan = payload["format_plan"]
    assert isinstance(format_plan, dict)
    evidence_items = format_plan["evidence_items"]
    assert isinstance(evidence_items, list)
    evidence_item = evidence_items[1]
    assert isinstance(evidence_item, dict)
    evidence_item["status"] = "discovered"

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any(
        "format_plan.evidence_items.1.status" in error
        and "scene PULSE-U01-SC002 has evidence_status planned" in error
        for error in errors
    )


def test_documentary_evidence_status_rejects_mixed_scene_carriers(
    repository_root: Path,
) -> None:
    payload = valid_documentary_unit_outline()
    scenes = payload["scenes"]
    assert isinstance(scenes, list)
    second_scene = scenes[1]
    assert isinstance(second_scene, dict)
    event_ids = second_scene["event_ids"]
    assert isinstance(event_ids, list)
    event_ids.append("PULSE-EV001")
    event_coverage = payload["event_coverage"]
    assert isinstance(event_coverage, list)
    coverage = event_coverage[0]
    assert isinstance(coverage, dict)
    scene_ids = coverage["scene_ids"]
    assert isinstance(scene_ids, list)
    scene_ids.append("PULSE-U01-SC002")

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any(
        "format_plan.evidence_items.0.status" in error
        and "scene PULSE-U01-SC002 has evidence_status planned" in error
        for error in errors
    )


@pytest.mark.parametrize(
    ("collection", "field", "invalid_reference", "expected_kind"),
    [
        ("scenes", "event_ids", "ALPINE-EV999", "event"),
        ("scenes", "plotline_ids", "ALPINE-PL99", "plotline"),
        ("event_coverage", "scene_ids", "ALPINE-E03-SC099", "scene"),
        ("plotline_coverage", "plotline_id", "OTHER-PL01", "plotline"),
        ("emotional_turns", "scene_id", "ALPINE-E03-SC099", "scene"),
    ],
)
def test_unit_outline_resolves_all_exact_references(
    repository_root: Path,
    collection: str,
    field: str,
    invalid_reference: str,
    expected_kind: str,
) -> None:
    payload = valid_unit_outline()
    entries = payload[collection]
    assert isinstance(entries, list)
    entry = entries[0]
    assert isinstance(entry, dict)
    entry[field] = [invalid_reference] if field.endswith("_ids") else invalid_reference

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any(f"{collection}.0.{field}" in error and expected_kind in error for error in errors)


@pytest.mark.parametrize(
    ("field", "invalid_value", "expected_location"),
    [
        ("scenes", None, "scenes"),
        ("event_coverage", None, "event_coverage"),
        ("midpoint", {"scene_id": [], "function": "Invalid reference type."}, "midpoint.scene_id"),
        ("resolution", {"scene_id": {}, "outcome": "Invalid reference type.", "unit_change": "Invalid reference type."}, "resolution.scene_id"),
    ],
)
def test_unit_outline_malformed_input_returns_diagnostics_without_traceback(
    repository_root: Path,
    field: str,
    invalid_value: object,
    expected_location: str,
) -> None:
    payload = valid_unit_outline()
    payload[field] = invalid_value

    errors = validate_artifact("unit-outline", payload, repository_root)

    assert any(expected_location in error for error in errors)


def valid_screenplay_metadata() -> dict[str, object]:
    return {
        "schema_version": "2.0",
        "project_id": "EMBER",
        "unit_id": "EMBER-U01",
        "source_event_ids": ["EMBER-EV001", "EMBER-EV002"],
        "scene_mappings": [
            {
                "scene_id": "EMBER-U01-SC001",
                "heading": "EXT. SALT ROAD - DUSK",
                "event_ids": ["EMBER-EV001", "EMBER-EV002"],
                "character_ids": ["EMBER-CH001", "EMBER-CH002"],
                "location_id": "EMBER-LO001",
                "objective": "Mara must secure passage before the storm arrives.",
                "conflict": "The keeper delays her without stating his fear.",
                "turn": "Mara trades away the map she needs for passage.",
            }
        ],
        "character_mappings": [
            {"character_id": "EMBER-CH001", "cue": "MARA"},
            {"character_id": "EMBER-CH002", "cue": "KEEPER"},
        ],
        "location_mappings": [
            {"location_id": "EMBER-LO001", "name": "Salt road checkpoint"}
        ],
        "setup_payoffs": [
            {
                "setup_event_id": "EMBER-EV001",
                "setup_scene_id": "EMBER-U01-SC001",
                "payoff_event_id": "EMBER-EV002",
                "payoff_scene_id": "EMBER-U01-SC001",
                "relationship": "The concealed map becomes the price of passage.",
            }
        ],
        "assumptions": [],
        "uncertainties": [],
    }


def test_valid_screenplay_metadata_passes(repository_root: Path) -> None:
    assert (
        validate_artifact(
            "screenplay-metadata", valid_screenplay_metadata(), repository_root
        )
        == []
    )


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("unit_id", "OTHER-U01", "EMBER-U## or EMBER-E##"),
        ("scene_id", "EMBER-U02-SC001", "EMBER-U01-SC###"),
        ("event_id", "OTHER-EV001", "EMBER-EV###"),
        ("character_id", "EMBER-CH001-extra", "EMBER-CH###"),
        ("location_id", "OTHER-LO001", "EMBER-LO###"),
    ],
)
def test_screenplay_metadata_rejects_nonexact_context_ids(
    repository_root: Path, field: str, value: str, expected: str
) -> None:
    payload = valid_screenplay_metadata()
    if field == "unit_id":
        payload[field] = value
    elif field == "scene_id":
        mappings = payload["scene_mappings"]
        assert isinstance(mappings, list)
        assert isinstance(mappings[0], dict)
        mappings[0][field] = value
    elif field == "event_id":
        mappings = payload["scene_mappings"]
        assert isinstance(mappings, list)
        assert isinstance(mappings[0], dict)
        mappings[0]["event_ids"] = [value]
    elif field == "character_id":
        mappings = payload["character_mappings"]
        assert isinstance(mappings, list)
        assert isinstance(mappings[0], dict)
        mappings[0][field] = value
    else:
        mappings = payload["location_mappings"]
        assert isinstance(mappings, list)
        assert isinstance(mappings[0], dict)
        mappings[0][field] = value

    errors = validate_artifact("screenplay-metadata", payload, repository_root)

    assert any(expected in error for error in errors)


def test_screenplay_metadata_rejects_duplicate_scene_mapping(
    repository_root: Path,
) -> None:
    payload = valid_screenplay_metadata()
    mappings = payload["scene_mappings"]
    assert isinstance(mappings, list)
    duplicate = dict(mappings[0])
    duplicate["heading"] = "EXT. SECOND ROAD - NIGHT"
    mappings.append(duplicate)

    errors = validate_artifact("screenplay-metadata", payload, repository_root)

    assert any(
        "scene_mappings.1.scene_id" in error
        and "duplicate scene mapping EMBER-U01-SC001" in error
        for error in errors
    )


def test_screenplay_metadata_rejects_unknown_event_character_and_location_refs(
    repository_root: Path,
) -> None:
    payload = valid_screenplay_metadata()
    mappings = payload["scene_mappings"]
    assert isinstance(mappings, list)
    assert isinstance(mappings[0], dict)
    mappings[0]["event_ids"] = ["EMBER-EV003"]
    mappings[0]["character_ids"] = ["EMBER-CH003"]
    mappings[0]["location_id"] = "EMBER-LO003"

    errors = validate_artifact("screenplay-metadata", payload, repository_root)

    assert any("unknown event EMBER-EV003" in error for error in errors)
    assert any("unknown character EMBER-CH003" in error for error in errors)
    assert any("unknown location EMBER-LO003" in error for error in errors)


def test_screenplay_metadata_rejects_undeclared_prose_field(
    repository_root: Path,
) -> None:
    payload = valid_screenplay_metadata()
    payload["screenplay_prose"] = "Do not duplicate the Fountain screenplay in JSON."

    errors = validate_artifact("screenplay-metadata", payload, repository_root)

    assert any(
        "screenplay_prose" in error and "unexpected" in error for error in errors
    )


def test_screenplay_metadata_requires_every_source_event_in_a_scene(
    repository_root: Path,
) -> None:
    payload = valid_screenplay_metadata()
    mappings = payload["scene_mappings"]
    assert isinstance(mappings, list)
    assert isinstance(mappings[0], dict)
    mappings[0]["event_ids"] = ["EMBER-EV001"]

    errors = validate_artifact("screenplay-metadata", payload, repository_root)

    assert any(
        "scene_mappings" in error
        and "source event EMBER-EV002 has no screenplay scene mapping" in error
        for error in errors
    )


def test_screenplay_metadata_setup_and_payoff_events_occur_in_mapped_scenes(
    repository_root: Path,
) -> None:
    payload = valid_screenplay_metadata()
    mappings = payload["scene_mappings"]
    assert isinstance(mappings, list)
    assert isinstance(mappings[0], dict)
    mappings[0]["event_ids"] = ["EMBER-EV001"]
    second_mapping = dict(mappings[0])
    second_mapping["scene_id"] = "EMBER-U01-SC002"
    second_mapping["heading"] = "EXT. SECOND ROAD - NIGHT"
    second_mapping["event_ids"] = ["EMBER-EV002"]
    mappings.append(second_mapping)
    setup_payoffs = payload["setup_payoffs"]
    assert isinstance(setup_payoffs, list)
    assert isinstance(setup_payoffs[0], dict)
    setup_payoffs[0]["setup_event_id"] = "EMBER-EV002"

    errors = validate_artifact("screenplay-metadata", payload, repository_root)

    assert any(
        "setup_payoffs.0.setup_event_id" in error
        and "EMBER-EV002 is not mapped to scene EMBER-U01-SC001" in error
        for error in errors
    )


def test_screenplay_metadata_requires_payoff_event_and_scene_together(
    repository_root: Path,
) -> None:
    payload = valid_screenplay_metadata()
    setup_payoffs = payload["setup_payoffs"]
    assert isinstance(setup_payoffs, list)
    assert isinstance(setup_payoffs[0], dict)
    setup_payoffs[0]["payoff_scene_id"] = None

    errors = validate_artifact("screenplay-metadata", payload, repository_root)

    assert any(
        "setup_payoffs.0" in error
        and "payoff_event_id and payoff_scene_id must both be null or both be IDs"
        in error
        for error in errors
    )


def valid_script_revision_plan() -> dict[str, object]:
    return {
        "schema_version": "2.0",
        "project_id": "FERRY",
        "unit_id": "FERRY-U01",
        "draft_version": "first-draft",
        "project_format": "short",
        "revision_scope": "A diagnosis-only pass for a 12-minute contained short.",
        "source_element_ids": [
            "FERRY-U01-SC001-D01",
            "FERRY-U01-SC001-A02",
            "FERRY-U01-SC002-D01",
            "FERRY-U01-SC003-A01",
            "FERRY-U01-SC003-D02",
            "FERRY-U01-SC003-D03",
        ],
        "approved_constraints": [
            {
                "constraint_id": "FERRY-CON001",
                "constraint_type": "canon",
                "statement": "Tomas sold the spare fuel cell before the story begins.",
                "protected_source_ids": ["FERRY-U01-SC002-D01"],
                "preservation_test": "The revised draft still treats the completed sale as prior action.",
            },
            {
                "constraint_id": "FERRY-AMB001",
                "constraint_type": "approved-ambiguity",
                "statement": "The final radio burst may be the missing mother or interference.",
                "protected_source_ids": [
                    "FERRY-U01-SC003-A01",
                    "FERRY-U01-SC003-D02",
                    "FERRY-U01-SC003-D03",
                ],
                "preservation_test": "No new evidence identifies the voice or rules out interference.",
            },
        ],
        "diagnosis_items": [
            {
                "diagnosis_id": "FERRY-U01-RV001",
                "category": "causality",
                "affected_ids": [
                    "FERRY-U01-SC001-A02",
                    "FERRY-U01-SC002-D01",
                ],
                "evidence": [
                    {
                        "source_id": "FERRY-U01-SC001-A02",
                        "observation": "The pawn ticket is hidden, but it changes no decision before the confession.",
                        "effect": "The reveal arrives by explanation instead of pressure from an earlier action.",
                    },
                    {
                        "source_id": "FERRY-U01-SC002-D01",
                        "observation": "Tomas states the completed sale and his motive in one uninterrupted line.",
                        "effect": "Cause, concealment, and consequence do not form an escalating chain.",
                    },
                ],
                "diagnosis": "The fuel-cell reveal is disclosed but not caused by the characters' present tactics.",
                "priority": 1,
                "dependency_impact": "upstream-story",
                "dependency_rationale": "The reveal mechanism controls later agency, stakes, and dialogue work.",
                "proposed_change": "Make Mira's inspection and Tomas's attempts to redirect it expose the pawn ticket before he chooses what to admit.",
                "change_target_ids": ["FERRY-U01-SC001-A02"],
                "execution_mode": "executable-change",
                "preserved_constraint_ids": ["FERRY-CON001"],
                "preservation_checks": [
                    {
                        "constraint_id": "FERRY-CON001",
                        "protected_source_ids": ["FERRY-U01-SC002-D01"],
                        "invariant": "The spare fuel cell was sold before the story begins.",
                        "verification_assertion": "The later rewrite still treats the sale as completed prior action.",
                    }
                ],
                "decision_request": None,
                "downstream_impact": [
                    "Recheck the dock confrontation's tactics and information order.",
                    "Recheck dialogue exposition after the reveal is made behavioral.",
                ],
                "status": "proposed",
                "assumptions": ["The pawn ticket remains a practical microbudget prop."],
                "uncertainties": ["The exact debt amount is intentionally unspecified."],
            },
            {
                "diagnosis_id": "FERRY-U01-RV002",
                "category": "dialogue",
                "affected_ids": [
                    "FERRY-U01-SC003-D02",
                    "FERRY-U01-SC003-D03",
                ],
                "evidence": [
                    {
                        "source_id": "FERRY-U01-SC003-D02",
                        "observation": "Tomas immediately names the most consequential interpretation of the burst.",
                        "effect": "The line explains the ambiguity before behavior can carry competing hopes.",
                    },
                    {
                        "source_id": "FERRY-U01-SC003-D03",
                        "observation": "Mira immediately states the alternative interpretation.",
                        "effect": "The paired labels flatten subtext while preserving neither character's tactic.",
                    },
                ],
                "diagnosis": "The final exchange explains both sides of the approved ambiguity instead of dramatizing how each sibling uses it.",
                "priority": 2,
                "dependency_impact": "line-craft",
                "dependency_rationale": "This line pass depends on the radio event and its ambiguity remaining unchanged.",
                "proposed_change": "Replace the interpretive labels with opposed playable responses to replaying or abandoning the signal, without adding identifying evidence.",
                "change_target_ids": [
                    "FERRY-U01-SC003-D02",
                    "FERRY-U01-SC003-D03",
                ],
                "execution_mode": "blocked-upstream-decision",
                "preserved_constraint_ids": ["FERRY-AMB001"],
                "preservation_checks": [
                    {
                        "constraint_id": "FERRY-AMB001",
                        "protected_source_ids": [
                            "FERRY-U01-SC003-A01",
                            "FERRY-U01-SC003-D02",
                            "FERRY-U01-SC003-D03",
                        ],
                        "invariant": "The burst remains attributable either to the missing mother or interference.",
                        "verification_assertion": "No changed line identifies the voice or removes interference as a viable reading.",
                    }
                ],
                "decision_request": {
                    "conflicting_constraint_ids": ["FERRY-AMB001"],
                    "decision_question": "May the approved ambiguity-bearing lines be changed while keeping both readings viable?",
                    "uncertainty": "The story owner has not approved changing protected ambiguity-bearing dialogue.",
                },
                "downstream_impact": [
                    "Recheck the ending beat for legible but unresolved emotional consequence."
                ],
                "status": "blocked",
                "assumptions": ["Both siblings recognize why the fragment matters."],
                "uncertainties": ["The approved ending may favor hope, caution, or equal tension."],
            },
        ],
        "assumptions": ["The source element ledger was approved for this revision pass."],
        "uncertainties": ["No target page count beyond the 12-minute intent was supplied."],
    }


@pytest.fixture
def retcon_request_script_revision_plan() -> dict[str, object]:
    """A real canon-conflicting request that retains the constraint reference."""
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["proposed_change"] = (
        "Retcon the completed sale so Tomas only considers selling the cell later."
    )
    items[0]["change_target_ids"] = ["FERRY-U01-SC002-D01"]
    return payload


def two_constraint_blocked_script_revision_plan() -> dict[str, object]:
    payload = valid_script_revision_plan()
    constraints = payload["approved_constraints"]
    items = payload["diagnosis_items"]
    assert isinstance(constraints, list)
    assert isinstance(items, list) and isinstance(items[0], dict)
    constraints.append(
        {
            "constraint_id": "FERRY-CON002",
            "constraint_type": "canon",
            "statement": "The completed sale remains known to Tomas.",
            "protected_source_ids": ["FERRY-U01-SC002-D01"],
            "preservation_test": "The later rewrite keeps Tomas aware of the completed sale.",
        }
    )
    items[0]["change_target_ids"] = ["FERRY-U01-SC002-D01"]
    items[0]["execution_mode"] = "blocked-upstream-decision"
    items[0]["preserved_constraint_ids"] = ["FERRY-CON001", "FERRY-CON002"]
    items[0]["preservation_checks"] = [
        {
            "constraint_id": "FERRY-CON001",
            "protected_source_ids": ["FERRY-U01-SC002-D01"],
            "invariant": "The spare fuel cell was sold before the story begins.",
            "verification_assertion": "The later rewrite still treats the sale as completed prior action.",
        },
        {
            "constraint_id": "FERRY-CON002",
            "protected_source_ids": ["FERRY-U01-SC002-D01"],
            "invariant": "Tomas knows that the sale was completed.",
            "verification_assertion": "The later rewrite does not erase Tomas's knowledge of the sale.",
        },
    ]
    items[0]["decision_request"] = {
        "conflicting_constraint_ids": ["FERRY-CON001", "FERRY-CON002"],
        "decision_question": "May the protected sale account be changed?",
        "uncertainty": "The requested target conflicts with two approved constraints.",
    }
    items[0]["status"] = "blocked"
    return payload


def test_valid_script_revision_plan_passes(repository_root: Path) -> None:
    assert (
        validate_artifact(
            "script-revision-plan", valid_script_revision_plan(), repository_root
        )
        == []
    )


@pytest.mark.parametrize("missing_field", ["affected_ids", "evidence"])
def test_script_revision_plan_rejects_generic_diagnosis_without_traceability(
    repository_root: Path, missing_field: str
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    del items[0][missing_field]

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(missing_field in error and "required" in error for error in errors)


def test_script_revision_plan_rejects_unknown_affected_id(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["affected_ids"] = ["FERRY-U01-SC999-D99"]
    items[0]["evidence"] = [
        {
            "source_id": "FERRY-U01-SC999-D99",
            "observation": "This source element was never declared.",
            "effect": "The note cannot be traced to the supplied draft.",
        }
    ]

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.0.affected_ids.0" in error
        and "unknown source element FERRY-U01-SC999-D99" in error
        for error in errors
    )


def test_script_revision_plan_rejects_duplicate_evidence_reference(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    evidence = items[0]["evidence"]
    assert isinstance(evidence, list) and isinstance(evidence[0], dict)
    evidence.append(
        {
            "source_id": evidence[0]["source_id"],
            "observation": "A second note points at the same element.",
            "effect": "Duplicate reference coverage obscures the evidence ledger.",
        }
    )

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.0.evidence.2.source_id" in error
        and "duplicate evidence reference FERRY-U01-SC001-A02" in error
        for error in errors
    )


def test_script_revision_plan_rejects_duplicate_affected_reference(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["affected_ids"] = [
        "FERRY-U01-SC001-A02",
        "FERRY-U01-SC001-A02",
    ]

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.0.affected_ids" in error
        and "non-unique elements" in error
        for error in errors
    )


def test_script_revision_plan_rejects_evidence_outside_affected_ids(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    evidence = items[0]["evidence"]
    assert isinstance(evidence, list) and isinstance(evidence[1], dict)
    evidence[1]["source_id"] = "FERRY-U01-SC001-D01"

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.0.evidence.1.source_id" in error
        and "is not listed in affected_ids" in error
        for error in errors
    )


def test_script_revision_plan_requires_evidence_for_every_affected_id(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    evidence = items[0]["evidence"]
    assert isinstance(evidence, list)
    items[0]["evidence"] = evidence[:1]

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.0.affected_ids.1" in error
        and "FERRY-U01-SC002-D01 has no evidence entry" in error
        for error in errors
    )


def test_script_revision_plan_rejects_duplicate_diagnosis_id(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list)
    assert isinstance(items[0], dict) and isinstance(items[1], dict)
    items[1]["diagnosis_id"] = items[0]["diagnosis_id"]

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.1.diagnosis_id" in error
        and "duplicate diagnosis ID FERRY-U01-RV001" in error
        for error in errors
    )


def test_script_revision_plan_rejects_duplicate_priority_rank(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[1], dict)
    items[1]["priority"] = 1

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.1.priority" in error and "duplicate priority 1" in error
        for error in errors
    )


def test_script_revision_plan_rejects_invalid_priority_rank(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["priority"] = 0

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.0.priority" in error and "less than the minimum" in error
        for error in errors
    )


def test_script_revision_plan_priority_matches_dependency_order(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list)
    assert isinstance(items[0], dict) and isinstance(items[1], dict)
    items[0]["dependency_impact"] = "line-craft"
    items[1]["dependency_impact"] = "upstream-story"

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.1.dependency_impact" in error
        and "must not follow lower-impact line-craft" in error
        for error in errors
    )


def test_script_revision_plan_rejects_invalid_status(repository_root: Path) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["status"] = "silently-rewritten"

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.0.status" in error
        and "silently-rewritten" in error
        and "is not one of" in error
        for error in errors
    )


def test_script_revision_plan_rejects_unknown_preserved_constraint(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["preserved_constraint_ids"] = ["FERRY-CON999"]

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.0.preserved_constraint_ids.0" in error
        and "unknown approved constraint FERRY-CON999" in error
        for error in errors
    )


def test_script_revision_plan_rejects_silent_approved_ambiguity_rewrite(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[1], dict)
    items[1]["preserved_constraint_ids"] = []

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.1.preserved_constraint_ids" in error
        and "must preserve affected approved constraint FERRY-AMB001" in error
        for error in errors
    )


def test_script_revision_plan_rejects_constraint_with_unknown_protected_source(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    constraints = payload["approved_constraints"]
    assert isinstance(constraints, list) and isinstance(constraints[0], dict)
    constraints[0]["protected_source_ids"] = ["FERRY-U01-SC999-A01"]

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "approved_constraints.0.protected_source_ids.0" in error
        and "unknown source element FERRY-U01-SC999-A01" in error
        for error in errors
    )


def test_script_revision_plan_rejects_rewritten_screenplay_payload(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    payload["rewritten_screenplay"] = "INT. FERRY CABIN - DAWN"

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "rewritten_screenplay" in error and "unexpected" in error
        for error in errors
    )


def test_script_revision_plan_malformed_input_returns_diagnostics_without_traceback(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    payload["source_element_ids"] = [None, ["nested"]]
    payload["approved_constraints"] = [{"constraint_id": ["bad"]}]
    payload["diagnosis_items"] = [
        {
            "diagnosis_id": ["bad"],
            "priority": "first",
            "affected_ids": [None],
            "evidence": [{"source_id": ["bad"]}],
            "preserved_constraint_ids": [None],
        }
    ]

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert errors
    assert all("Traceback" not in error for error in errors)


@pytest.mark.parametrize(
    "diagnosis_id",
    ["FERRY-U01-RV003", "FERRY-U01-RV009", "FERRY-U01-RV002-extra"],
)
def test_script_revision_plan_requires_exact_nonfirst_diagnosis_position(
    repository_root: Path, diagnosis_id: str
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[1], dict)
    items[1]["diagnosis_id"] = diagnosis_id

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.1.diagnosis_id" in error
        and "must equal FERRY-U01-RV002 for plan position 2" in error
        for error in errors
    )


def test_script_revision_plan_rejects_out_of_order_diagnosis_ids(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list)
    assert isinstance(items[0], dict) and isinstance(items[1], dict)
    items[0]["diagnosis_id"], items[1]["diagnosis_id"] = (
        items[1]["diagnosis_id"],
        items[0]["diagnosis_id"],
    )

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.0.diagnosis_id" in error
        and "must equal FERRY-U01-RV001 for plan position 1" in error
        for error in errors
    )
    assert any(
        "diagnosis_items.1.diagnosis_id" in error
        and "must equal FERRY-U01-RV002 for plan position 2" in error
        for error in errors
    )


def test_script_revision_plan_requires_one_preservation_check_per_reference(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["preservation_checks"] = []

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.0.preservation_checks" in error
        and "missing check for preserved constraint FERRY-CON001" in error
        for error in errors
    )


def test_script_revision_plan_requires_exact_protected_sources_in_check(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    checks = items[0]["preservation_checks"]
    assert isinstance(checks, list) and isinstance(checks[0], dict)
    checks[0]["protected_source_ids"] = ["FERRY-U01-SC001-A02"]

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.0.preservation_checks.0.protected_source_ids" in error
        and "must exactly match approved constraint FERRY-CON001 protected_source_ids"
        in error
        for error in errors
    )


@pytest.mark.parametrize("status", ["proposed", "approved"])
def test_script_revision_plan_blocks_executable_retcon_even_with_constraint_id(
    repository_root: Path,
    retcon_request_script_revision_plan: dict[str, object],
    status: str,
) -> None:
    payload = retcon_request_script_revision_plan
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["execution_mode"] = "executable-change"
    items[0]["decision_request"] = None
    items[0]["status"] = status

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.0.change_target_ids.0" in error
        and "targets protected source FERRY-U01-SC002-D01 from FERRY-CON001"
        in error
        and "requires blocked-upstream-decision" in error
        for error in errors
    )


def test_script_revision_plan_accepts_retcon_request_only_as_blocked_decision(
    repository_root: Path,
    retcon_request_script_revision_plan: dict[str, object],
) -> None:
    payload = retcon_request_script_revision_plan
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["execution_mode"] = "blocked-upstream-decision"
    items[0]["decision_request"] = {
        "conflicting_constraint_ids": ["FERRY-CON001"],
        "decision_question": "May the completed pre-story sale be retconned?",
        "uncertainty": "The requested retcon conflicts with approved canon.",
    }
    items[0]["status"] = "blocked"

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert errors == []


def test_script_revision_plan_blocked_conflicts_match_protected_targets(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[1], dict)
    decision = items[1]["decision_request"]
    assert isinstance(decision, dict)
    decision["conflicting_constraint_ids"] = []

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.1.decision_request.conflicting_constraint_ids" in error
        and "must exactly match protected target conflicts: FERRY-AMB001" in error
        for error in errors
    )


@pytest.mark.parametrize(
    "conflicting_constraint_ids",
    [
        ["FERRY-CON001", "FERRY-CON002"],
        ["FERRY-CON002", "FERRY-CON001"],
    ],
)
def test_script_revision_plan_accepts_complete_conflict_set_in_either_order(
    repository_root: Path, conflicting_constraint_ids: list[str]
) -> None:
    payload = two_constraint_blocked_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    decision = items[0]["decision_request"]
    assert isinstance(decision, dict)
    decision["conflicting_constraint_ids"] = conflicting_constraint_ids

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert errors == []


@pytest.mark.parametrize(
    "conflicting_constraint_ids",
    [
        ["FERRY-CON001"],
        ["FERRY-CON001", "FERRY-CON002", "FERRY-AMB001"],
    ],
)
def test_script_revision_plan_rejects_incomplete_or_extra_conflict_set(
    repository_root: Path, conflicting_constraint_ids: list[str]
) -> None:
    payload = two_constraint_blocked_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    decision = items[0]["decision_request"]
    assert isinstance(decision, dict)
    decision["conflicting_constraint_ids"] = conflicting_constraint_ids

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.0.decision_request.conflicting_constraint_ids" in error
        and "must exactly match protected target conflicts: FERRY-CON001, FERRY-CON002"
        in error
        for error in errors
    )


@pytest.mark.parametrize(
    ("target_id", "expected"),
    [
        ("FERRY-U01-SC999-A01", "unknown source element FERRY-U01-SC999-A01"),
        ("FERRY-U01-SC001-D01", "is not listed in affected_ids"),
    ],
)
def test_script_revision_plan_change_targets_resolve_to_affected_source(
    repository_root: Path, target_id: str, expected: str
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["change_target_ids"] = [target_id]

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.0.change_target_ids.0" in error and expected in error
        for error in errors
    )


def test_script_revision_plan_rejects_duplicate_preservation_check(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    checks = items[0]["preservation_checks"]
    assert isinstance(checks, list) and isinstance(checks[0], dict)
    checks.append(dict(checks[0]))

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.0.preservation_checks.1.constraint_id" in error
        and "duplicate check for FERRY-CON001" in error
        for error in errors
    )


def test_script_revision_plan_rejects_check_without_preserved_reference(
    repository_root: Path,
) -> None:
    payload = valid_script_revision_plan()
    items = payload["diagnosis_items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    checks = items[0]["preservation_checks"]
    assert isinstance(checks, list)
    checks.append(
        {
            "constraint_id": "FERRY-AMB001",
            "protected_source_ids": [
                "FERRY-U01-SC003-A01",
                "FERRY-U01-SC003-D02",
                "FERRY-U01-SC003-D03",
            ],
            "invariant": "The radio burst remains ambiguous.",
            "verification_assertion": "Both readings remain viable.",
        }
    )

    errors = validate_artifact("script-revision-plan", payload, repository_root)

    assert any(
        "diagnosis_items.0.preservation_checks.1.constraint_id" in error
        and "is not listed in preserved_constraint_ids" in error
        for error in errors
    )


def valid_vfx_plan() -> dict[str, object]:
    """Compact literal fixture for one effect shot and one no-VFX shot."""
    return {
        "schema_version": "2.0",
        "project_id": "ORBIT",
        "source_context": {
            "scenes": [
                {
                    "scene_id": "ORBIT-S01",
                    "source_reference": "SRC-S01",
                }
            ],
            "shots": [
                {
                    "scene_id": "ORBIT-S01",
                    "shot_id": "ORBIT-S01-SH001",
                    "supplied_facts": [
                        {
                            "category": "visual",
                            "value": "A cyan holographic star map hovers above the console.",
                            "source_reference": "SRC-SH001-VISUAL",
                        },
                        {
                            "category": "camera",
                            "value": "A slow 30 cm push-in ends on Mara's hand beneath the map.",
                            "source_reference": "SRC-SH001-CAMERA",
                        },
                        {
                            "category": "lens",
                            "value": "40 mm lens.",
                            "source_reference": "SRC-SH001-LENS",
                        },
                        {
                            "category": "lighting",
                            "value": "Warm console practicals contrast with cyan interactive light from the map.",
                            "source_reference": "SRC-SH001-LIGHTING",
                        },
                        {
                            "category": "performance",
                            "value": "Mara flinches when the map glitches.",
                            "source_reference": "SRC-SH001-PERFORMANCE",
                        },
                    ],
                },
                {
                    "scene_id": "ORBIT-S01",
                    "shot_id": "ORBIT-S01-SH002",
                    "supplied_facts": [
                        {
                            "category": "visual",
                            "value": "Mara and Ivo exchange the brass key across the console.",
                            "source_reference": "SRC-SH002-VISUAL",
                        },
                        {
                            "category": "camera",
                            "value": "Locked medium two-shot.",
                            "source_reference": "SRC-SH002-CAMERA",
                        },
                        {
                            "category": "lens",
                            "value": "40 mm lens.",
                            "source_reference": "SRC-SH002-LENS",
                        },
                        {
                            "category": "lighting",
                            "value": "Only the warm console practicals light the exchange.",
                            "source_reference": "SRC-SH002-LIGHTING",
                        },
                        {
                            "category": "performance",
                            "value": "The exchange is performed entirely in camera.",
                            "source_reference": "SRC-SH002-PERFORMANCE",
                        },
                    ],
                },
            ],
        },
        "applicability": [
            {
                "shot_id": "ORBIT-S01-SH001",
                "classification": "effect",
                "effect_ids": ["ORBIT-FX001"],
                "reason": "The supplied hologram requires an integration plan.",
            },
            {
                "shot_id": "ORBIT-S01-SH002",
                "classification": "no-vfx",
                "effect_ids": [],
                "reason": "The supplied exchange is entirely in camera.",
            },
        ],
        "effects": [
            {
                "effect_id": "ORBIT-FX001",
                "shot_ids": ["ORBIT-S01-SH001"],
                "uncertainty_ids": ["ORBIT-UNC001"],
                "dramatic_purpose": "Make the map glitch trigger Mara's flinch.",
                "visual_purpose": "Read as a cyan map hovering above the console.",
                "decomposition": ["map volume", "glitch event", "hand occlusion"],
                "practical_digital_boundary": {
                    "status": "unresolved",
                    "practical_scope": "Cyan interactive light may be photographed.",
                    "digital_scope": "The map and glitch remain digital candidates.",
                    "uncertainty_id": "ORBIT-UNC001",
                },
                "clean_plate": {
                    "decision": "required",
                    "reason": "Preserve the console behind the map and hand.",
                },
                "tracking": {
                    "decision": "required",
                    "requirements": ["Record the push-in and console reference points."],
                },
                "camera_lens_lighting_metadata": [
                    {
                        "shot_id": "ORBIT-S01-SH001",
                        "category": "camera",
                        "value": "A slow 30 cm push-in ends on Mara's hand beneath the map.",
                        "source_reference": "SRC-SH001-CAMERA",
                        "provenance_status": "supplied",
                    },
                    {
                        "shot_id": "ORBIT-S01-SH001",
                        "category": "lens",
                        "value": "40 mm lens.",
                        "source_reference": "SRC-SH001-LENS",
                        "provenance_status": "supplied",
                    },
                    {
                        "shot_id": "ORBIT-S01-SH001",
                        "category": "lighting",
                        "value": "Warm console practicals contrast with cyan interactive light from the map.",
                        "source_reference": "SRC-SH001-LIGHTING",
                        "provenance_status": "supplied",
                    },
                ],
                "mattes_holdouts": ["Preserve Mara's hand as a foreground holdout."],
                "reference_capture": ["Capture console and hand spatial reference."],
                "practical_interaction": ["Retain or recreate cyan response on hand and console."],
                "simulation": {
                    "status": "not-required",
                    "requirements": [],
                    "uncertainty_id": None,
                },
                "capture_generation_elements": ["clean console plate", "map design reference"],
                "integration_assumptions": ["Map placement remains fixed to the console."],
                "continuity": ["Glitch timing remains synchronized with Mara's flinch."],
                "dependencies": [
                    {
                        "dependency": "Approve the practical/digital boundary.",
                        "owner": "human VFX and photography leads",
                    }
                ],
                "human_safety_handoff": {
                    "required": True,
                    "review": "A qualified human safety lead reviews any on-set emitter or marker plan.",
                },
                "acceptance_criteria": [
                    "The cyan map hovers without tracking drift.",
                    "The glitch remains synchronized with Mara's flinch.",
                ],
            }
        ],
        "assumptions": ["Map placement is proposed pending review."],
        "approval_evidence": [],
        "supplied_boundary_evidence": [],
        "uncertainties": [
            {
                "uncertainty_id": "ORBIT-UNC001",
                "description": "The practical-versus-digital interaction method is unresolved.",
                "effect_ids": ["ORBIT-FX001"],
                "shot_ids": ["ORBIT-S01-SH001"],
                "owner": "human VFX and photography leads",
            }
        ],
    }


def test_vfx_plan_requires_source_context(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    payload.pop("source_context")

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert "$: 'source_context' is a required property" in errors


def test_vfx_plan_rejects_unknown_shot_reference(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effects[0]["shot_ids"] = ["ORBIT-S01-SH999"]

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any("effects.0.shot_ids.0" in error and "unknown shot" in error for error in errors)


def test_vfx_plan_requires_clean_plate_decision(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effects[0].pop("clean_plate")

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any("effects.0" in error and "clean_plate" in error for error in errors)


def test_vfx_plan_unresolved_boundary_requires_uncertainty(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    payload["uncertainties"] = []

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "effects.0.practical_digital_boundary.uncertainty_id" in error
        and "unknown uncertainty" in error
        for error in errors
    )


def test_vfx_plan_requires_nonempty_dramatic_purpose(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effects[0]["dramatic_purpose"] = ""

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any("effects.0.dramatic_purpose" in error and "non-empty" in error for error in errors)


def test_vfx_plan_rejects_no_vfx_effect_collision(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    applicability = payload["applicability"]
    assert isinstance(applicability, list) and isinstance(applicability[1], dict)
    applicability[1]["effect_ids"] = ["ORBIT-FX001"]

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "applicability.1.effect_ids" in error and "no-vfx" in error
        for error in errors
    )


@pytest.mark.parametrize(
    "effect_id",
    ["ORBIT-FX000", "OTHER-FX001", "ORBIT-FX001-tail", "ORBIT-FX001\n"],
)
def test_vfx_plan_requires_exact_positive_project_effect_ids(
    repository_root: Path, effect_id: str
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effects[0]["effect_id"] = effect_id

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "effects.0.effect_id" in error and "must match ORBIT-FX###" in error
        for error in errors
    )


def test_vfx_plan_rejects_shot_scene_lineage_mismatch(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    shots = context["shots"]
    assert isinstance(shots, list) and isinstance(shots[0], dict)
    shots[0]["scene_id"] = "ORBIT-S99"

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "source_context.shots.0.scene_id" in error
        and "does not match scene ORBIT-S01 encoded by shot ORBIT-S01-SH001" in error
        for error in errors
    )


def test_vfx_plan_rejects_duplicate_source_shot(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    shots = context["shots"]
    assert isinstance(shots, list) and isinstance(shots[0], dict)
    shots.append(copy.deepcopy(shots[0]))

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "source_context.shots.2.shot_id" in error
        and "duplicate supplied shot ID ORBIT-S01-SH001" in error
        for error in errors
    )


def test_vfx_plan_requires_one_applicability_record_per_source_shot(
    repository_root: Path,
) -> None:
    payload = valid_vfx_plan()
    applicability = payload["applicability"]
    assert isinstance(applicability, list)
    applicability.pop()

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "applicability: missing classification for supplied shot ORBIT-S01-SH002"
        in error
        for error in errors
    )


def test_vfx_plan_rejects_duplicate_applicability_record(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    applicability = payload["applicability"]
    assert isinstance(applicability, list) and isinstance(applicability[0], dict)
    applicability.append(copy.deepcopy(applicability[0]))

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "applicability.2.shot_id" in error
        and "duplicate classification for ORBIT-S01-SH001" in error
        for error in errors
    )


def test_vfx_plan_rejects_unknown_no_vfx_applicability_shot(
    repository_root: Path,
) -> None:
    payload = valid_vfx_plan()
    applicability = payload["applicability"]
    assert isinstance(applicability, list)
    applicability.append(
        {
            "shot_id": "ORBIT-S01-SH999",
            "classification": "no-vfx",
            "effect_ids": [],
            "reason": "No VFX is requested for this shot.",
        }
    )

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "applicability.2.shot_id" in error
        and "unknown supplied shot ORBIT-S01-SH999" in error
        for error in errors
    )


def test_vfx_plan_requires_source_shot_scene_to_be_declared(
    repository_root: Path,
) -> None:
    payload = valid_vfx_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    scenes = context["scenes"]
    assert isinstance(scenes, list) and isinstance(scenes[0], dict)
    scenes[0]["scene_id"] = "ORBIT-S99"

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "source_context.shots.0.scene_id" in error
        and "ORBIT-S01 is not declared in source_context.scenes" in error
        for error in errors
    )


def test_vfx_plan_requires_inverse_effect_applicability(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    applicability = payload["applicability"]
    assert isinstance(applicability, list) and isinstance(applicability[0], dict)
    applicability[0]["effect_ids"] = []

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "applicability.0.effect_ids" in error
        and "must list effect ORBIT-FX001 assigned to ORBIT-S01-SH001" in error
        for error in errors
    )


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("effect_ids", ["ORBIT-FX999"], "unknown effect ORBIT-FX999"),
        ("shot_ids", ["ORBIT-S01-SH999"], "unknown shot ORBIT-S01-SH999"),
    ],
)
def test_vfx_plan_uncertainty_owner_references_resolve(
    repository_root: Path, field: str, value: list[str], expected: str
) -> None:
    payload = valid_vfx_plan()
    uncertainties = payload["uncertainties"]
    assert isinstance(uncertainties, list) and isinstance(uncertainties[0], dict)
    uncertainties[0][field] = value

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(f"uncertainties.0.{field}.0" in error and expected in error for error in errors)


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("value", "A different camera move."),
        ("source_reference", "SRC-SH999-CAMERA"),
    ],
)
def test_vfx_plan_supplied_metadata_exact_binds_to_shot_ledger(
    repository_root: Path, field: str, replacement: str
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    metadata = effects[0]["camera_lens_lighting_metadata"]
    assert isinstance(metadata, list) and isinstance(metadata[0], dict)
    metadata[0][field] = replacement

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "effects.0.camera_lens_lighting_metadata.0" in error
        and "supplied claim must exactly match category, value, and source_reference"
        in error
        and "shot ORBIT-S01-SH001" in error
        for error in errors
    )


def test_vfx_plan_supplied_claim_cannot_bind_cross_shot(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    metadata = effects[0]["camera_lens_lighting_metadata"]
    assert isinstance(metadata, list) and isinstance(metadata[0], dict)
    metadata[0] = {
        "shot_id": "ORBIT-S01-SH001",
        "category": "camera",
        "value": "Locked medium two-shot.",
        "source_reference": "SRC-SH002-CAMERA",
        "provenance_status": "supplied",
    }

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "effects.0.camera_lens_lighting_metadata.0" in error
        and "shot ORBIT-S01-SH001" in error
        for error in errors
    )


def test_vfx_plan_rejects_duplicate_source_fact(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    shots = context["shots"]
    assert isinstance(shots, list) and isinstance(shots[0], dict)
    facts = shots[0]["supplied_facts"]
    assert isinstance(facts, list) and isinstance(facts[0], dict)
    facts.append(copy.deepcopy(facts[0]))

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "source_context.shots.0.supplied_facts.5" in error
        and "duplicate supplied fact" in error
        for error in errors
    )


@pytest.mark.parametrize(
    ("container", "status_field", "status", "uncertainty_path"),
    [
        ("clean_plate", "decision", "unresolved", "clean_plate.uncertainty_id"),
        ("tracking", "decision", "unresolved", "tracking.uncertainty_id"),
        ("simulation", "status", "unresolved", "simulation.uncertainty_id"),
    ],
)
def test_vfx_plan_unresolved_method_requires_linked_uncertainty(
    repository_root: Path,
    container: str,
    status_field: str,
    status: str,
    uncertainty_path: str,
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    decision = effects[0][container]
    assert isinstance(decision, dict)
    decision[status_field] = status
    decision["uncertainty_id"] = None

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        f"effects.0.{uncertainty_path}" in error
        and "unresolved decision requires uncertainty_id" in error
        for error in errors
    )


@pytest.mark.parametrize(
    ("container", "status_field", "status"),
    [
        ("practical_digital_boundary", "status", "confirmed"),
        ("simulation", "status", "confirmed"),
    ],
)
def test_vfx_plan_confirmed_method_cannot_retain_uncertainty(
    repository_root: Path, container: str, status_field: str, status: str
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    decision = effects[0][container]
    assert isinstance(decision, dict)
    decision[status_field] = status
    decision["uncertainty_id"] = "ORBIT-UNC001"

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        f"effects.0.{container}.uncertainty_id" in error
        and "confirmed decision cannot retain uncertainty_id" in error
        for error in errors
    )


@pytest.mark.parametrize(
    ("container", "state_field", "state"),
    [
        ("clean_plate", "decision", "required"),
        ("tracking", "decision", "not-required"),
    ],
)
def test_vfx_plan_resolved_method_cannot_retain_uncertainty(
    repository_root: Path, container: str, state_field: str, state: str
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    decision = effects[0][container]
    assert isinstance(decision, dict)
    decision[state_field] = state
    decision["uncertainty_id"] = "ORBIT-UNC001"

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        f"effects.0.{container}.uncertainty_id" in error
        and "resolved decision cannot retain uncertainty_id" in error
        for error in errors
    )


def test_vfx_plan_requires_nonempty_uncertainty_ownership(
    repository_root: Path,
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    boundary = effects[0]["practical_digital_boundary"]
    assert isinstance(boundary, dict)
    boundary["status"] = "confirmed"
    boundary["uncertainty_id"] = None
    uncertainties = payload["uncertainties"]
    assert isinstance(uncertainties, list) and isinstance(uncertainties[0], dict)
    uncertainties[0]["effect_ids"] = []
    uncertainties[0]["shot_ids"] = []

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "uncertainties.0.effect_ids" in error and "should be non-empty" in error
        for error in errors
    )
    assert any(
        "uncertainties.0.shot_ids" in error and "should be non-empty" in error
        for error in errors
    )


def test_vfx_plan_rejects_uncertainty_shot_unrelated_to_its_effect(
    repository_root: Path,
) -> None:
    payload = valid_vfx_plan()
    uncertainties = payload["uncertainties"]
    assert isinstance(uncertainties, list) and isinstance(uncertainties[0], dict)
    uncertainties[0]["shot_ids"] = ["ORBIT-S01-SH001", "ORBIT-S01-SH002"]

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "uncertainties.0.shot_ids.1" in error
        and "ORBIT-S01-SH002 is not assigned to its effects" in error
        for error in errors
    )


@pytest.mark.parametrize(
    "forbidden",
    [
        "Use After Effects to composite the map.",
        "Send the plate to https://vendor.example/upload.",
        "Store API_TOKEN=secret123 for rendering.",
        "Budget $5,000 and schedule two days for cleanup.",
    ],
)
def test_vfx_plan_rejects_forbidden_operational_content(
    repository_root: Path, forbidden: str
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effects[0]["integration_assumptions"] = [forbidden]

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "effects.0.integration_assumptions.0" in error
        and "forbidden operational content" in error
        for error in errors
    )


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("source_context", "shots"), [None]),
        (("effects",), [None]),
        (("applicability",), [None]),
        (("uncertainties",), [None]),
    ],
)
def test_vfx_plan_malformed_nodes_never_traceback(
    repository_root: Path, path: tuple[str, ...], value: object
) -> None:
    payload = valid_vfx_plan()
    target: object = payload
    for component in path[:-1]:
        assert isinstance(target, dict)
        target = target[component]
    assert isinstance(target, dict)
    target[path[-1]] = value

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert errors


def test_vfx_plan_accepts_fully_animated_effect_without_live_capture(
    repository_root: Path,
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effect = effects[0]
    effect["practical_digital_boundary"] = {
        "status": "confirmed",
        "practical_scope": "No photographed practical element applies.",
        "digital_scope": "The energy effect is fully animated.",
        "uncertainty_id": None,
        "approval_id": "ORBIT-APR001",
    }
    effect["clean_plate"] = {
        "decision": "waived",
        "reason": "The supplied shot is fully animated.",
    }
    effect["tracking"] = {
        "decision": "not-required",
        "requirements": [],
    }
    effect["reference_capture"] = ["Use approved authored style and motion references."]
    effect["practical_interaction"] = ["Author light response within the animated scene."]
    effect["simulation"] = {
        "status": "confirmed",
        "requirements": ["Preserve the approved energy flow and dissipation behavior."],
        "uncertainty_id": None,
        "approval_id": "ORBIT-APR002",
    }
    effect["uncertainty_ids"] = ["ORBIT-UNC002"]
    payload["uncertainties"] = [
        {
            "uncertainty_id": "ORBIT-UNC002",
            "description": "Density variation remains unresolved across the energy effect.",
            "effect_ids": ["ORBIT-FX001"],
            "shot_ids": ["ORBIT-S01-SH001"],
            "owner": "human animation and VFX leads",
        }
    ]
    payload["approval_evidence"] = [
        {
            "approval_id": "ORBIT-APR001",
            "kind": "practical-digital-boundary",
            "effect_id": "ORBIT-FX001",
            "shot_ids": ["ORBIT-S01-SH001"],
            "practical_scope": "No photographed practical element applies.",
            "digital_scope": "The energy effect is fully animated.",
            "source_reference": "SRC-APPROVED-BOUNDARY",
        },
        {
            "approval_id": "ORBIT-APR002",
            "kind": "simulation",
            "effect_id": "ORBIT-FX001",
            "shot_ids": ["ORBIT-S01-SH001"],
            "requirements": [
                "Preserve the approved energy flow and dissipation behavior."
            ],
            "source_reference": "SRC-APPROVED-SIMULATION",
        },
    ]

    assert validate_artifact("vfx-plan", payload, repository_root) == []


def test_vfx_plan_accepts_live_action_cleanup_effect(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effect = effects[0]
    effect["visual_purpose"] = "Remove a photographed support without changing the key or contact shadow."
    effect["clean_plate"] = {
        "decision": "required",
        "reason": "Reveal the background behind the support.",
    }
    effect["tracking"] = {
        "decision": "not-required",
        "requirements": [],
    }

    assert validate_artifact("vfx-plan", payload, repository_root) == []


def test_vfx_plan_requires_all_five_source_fact_categories(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    shots = context["shots"]
    assert isinstance(shots, list) and isinstance(shots[0], dict)
    facts = shots[0]["supplied_facts"]
    assert isinstance(facts, list)
    facts.pop()

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "source_context.shots.0.supplied_facts" in error
        and "missing required category performance" in error
        for error in errors
    )


@pytest.mark.parametrize(
    "uncertainty_id",
    ["ORBIT-UNC000", "OTHER-UNC001", "ORBIT-UNC001-tail", "ORBIT-UNC001\n"],
)
def test_vfx_plan_requires_exact_positive_project_uncertainty_ids(
    repository_root: Path, uncertainty_id: str
) -> None:
    payload = valid_vfx_plan()
    uncertainties = payload["uncertainties"]
    assert isinstance(uncertainties, list) and isinstance(uncertainties[0], dict)
    uncertainties[0]["uncertainty_id"] = uncertainty_id

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "uncertainties.0.uncertainty_id" in error
        and "must match ORBIT-UNC###" in error
        for error in errors
    )


def test_vfx_plan_rejects_duplicate_uncertainty_id(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    uncertainties = payload["uncertainties"]
    assert isinstance(uncertainties, list) and isinstance(uncertainties[0], dict)
    uncertainties.append(copy.deepcopy(uncertainties[0]))

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "uncertainties.1.uncertainty_id" in error
        and "duplicate uncertainty ID ORBIT-UNC001" in error
        for error in errors
    )


def test_vfx_plan_unresolved_owner_link_is_bidirectional(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    uncertainties = payload["uncertainties"]
    assert isinstance(uncertainties, list) and isinstance(uncertainties[0], dict)
    uncertainties[0]["effect_ids"] = []

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "effects.0.practical_digital_boundary.uncertainty_id" in error
        and "ORBIT-UNC001 does not list effect ORBIT-FX001" in error
        for error in errors
    )


def test_vfx_plan_effect_classification_requires_effect(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    applicability = payload["applicability"]
    assert isinstance(effects, list)
    assert isinstance(applicability, list) and isinstance(applicability[0], dict)
    effects.clear()
    applicability[0]["effect_ids"] = []

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "applicability.0.effect_ids" in error
        and "effect classification requires at least one effect" in error
        for error in errors
    )


def test_vfx_plan_accepts_complete_no_vfx_inventory(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    payload["effects"] = []
    applicability = payload["applicability"]
    assert isinstance(applicability, list)
    for record in applicability:
        assert isinstance(record, dict)
        record["classification"] = "no-vfx"
        record["effect_ids"] = []
        record["reason"] = "No effect is requested for this supplied shot."
    payload["uncertainties"] = []

    assert validate_artifact("vfx-plan", payload, repository_root) == []


@pytest.mark.parametrize(
    ("container", "state_field", "state", "requirements", "expected"),
    [
        ("tracking", "decision", "required", [], "required tracking needs requirements"),
        ("tracking", "decision", "not-required", ["Track the table."], "not-required tracking must have no requirements"),
        ("simulation", "status", "confirmed", [], "confirmed simulation needs requirements"),
        ("simulation", "status", "not-required", ["Simulate sparks."], "not-required simulation must have no requirements"),
    ],
)
def test_vfx_plan_method_state_matches_requirements(
    repository_root: Path,
    container: str,
    state_field: str,
    state: str,
    requirements: list[str],
    expected: str,
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    record = effects[0][container]
    assert isinstance(record, dict)
    record[state_field] = state
    record["requirements"] = requirements
    record["uncertainty_id"] = None

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(f"effects.0.{container}.requirements" in error and expected in error for error in errors)


def test_vfx_plan_safety_handoff_cannot_claim_approval(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    safety = effects[0]["human_safety_handoff"]
    assert isinstance(safety, dict)
    safety["review"] = "The effect is safe and approved for performers."

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "effects.0.human_safety_handoff.review" in error
        and "safety handoff cannot claim approval" in error
        for error in errors
    )


def test_vfx_plan_rejects_foreign_project_scene_and_shot_lineage(
    repository_root: Path,
) -> None:
    payload = json.loads(
        json.dumps(valid_vfx_plan()).replace("ORBIT-S01", "FOREIGN-U09-S99")
    )

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "source_context.scenes.0.scene_id" in error
        and "'FOREIGN-U09-S99' must belong to project ORBIT" in error
        for error in errors
    )
    assert any(
        "source_context.shots.0.shot_id" in error
        and "'FOREIGN-U09-S99-SH001' must belong to project ORBIT" in error
        for error in errors
    )


def test_vfx_plan_exact_binds_metadata_category_to_source_fact(
    repository_root: Path,
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    metadata = effects[0]["camera_lens_lighting_metadata"]
    assert isinstance(metadata, list) and isinstance(metadata[0], dict)
    metadata[0]["category"] = "lens"

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "effects.0.camera_lens_lighting_metadata.0" in error
        and "must exactly match category, value, and source_reference" in error
        for error in errors
    )


def test_vfx_plan_requires_one_camera_lens_and_lighting_claim_per_effect_shot(
    repository_root: Path,
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    metadata = effects[0]["camera_lens_lighting_metadata"]
    assert isinstance(metadata, list) and isinstance(metadata[1], dict)
    metadata[1]["category"] = "camera"

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "effects.0.camera_lens_lighting_metadata" in error
        and "must contain exactly one lens claim for shot ORBIT-S01-SH001" in error
        for error in errors
    )


def test_vfx_plan_requires_source_bound_approval_for_approved_metadata(
    repository_root: Path,
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    metadata = effects[0]["camera_lens_lighting_metadata"]
    assert isinstance(metadata, list) and isinstance(metadata[0], dict)
    metadata[0].update(
        {
            "provenance_status": "approved",
            "value": "Fabricated approved camera motion.",
            "source_reference": "FABRICATED-APPROVAL",
        }
    )

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "effects.0.camera_lens_lighting_metadata.0" in error
        and "approved claim requires source-bound approval evidence" in error
        for error in errors
    )


def vfx_plan_with_confirmed_source_bound_decisions() -> dict[str, object]:
    """Build a plan whose decision evidence declares the approved content."""
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effect = effects[0]
    effect["practical_digital_boundary"] = {
        "status": "confirmed",
        "practical_scope": "Use only the approved interactive console light.",
        "digital_scope": "Render the map volume and its glitch digitally.",
        "uncertainty_id": None,
        "approval_id": "ORBIT-APR001",
    }
    effect["simulation"] = {
        "status": "confirmed",
        "requirements": [
            "Preserve the approved energy flow and dissipation behavior."
        ],
        "uncertainty_id": None,
        "approval_id": "ORBIT-APR002",
    }
    payload["approval_evidence"] = [
        {
            "approval_id": "ORBIT-APR001",
            "kind": "practical-digital-boundary",
            "effect_id": "ORBIT-FX001",
            "shot_ids": ["ORBIT-S01-SH001"],
            "practical_scope": "Use only the approved interactive console light.",
            "digital_scope": "Render the map volume and its glitch digitally.",
            "source_reference": "SRC-APPROVED-BOUNDARY",
        },
        {
            "approval_id": "ORBIT-APR002",
            "kind": "simulation",
            "effect_id": "ORBIT-FX001",
            "shot_ids": ["ORBIT-S01-SH001"],
            "requirements": [
                "Preserve the approved energy flow and dissipation behavior."
            ],
            "source_reference": "SRC-APPROVED-SIMULATION",
        },
    ]
    return payload


def test_vfx_plan_confirmed_simulation_requirements_exactly_bind_approval_evidence(
    repository_root: Path,
) -> None:
    payload = vfx_plan_with_confirmed_source_bound_decisions()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    simulation = effects[0]["simulation"]
    assert isinstance(simulation, dict)
    simulation["requirements"] = ["A different fabricated approved behavior."]

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert (
        "effects.0.simulation.requirements: must exactly match approval evidence "
        "ORBIT-APR002"
    ) in errors


def test_vfx_plan_confirmed_boundary_scopes_exactly_bind_approval_evidence(
    repository_root: Path,
) -> None:
    payload = vfx_plan_with_confirmed_source_bound_decisions()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    boundary = effects[0]["practical_digital_boundary"]
    assert isinstance(boundary, dict)
    boundary["practical_scope"] = "A different fabricated practical scope."
    boundary["digital_scope"] = "A different fabricated digital scope."

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert (
        "effects.0.practical_digital_boundary.practical_scope: must exactly "
        "match approval evidence ORBIT-APR001"
    ) in errors
    assert (
        "effects.0.practical_digital_boundary.digital_scope: must exactly "
        "match approval evidence ORBIT-APR001"
    ) in errors


@pytest.mark.parametrize(
    ("container", "status_field"),
    [
        ("practical_digital_boundary", "status"),
        ("simulation", "status"),
    ],
)
def test_vfx_plan_confirmed_decision_requires_source_bound_approval_evidence(
    repository_root: Path, container: str, status_field: str
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    decision = effects[0][container]
    assert isinstance(decision, dict)
    decision[status_field] = "confirmed"
    decision["uncertainty_id"] = None
    if container == "simulation":
        decision["requirements"] = ["Preserve the supplied energy behavior."]

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        f"effects.0.{container}" in error
        and "confirmed decision requires source-bound approval evidence" in error
        for error in errors
    )


def test_vfx_plan_rejects_unreal_engine_prescription(
    repository_root: Path,
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effects[0]["integration_assumptions"] = [
        "Use Unreal Engine to build the creature extension."
    ]

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert (
        "effects.0.integration_assumptions.0: forbidden operational content"
        in errors
    )


def test_vfx_plan_allows_fictional_fusion_energy(repository_root: Path) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effects[0]["integration_assumptions"] = [
        "Depict fusion energy inside the fictional reactor."
    ]

    assert validate_artifact("vfx-plan", payload, repository_root) == []


def test_vfx_plan_required_safety_handoff_rejects_guarantee_and_waived_review(
    repository_root: Path,
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    safety = effects[0]["human_safety_handoff"]
    assert isinstance(safety, dict)
    safety["review"] = (
        "The artifact guarantees a risk-free method and needs no specialist review."
    )

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert (
        "effects.0.human_safety_handoff.review: required safety handoff cannot "
        "guarantee safety outcomes"
    ) in errors
    assert (
        "effects.0.human_safety_handoff.review: required safety handoff cannot "
        "claim risk-free method"
    ) in errors
    assert (
        "effects.0.human_safety_handoff.review: required safety handoff cannot "
        "waive specialist review"
    ) in errors
    assert (
        "effects.0.human_safety_handoff.review: required safety handoff must "
        "state qualified human review"
    ) in errors


def vfx_plan_with_supplied_fully_animated_boundary() -> dict[str, object]:
    """Build an all-authored boundary from supplied source evidence."""
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effect = effects[0]
    effect["practical_digital_boundary"] = {
        "status": "confirmed",
        "practical_scope": "No photographed practical element applies.",
        "digital_scope": "The energy effect is fully animated.",
        "uncertainty_id": None,
        "supplied_evidence_id": "ORBIT-SBE001",
    }
    effect["clean_plate"] = {
        "decision": "waived",
        "reason": "The supplied shot is fully animated.",
    }
    effect["tracking"] = {
        "decision": "not-required",
        "requirements": [],
    }
    uncertainties = payload["uncertainties"]
    assert isinstance(uncertainties, list) and isinstance(uncertainties[0], dict)
    uncertainties[0]["description"] = "Density variation remains unresolved."
    payload["supplied_boundary_evidence"] = [
        {
            "supplied_evidence_id": "ORBIT-SBE001",
            "effect_id": "ORBIT-FX001",
            "shot_ids": ["ORBIT-S01-SH001"],
            "practical_scope": "No photographed practical element applies.",
            "digital_scope": "The energy effect is fully animated.",
            "source_reference": "SRC-S01",
        }
    ]
    return payload


def test_vfx_plan_accepts_supplied_fully_animated_boundary_without_approval_or_uncertainty(
    repository_root: Path,
) -> None:
    payload = vfx_plan_with_supplied_fully_animated_boundary()

    assert validate_artifact("vfx-plan", payload, repository_root) == []


def test_vfx_plan_rejects_supplied_boundary_with_unregistered_source_reference(
    repository_root: Path,
) -> None:
    payload = vfx_plan_with_supplied_fully_animated_boundary()
    evidence = payload["supplied_boundary_evidence"]
    assert isinstance(evidence, list) and isinstance(evidence[0], dict)
    evidence[0]["source_reference"] = "FABRICATED-BOUNDARY-SOURCE"

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert (
        "supplied_boundary_evidence.0.source_reference: "
        "FABRICATED-BOUNDARY-SOURCE is not declared in source_context"
    ) in errors


def test_vfx_plan_rejects_confirmed_boundary_with_both_evidence_paths(
    repository_root: Path,
) -> None:
    payload = vfx_plan_with_confirmed_source_bound_decisions()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    boundary = effects[0]["practical_digital_boundary"]
    assert isinstance(boundary, dict)
    boundary["supplied_evidence_id"] = "ORBIT-SBE001"
    payload["supplied_boundary_evidence"] = [
        {
            "supplied_evidence_id": "ORBIT-SBE001",
            "effect_id": "ORBIT-FX001",
            "shot_ids": ["ORBIT-S01-SH001"],
            "practical_scope": "Use only the approved interactive console light.",
            "digital_scope": "Render the map volume and its glitch digitally.",
            "source_reference": "SRC-S01",
        }
    ]

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert (
        "effects.0.practical_digital_boundary: confirmed decision cannot retain "
        "both approval_id and supplied_evidence_id"
    ) in errors


def test_vfx_plan_requires_effect_level_inverse_uncertainty_link(
    repository_root: Path,
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effects[0].pop("uncertainty_ids")

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "effects.0.uncertainty_ids" in error
        and "must list ORBIT-UNC001" in error
        for error in errors
    )


@pytest.mark.parametrize(
    "vendor", ["Cinema 4D", "DaVinci Resolve", "Avid", "Fusion"]
)
def test_vfx_plan_rejects_vendor_prescriptions_added_to_the_covered_list(
    repository_root: Path, vendor: str
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effects[0]["integration_assumptions"] = [
        f"Use {vendor} to complete the effect."
    ]

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "effects.0.integration_assumptions.0" in error
        and "forbidden operational content" in error
        for error in errors
    )


@pytest.mark.parametrize(
    "assumption",
    [
        "Use Fusion to composite the effect.",
        "Composite the effect in Fusion.",
        "Composite the effect with Fusion.",
        "Composite the effect via Fusion.",
    ],
)
def test_vfx_plan_rejects_fusion_in_explicit_tool_context(
    repository_root: Path, assumption: str
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effects[0]["integration_assumptions"] = [assumption]

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert (
        "effects.0.integration_assumptions.0: forbidden operational content"
        in errors
    )


@pytest.mark.parametrize(
    "assumption",
    [
        "Use fusion energy as the fictional reactor motif.",
        "Use fusion reaction as the fictional reactor motif.",
        "Use fusion reactor imagery as the fictional motif.",
    ],
)
def test_vfx_plan_allows_fusion_as_fictional_motif_after_use(
    repository_root: Path, assumption: str
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effects[0]["integration_assumptions"] = [assumption]

    assert validate_artifact("vfx-plan", payload, repository_root) == []


@pytest.mark.parametrize(
    "review",
    [
        "A qualified human reviewer can guarantee the outcome.",
        "A qualified human reviewer will guarantee the outcome.",
        "A qualified human reviewer does guarantee the outcome.",
        "A qualified human reviewer guarantees the outcome.",
        "A qualified human reviewer guaranteed the outcome.",
        "A qualified human reviewer is guaranteeing the outcome.",
    ],
)
def test_vfx_plan_rejects_affirmative_safety_guarantee_inflections(
    repository_root: Path, review: str
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    safety = effects[0]["human_safety_handoff"]
    assert isinstance(safety, dict)
    safety["review"] = review

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert (
        "effects.0.human_safety_handoff.review: required safety handoff cannot "
        "guarantee safety outcomes"
    ) in errors


@pytest.mark.parametrize(
    "review",
    [
        "A qualified human reviewer does not guarantee the outcome.",
        "A qualified human reviewer cannot guarantee the outcome.",
        "A qualified human reviewer will never guarantee the outcome.",
    ],
)
def test_vfx_plan_allows_negated_safety_guarantee_disclaimers(
    repository_root: Path, review: str
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    safety = effects[0]["human_safety_handoff"]
    assert isinstance(safety, dict)
    safety["review"] = review

    assert validate_artifact("vfx-plan", payload, repository_root) == []


@pytest.mark.parametrize(
    "review",
    [
        "A qualified human reviewer says review is not required for this method.",
        "A qualified human reviewer need not review this method.",
        "A qualified human reviewer says no review needed for this method.",
    ],
)
def test_vfx_plan_rejects_required_safety_review_negations(
    repository_root: Path, review: str
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    safety = effects[0]["human_safety_handoff"]
    assert isinstance(safety, dict)
    safety["review"] = review

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert (
        "effects.0.human_safety_handoff.review: required safety handoff cannot "
        "waive specialist review"
    ) in errors


@pytest.mark.parametrize(
    "review",
    [
        "No qualified human review is needed for this method.",
        "No qualified human review is required for this method.",
        "No qualified human review is necessary for this method.",
        "No human safety review is needed for this method.",
        "No human safety review is required for this method.",
        "No human safety review is necessary for this method.",
        "No specialist review is needed; qualified human safety review is described only for context.",
        "No specialist review is required for this method.",
        "No specialist review is necessary for this method.",
        "Qualified human review is not needed for this method.",
        "Qualified human review is not required for this method.",
        "Qualified human review is not necessary for this method.",
        "Specialist review is not needed for this method.",
        "Specialist review is not required for this method.",
        "Specialist review is not necessary for this method.",
        "No review needed for this method.",
    ],
)
def test_vfx_plan_rejects_required_safety_review_negation_variants(
    repository_root: Path, review: str
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    safety = effects[0]["human_safety_handoff"]
    assert isinstance(safety, dict)
    safety["review"] = review

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert (
        "effects.0.human_safety_handoff.review: required safety handoff cannot "
        "waive specialist review"
    ) in errors


@pytest.mark.parametrize(
    ("location", "replacement"),
    [
        ("integration_assumptions", "Resolve the hand holdout before review."),
        (
            "human_safety_handoff",
            "The planner does not declare the marker method safe; qualified human review is required.",
        ),
    ],
)
def test_vfx_plan_allows_non_prescriptive_resolve_and_negated_safety_disclaimer(
    repository_root: Path, location: str, replacement: str
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    effect = effects[0]
    if location == "integration_assumptions":
        effect[location] = [replacement]
    else:
        safety = effect[location]
        assert isinstance(safety, dict)
        safety["review"] = replacement

    assert validate_artifact("vfx-plan", payload, repository_root) == []


def test_vfx_plan_accepts_hyphenated_qualified_human_safety_reviewer(
    repository_root: Path,
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    safety = effects[0]["human_safety_handoff"]
    assert isinstance(safety, dict)
    safety["review"] = (
        "A qualified human-safety reviewer must review any water interaction "
        "and any marker or reference activity near Lena; this plan does not "
        "claim approval."
    )

    assert validate_artifact("vfx-plan", payload, repository_root) == []


def test_vfx_plan_rejects_planner_safety_approval_and_waived_human_review(
    repository_root: Path,
) -> None:
    payload = valid_vfx_plan()
    effects = payload["effects"]
    assert isinstance(effects, list) and isinstance(effects[0], dict)
    safety = effects[0]["human_safety_handoff"]
    assert isinstance(safety, dict)
    safety["review"] = (
        "The planner approves the marker method and no human review is necessary."
    )

    errors = validate_artifact("vfx-plan", payload, repository_root)

    assert any(
        "effects.0.human_safety_handoff.review" in error
        and "planner cannot approve safety method" in error
        for error in errors
    )
    assert any(
        "effects.0.human_safety_handoff.review" in error
        and "human review cannot be waived" in error
        for error in errors
    )


def test_vfx_plan_template_validates_live_contract(repository_root: Path) -> None:
    template_path = (
        repository_root
        / ".agents"
        / "skills"
        / "vfx-planner"
        / "assets"
        / "vfx-plan.template.json"
    )
    template = json.loads(template_path.read_text(encoding="utf-8"))

    assert validate_artifact("vfx-plan", template, repository_root) == []


def test_valid_edit_plan_passes_schema_and_semantic_validation(
    repository_root: Path,
) -> None:
    assert validate_artifact("edit-plan", valid_edit_plan(), repository_root) == []


def test_edit_plan_rejects_duplicate_segment_ids(repository_root: Path) -> None:
    payload = valid_edit_plan()
    segments = payload["segments"]
    assert isinstance(segments, list)
    first = segments[0]
    second = segments[1]
    assert isinstance(first, dict)
    assert isinstance(second, dict)
    second["segment_id"] = first["segment_id"]

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any("segments.1.segment_id: duplicate segment ID" in error for error in errors)


def test_edit_plan_rejects_segment_id_outside_declared_unit(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    segments = payload["segments"]
    assert isinstance(segments, list)
    first = segments[0]
    assert isinstance(first, dict)
    first["segment_id"] = "LANTERN-U02-ED001"

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "segments.0.segment_id: 'LANTERN-U02-ED001' must match LANTERN-U01-ED###"
        in error
        for error in errors
    )


def test_edit_plan_rejects_unknown_shot_ids_in_segments_and_alternatives(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    segments = payload["segments"]
    assert isinstance(segments, list)
    first = segments[0]
    assert isinstance(first, dict)
    first["source_shot_ids"] = ["LANTERN-U01-S01-SH999"]
    alternatives = first["alternatives"]
    assert isinstance(alternatives, list)
    alternative = alternatives[0]
    assert isinstance(alternative, dict)
    alternative["source_shot_ids"] = ["LANTERN-U01-S02-SH001"]

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any("segments.0.source_shot_ids.0: unknown shot ID" in error for error in errors)
    assert any(
        "segments.0.alternatives.0.source_shot_ids.0: unknown shot ID" in error
        for error in errors
    )


def test_edit_plan_rejects_unknown_media_ids_in_segments_and_alternatives(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    segments = payload["segments"]
    assert isinstance(segments, list)
    first = segments[0]
    assert isinstance(first, dict)
    first["source_media_ids"] = ["LANTERN-MD999"]
    alternatives = first["alternatives"]
    assert isinstance(alternatives, list)
    alternative = alternatives[0]
    assert isinstance(alternative, dict)
    alternative["source_media_ids"] = ["LANTERN-MD998"]

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any("segments.0.source_media_ids.0: unknown media ID" in error for error in errors)
    assert any(
        "segments.0.alternatives.0.source_media_ids.0: unknown media ID" in error
        for error in errors
    )


def test_edit_plan_rejects_nonascending_assembly_order(repository_root: Path) -> None:
    payload = valid_edit_plan()
    segments = payload["segments"]
    assert isinstance(segments, list)
    second = segments[1]
    assert isinstance(second, dict)
    second["assembly_order"] = 1

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "segments.1.assembly_order: must be greater than the previous assembly order"
        in error
        for error in errors
    )


def test_edit_plan_rejects_exact_timecodes_for_planned_segments(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    segments = payload["segments"]
    assert isinstance(segments, list)
    second = segments[1]
    assert isinstance(second, dict)
    intent = second["in_out_intent"]
    assert isinstance(intent, dict)
    intent["exact_source_in"] = "01:00:20:00"
    intent["exact_source_out"] = "01:00:23:12"

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "segments.1.in_out_intent: exact source timecodes require inspected evidence"
        in error
        for error in errors
    )


def test_edit_plan_rejects_picture_lock_without_inspected_evidence(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    segments = payload["segments"]
    assert isinstance(segments, list)
    second = segments[1]
    assert isinstance(second, dict)
    second["lock_status"] = "picture-locked"

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "segments.1.lock_status: picture-locked requires inspected evidence" in error
        for error in errors
    )


def test_edit_plan_rejects_inspected_claim_without_reviewed_media(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    segments = payload["segments"]
    assert isinstance(segments, list)
    second = segments[1]
    assert isinstance(second, dict)
    second["evidence_status"] = "inspected"

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "segments.1.evidence_status: inspected requires at least one source media ID"
        in error
        for error in errors
    )


def test_edit_plan_template_is_schema_and_semantically_valid(
    repository_root: Path,
) -> None:
    path = (
        repository_root
        / ".agents"
        / "skills"
        / "film-editor"
        / "assets"
        / "edit-plan.template.json"
    )
    template = json.loads(path.read_text(encoding="utf-8"))

    assert validate_artifact("edit-plan", template, repository_root) == []


def add_current_edit_lock_decision(payload: dict[str, object]) -> None:
    source_context = payload["source_context"]
    segments = payload["segments"]
    assert isinstance(source_context, dict)
    assert isinstance(segments, list) and isinstance(segments[0], dict)
    lock_decisions = source_context["lock_decisions"]
    assert isinstance(lock_decisions, list)
    lock_decisions.append(
        {
            "lock_decision_id": "LANTERN-LK001",
            "segment_id": "LANTERN-U01-ED001",
            "source_media_ids": ["LANTERN-MD001"],
            "decision": "picture-locked",
            "current": True,
            "source_reference": (
                "post/edit-lock-decisions.json#/decisions/LANTERN-LK001"
            ),
        }
    )
    segments[0]["lock_status"] = "picture-locked"
    segments[0]["lock_decision_id"] = "LANTERN-LK001"


def test_edit_plan_accepts_current_source_bound_picture_lock(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    add_current_edit_lock_decision(payload)

    assert validate_artifact("edit-plan", payload, repository_root) == []


def test_edit_plan_rejects_inspected_picture_lock_without_supplied_decision(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    segments = payload["segments"]
    assert isinstance(segments, list) and isinstance(segments[0], dict)
    segments[0]["lock_status"] = "picture-locked"

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "segments.0.lock_status: picture-locked requires a supplied current lock decision"
        in error
        for error in errors
    )


def test_edit_plan_rejects_picture_lock_for_human_review_media(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    source_context = payload["source_context"]
    assert isinstance(source_context, dict)
    media_items = source_context["media_items"]
    assert isinstance(media_items, list) and isinstance(media_items[0], dict)
    media_items[0]["review_status"] = "human-review"
    add_current_edit_lock_decision(payload)

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "segments.0.lock_status: picture-locked requires approved source media; "
        "LANTERN-MD001 is human-review" in error
        for error in errors
    )


def test_edit_plan_rejects_noncurrent_lock_decision(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    add_current_edit_lock_decision(payload)
    source_context = payload["source_context"]
    assert isinstance(source_context, dict)
    decisions = source_context["lock_decisions"]
    assert isinstance(decisions, list) and isinstance(decisions[0], dict)
    decisions[0]["current"] = False

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "source_context.lock_decisions.0.current" in error
        and "True was expected" in error
        for error in errors
    )


def test_edit_plan_rejects_lock_decision_with_inexact_media_binding(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    source_context = payload["source_context"]
    segments = payload["segments"]
    assert isinstance(source_context, dict)
    assert isinstance(segments, list) and isinstance(segments[0], dict)
    media_items = source_context["media_items"]
    assert isinstance(media_items, list)
    media_items.append(
        {
            "media_id": "LANTERN-MD002",
            "shot_id": "LANTERN-U01-S01-SH002",
            "review_status": "approved",
            "source_reference": "production/media-review-report.json#/items/1",
        }
    )
    segments[0]["source_shot_ids"] = [
        "LANTERN-U01-S01-SH001",
        "LANTERN-U01-S01-SH002",
    ]
    segments[0]["source_media_ids"] = ["LANTERN-MD001", "LANTERN-MD002"]
    add_current_edit_lock_decision(payload)

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "segments.0.lock_decision_id: LANTERN-LK001 must bind exactly the "
        "segment source media IDs" in error
        for error in errors
    )


def test_edit_plan_rejects_timing_evidence_boundary_mismatch(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    segments = payload["segments"]
    assert isinstance(segments, list) and isinstance(segments[0], dict)
    intent = segments[0]["in_out_intent"]
    assert isinstance(intent, dict)
    intent["exact_source_out"] = "01:00:18:03"

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "segments.0.timing_evidence_id: LANTERN-TM001 does not establish exact "
        "boundaries 01:00:12:08-01:00:18:03" in error
        for error in errors
    )


def test_edit_plan_rejects_planned_timecode_syntax_in_prose(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    segments = payload["segments"]
    assert isinstance(segments, list) and isinstance(segments[1], dict)
    segments[1]["rhythm"] = "Cut at 01:00:20:00 after the comparison."

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "segments.1.rhythm: exact timecode 01:00:20:00 requires applicable "
        "timing evidence" in error
        for error in errors
    )


def test_edit_plan_rejects_unbound_inspected_timecode_syntax_in_prose(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    segments = payload["segments"]
    assert isinstance(segments, list) and isinstance(segments[0], dict)
    transition = segments[0]["transition"]
    assert isinstance(transition, dict)
    transition["intent"] = "Cut at 01:00:17:00 to preserve the qualifying phrase."

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "segments.0.transition.intent: exact timecode 01:00:17:00 is not "
        "established by LANTERN-TM001" in error
        for error in errors
    )


def test_edit_plan_accepts_safe_qualitative_timing_language(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    segments = payload["segments"]
    assert isinstance(segments, list) and isinstance(segments[1], dict)
    segments[1]["rhythm"] = (
        "Hold for two breaths and cut only after the complete sentence ends."
    )
    segments[1]["motion"] = "Leave on the next supplied gesture if one is inspected."

    assert validate_artifact("edit-plan", payload, repository_root) == []


def test_edit_plan_rejects_primary_media_to_shot_mismatch(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    segments = payload["segments"]
    assert isinstance(segments, list) and isinstance(segments[0], dict)
    segments[0]["source_shot_ids"] = ["LANTERN-U01-S01-SH002"]

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "segments.0.source_media_ids.0: media ID LANTERN-MD001 belongs to "
        "unreferenced shot LANTERN-U01-S01-SH001" in error
        for error in errors
    )


def test_edit_plan_rejects_alternative_media_to_shot_mismatch(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    segments = payload["segments"]
    assert isinstance(segments, list) and isinstance(segments[0], dict)
    alternatives = segments[0]["alternatives"]
    assert isinstance(alternatives, list) and isinstance(alternatives[0], dict)
    alternatives[0]["source_media_ids"] = ["LANTERN-MD001"]

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "segments.0.alternatives.0.source_media_ids.0: media ID LANTERN-MD001 "
        "belongs to unreferenced shot LANTERN-U01-S01-SH001" in error
        for error in errors
    )


def test_edit_plan_rejects_overlapping_but_inexact_project_ownership(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    payload["project_id"] = "LANT"

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "unit_id: 'LANTERN-U01' must match declared project LANT as LANT-U## or LANT-E##"
        in error
        for error in errors
    )
    assert any(
        "source_context.media_items.0.media_id: 'LANTERN-MD001' must match LANT-MD###"
        in error
        for error in errors
    )


def test_edit_plan_accepts_hyphenated_exact_project_ownership(
    repository_root: Path,
) -> None:
    document = json.dumps(valid_edit_plan()).replace("LANTERN", "NORTH-LANTERN")
    payload = json.loads(document)

    assert validate_artifact("edit-plan", payload, repository_root) == []


def test_edit_plan_rejects_scene_outside_unit_and_shot_scene_mismatch(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    source_context = payload["source_context"]
    assert isinstance(source_context, dict)
    shots = source_context["shots"]
    assert isinstance(shots, list)
    assert isinstance(shots[0], dict) and isinstance(shots[1], dict)
    shots[0]["scene_id"] = "LANTERN-U02-S01"
    shots[1]["scene_id"] = "LANTERN-U01-S02"

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "source_context.shots.0.scene_id: 'LANTERN-U02-S01' must belong to unit "
        "LANTERN-U01" in error
        for error in errors
    )
    assert any(
        "source_context.shots.0.shot_id: LANTERN-U01-S01-SH001 does not match "
        "declared scene LANTERN-U02-S01" in error
        for error in errors
    )
    assert any(
        "source_context.shots.1.shot_id: LANTERN-U01-S01-SH002 does not match "
        "declared scene LANTERN-U01-S02" in error
        for error in errors
    )


def test_edit_plan_duplicate_registry_and_order_diagnostics_are_deterministic(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    source_context = payload["source_context"]
    segments = payload["segments"]
    assert isinstance(source_context, dict) and isinstance(segments, list)
    shots = source_context["shots"]
    media_items = source_context["media_items"]
    assert isinstance(shots, list) and isinstance(media_items, list)
    duplicate_shot = copy.deepcopy(shots[0])
    duplicate_media = copy.deepcopy(media_items[0])
    assert isinstance(duplicate_shot, dict) and isinstance(duplicate_media, dict)
    duplicate_shot["source_reference"] = "other-shot-list.json#/shots/9"
    duplicate_media["source_reference"] = "other-review.json#/items/9"
    shots.append(duplicate_shot)
    media_items.append(duplicate_media)
    assert isinstance(segments[1], dict)
    segments[1]["assembly_order"] = 1

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert errors == [
        "source_context.shots.2.shot_id: duplicate supplied shot ID "
        "LANTERN-U01-S01-SH001",
        "source_context.media_items.1.media_id: duplicate supplied media ID "
        "LANTERN-MD001",
        "segments.1.assembly_order: must be greater than the previous assembly order",
    ]


def test_edit_plan_rejects_lock_decision_bound_to_different_existing_segment(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    add_current_edit_lock_decision(payload)
    source_context = payload["source_context"]
    assert isinstance(source_context, dict)
    lock_decisions = source_context["lock_decisions"]
    assert isinstance(lock_decisions, list) and isinstance(lock_decisions[0], dict)
    lock_decisions[0]["segment_id"] = "LANTERN-U01-ED002"

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "segments.0.lock_decision_id: LANTERN-LK001 must bind segment "
        "LANTERN-U01-ED001" in error
        for error in errors
    )


def test_edit_plan_rejects_timing_evidence_bound_to_different_registered_media(
    repository_root: Path,
) -> None:
    payload = valid_edit_plan()
    source_context = payload["source_context"]
    assert isinstance(source_context, dict)
    media_items = source_context["media_items"]
    timing_evidence = source_context["timing_evidence"]
    assert isinstance(media_items, list)
    assert isinstance(timing_evidence, list) and isinstance(timing_evidence[0], dict)
    media_items.append(
        {
            "media_id": "LANTERN-MD002",
            "shot_id": "LANTERN-U01-S01-SH002",
            "review_status": "approved",
            "source_reference": "production/media-review-report.json#/items/1",
        }
    )
    timing_evidence[0]["media_id"] = "LANTERN-MD002"

    errors = validate_artifact("edit-plan", payload, repository_root)

    assert any(
        "segments.0.timing_evidence_id: LANTERN-TM001 belongs to "
        "unreferenced media LANTERN-MD002" in error
        for error in errors
    )


def valid_sound_post_plan() -> dict[str, object]:
    responsibilities = [
        "dialogue-edit",
        "repair",
        "adr",
        "foley",
        "ambience",
        "effects",
        "sound-design",
        "transition",
        "intentional-silence",
        "premix-group",
        "automation",
        "mix-priority",
        "accessibility",
        "loudness-assumption",
        "mastering",
    ]
    items: list[dict[str, object]] = []
    for index, responsibility in enumerate(responsibilities, start=1):
        item: dict[str, object] = {
            "sound_post_item_id": f"LANTERN-U01-PS{index:03d}",
            "responsibility": responsibility,
            "edit_segment_ids": ["LANTERN-U01-ED001"],
            "dramatic_purpose": "Protect the scene's quiet technical tension.",
            "perspective": {
                "mode": "spatial-focus",
                "intent": "Keep the listener inside the confined interior.",
            },
            "state": "planned",
            "instruction": "Complete this work only after the named source inputs are supplied.",
        }
        if responsibility == "intentional-silence":
            item["dramatic_purpose"] = "Create a held breath before the subjective reveal."
            item["perspective"] = {
                "mode": "subjective",
                "intent": "Hold the listener in the character's narrowed attention.",
            }
        if responsibility in {"dialogue-edit", "repair", "adr", "mix-priority"}:
            item["perspective"] = {
                "mode": "dialogue-focus",
                "intent": "Keep story-critical speech intelligible in the intended space.",
            }
        if responsibility == "accessibility":
            item["perspective"] = {
                "mode": "accessibility",
                "intent": "Identify the sound information an access handoff must preserve.",
            }
        if responsibility == "loudness-assumption":
            item["delivery_assumption"] = (
                "Confirm the distributor's target loudness specification before mixing."
            )
        items.append(item)

    return {
        "schema_version": "2.0",
        "project_id": "LANTERN",
        "unit_id": "LANTERN-U01",
        "project_format": "short",
        "source_context": {
            "edit_plan_reference": "post/LANTERN-U01/edit-plan.json",
            "edit_segments": [
                {
                    "segment_id": "LANTERN-U01-ED001",
                    "source_reference": "post/LANTERN-U01/edit-plan.json#/segments/0",
                }
            ],
            "measurement_evidence": [],
            "inspection_evidence": [],
        },
        "items": items,
        "assumptions": [
            "No production audio, mix session, or delivery specification is supplied."
        ],
        "uncertainties": [
            "Repair, ADR, sync, and compliance remain unresolved until source material is supplied."
        ],
    }


def test_valid_sound_post_plan_binds_typed_work_to_declared_edit_segments(
    repository_root: Path,
) -> None:
    assert validate_artifact("sound-post-plan", valid_sound_post_plan(), repository_root) == []


def test_sound_post_plan_template_is_valid(repository_root: Path) -> None:
    path = (
        repository_root
        / ".agents"
        / "skills"
        / "sound-post-designer"
        / "assets"
        / "sound-post-plan.template.json"
    )
    template = json.loads(path.read_text(encoding="utf-8"))

    assert validate_artifact("sound-post-plan", template, repository_root) == []


def test_music_plan_template_is_valid(repository_root: Path) -> None:
    path = repository_root / ".agents" / "skills" / "music-story-designer" / "assets" / "music-plan.template.json"
    template = json.loads(path.read_text(encoding="utf-8"))
    assert validate_artifact("music-plan", template, repository_root) == []


def test_vfx_post_plan_template_is_valid(repository_root: Path) -> None:
    path = repository_root / ".agents" / "skills" / "vfx-post-supervisor" / "assets" / "vfx-post-plan.template.json"
    template = json.loads(path.read_text(encoding="utf-8"))
    assert validate_artifact("vfx-post-plan", template, repository_root) == []


def test_color_plan_template_is_valid(repository_root: Path) -> None:
    path = repository_root / ".agents" / "skills" / "color-grading-designer" / "assets" / "color-plan.template.json"
    template = json.loads(path.read_text(encoding="utf-8"))
    assert validate_artifact("color-plan", template, repository_root) == []


def test_titles_captions_plan_template_is_valid(repository_root: Path) -> None:
    path = repository_root / ".agents" / "skills" / "titles-captions-designer" / "assets" / "titles-captions-plan.template.json"
    template = json.loads(path.read_text(encoding="utf-8"))
    assert validate_artifact("titles-captions-plan", template, repository_root) == []


def test_mastering_qc_plan_template_is_valid(repository_root: Path) -> None:
    path = repository_root / ".agents" / "skills" / "mastering-qc-supervisor" / "assets" / "mastering-qc-plan.template.json"
    template = json.loads(path.read_text(encoding="utf-8"))
    assert validate_artifact("mastering-qc-plan", template, repository_root) == []


def test_sound_post_plan_rejects_unknown_and_uncovered_edit_segments(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    source_context = payload["source_context"]
    assert isinstance(source_context, dict)
    edit_segments = source_context["edit_segments"]
    assert isinstance(edit_segments, list)
    edit_segments.append(
        {
            "segment_id": "LANTERN-U01-ED002",
            "source_reference": "post/LANTERN-U01/edit-plan.json#/segments/1",
        }
    )
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["edit_segment_ids"] = ["LANTERN-U01-ED999"]

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any("items.0.edit_segment_ids.0: unknown edit segment ID LANTERN-U01-ED999" in error for error in errors)
    assert any("source_context.edit_segments: declared edit segment LANTERN-U01-ED002 is not covered" in error for error in errors)


def test_sound_post_plan_rejects_duplicate_item_ids(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list)
    assert isinstance(items[1], dict)
    items[1]["sound_post_item_id"] = "LANTERN-U01-PS001"

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any(
        "items.1.sound_post_item_id: duplicate sound post item ID LANTERN-U01-PS001"
        in error
        for error in errors
    )


def test_sound_post_plan_rejects_intentional_silence_without_dramatic_purpose(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[8], dict)
    items[8]["dramatic_purpose"] = ""

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any("items.8.dramatic_purpose" in error for error in errors)


def test_sound_post_plan_requires_exact_measurement_evidence(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["numeric_measurements"] = [
        {
            "measurement_id": "LANTERN-MS001",
            "category": "loudness",
            "metric": "integrated-loudness",
            "value": -24.0,
            "unit": "LUFS",
            "claim": "Measured dialogue loudness.",
        }
    ]

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any("items.0.numeric_measurements.0.measurement_id: unknown measurement evidence ID LANTERN-MS001" in error for error in errors)


def test_sound_post_plan_rejects_assertive_free_text_claims_but_allows_safe_qualifications(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["instruction"] = "The final master was delivered, approved, and compliant."

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any("items.0.instruction: assertive prohibited claim" in error for error in errors)

    safe_payload = valid_sound_post_plan()
    safe_payload["assumptions"] = [
        "No audio was measured; the target assumption awaits a delivery specification."
    ]
    safe_payload["uncertainties"] = ["Mix approval is awaiting approval from the authorized reviewer."]

    assert validate_artifact("sound-post-plan", safe_payload, repository_root) == []


def test_sound_post_plan_rejects_bare_completion_and_approval_claims_in_free_text(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[14], dict)
    items[14]["instruction"] = "Approval received; mastering complete; delivery sent."

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any("items.14.instruction: assertive prohibited claim" in error for error in errors)


def test_sound_post_plan_rejects_prohibited_claims_in_perspective_intent(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["perspective"] = {
        "mode": "dialogue-focus",
        "intent": "The dialogue master was delivered.",
    }

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any("items.0.perspective.intent: assertive prohibited claim" in error for error in errors)


def test_sound_post_plan_rejects_measurement_unit_syntax_outside_structured_measurements(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["instruction"] = "Keep the dialogue under -24 LUFS after the planned pass."

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any("items.0.instruction: measurement-unit syntax is allowed only in numeric_measurements" in error for error in errors)

    safe_payload = valid_sound_post_plan()
    safe_items = safe_payload["items"]
    assert isinstance(safe_items, list) and isinstance(safe_items[0], dict)
    safe_items[0]["instruction"] = "Use three layers around ED001; no loudness was measured."

    assert validate_artifact("sound-post-plan", safe_payload, repository_root) == []


def test_sound_post_plan_binds_metric_category_value_and_unit_to_evidence(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    source_context = payload["source_context"]
    assert isinstance(source_context, dict)
    source_context["measurement_evidence"] = [
        {
            "measurement_id": "LANTERN-MS001",
            "category": "loudness",
            "metric": "integrated-loudness",
            "value": -24.0,
            "unit": "LUFS",
            "source_reference": "audio/LANTERN-U01-mix.wav#metering",
        }
    ]
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["numeric_measurements"] = [
        {
            "measurement_id": "LANTERN-MS001",
            "category": "loudness",
            "metric": "true-peak",
            "value": -24.0,
            "unit": "LUFS",
            "claim": "Supplied integrated loudness record.",
        }
    ]

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any(
        "items.0.numeric_measurements.0: category, metric, value, and unit must exactly match measurement evidence LANTERN-MS001"
        in error
        for error in errors
    )

    measurements = items[0]["numeric_measurements"]
    assert isinstance(measurements, list) and isinstance(measurements[0], dict)
    measurements[0]["metric"] = "integrated-loudness"

    assert validate_artifact("sound-post-plan", payload, repository_root) == []


def test_sound_post_plan_requires_applicable_named_evidence_for_inspection(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    source_context = payload["source_context"]
    assert isinstance(source_context, dict)
    source_context["inspection_evidence"] = [
        {
            "evidence_id": "LANTERN-IN001",
            "evidence_kind": "audio",
            "source_reference": "audio/LANTERN-U01-production.wav",
        }
    ]
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["state"] = "inspected"

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any(
        "items.0.inspection_evidence_ids: inspected requires at least one applicable named evidence ID"
        in error
        for error in errors
    )


def test_sound_post_plan_rejects_unbound_or_inapplicable_inspection_evidence(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    source_context = payload["source_context"]
    assert isinstance(source_context, dict)
    source_context["inspection_evidence"] = [
        {
            "evidence_id": "LANTERN-IN001",
            "evidence_kind": "picture",
            "source_reference": "picture/LANTERN-U01-reference.mov",
        },
        {
            "evidence_id": "LANTERN-IN001",
            "evidence_kind": "audio",
            "source_reference": "audio/LANTERN-U01-production.wav",
        },
    ]
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["state"] = "planned"
    items[0]["inspection_evidence_ids"] = ["LANTERN-IN001"]

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any(
        "source_context.inspection_evidence.1.evidence_id: duplicate inspection evidence ID LANTERN-IN001"
        in error
        for error in errors
    )
    assert any(
        "items.0.inspection_evidence_ids: only inspected items may bind inspection evidence"
        in error
        for error in errors
    )

    source_context["inspection_evidence"] = [
        {
            "evidence_id": "LANTERN-IN001",
            "evidence_kind": "picture",
            "source_reference": "picture/LANTERN-U01-reference.mov",
        }
    ]
    items[0]["state"] = "inspected"

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any(
        "items.0.inspection_evidence_ids: evidence LANTERN-IN001 is not applicable to dialogue-edit inspection"
        in error
        for error in errors
    )


def test_sound_post_plan_rejects_placeholder_only_silence_purpose_but_not_ordinary_words(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[8], dict)
    items[8]["dramatic_purpose"] = "TBD"

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any(
        "items.8.dramatic_purpose: intentional-silence cannot use a placeholder-only purpose"
        in error
        for error in errors
    )

    safe_payload = valid_sound_post_plan()
    safe_items = safe_payload["items"]
    assert isinstance(safe_items, list) and isinstance(safe_items[8], dict)
    safe_items[8]["dramatic_purpose"] = "Hold while the next question remains pending."

    assert validate_artifact("sound-post-plan", safe_payload, repository_root) == []


def test_sound_post_plan_enforces_exact_hyphenated_project_ownership_and_evidence_binding(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    payload["project_id"] = "LANTERN-2"
    payload["unit_id"] = "LANTERN-2-U01"
    source_context = payload["source_context"]
    assert isinstance(source_context, dict)
    edit_segments = source_context["edit_segments"]
    assert isinstance(edit_segments, list) and isinstance(edit_segments[0], dict)
    edit_segments[0]["segment_id"] = "LANTERN-U01-ED001"

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any(
        "source_context.edit_segments.0.segment_id: 'LANTERN-U01-ED001' must match LANTERN-2-U01-ED###"
        in error
        for error in errors
    )


def test_sound_post_plan_requires_structured_non_placeholder_perspective(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["perspective"] = {"mode": "dialogue-focus", "intent": "TBD"}

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any("items.0.perspective.intent: must not be a placeholder-only value" in error for error in errors)


def test_sound_post_plan_rejects_assertive_claims_in_numeric_measurement_claims(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    source_context = payload["source_context"]
    assert isinstance(source_context, dict)
    source_context["measurement_evidence"] = [
        {
            "measurement_id": "LANTERN-MS001",
            "category": "loudness",
            "metric": "integrated-loudness",
            "value": -24.0,
            "unit": "LUFS",
            "source_reference": "audio/LANTERN-U01-mix.wav#metering",
        }
    ]
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["numeric_measurements"] = [
        {
            "measurement_id": "LANTERN-MS001",
            "category": "loudness",
            "metric": "integrated-loudness",
            "value": -24.0,
            "unit": "LUFS",
            "claim": "The final master was delivered and compliant.",
        }
    ]

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any(
        "items.0.numeric_measurements.0.claim: assertive prohibited claim" in error
        for error in errors
    )

    measurements = items[0]["numeric_measurements"]
    assert isinstance(measurements, list) and isinstance(measurements[0], dict)
    measurements[0]["claim"] = "Supplied record; approval remains awaiting input."

    assert validate_artifact("sound-post-plan", payload, repository_root) == []


def test_sound_post_plan_rejects_affirmative_claim_after_safe_adversative_clause(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[14], dict)
    items[14]["instruction"] = "No source is supplied, but the final master was delivered."

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any("items.14.instruction: assertive prohibited claim" in error for error in errors)

    items[14]["instruction"] = "No source is supplied; approval is awaiting input if a review is requested."

    assert validate_artifact("sound-post-plan", payload, repository_root) == []


def test_sound_post_plan_does_not_leak_safe_polarity_across_clause_boundaries(
    repository_root: Path,
) -> None:
    for instruction in (
        "No source is supplied although the final master was delivered.",
        "No source is supplied while the final master was delivered.",
        "No source is supplied — the final master was delivered.",
        "No source is supplied and the final master was delivered.",
    ):
        payload = valid_sound_post_plan()
        items = payload["items"]
        assert isinstance(items, list) and isinstance(items[14], dict)
        items[14]["instruction"] = instruction

        errors = validate_artifact("sound-post-plan", payload, repository_root)

        assert any("items.14.instruction: assertive prohibited claim" in error for error in errors)


def test_sound_post_plan_normalizes_placeholder_only_silence_and_perspective_values(
    repository_root: Path,
) -> None:
    for placeholder in ("TBD:", "[TBD]", "pending...", "N/A:"):
        payload = valid_sound_post_plan()
        items = payload["items"]
        assert isinstance(items, list) and isinstance(items[8], dict)
        items[8]["dramatic_purpose"] = placeholder
        items[8]["perspective"] = {"mode": "subjective", "intent": placeholder}

        errors = validate_artifact("sound-post-plan", payload, repository_root)

        assert any(
            "items.8.dramatic_purpose: intentional-silence cannot use a placeholder-only purpose"
            in error
            for error in errors
        )
        assert any(
            "items.8.perspective.intent: must not be a placeholder-only value" in error
            for error in errors
        )

    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[8], dict)
    items[8]["dramatic_purpose"] = "Hold while the next reply remains pending."
    items[8]["perspective"] = {
        "mode": "subjective",
        "intent": "Keep the listener with an unresolved question, not a TBD marker.",
    }

    assert validate_artifact("sound-post-plan", payload, repository_root) == []


def test_sound_post_plan_enforces_perspective_modes_for_every_responsibility(
    repository_root: Path,
) -> None:
    allowed_modes = {
        "dialogue-edit": "dialogue-focus",
        "repair": "dialogue-focus",
        "adr": "dialogue-focus",
        "foley": "spatial-focus",
        "ambience": "objective",
        "effects": "spatial-focus",
        "sound-design": "subjective",
        "transition": "objective",
        "intentional-silence": "subjective",
        "premix-group": "spatial-focus",
        "automation": "subjective",
        "mix-priority": "dialogue-focus",
        "accessibility": "accessibility",
        "loudness-assumption": "not-applicable-from-supplied-material",
        "mastering": "not-applicable-from-supplied-material",
    }
    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list)
    for item in items:
        assert isinstance(item, dict)
        responsibility = item["responsibility"]
        assert isinstance(responsibility, str)
        perspective = item["perspective"]
        assert isinstance(perspective, dict)
        perspective["mode"] = allowed_modes[responsibility]

    assert validate_artifact("sound-post-plan", payload, repository_root) == []

    for item in items:
        assert isinstance(item, dict)
        perspective = item["perspective"]
        assert isinstance(perspective, dict)
        perspective["mode"] = "accessibility" if item["responsibility"] != "accessibility" else "objective"

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    for index in range(15):
        assert any(f"items.{index}.perspective.mode:" in error for error in errors)


def test_sound_post_plan_allows_provisional_numeric_target_only_for_loudness_assumption(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[13], dict)
    items[13]["delivery_assumption"] = "Use the provisional -24 LUFS target if the supplied specification confirms it."

    assert validate_artifact("sound-post-plan", payload, repository_root) == []

    assert isinstance(items[0], dict)
    items[0]["delivery_assumption"] = "Use the provisional -24 LUFS target."

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any(
        "items.0.delivery_assumption: only loudness-assumption may declare a numeric target"
        in error
        for error in errors
    )

    del items[0]["delivery_assumption"]
    items[13]["delivery_assumption"] = "Measured -24 LUFS target is compliant and delivered."

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any("items.13.delivery_assumption: assertive prohibited claim" in error for error in errors)


def test_sound_post_plan_rejects_leading_adversative_clause_before_affirmative_claim(
    repository_root: Path,
) -> None:
    for instruction in (
        "Although no source is supplied, the final master was delivered.",
        "While no source is supplied, the final master was delivered.",
    ):
        payload = valid_sound_post_plan()
        items = payload["items"]
        assert isinstance(items, list) and isinstance(items[14], dict)
        items[14]["instruction"] = instruction

        errors = validate_artifact("sound-post-plan", payload, repository_root)

        assert any("items.14.instruction: assertive prohibited claim" in error for error in errors)

    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[14], dict)
    items[14]["instruction"] = (
        "After source review, await approval; if a specification is supplied, use its target; "
        "until human handoff, no master is delivered."
    )

    assert validate_artifact("sound-post-plan", payload, repository_root) == []


def test_sound_post_plan_rejects_numeric_measurement_claim_units_and_metric_contradiction(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    source_context = payload["source_context"]
    assert isinstance(source_context, dict)
    source_context["measurement_evidence"] = [
        {
            "measurement_id": "LANTERN-MS001",
            "category": "loudness",
            "metric": "integrated-loudness",
            "value": -24.0,
            "unit": "LUFS",
            "source_reference": "audio/LANTERN-U01-mix.wav#metering",
        }
    ]
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["numeric_measurements"] = [
        {
            "measurement_id": "LANTERN-MS001",
            "category": "loudness",
            "metric": "integrated-loudness",
            "value": -24.0,
            "unit": "LUFS",
            "claim": "True peak was -1 dBTP.",
        }
    ]

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any(
        "items.0.numeric_measurements.0.claim: measurement-unit syntax is allowed only in structured measurement fields"
        in error
        for error in errors
    )
    assert any(
        "items.0.numeric_measurements.0.claim: contradicts structured metric integrated-loudness"
        in error
        for error in errors
    )

    measurements = items[0]["numeric_measurements"]
    assert isinstance(measurements, list) and isinstance(measurements[0], dict)
    measurements[0]["claim"] = "Supplied integrated-loudness record for the declared source."

    assert validate_artifact("sound-post-plan", payload, repository_root) == []


def test_sound_post_plan_normalizes_unicode_placeholder_only_values(
    repository_root: Path,
) -> None:
    for placeholder in ("TBD —", "“TBD”", "T.B.D."):
        payload = valid_sound_post_plan()
        items = payload["items"]
        assert isinstance(items, list) and isinstance(items[8], dict)
        items[8]["dramatic_purpose"] = placeholder
        items[8]["perspective"] = {"mode": "subjective", "intent": placeholder}

        errors = validate_artifact("sound-post-plan", payload, repository_root)

        assert any(
            "items.8.dramatic_purpose: intentional-silence cannot use a placeholder-only purpose"
            in error
            for error in errors
        )
        assert any(
            "items.8.perspective.intent: must not be a placeholder-only value" in error
            for error in errors
        )

    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[8], dict)
    items[8]["dramatic_purpose"] = "TBD markers are never a dramatic purpose."
    items[8]["perspective"] = {
        "mode": "subjective",
        "intent": "Keep the listener with uncertainty rather than a TBD marker.",
    }

    assert validate_artifact("sound-post-plan", payload, repository_root) == []


def test_sound_post_plan_requires_loudness_target_language_for_numeric_delivery_assumption(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[13], dict)
    items[13]["delivery_assumption"] = "Observed -24 LUFS in the supplied mix."

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any(
        "items.13.delivery_assumption: numeric target must be marked provisional, target, assumed, or conditional"
        in error
        for error in errors
    )

    items[13]["delivery_assumption"] = "Use provisional -24 LUFS target if specification confirms."

    assert validate_artifact("sound-post-plan", payload, repository_root) == []


def test_sound_post_plan_rejects_observed_numeric_delivery_reading_despite_pending_language(
    repository_root: Path,
) -> None:
    payload = valid_sound_post_plan()
    items = payload["items"]
    assert isinstance(items, list) and isinstance(items[13], dict)
    items[13]["delivery_assumption"] = "Observed -24 LUFS in the supplied mix, pending confirmation."

    errors = validate_artifact("sound-post-plan", payload, repository_root)

    assert any(
        "items.13.delivery_assumption: numeric delivery assumption cannot describe an observed reading"
        in error
        for error in errors
    )

import copy

from cine_skills.artifacts import validate_artifact


def planned_color_plan() -> dict[str, object]:
    return {
        "schema_version": "0.3.0",
        "project_id": "DAY",
        "unit_id": "DAY-U01",
        "source_context": {
            "edit_segments": [
                {"segment_id": "DAY-U01-ED001", "source_reference": "post/edit-plan.json#/segments/0"},
                {"segment_id": "DAY-U01-ED002", "source_reference": "post/edit-plan.json#/segments/1"},
            ],
            "vfx_items": [],
            "media_versions": [],
            "metadata_records": [],
            "evidence": [],
        },
        "color_management": {
            "input_policy": "Identify each source encoding from applicable metadata; do not infer it from filenames.",
            "working_space": {"value": "scene-referred wide-gamut working space", "state": "proposed"},
            "output_intent": "Select an output transform only after the display target and viewing conditions are supplied.",
        },
        "display_targets": [],
        "items": [
            {
                "item_id": "DAY-U01-CL001",
                "edit_segment_ids": ["DAY-U01-ED001", "DAY-U01-ED002"],
                "vfx_item_ids": [],
                "source_version_ids": [],
                "graded_version_id": None,
                "observed_input": {"state": "uninspected", "source_version_id": None, "findings": [], "evidence_ids": []},
                "desired_look": "Warm, welcoming daylight with credible separation between direct sun and open shade.",
                "input_encoding": {"value": "unknown", "state": "unknown", "metadata_record_ids": []},
                "balance_and_matching": "Balance neutrals first, then match skin, foliage, sky, and shadow density while preserving motivated differences.",
                "exposure_and_contrast": "Retain shadow texture and shape gentle highlight roll-off after inspection.",
                "palette": {"intent": "Warm midtones with restrained highlight saturation.", "protected_colors": ["Natural complexion and neutral whites"], "selective_treatments": ["If inspection supports it, isolate facial shaping without flattening environmental coolness."]},
                "vfx_handoff": "Verify VFX and camera-source encodings independently before normalization.",
                "display_target_ids": [],
                "trim_assumptions": ["Numeric trims remain pending image and target-display inspection."],
                "match_state": "planned",
                "evidence_ids": [],
                "approval": {"state": "not-requested", "evidence_ids": []},
            }
        ],
        "story_arc": "Move from neutral orientation toward restrained warmth without implying an observed result.",
        "assumptions": ["No source media, camera metadata, or display specification was supplied."],
        "uncertainties": ["Input encodings, measured exposure, and final display intent remain unknown."],
    }


def approved_color_plan() -> dict[str, object]:
    payload = planned_color_plan()
    context = payload["source_context"]
    item = payload["items"][0]
    assert isinstance(context, dict) and isinstance(item, dict)
    context["media_versions"] = [
        {"media_id": "DAY-MD001", "version_id": "DAY-MD001-v003", "roles": ["source"], "segment_ids": ["DAY-U01-ED001", "DAY-U01-ED002"], "source_reference": "media/camera-original-v003.mov"},
        {"media_id": "DAY-MD002", "version_id": "DAY-MD002-v007", "roles": ["graded-output"], "segment_ids": ["DAY-U01-ED001", "DAY-U01-ED002"], "source_reference": "review/grade-v007.mov"},
    ]
    context["metadata_records"] = [
        {"metadata_id": "DAY-CM001", "segment_id": "DAY-U01-ED001", "version_id": "DAY-MD001-v003", "field": "input-encoding", "value": "ARRI LogC3 / ARRI Wide Gamut 3", "source_reference": "camera/report.xml#/clip/1"},
        {"metadata_id": "DAY-CM002", "segment_id": "DAY-U01-ED002", "version_id": "DAY-MD001-v003", "field": "input-encoding", "value": "ARRI LogC3 / ARRI Wide Gamut 3", "source_reference": "camera/report.xml#/clip/2"},
    ]
    context["evidence"] = [
        {"evidence_id": "DAY-CE001", "evidence_type": "inspection", "item_id": "DAY-U01-CL001", "segment_ids": ["DAY-U01-ED001", "DAY-U01-ED002"], "version_id": "DAY-MD002-v007", "claim": "shot-match", "value": "approved-match-v007", "source_reference": "review/v007-inspection.json"},
        {"evidence_id": "DAY-CE002", "evidence_type": "human-approval", "item_id": "DAY-U01-CL001", "segment_ids": ["DAY-U01-ED001", "DAY-U01-ED002"], "version_id": "DAY-MD002-v007", "claim": "approval", "value": "approved-match-v007", "source_reference": "review/v007-approval.json"},
    ]
    item["source_version_ids"] = ["DAY-MD001-v003"]
    item["graded_version_id"] = "DAY-MD002-v007"
    item["input_encoding"] = {"value": "ARRI LogC3 / ARRI Wide Gamut 3", "state": "declared", "metadata_record_ids": ["DAY-CM001", "DAY-CM002"]}
    item["match_state"] = "approved"
    item["evidence_ids"] = ["DAY-CE001"]
    item["approval"] = {"state": "approved", "evidence_ids": ["DAY-CE001", "DAY-CE002"]}
    return payload


def errors(payload: dict[str, object], repository_root) -> list[str]:
    return validate_artifact("color-plan", payload, repository_root)


def test_color_plan_allows_substantive_honest_planning_without_media(repository_root) -> None:
    assert errors(planned_color_plan(), repository_root) == []


def test_color_plan_allows_exact_value_and_version_backed_approval(repository_root) -> None:
    assert errors(approved_color_plan(), repository_root) == []


def test_color_plan_enforces_project_unit_and_item_id_shapes(repository_root) -> None:
    payload = planned_color_plan()
    payload["unit_id"] = "OTHER-U01"
    payload["items"][0]["item_id"] = "DAY-U01-CL000"
    result = errors(payload, repository_root)
    assert any("unit_id" in error and "DAY-U## or DAY-E##" in error for error in result)
    assert any("color item ID" in error and "OTHER-U01-CL###" in error for error in result)


def test_color_plan_rejects_unknown_edit_and_vfx_references_even_while_planned(repository_root) -> None:
    payload = planned_color_plan()
    payload["items"][0]["edit_segment_ids"] = ["DAY-U01-ED099"]
    payload["items"][0]["vfx_item_ids"] = ["DAY-U01-FX099"]
    result = errors(payload, repository_root)
    assert any("unknown edit segment ID DAY-U01-ED099" in error for error in result)
    assert any("unknown VFX post item ID DAY-U01-FX099" in error for error in result)


def test_color_plan_rejects_declared_input_without_metadata_for_every_segment(repository_root) -> None:
    payload = approved_color_plan()
    payload["items"][0]["input_encoding"]["metadata_record_ids"] = ["DAY-CM001"]
    result = errors(payload, repository_root)
    assert any("declared input encoding" in error and "DAY-U01-ED002" in error for error in result)


def test_color_plan_binds_metadata_to_exact_segment_version_field_and_value(repository_root) -> None:
    payload = approved_color_plan()
    payload["source_context"]["metadata_records"][0]["value"] = "ACEScg"
    result = errors(payload, repository_root)
    assert any("does not attest exact input-encoding value" in error for error in result)


def test_color_plan_rejects_approved_match_without_current_output_inspection(repository_root) -> None:
    payload = approved_color_plan()
    payload["source_context"]["evidence"][0]["version_id"] = "DAY-MD001-v003"
    result = errors(payload, repository_root)
    assert any("approved match requires inspection evidence" in error for error in result)


def test_color_plan_binds_approval_to_exact_item_segments_version_and_value(repository_root) -> None:
    payload = approved_color_plan()
    payload["source_context"]["evidence"][1]["value"] = "approved-match-v006"
    result = errors(payload, repository_root)
    assert any("approval evidence" in error and "same claimed value" in error for error in result)


def test_color_plan_rejects_unknown_populated_references_in_provisional_states(repository_root) -> None:
    payload = planned_color_plan()
    item = payload["items"][0]
    item["source_version_ids"] = ["DAY-MD999-v001"]
    item["graded_version_id"] = "DAY-MD998-v001"
    item["display_target_ids"] = ["DAY-DT999"]
    item["evidence_ids"] = ["DAY-CE999"]
    result = errors(payload, repository_root)
    assert any("unknown source media version ID DAY-MD999-v001" in error for error in result)
    assert any("unknown graded media version ID DAY-MD998-v001" in error for error in result)
    assert any("unknown display target ID DAY-DT999" in error for error in result)
    assert any("unknown evidence ID DAY-CE999" in error for error in result)


def test_color_plan_rejects_unsupported_display_values(repository_root) -> None:
    payload = planned_color_plan()
    payload["display_targets"] = [{"target_id": "DAY-DT001", "intent": "HDR", "standard": "mystery-hdr", "viewing_environment": "Unknown room", "state": "proposed", "source_reference": "brief.md"}]
    payload["items"][0]["display_target_ids"] = ["DAY-DT001"]
    result = errors(payload, repository_root)
    assert any("standard" in error and "not one of" in error for error in result)


def test_color_plan_does_not_encode_unsupported_display_review_as_target_state(repository_root) -> None:
    payload = planned_color_plan()
    payload["display_targets"] = [{"target_id": "DAY-DT001", "intent": "SDR", "standard": "rec709-gamma24", "viewing_environment": "Dim review room", "state": "reviewed", "source_reference": "display/specification.json"}]
    result = errors(payload, repository_root)
    assert any("display_targets.0.state" in error and "not one of" in error for error in result)


def test_color_plan_rejects_evidence_path_as_authenticity_proof(repository_root) -> None:
    payload = planned_color_plan()
    context = payload["source_context"]
    context["media_versions"] = [{"media_id": "DAY-MD002", "version_id": "DAY-MD002-v007", "roles": ["graded-output"], "segment_ids": ["DAY-U01-ED001", "DAY-U01-ED002"], "source_reference": "review/grade-v007.mov"}]
    context["evidence"] = [{"evidence_id": "DAY-CE001", "evidence_type": "source-reference", "item_id": "DAY-U01-CL001", "segment_ids": ["DAY-U01-ED001", "DAY-U01-ED002"], "version_id": "DAY-MD002-v007", "claim": "shot-match", "value": "approved-match-v007", "source_reference": "review/plausible-name.json"}]
    payload["items"][0]["graded_version_id"] = "DAY-MD002-v007"
    payload["items"][0]["match_state"] = "approved"
    payload["items"][0]["evidence_ids"] = ["DAY-CE001"]
    result = errors(payload, repository_root)
    assert any("evidence_type" in error and "not one of" in error for error in result)


def test_color_plan_rejects_observations_without_exact_inspection_evidence(repository_root) -> None:
    payload = planned_color_plan()
    payload["items"][0]["observed_input"] = {"state": "inspected", "source_version_id": "DAY-MD001-v003", "findings": ["Highlights clip in the exterior."], "evidence_ids": []}
    result = errors(payload, repository_root)
    assert any("observed input requires inspection evidence" in error for error in result)

    payload["items"][0]["observed_input"] = {"state": "uninspected", "source_version_id": None, "findings": ["Highlights clip in the exterior."], "evidence_ids": []}
    result = errors(payload, repository_root)
    assert any("uninspected input cannot contain findings" in error for error in result)


def test_color_plan_binds_observed_findings_to_source_version_and_exact_values(repository_root) -> None:
    payload = approved_color_plan()
    payload["source_context"]["evidence"].append({"evidence_id": "DAY-CE003", "evidence_type": "inspection", "item_id": "DAY-U01-CL001", "segment_ids": ["DAY-U01-ED001", "DAY-U01-ED002"], "version_id": "DAY-MD001-v003", "claim": "observed-input", "value": "Highlights retain texture.", "source_reference": "review/source-v003-inspection.json"})
    payload["items"][0]["observed_input"] = {"state": "inspected", "source_version_id": "DAY-MD001-v003", "findings": ["Highlights clip in the exterior."], "evidence_ids": ["DAY-CE003"]}
    result = errors(payload, repository_root)
    assert any("finding lacks exact source-version inspection evidence" in error for error in result)


def test_color_plan_requires_each_source_version_segment_pair_for_declared_input(repository_root) -> None:
    payload = approved_color_plan()
    payload["source_context"]["media_versions"].append({"media_id": "DAY-MD003", "version_id": "DAY-MD003-v001", "roles": ["source"], "segment_ids": ["DAY-U01-ED002"], "source_reference": "media/second-camera-v001.mov"})
    payload["items"][0]["source_version_ids"].append("DAY-MD003-v001")
    result = errors(payload, repository_root)
    assert any("DAY-U01-ED002" in error and "DAY-MD003-v001" in error and "declared input encoding" in error for error in result)


def test_color_plan_rejects_output_only_source_versions(repository_root) -> None:
    payload = approved_color_plan()
    payload["source_context"]["media_versions"][0]["roles"] = ["graded-output"]
    result = errors(payload, repository_root)
    assert any("source-capable role" in error for error in result)


def test_color_plan_keeps_working_space_an_assumption_not_a_metadata_declaration(repository_root) -> None:
    payload = approved_color_plan()
    payload["color_management"]["working_space"] = {"value": "ACEScg", "state": "declared"}
    result = errors(payload, repository_root)
    assert any("working_space.state" in error and "not one of" in error for error in result)


def test_color_plan_rejects_declared_input_without_an_applicable_source_version(repository_root) -> None:
    payload = planned_color_plan()
    payload["items"][0]["input_encoding"] = {"value": "ACEScg", "state": "declared", "metadata_record_ids": []}
    result = errors(payload, repository_root)
    assert any("declared input encoding requires an applicable source version" in error for error in result)


def test_color_plan_rejects_unused_metadata_for_a_segment_outside_its_version(repository_root) -> None:
    payload = approved_color_plan()
    payload["source_context"]["media_versions"].append({"media_id": "DAY-MD003", "version_id": "DAY-MD003-v001", "roles": ["source"], "segment_ids": ["DAY-U01-ED002"], "source_reference": "media/second-camera-v001.mov"})
    payload["source_context"]["metadata_records"].append({"metadata_id": "DAY-CM003", "segment_id": "DAY-U01-ED001", "version_id": "DAY-MD003-v001", "field": "input-encoding", "value": "ACEScg", "source_reference": "camera/unused.xml"})

    result = errors(payload, repository_root)

    assert any("metadata_records.2.segment_id" in error and "DAY-U01-ED001" in error and "DAY-MD003-v001" in error for error in result)


def test_color_plan_allows_unused_metadata_for_a_segment_covered_by_its_version(repository_root) -> None:
    payload = approved_color_plan()
    payload["source_context"]["media_versions"].append({"media_id": "DAY-MD003", "version_id": "DAY-MD003-v001", "roles": ["source"], "segment_ids": ["DAY-U01-ED001"], "source_reference": "media/second-camera-v001.mov"})
    payload["source_context"]["metadata_records"].append({"metadata_id": "DAY-CM003", "segment_id": "DAY-U01-ED001", "version_id": "DAY-MD003-v001", "field": "input-encoding", "value": "ACEScg", "source_reference": "camera/unused.xml"})

    assert errors(payload, repository_root) == []


def test_color_plan_rejects_unused_evidence_with_incomplete_segments_or_wrong_claim_version(repository_root) -> None:
    payload = approved_color_plan()
    payload["source_context"]["evidence"].extend([
        {"evidence_id": "DAY-CE003", "evidence_type": "human-approval", "item_id": "DAY-U01-CL001", "segment_ids": ["DAY-U01-ED001"], "version_id": "DAY-MD002-v007", "claim": "approval", "value": "unused-approval", "source_reference": "review/unused-approval.json"},
        {"evidence_id": "DAY-CE004", "evidence_type": "inspection", "item_id": "DAY-U01-CL001", "segment_ids": ["DAY-U01-ED001", "DAY-U01-ED002"], "version_id": "DAY-MD002-v007", "claim": "observed-input", "value": "unused-observation", "source_reference": "review/unused-source-inspection.json"},
        {"evidence_id": "DAY-CE005", "evidence_type": "inspection", "item_id": "DAY-U01-CL001", "segment_ids": ["DAY-U01-ED001", "DAY-U01-ED002"], "version_id": "DAY-MD001-v003", "claim": "shot-match", "value": "unused-match", "source_reference": "review/unused-match-inspection.json"},
    ])

    result = errors(payload, repository_root)

    assert any("evidence.2.segment_ids" in error and "complete target item segment set" in error for error in result)
    assert any("evidence.3.version_id" in error and "source version" in error for error in result)
    assert any("evidence.4.version_id" in error and "graded-output version" in error for error in result)


def test_color_plan_allows_unused_evidence_with_complete_segments_and_claim_versions(repository_root) -> None:
    payload = approved_color_plan()
    payload["source_context"]["evidence"].extend([
        {"evidence_id": "DAY-CE003", "evidence_type": "inspection", "item_id": "DAY-U01-CL001", "segment_ids": ["DAY-U01-ED001", "DAY-U01-ED002"], "version_id": "DAY-MD001-v003", "claim": "observed-input", "value": "unused-observation", "source_reference": "review/unused-source-inspection.json"},
        {"evidence_id": "DAY-CE004", "evidence_type": "human-approval", "item_id": "DAY-U01-CL001", "segment_ids": ["DAY-U01-ED001", "DAY-U01-ED002"], "version_id": "DAY-MD002-v007", "claim": "approval", "value": "unused-approval", "source_reference": "review/unused-approval.json"},
    ])

    assert errors(payload, repository_root) == []

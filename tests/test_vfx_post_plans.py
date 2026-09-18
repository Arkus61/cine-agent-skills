import copy

from cine_skills.artifacts import validate_artifact


def valid_planned_vfx_post_plan() -> dict[str, object]:
    return {
        "schema_version": "0.3.0",
        "project_id": "GLASS",
        "unit_id": "GLASS-U01",
        "source_context": {
            "preproduction_effects": [
                {"effect_id": "GLASS-FX001", "source_reference": "production/vfx-plan.json#/effects/0"}
            ],
            "edit_segments": [
                {"segment_id": "GLASS-U01-ED001", "source_reference": "post/edit-plan.json#/segments/0"}
            ],
            "media_versions": [],
            "evidence": [],
            "delivery_targets": [],
        },
        "items": [{
            "item_id": "GLASS-U01-FX001",
            "preproduction_effect_ids": ["GLASS-FX001"],
            "edit_segment_ids": ["GLASS-U01-ED001"],
            "purpose": "Plan a screen replacement with finger occlusions during the camera move.",
            "source_version_ids": [],
            "current_output_version_id": None,
            "workstreams": [
                {"type": "plate", "applicability": "awaiting-input", "action": "Confirm plate identity, frame range, and handles before turnover.", "assumption": "No plate metadata or media was supplied."},
                {"type": "tracking", "applicability": "planned", "action": "Validate perspective and track stability through the camera move.", "assumption": "Camera and lens data remain awaiting turnover."},
                {"type": "rotoscoping", "applicability": "planned", "action": "Plan finger holdouts and inspect edge transitions when media arrives.", "assumption": "Occlusion frames have not been inspected."},
                {"type": "compositing", "applicability": "planned", "action": "Integrate perspective, reflections, black level, and interactive light.", "assumption": "Plate and insert versions remain awaiting media."},
                {"type": "lens-integration", "applicability": "planned", "action": "Match distortion, motion blur, and defocus to supplied evidence.", "assumption": "Lens characteristics are unknown."},
                {"type": "grain-integration", "applicability": "planned", "action": "Match grain only after the plate and delivery path are identified.", "assumption": "Grain characteristics have not been measured."},
            ],
            "dependency_ids": [],
            "review_status": "planned",
            "review_evidence_ids": [],
            "delivery": {"status": "not-planned", "target_id": None, "evidence_ids": []},
            "handoff_assumptions": ["Plate range, handles, lens data, and color pipeline remain awaiting turnover."],
        }],
        "dependencies": [],
        "assumptions": ["No media was supplied for inspection."],
        "uncertainties": ["Output version and final delivery specification remain unknown."],
    }


def evidence_backed_vfx_post_plan() -> dict[str, object]:
    payload = valid_planned_vfx_post_plan()
    context = payload["source_context"]
    item = payload["items"][0]
    assert isinstance(context, dict) and isinstance(item, dict)
    context["media_versions"] = [
        {"media_id": "GLASS-MD001", "version_id": "GLASS-MD001-v007", "roles": ["output"], "source_reference": "review/screen-comp-v007.mov"}
    ]
    context["evidence"] = [
        {"evidence_id": "GLASS-EV001", "evidence_type": "inspection", "item_id": "GLASS-U01-FX001", "version_id": "GLASS-MD001-v007", "source_reference": "review/v007-inspection.json"},
        {"evidence_id": "GLASS-EV002", "evidence_type": "human-approval", "item_id": "GLASS-U01-FX001", "version_id": "GLASS-MD001-v007", "source_reference": "review/v007-approval.json"},
        {"evidence_id": "GLASS-EV003", "evidence_type": "delivery-verification", "item_id": "GLASS-U01-FX001", "version_id": "GLASS-MD001-v007", "target_id": "GLASS-DT001", "source_reference": "delivery/v007-verification.json"},
    ]
    context["delivery_targets"] = [
        {"target_id": "GLASS-DT001", "specification": "16-bit image sequence, agreed frame range and color encoding", "source_reference": "delivery/specification.json"}
    ]
    item["source_version_ids"] = []
    item["current_output_version_id"] = "GLASS-MD001-v007"
    item["review_status"] = "approved"
    item["review_evidence_ids"] = ["GLASS-EV001", "GLASS-EV002"]
    item["delivery"] = {"status": "verified", "target_id": "GLASS-DT001", "evidence_ids": ["GLASS-EV003"]}
    return payload


def errors(payload: dict[str, object], repository_root) -> list[str]:
    return validate_artifact("vfx-post-plan", payload, repository_root)


def test_vfx_post_plan_allows_honest_planning_without_media(repository_root) -> None:
    assert errors(valid_planned_vfx_post_plan(), repository_root) == []


def test_vfx_post_plan_allows_exact_evidence_backed_approval_and_delivery(repository_root) -> None:
    assert errors(evidence_backed_vfx_post_plan(), repository_root) == []


def test_vfx_post_plan_enforces_distinct_exact_owner_namespaces(repository_root) -> None:
    payload = valid_planned_vfx_post_plan()
    payload["source_context"]["preproduction_effects"][0]["effect_id"] = "GLASS-U01-FX001"
    payload["items"][0]["item_id"] = "GLASS-FX001"
    result = errors(payload, repository_root)
    assert any("preproduction effect ID" in error and "GLASS-FX###" in error for error in result)
    assert any("post item ID" in error and "GLASS-U01-FX###" in error for error in result)


def test_vfx_post_plan_rejects_missing_and_unknown_source_links(repository_root) -> None:
    payload = valid_planned_vfx_post_plan()
    payload["items"][0]["preproduction_effect_ids"] = []
    payload["items"][0]["edit_segment_ids"] = ["GLASS-U01-ED099"]
    payload["items"][0]["source_version_ids"] = ["GLASS-MD099-v001"]
    result = errors(payload, repository_root)
    assert any("at least one preproduction VFX link" in error for error in result)
    assert any("unknown edit segment ID GLASS-U01-ED099" in error for error in result)
    assert any("unknown media version ID GLASS-MD099-v001" in error for error in result)


def test_vfx_post_plan_binds_review_evidence_to_exact_item_and_version(repository_root) -> None:
    payload = evidence_backed_vfx_post_plan()
    payload["source_context"]["evidence"][0]["item_id"] = "GLASS-U01-FX099"
    payload["source_context"]["evidence"][1]["version_id"] = "GLASS-MD001-v006"
    result = errors(payload, repository_root)
    assert any("unknown post item ID GLASS-U01-FX099" in error for error in result)
    assert any("unknown media version ID GLASS-MD001-v006" in error for error in result)
    assert any("does not attest exact item and current version" in error for error in result)


def test_vfx_post_plan_rejects_stale_version_approval(repository_root) -> None:
    payload = evidence_backed_vfx_post_plan()
    context = payload["source_context"]
    context["media_versions"].append({"media_id": "GLASS-MD001", "version_id": "GLASS-MD001-v006", "roles": ["output"], "source_reference": "review/screen-comp-v006.mov"})
    context["evidence"][0]["version_id"] = "GLASS-MD001-v006"
    context["evidence"][1]["version_id"] = "GLASS-MD001-v006"
    result = errors(payload, repository_root)
    assert any("approved requires inspection and human-approval evidence for current version GLASS-MD001-v007" in error for error in result)


def test_vfx_post_plan_requires_ordered_acyclic_dependencies(repository_root) -> None:
    payload = valid_planned_vfx_post_plan()
    second = copy.deepcopy(payload["items"][0])
    second["item_id"] = "GLASS-U01-FX002"
    payload["items"].append(second)
    payload["dependencies"] = [
        {"dependency_id": "GLASS-DEP001", "upstream_item_id": "GLASS-U01-FX002", "downstream_item_id": "GLASS-U01-FX001", "order": 2, "purpose": "Second before first."},
        {"dependency_id": "GLASS-DEP002", "upstream_item_id": "GLASS-U01-FX001", "downstream_item_id": "GLASS-U01-FX002", "order": 1, "purpose": "First before second."},
    ]
    payload["items"][0]["dependency_ids"] = ["GLASS-DEP001"]
    payload["items"][1]["dependency_ids"] = ["GLASS-DEP002"]
    result = errors(payload, repository_root)
    assert any("dependency order must be strictly ascending" in error for error in result)
    assert any("dependency cycle" in error for error in result)


def test_vfx_post_plan_rejects_delivery_claim_without_target_or_exact_evidence(repository_root) -> None:
    payload = valid_planned_vfx_post_plan()
    payload["items"][0]["delivery"] = {"status": "verified", "target_id": None, "evidence_ids": []}
    result = errors(payload, repository_root)
    assert any("verified delivery requires a declared target" in error for error in result)
    assert any("verified delivery requires delivery-verification evidence" in error for error in result)


def test_vfx_post_plan_requires_actionable_workstreams_and_no_media_assumptions(repository_root) -> None:
    payload = valid_planned_vfx_post_plan()
    payload["items"][0]["workstreams"] = [
        {"type": "tracking", "applicability": "planned", "action": "Validate the track through the cut and assumed handles.", "assumption": "Camera and lens data are not supplied."},
        {"type": "compositing", "applicability": "planned", "action": "Integrate screen perspective, finger holdouts, reflections, defocus, and grain.", "assumption": "Plate and output versions remain awaiting media."},
    ]
    assert errors(payload, repository_root) == []
    payload["items"][0]["workstreams"][0]["action"] = ""
    assert any("action" in error for error in errors(payload, repository_root))


def test_vfx_post_plan_binds_delivery_verification_to_exact_target(repository_root) -> None:
    payload = evidence_backed_vfx_post_plan()
    payload["source_context"]["delivery_targets"].append(
        {"target_id": "GLASS-DT002", "specification": "Review proxy only", "source_reference": "delivery/review-specification.json"}
    )
    payload["source_context"]["evidence"][2]["target_id"] = "GLASS-DT002"
    result = errors(payload, repository_root)
    assert any("does not attest exact delivery target GLASS-DT001" in error for error in result)


def test_vfx_post_plan_validates_registry_ownership_and_version_association(repository_root) -> None:
    payload = evidence_backed_vfx_post_plan()
    payload["source_context"]["media_versions"][0]["media_id"] = "WOOD-MD001"
    payload["source_context"]["evidence"][0]["evidence_id"] = "WOOD-EV001"
    result = errors(payload, repository_root)
    assert any("media ID" in error and "GLASS-MD###" in error for error in result)
    assert any("version ID" in error and "declared media ID" in error for error in result)
    assert any("evidence ID" in error and "GLASS-EV###" in error for error in result)


def test_vfx_post_plan_rejects_unknown_populated_references_in_nonfinal_states(repository_root) -> None:
    payload = valid_planned_vfx_post_plan()
    item = payload["items"][0]
    item["current_output_version_id"] = "GLASS-MD999-v001"
    item["review_evidence_ids"] = ["GLASS-EV999"]
    item["delivery"] = {"status": "candidate", "target_id": "GLASS-DT999", "evidence_ids": ["GLASS-EV998"]}
    result = errors(payload, repository_root)
    assert any("unknown current output version ID" in error for error in result)
    assert any("unknown evidence ID GLASS-EV999" in error for error in result)
    assert any("unknown delivery target ID GLASS-DT999" in error for error in result)
    assert any("unknown evidence ID GLASS-EV998" in error for error in result)


def test_vfx_post_plan_requires_dependency_backlinks_and_topological_order(repository_root) -> None:
    payload = valid_planned_vfx_post_plan()
    for number in (2, 3):
        item = copy.deepcopy(payload["items"][0])
        item["item_id"] = f"GLASS-U01-FX00{number}"
        payload["items"].append(item)
    payload["dependencies"] = [
        {"dependency_id": "GLASS-DEP001", "upstream_item_id": "GLASS-U01-FX002", "downstream_item_id": "GLASS-U01-FX003", "order": 1, "purpose": "Middle before final."},
        {"dependency_id": "GLASS-DEP002", "upstream_item_id": "GLASS-U01-FX001", "downstream_item_id": "GLASS-U01-FX002", "order": 2, "purpose": "First before middle."},
    ]
    payload["items"][1]["dependency_ids"] = ["GLASS-DEP002"]
    result = errors(payload, repository_root)
    assert any("missing from downstream item" in error for error in result)
    assert any("dependency order contradicts execution order" in error for error in result)


def test_vfx_post_plan_rejects_unsupported_complete_workstream(repository_root) -> None:
    payload = valid_planned_vfx_post_plan()
    payload["items"][0]["workstreams"][0]["applicability"] = "complete"
    result = errors(payload, repository_root)
    assert any("complete requires inspection evidence for the current version" in error for error in result)


def test_vfx_post_plan_separates_source_and_output_version_roles(repository_root) -> None:
    payload = evidence_backed_vfx_post_plan()
    context = payload["source_context"]
    item = payload["items"][0]
    context["media_versions"][0]["roles"] = ["plate", "source"]
    item["source_version_ids"] = ["GLASS-MD001-v007"]
    result = errors(payload, repository_root)
    assert any("current output version" in error and "output role" in error for error in result)
    assert any("review evidence" in error and "output role" in error for error in result)
    assert any("delivery evidence" in error and "output role" in error for error in result)


def test_vfx_post_plan_rejects_output_only_source_and_allows_reused_output_source(repository_root) -> None:
    payload = valid_planned_vfx_post_plan()
    payload["source_context"]["media_versions"] = [
        {"media_id": "GLASS-MD001", "version_id": "GLASS-MD001-v001", "roles": ["output"], "source_reference": "upstream/output-v001.exr"}
    ]
    payload["items"][0]["source_version_ids"] = ["GLASS-MD001-v001"]
    assert any("source-capable role" in error for error in errors(payload, repository_root))

    payload["source_context"]["media_versions"][0]["roles"] = ["source", "output"]
    assert errors(payload, repository_root) == []


def test_vfx_post_plan_requires_current_output_for_version_specific_review(repository_root) -> None:
    for status in ("candidate", "changes-requested"):
        payload = valid_planned_vfx_post_plan()
        payload["items"][0]["review_status"] = status
        result = errors(payload, repository_root)
        assert any(status in error and "known current output version" in error for error in result)

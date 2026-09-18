import copy

from cine_skills.artifacts import validate_artifact


def planned_titles_plan() -> dict[str, object]:
    return {
        "schema_version": "0.3.0",
        "project_id": "SPARK",
        "unit_id": "SPARK-U01",
        "source_context": {
            "edit_segments": [{"segment_id": "SPARK-U01-ED001", "source_reference": "post/edit-plan.json#/segments/0"}],
            "edit_versions": [],
            "text_sources": [{"text_source_id": "SPARK-TS001", "kind": "supplied-dialogue", "text": "We begin today.", "source_reference": "story/screenplay.fountain#dialogue-12"}],
            "timing_records": [],
            "evidence": [],
        },
        "items": [{
            "item_id": "SPARK-U01-TT001",
            "type": "accessibility-caption",
            "edit_segment_id": "SPARK-U01-ED001",
            "text": {"content": "We begin today.", "content_kind": "dialogue", "state": "supplied", "text_source_id": "SPARK-TS001"},
            "placement": {"region": "lower-center above anticipated platform UI", "safe_area_state": "proposed", "exception_rationale": None},
            "timing": {"mode": "creative-intent", "intent": "Enter with the spoken phrase and leave enough room for the following sound description.", "timing_record_id": None},
            "typography_intent": "Use a clear sans serif with weight and size chosen after testing on the actual vertical frame.",
            "readability": {"contrast_strategy": "Test across every changing background; add a restrained backing treatment when needed.", "line_break_intent": "Break at semantic phrase boundaries.", "reading_speed_target": None, "line_length_target": None, "specification_reference": None},
            "language": "en",
            "speaker_identification": {"state": "not-required", "value": None},
            "sound_description": {"state": "not-applicable", "value": None},
            "presentation": {"mode": "sidecar", "assumption": "Sidecar remains proposed until the delivery specification is supplied."},
            "revision": "r001",
            "approval": {"state": "not-requested", "evidence_ids": []},
        }],
        "hierarchy_and_rhythm": "Keep the spoken caption primary and separate a later phone-ring description as its own readable event.",
        "credits_scope": {"state": "unresolved", "entries": [], "clearance_note": "Names, ordering, organizations, and rights language require supplied billing and legal review."},
        "assumptions": ["No locked edit, output-timeline metadata, media, platform specification, or review was supplied."],
        "uncertainties": ["Exact cue bounds, safe area, typeface, reading speed, line length, and delivery format remain unresolved."],
    }


def approved_titles_plan() -> dict[str, object]:
    payload = planned_titles_plan()
    context = payload["source_context"]
    item = payload["items"][0]
    assert isinstance(context, dict) and isinstance(item, dict)
    context["edit_versions"] = [{"edit_version_id": "SPARK-EV003", "status": "locked", "lock_decision_id": "SPARK-LK001", "segment_ids": ["SPARK-U01-ED001"], "source_reference": "post/edit-plan.json#/lock-decisions/0"}]
    context["timing_records"] = [{"timing_record_id": "SPARK-TM001", "item_id": "SPARK-U01-TT001", "segment_id": "SPARK-U01-ED001", "edit_version_id": "SPARK-EV003", "coordinate_space": "output-timeline", "timebase": {"frames_per_second": "24", "drop_frame": False}, "start_frame": 24, "end_frame": 72, "start_timecode": "00:00:01:00", "end_timecode": "00:00:03:00", "source_reference": "post/cue-sheet-v003.json#/cues/0"}]
    context["evidence"] = [
        {"evidence_id": "SPARK-TE001", "evidence_type": "review", "claim": "current-item-review", "item_id": "SPARK-U01-TT001", "segment_id": "SPARK-U01-ED001", "edit_version_id": "SPARK-EV003", "revision": "r001", "content": "We begin today.", "language": "en", "speaker_identification": {"state": "not-required", "value": None}, "sound_description": {"state": "not-applicable", "value": None}, "placement_region": "lower-center above anticipated platform UI", "timing_record_id": "SPARK-TM001", "decision_value": "approved-r001-ev003", "source_reference": "review/titles-v003.json"},
        {"evidence_id": "SPARK-TE002", "evidence_type": "human-approval", "claim": "approval", "item_id": "SPARK-U01-TT001", "segment_id": "SPARK-U01-ED001", "edit_version_id": "SPARK-EV003", "revision": "r001", "content": "We begin today.", "language": "en", "speaker_identification": {"state": "not-required", "value": None}, "sound_description": {"state": "not-applicable", "value": None}, "placement_region": "lower-center above anticipated platform UI", "timing_record_id": "SPARK-TM001", "decision_value": "approved-r001-ev003", "source_reference": "review/editorial-approval-v003.json"},
    ]
    for record in context["evidence"]:
        record.update(content_kind=item["text"]["content_kind"], text_state=item["text"]["state"], text_source=copy.deepcopy(context["text_sources"][0]))
    item["timing"] = {"mode": "exact-supplied", "intent": "Use the supplied output-timeline cue on locked edit SPARK-EV003.", "timing_record_id": "SPARK-TM001"}
    item["approval"] = {"state": "approved", "evidence_ids": ["SPARK-TE001", "SPARK-TE002"]}
    return payload


def errors(payload, repository_root):
    return validate_artifact("titles-captions-plan", payload, repository_root)


def test_titles_plan_accepts_useful_no_media_creative_intent(repository_root) -> None:
    assert errors(planned_titles_plan(), repository_root) == []


def test_titles_plan_accepts_proposed_nonspeech_caption_with_editorial_provenance(repository_root) -> None:
    payload = planned_titles_plan()
    payload["source_context"]["text_sources"].append({
        "text_source_id": "SPARK-TS002",
        "kind": "editorial-proposal",
        "text": "[doorbell rings]",
        "source_reference": "editorial/caption-proposals.json#/items/0",
    })
    item = payload["items"][0]
    item["text"] = {
        "content": "[doorbell rings]",
        "content_kind": "nonspeech",
        "state": "proposed",
        "text_source_id": "SPARK-TS002",
    }
    item["speaker_identification"] = {"state": "not-applicable", "value": None}
    item["sound_description"] = {"state": "proposed", "value": "doorbell rings"}

    assert errors(payload, repository_root) == []


def test_titles_plan_accepts_exact_current_timeline_timing_and_approval(repository_root) -> None:
    assert errors(approved_titles_plan(), repository_root) == []


def test_titles_plan_rejects_missing_caption_language_and_dialogue_source(repository_root) -> None:
    payload = planned_titles_plan()
    payload["items"][0]["language"] = None
    payload["items"][0]["text"]["text_source_id"] = None
    result = errors(payload, repository_root)
    assert any("language" in error and "caption" in error for error in result)
    assert any("dialogue caption requires" in error for error in result)


def test_titles_plan_rejects_unsafe_placement_without_exception(repository_root) -> None:
    payload = planned_titles_plan()
    payload["items"][0]["placement"] = {"region": "over platform controls", "safe_area_state": "exception", "exception_rationale": None}
    assert any("exception rationale" in error for error in errors(payload, repository_root))


def test_titles_plan_rejects_exact_timing_without_current_locked_edit_metadata(repository_root) -> None:
    payload = planned_titles_plan()
    payload["items"][0]["timing"] = {"mode": "exact-supplied", "intent": "Use supplied values.", "timing_record_id": None}
    assert any("exact timing requires" in error for error in errors(payload, repository_root))


def test_titles_plan_rejects_source_media_coordinates_as_timeline_timing(repository_root) -> None:
    payload = approved_titles_plan()
    payload["source_context"]["timing_records"][0]["coordinate_space"] = "source-media"
    assert any("output-timeline" in error for error in errors(payload, repository_root))


def test_titles_plan_rejects_mismatched_timecode_frames_and_reversed_bounds(repository_root) -> None:
    payload = approved_titles_plan()
    payload["source_context"]["timing_records"][0]["end_frame"] = 12
    result = errors(payload, repository_root)
    assert any("ordered bounds" in error for error in result)
    payload = approved_titles_plan()
    payload["source_context"]["timing_records"][0]["start_timecode"] = "00:00:02:00"
    assert any("does not match" in error for error in errors(payload, repository_root))


def test_titles_plan_rejects_stale_approval_content_revision_placement_and_edit(repository_root) -> None:
    mutations = [
        ("content", "Changed words"),
        ("revision", "r000"),
        ("placement_region", "upper-center"),
        ("edit_version_id", "SPARK-EV002"),
    ]
    for field, value in mutations:
        payload = approved_titles_plan()
        payload["source_context"]["evidence"][0][field] = value
        result = errors(payload, repository_root)
        assert any("exact current item content, revision, placement, timing, segment, and edit version" in error for error in result), (field, result)


def test_titles_plan_rejects_approval_after_accessibility_fields_change(repository_root) -> None:
    mutations = [
        ("language", "fr"),
        ("speaker_identification", {"state": "supplied", "value": "NARRATOR"}),
        ("sound_description", {"state": "supplied", "value": "door closes"}),
    ]
    for field, value in mutations:
        payload = approved_titles_plan()
        payload["items"][0][field] = value
        result = errors(payload, repository_root)
        assert any("exact current item" in error for error in result), (field, result)


def test_titles_plan_rejects_final_approval_without_matching_review_and_human_evidence(repository_root) -> None:
    payload = approved_titles_plan()
    payload["source_context"]["evidence"][1]["decision_value"] = "different-decision"
    assert any("same decision value" in error for error in errors(payload, repository_root))


def test_titles_plan_rejects_duplicate_cross_owned_and_dangling_ids(repository_root) -> None:
    payload = planned_titles_plan()
    duplicate = copy.deepcopy(payload["items"][0])
    duplicate["edit_segment_id"] = "OTHER-U01-ED001"
    payload["items"].append(duplicate)
    result = errors(payload, repository_root)
    assert any("duplicate titles/captions item ID" in error for error in result)
    assert any("unknown edit segment" in error for error in result)


def test_titles_plan_validates_unused_registry_records_internally(repository_root) -> None:
    payload = approved_titles_plan()
    payload["source_context"]["edit_versions"].append({"edit_version_id": "SPARK-EV004", "status": "locked", "lock_decision_id": "OTHER-LK001", "segment_ids": ["OTHER-U01-ED001"], "source_reference": "post/other.json"})
    payload["source_context"]["timing_records"].append({"timing_record_id": "SPARK-TM002", "item_id": "SPARK-U01-TT999", "segment_id": "OTHER-U01-ED001", "edit_version_id": "SPARK-EV004", "coordinate_space": "output-timeline", "timebase": {"frames_per_second": "24", "drop_frame": False}, "start_frame": 1, "end_frame": 2, "start_timecode": "00:00:00:01", "end_timecode": "00:00:00:02", "source_reference": "post/unused.json"})
    result = errors(payload, repository_root)
    assert any("lock decision ID" in error for error in result)
    assert any("unknown edit segment" in error for error in result)
    assert any("unknown titles/captions item" in error for error in result)


def test_titles_plan_rejects_unused_timing_record_for_items_other_segment(repository_root) -> None:
    payload = approved_titles_plan()
    payload["source_context"]["edit_segments"].append({"segment_id": "SPARK-U01-ED002", "source_reference": "post/edit-plan.json#/segments/1"})
    payload["source_context"]["edit_versions"][0]["segment_ids"].append("SPARK-U01-ED002")
    payload["source_context"]["timing_records"].append({"timing_record_id": "SPARK-TM002", "item_id": "SPARK-U01-TT001", "segment_id": "SPARK-U01-ED002", "edit_version_id": "SPARK-EV003", "coordinate_space": "output-timeline", "timebase": {"frames_per_second": "24", "drop_frame": False}, "start_frame": 96, "end_frame": 120, "start_timecode": "00:00:04:00", "end_timecode": "00:00:05:00", "source_reference": "post/unused.json"})

    assert any("target item's edit segment" in error for error in errors(payload, repository_root))


def test_titles_plan_rejects_non_drop_timecode_frame_component_at_or_above_fps(repository_root) -> None:
    for invalid_component in ("24", "99"):
        payload = approved_titles_plan()
        payload["source_context"]["timing_records"][0]["start_timecode"] = f"00:00:00:{invalid_component}"
        result = errors(payload, repository_root)
        assert any("frame component" in error for error in result), (invalid_component, result)


def test_titles_plan_rejects_supplied_text_that_disagrees_with_source_record(repository_root) -> None:
    payload = planned_titles_plan()
    payload["items"][0]["text"]["content"] = "Invented performance wording"
    assert any("must equal its supplied text source" in error for error in errors(payload, repository_root))


def test_titles_plan_rejects_incompatible_content_kind(repository_root) -> None:
    for item_type in ("subtitle", "accessibility-caption"):
        for content_kind in ("title", "credit"):
            payload = planned_titles_plan()
            payload["items"][0]["type"] = item_type
            payload["items"][0]["text"].update(content_kind=content_kind, state="proposed")
            assert any("content kind" in error for error in errors(payload, repository_root))


def test_titles_plan_resolves_proposed_title_source(repository_root) -> None:
    payload = planned_titles_plan()
    payload["items"][0]["type"] = "main-title"
    payload["items"][0]["text"].update(content_kind="title", state="proposed", text_source_id="SPARK-TS999")
    assert any("unknown text source" in error for error in errors(payload, repository_root))


def test_titles_plan_rejects_reclassification_with_unchanged_approval(repository_root) -> None:
    payload = approved_titles_plan()
    payload["items"][0]["text"].update(content_kind="nonspeech", state="proposed")
    payload["source_context"]["text_sources"][0]["kind"] = "editorial-proposal"
    assert any("exact current item" in error for error in errors(payload, repository_root))


def test_titles_plan_rejects_provenance_changes_with_unchanged_approval(repository_root) -> None:
    for mutation in ("state", "source_reference", "text_source_id"):
        payload = approved_titles_plan()
        if mutation == "state":
            payload["items"][0]["text"]["state"] = "proposed"
        elif mutation == "source_reference":
            payload["source_context"]["text_sources"][0]["source_reference"] = "different/dialogue.txt"
        else:
            source = copy.deepcopy(payload["source_context"]["text_sources"][0])
            source["text_source_id"] = "SPARK-TS002"
            payload["source_context"]["text_sources"].append(source)
            payload["items"][0]["text"]["text_source_id"] = "SPARK-TS002"
        assert any("exact current item" in error for error in errors(payload, repository_root)), mutation


def test_titles_plan_accepts_approved_nonspeech_with_matching_evidence(repository_root) -> None:
    payload = approved_titles_plan()
    item = payload["items"][0]
    item["text"].update(content="[doorbell rings]", content_kind="nonspeech", state="proposed")
    source = payload["source_context"]["text_sources"][0]
    source.update(kind="editorial-proposal", text="[doorbell rings]", source_reference="editorial/sound-proposals.json")
    for record in payload["source_context"]["evidence"]:
        record.update(content=item["text"]["content"], content_kind="nonspeech", text_state="proposed", text_source=copy.deepcopy(source))
    assert errors(payload, repository_root) == []


def test_titles_plan_accepts_compatible_title_credit_and_dialogue_types(repository_root) -> None:
    for item_type, kind in (("main-title", "title"), ("intertitle", "title"), ("lower-third", "title"), ("credit", "credit"), ("subtitle", "dialogue")):
        payload = planned_titles_plan()
        payload["items"][0]["type"] = item_type
        payload["items"][0]["text"]["content_kind"] = kind
        if kind != "dialogue":
            payload["items"][0]["text"].update(state="proposed", text_source_id=None)
        assert errors(payload, repository_root) == []

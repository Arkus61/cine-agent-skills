import copy

from cine_skills.artifacts import validate_artifact


def valid_music_plan() -> dict[str, object]:
    return {
        "schema_version": "0.3.0",
        "project_id": "LANTERN",
        "unit_id": "LANTERN-U01",
        "project_format": "short",
        "source_context": {
            "edit_plan_reference": "post/edit-plan.json",
            "edit_segments": [
                {"segment_id": "LANTERN-U01-ED001", "source_reference": "post/edit-plan.json#/segments/0"},
                {"segment_id": "LANTERN-U01-ED002", "source_reference": "post/edit-plan.json#/segments/1"},
            ],
            "characters": [{"character_id": "LANTERN-CH001", "source_reference": "story/character-arcs.json#/characters/0"}],
            "themes": [{"theme_id": "LANTERN-TH001", "source_reference": "story/story-concept.json#/theme"}],
            "protected_dialogue": [{"dialogue_id": "LANTERN-DG001", "edit_segment_id": "LANTERN-U01-ED001", "source_reference": "post/edit-plan.json#/segments/0"}],
            "locked_duration_evidence": [],
            "review_rights_evidence": [],
        },
        "spotting": [
            {"spotting_id": "LANTERN-U01-MU001", "edit_segment_id": "LANTERN-U01-ED001", "decision": "scored", "narrative_purpose": "Hold tension below the protected reveal.", "cue_id": "LANTERN-U01-MU001"},
            {"spotting_id": "LANTERN-U01-MU002", "edit_segment_id": "LANTERN-U01-ED002", "decision": "unscored", "narrative_purpose": "Let the aftermath remain exposed and unresolved."},
        ],
        "cues": [{
            "cue_id": "LANTERN-U01-MU001",
            "edit_segment_ids": ["LANTERN-U01-ED001"],
            "thematic_role": "Withhold the inherited-guilt idea as unstable texture.",
            "leitmotif_bindings": [{"binding_type": "character", "binding_id": "LANTERN-CH001", "transformation": "Fragmented, non-melodic interval."}, {"binding_type": "theme", "binding_id": "LANTERN-TH001", "transformation": "Deferred harmonic implication."}],
            "entry_exit_logic": {"entry": "Enter after the image establishes space.", "exit": "Thin to silence before the last consonant."},
            "energy_curve": "Low and suspended; no impact accent.",
            "instrumentation_intent": "Proposed bowed-metal and low-string texture, not a recording claim.",
            "diegetic_status": "nondiegetic",
            "dialogue_interaction": {"dialogue_id": "LANTERN-DG001", "priority": "dialogue", "approach": "Duck and thin the texture around intelligible phrases."},
            "transition": "Dissolve the texture into room tone.",
            "silence_alternative": "Use complete silence if the whisper loses intelligibility.",
            "source_assumption": "Planned original score; composer, rights, and recording remain awaiting input.",
            "state": "planned",
            "approval_boundary": "Requires composer and editorial approval before commitment.",
        }],
        "assumptions": ["Picture timing, composer, rights, and approval are not supplied."],
        "uncertainties": ["Conform entries and exits after a locked edit is supplied."],
    }


def errors(payload: dict[str, object], repository_root) -> list[str]:
    return validate_artifact("music-plan", payload, repository_root)


def test_valid_music_plan_is_schema_and_semantically_valid(repository_root) -> None:
    assert errors(valid_music_plan(), repository_root) == []


def test_music_plan_rejects_foreign_duplicate_and_unknown_references(repository_root) -> None:
    payload = valid_music_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    context["edit_segments"].append({"segment_id": "LANTERN-U01-ED001", "source_reference": "duplicate"})
    context["characters"].append({"character_id": "OTHER-CH001", "source_reference": "foreign"})
    payload["spotting"][0]["edit_segment_id"] = "LANTERN-U01-ED099"
    payload["cues"].append(copy.deepcopy(payload["cues"][0]))
    result = errors(payload, repository_root)
    assert any("duplicate" in error and "edit segment" in error for error in result)
    assert any("must belong to project" in error for error in result)
    assert any("unknown edit segment" in error for error in result)
    assert any("duplicate cue ID" in error for error in result)


def test_music_plan_requires_complete_spotting_and_an_intentional_unscored_decision(repository_root) -> None:
    payload = valid_music_plan()
    payload["spotting"] = [payload["spotting"][0]]
    result = errors(payload, repository_root)
    assert any("not covered by an explicit spotting decision" in error for error in result)
    payload = valid_music_plan()
    payload["spotting"][1]["decision"] = "scored"
    payload["spotting"][1]["cue_id"] = "LANTERN-U01-MU001"
    result = errors(payload, repository_root)
    assert any("at least one explicit unscored" in error for error in result)


def test_music_plan_requires_structured_dialogue_priority_for_protected_dialogue(repository_root) -> None:
    payload = valid_music_plan()
    payload["cues"][0].pop("dialogue_interaction")
    result = errors(payload, repository_root)
    assert any("protected dialogue" in error and "priority" in error for error in result)


def test_music_plan_binds_exact_duration_and_timecode_to_locked_evidence(repository_root) -> None:
    payload = valid_music_plan()
    payload["cues"][0]["entry_exit_logic"]["exact_start_timecode"] = "00:00:05:00"
    payload["cues"][0]["entry_exit_logic"]["exact_end_timecode"] = "00:00:10:00"
    result = errors(payload, repository_root)
    assert any("locked-duration evidence" in error for error in result)
    payload = valid_music_plan()
    payload["cues"][0]["energy_curve"] = "Rise for exactly 5 seconds after 00:00:05:00."
    result = errors(payload, repository_root)
    assert any("exact duration/timecode" in error for error in result)


def test_music_plan_requires_locked_duration_evidence_for_the_same_cue_segments(repository_root) -> None:
    payload = valid_music_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    context["locked_duration_evidence"] = [{"duration_evidence_id": "LANTERN-DU001", "edit_segment_ids": ["LANTERN-U01-ED002"], "exact_start_timecode": "00:00:05:00", "exact_end_timecode": "00:00:10:00", "lock_status": "picture-locked", "source_reference": "post/edit-plan.json#/locks/0"}]
    cue = payload["cues"][0]
    cue["entry_exit_logic"]["exact_start_timecode"] = "00:00:05:00"
    cue["entry_exit_logic"]["exact_end_timecode"] = "00:00:10:00"
    cue["locked_duration_evidence_ids"] = ["LANTERN-DU001"]
    result = errors(payload, repository_root)
    assert any("does not cover every cue edit segment" in error for error in result)
    payload = valid_music_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    context["locked_duration_evidence"] = [{"duration_evidence_id": "LANTERN-DU001", "edit_segment_ids": ["LANTERN-U01-ED001"], "exact_start_timecode": "00:00:05:00", "exact_end_timecode": "00:00:10:00", "lock_status": "picture-locked", "source_reference": "post/edit-plan.json#/locks/0"}]
    cue = payload["cues"][0]
    cue["entry_exit_logic"]["exact_start_timecode"] = "00:00:05:00"
    cue["entry_exit_logic"]["exact_end_timecode"] = "00:00:10:00"
    cue["locked_duration_evidence_ids"] = ["LANTERN-DU001"]
    assert errors(payload, repository_root) == []
    payload["cues"][0]["entry_exit_logic"]["exact_end_timecode"] = "00:00:11:00"
    result = errors(payload, repository_root)
    assert any("must match bound locked-duration evidence" in error for error in result)


def test_music_plan_rejects_artist_and_copyrighted_melody_imitation_in_all_relevant_prose(repository_root) -> None:
    payload = valid_music_plan()
    payload["cues"][0]["instrumentation_intent"] = "Compose in the style of living artist Ada Example."
    payload["cues"][0]["source_assumption"] = "Copy the copyrighted melody from a famous song."
    result = errors(payload, repository_root)
    assert sum("imitation or copyrighted-song/melody copying" in error for error in result) >= 2


def test_music_plan_evidence_gates_completion_claims_but_allows_planned_conditionals(repository_root) -> None:
    payload = valid_music_plan()
    payload["cues"][0]["state"] = "approved"
    payload["cues"][0]["approval_boundary"] = "Approved and delivered to the mix."
    result = errors(payload, repository_root)
    assert any("applicable named review/rights evidence" in error for error in result)
    assert any("assertive completion claim" in error for error in result)
    assert errors(valid_music_plan(), repository_root) == []


def test_music_plan_qualifies_each_completion_claim_independently(repository_root) -> None:
    payload = valid_music_plan()
    payload["cues"][0]["approval_boundary"] = "The cue is approved pending delivery."

    result = errors(payload, repository_root)

    assert any("assertive completion claim" in error for error in result)


def test_music_plan_allows_predicate_local_negatives_and_pending_approval(repository_root) -> None:
    payload = valid_music_plan()
    payload["cues"][0]["approval_boundary"] = (
        "The cue is not approved and not delivered; approval remains pending."
    )

    assert errors(payload, repository_root) == []

    payload["cues"][0]["approval_boundary"] = (
        "The cue is not approved or delivered; approval remains pending."
    )

    assert errors(payload, repository_root) == []

    payload["cues"][0]["approval_boundary"] = "Approval remains pending."
    payload["assumptions"].append(
        "Room tone is an editorial possibility, not supplied media or a verified recorded fact."
    )
    payload["uncertainties"].append(
        "Picture duration remains unknown because no locked timing evidence was supplied."
    )

    assert errors(payload, repository_root) == []


def test_music_plan_requires_applicable_review_rights_evidence_for_completed_cue_claims(repository_root) -> None:
    payload = valid_music_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    context["review_rights_evidence"] = [{"evidence_id": "LANTERN-ME001", "claim_type": "approved", "cue_ids": ["LANTERN-U01-MU099"], "source_reference": "review/minutes.md"}]
    cue = payload["cues"][0]
    cue["state"] = "approved"
    cue["review_rights_evidence_ids"] = ["LANTERN-ME001"]
    result = errors(payload, repository_root)
    assert any("not applicable to cue" in error for error in result)
    payload = valid_music_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    context["review_rights_evidence"] = [{"evidence_id": "LANTERN-ME001", "claim_type": "approved", "cue_ids": ["LANTERN-U01-MU001"], "source_reference": "review/minutes.md"}]
    cue = payload["cues"][0]
    cue["state"] = "approved"
    cue["review_rights_evidence_ids"] = ["LANTERN-ME001"]
    assert errors(payload, repository_root) == []


def test_music_plan_allows_only_evidence_attested_completion_prose(repository_root) -> None:
    payload = valid_music_plan()
    cue = payload["cues"][0]
    cue["state"] = "approved"
    cue["approval_boundary"] = "Approved for this cue by the named review."
    assert any("assertive completion claim" in error for error in errors(payload, repository_root))
    context = payload["source_context"]
    assert isinstance(context, dict)
    context["review_rights_evidence"] = [{"evidence_id": "LANTERN-ME001", "claim_type": "approved", "cue_ids": ["LANTERN-U01-MU001"], "source_reference": "review/minutes.md"}]
    cue["review_rights_evidence_ids"] = ["LANTERN-ME001"]
    assert errors(payload, repository_root) == []
    cue["approval_boundary"] = "Delivered and licensed for this cue."
    result = errors(payload, repository_root)
    assert any("assertive completion claim" in error for error in result)


def test_music_plan_rejects_named_person_imitation_but_allows_general_style_descriptors(repository_root) -> None:
    payload = valid_music_plan()
    payload["cues"][0]["instrumentation_intent"] = "Make it sound like Taylor Swift."
    assert any("imitation" in error for error in errors(payload, repository_root))
    payload = valid_music_plan()
    payload["cues"][0]["instrumentation_intent"] = "Proposed 1980s synth texture for minimalist psychological horror."
    assert errors(payload, repository_root) == []


def test_music_plan_requires_one_protected_dialogue_decision_per_protected_segment(repository_root) -> None:
    payload = valid_music_plan()
    context = payload["source_context"]
    assert isinstance(context, dict)
    context["protected_dialogue"].append({"dialogue_id": "LANTERN-DG002", "edit_segment_id": "LANTERN-U01-ED002", "source_reference": "post/edit-plan.json#/segments/1"})
    context["edit_segments"].append({"segment_id": "LANTERN-U01-ED003", "source_reference": "post/edit-plan.json#/segments/2"})
    payload["spotting"][1] = {"spotting_id": "LANTERN-U01-MU002", "edit_segment_id": "LANTERN-U01-ED002", "decision": "scored", "narrative_purpose": "Carry the cue through the second protected line.", "cue_id": "LANTERN-U01-MU001"}
    payload["spotting"].append({"spotting_id": "LANTERN-U01-MU003", "edit_segment_id": "LANTERN-U01-ED003", "decision": "unscored", "narrative_purpose": "Leave the final reaction exposed."})
    cue = payload["cues"][0]
    cue["edit_segment_ids"].append("LANTERN-U01-ED002")
    result = errors(payload, repository_root)
    assert any("same segment" in error for error in result)
    cue.pop("dialogue_interaction")
    cue["dialogue_interactions"] = [
        {"dialogue_id": "LANTERN-DG001", "priority": "dialogue", "approach": "Duck below each intelligible phrase."},
        {"dialogue_id": "LANTERN-DG002", "priority": "dialogue", "approach": "Hold music below the product line."},
    ]
    assert errors(payload, repository_root) == []


def test_music_plan_requires_exact_bidirectional_spotting_cue_coverage(repository_root) -> None:
    payload = valid_music_plan()
    payload["cues"][0]["edit_segment_ids"].append("LANTERN-U01-ED002")
    result = errors(payload, repository_root)
    assert any("unscored" in error and "must not cover" in error for error in result)


def test_music_plan_rejects_ambiguous_duplicate_and_out_of_cue_dialogue_bindings(repository_root) -> None:
    payload = valid_music_plan()
    payload["cues"][0]["dialogue_interactions"] = [copy.deepcopy(payload["cues"][0]["dialogue_interaction"])]
    assert any("mutually exclusive" in error for error in errors(payload, repository_root))

    payload = valid_music_plan()
    payload["cues"][0].pop("dialogue_interaction")
    interaction = {"dialogue_id": "LANTERN-DG001", "priority": "dialogue", "approach": "Protect the line."}
    payload["cues"][0]["dialogue_interactions"] = [interaction, copy.deepcopy(interaction)]
    assert any("duplicate/conflicting" in error for error in errors(payload, repository_root))

    payload = valid_music_plan()
    payload["source_context"]["protected_dialogue"].append({"dialogue_id": "LANTERN-DG002", "edit_segment_id": "LANTERN-U01-ED002", "source_reference": "post/edit-plan.json#/segments/1"})
    payload["cues"][0]["dialogue_interaction"]["dialogue_id"] = "LANTERN-DG002"
    assert any("outside cue edit segments" in error for error in errors(payload, repository_root))


def test_music_plan_rejects_empty_or_placeholder_unscored_purpose(repository_root) -> None:
    for purpose in ("   ", "N/A", "—?!", " n. a. "):
        payload = valid_music_plan()
        payload["spotting"][1]["narrative_purpose"] = purpose
        assert any("non-placeholder" in error for error in errors(payload, repository_root)), purpose


def test_music_plan_requires_well_formed_paired_ordered_exact_timecodes_and_equal_evidence(repository_root) -> None:
    payload = valid_music_plan()
    payload["cues"][0]["entry_exit_logic"]["exact_start_timecode"] = "not-a-timecode"
    assert any("well-formed" in error for error in errors(payload, repository_root))

    payload = valid_music_plan()
    payload["cues"][0]["entry_exit_logic"]["exact_start_timecode"] = "00:00:10:00"
    payload["cues"][0]["entry_exit_logic"]["exact_end_timecode"] = "00:00:05:00"
    assert any("later than" in error for error in errors(payload, repository_root))

    payload = valid_music_plan()
    payload["source_context"]["locked_duration_evidence"] = [
        {"duration_evidence_id": "LANTERN-DU001", "edit_segment_ids": ["LANTERN-U01-ED001"], "exact_start_timecode": "00:00:05:00", "exact_end_timecode": "00:00:10:00", "lock_status": "picture-locked", "source_reference": "locks/1"},
        {"duration_evidence_id": "LANTERN-DU002", "edit_segment_ids": ["LANTERN-U01-ED001"], "exact_start_timecode": "00:00:05:00", "exact_end_timecode": "00:00:11:00", "lock_status": "picture-locked", "source_reference": "locks/2"},
    ]
    payload["cues"][0]["entry_exit_logic"].update(exact_start_timecode="00:00:05:00", exact_end_timecode="00:00:10:00")
    payload["cues"][0]["locked_duration_evidence_ids"] = ["LANTERN-DU001", "LANTERN-DU002"]
    assert any("evidence LANTERN-DU002" in error and "must match" in error for error in errors(payload, repository_root))

    payload = valid_music_plan()
    payload["source_context"]["locked_duration_evidence"] = [{"duration_evidence_id": "LANTERN-DU001", "edit_segment_ids": ["LANTERN-U01-ED001"], "exact_start_timecode": "bad", "exact_end_timecode": "00:00:05:00", "lock_status": "picture-locked", "source_reference": "locks/1"}]
    assert any("locked_duration_evidence.0.exact_start_timecode" in error and "well-formed" in error for error in errors(payload, repository_root))


def test_music_plan_rejects_bare_exact_duration_prose_in_all_narrative_fields(repository_root) -> None:
    payload = valid_music_plan()
    payload["cues"][0]["dialogue_interaction"]["approach"] = "Cue lasts 5 seconds under the line."
    payload["assumptions"].append("Cue lasts 7 minutes.")
    result = errors(payload, repository_root)
    assert any("dialogue_interactions" in error and "exact duration/timecode" in error for error in result)
    assert any("assumptions" in error and "exact duration/timecode" in error for error in result)


def test_music_plan_rejects_duplicate_spots_crosswired_cues_and_unsafe_unscored_purpose(repository_root) -> None:
    payload = valid_music_plan()
    payload["spotting"].append({"spotting_id": "LANTERN-U01-MU003", "edit_segment_id": "LANTERN-U01-ED002", "decision": "unscored", "narrative_purpose": "TBD"})
    payload["spotting"][0]["edit_segment_id"] = "LANTERN-U01-ED002"
    result = errors(payload, repository_root)
    assert any("duplicate/conflicting" in error for error in result)
    assert any("non-placeholder" in error for error in result)
    assert any("must cover its spotting edit segment" in error for error in result)


def test_music_plan_uses_clause_local_completion_gates_and_generic_in_style_of_phrase(repository_root) -> None:
    payload = valid_music_plan()
    payload["cues"][0]["instrumentation_intent"] = "Proposed in the style of 1980s synthwave texture."
    payload["cues"][0]["approval_boundary"] = "Awaiting composer, but cue was approved and delivered."
    result = errors(payload, repository_root)
    assert not any("imitation" in error for error in result)
    assert any("assertive completion claim" in error for error in result)


def test_music_plan_rejects_leading_conditional_bypass_and_punctuated_placeholder(repository_root) -> None:
    payload = valid_music_plan()
    payload["cues"][0]["approval_boundary"] = "Although no evidence is supplied, the cue was approved and delivered."
    payload["spotting"][1]["narrative_purpose"] = "“TBD:”"
    result = errors(payload, repository_root)
    assert any("assertive completion claim" in error for error in result)
    assert any("non-placeholder" in error for error in result)


def test_music_plan_rejects_unknown_theme_and_invalid_protected_dialogue_binding(repository_root) -> None:
    payload = valid_music_plan()
    payload["cues"][0]["leitmotif_bindings"][1]["binding_id"] = "LANTERN-TH099"
    payload["cues"][0]["dialogue_interaction"]["dialogue_id"] = "LANTERN-DG099"
    result = errors(payload, repository_root)
    assert any("unknown theme ID" in error for error in result)
    assert any("unknown protected dialogue ID" in error for error in result)

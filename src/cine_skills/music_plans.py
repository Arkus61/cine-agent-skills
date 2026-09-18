"""Semantic validation for source-bound music spotting plans."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping
from typing import Any, Iterator


_POSITIVE_ID = r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
_TIMECODE = re.compile(r"(?<![0-9])(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]:[0-9]{2,3}(?![0-9])")
_EXACT_DURATION = re.compile(r"\b(?:exactly|exact)\s+\d+(?:\.\d+)?\s*(?:ms|milliseconds?|seconds?|minutes?)\b", re.I)
_BARE_DURATION = re.compile(r"\b\d+(?:\.\d+)?\s*(?:ms|milliseconds?|seconds?|minutes?)\b", re.I)
_IMITATION = re.compile(r"\bimitat(?:e|ion)\b|\bcopy\b.*\b(?:song|melody|copyright(?:ed)?)\b|\b(?:copyright(?:ed)?\s+(?:song|melody)|(?:song|melody)\s+from)\b", re.I)
_COMPLETION = re.compile(r"\b(?:approved|reviewed|licensed|cleared|delivered|recorded|composed|picture[- ]locked|locked)\b", re.I)
_COMPLETED_STATES = {"composed", "recorded", "reviewed", "approved", "licensed", "cleared", "locked", "delivered"}


def _strings(value: Any, location: str = "$") -> Iterator[tuple[str, str]]:
    if isinstance(value, str):
        yield location, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _strings(item, f"{location}.{index}")
    elif isinstance(value, Mapping):
        for key, item in value.items():
            yield from _strings(item, f"{location}.{key}")


def validate_music_plan_contract(payload: Mapping[str, Any]) -> list[str]:
    """Validate ownership, spotting coverage, evidence gates, and music safety."""
    errors: list[str] = []
    project_id, unit_id = payload.get("project_id"), payload.get("unit_id")
    if not isinstance(project_id, str) or not isinstance(unit_id, str):
        return errors
    if re.fullmatch(rf"{re.escape(project_id)}-(?:U|E)(?:0[1-9]|[1-9][0-9])", unit_id) is None:
        errors.append(f"unit_id: {unit_id!r} must match declared project {project_id} as {project_id}-U## or {project_id}-E##")
    context = payload.get("source_context")
    if not isinstance(context, Mapping):
        return errors
    segments = _register(context, "edit_segments", "segment_id", rf"{re.escape(unit_id)}-ED{_POSITIVE_ID}", "edit segment", errors)
    characters = _register(context, "characters", "character_id", rf"{re.escape(project_id)}-CH{_POSITIVE_ID}", "character", errors)
    themes = _register(context, "themes", "theme_id", rf"{re.escape(project_id)}-TH{_POSITIVE_ID}", "theme", errors)
    dialogue = _register(context, "protected_dialogue", "dialogue_id", rf"{re.escape(project_id)}-DG{_POSITIVE_ID}", "protected dialogue", errors)
    for index, record in enumerate(context.get("protected_dialogue", [])):
        if isinstance(record, Mapping) and isinstance(record.get("edit_segment_id"), str) and record["edit_segment_id"] not in segments:
            errors.append(f"source_context.protected_dialogue.{index}.edit_segment_id: unknown edit segment ID {record['edit_segment_id']}")
    durations = _register_records(context, "locked_duration_evidence", "duration_evidence_id", rf"{re.escape(project_id)}-DU{_POSITIVE_ID}", "locked-duration evidence", errors)
    evidence = _register_records(context, "review_rights_evidence", "evidence_id", rf"{re.escape(project_id)}-ME{_POSITIVE_ID}", "review/rights evidence", errors)
    for index, record in enumerate(context.get("locked_duration_evidence", [])):
        if isinstance(record, Mapping):
            for segment_id in record.get("edit_segment_ids", []):
                if isinstance(segment_id, str) and segment_id not in segments:
                    errors.append(f"source_context.locked_duration_evidence.{index}.edit_segment_ids: unknown edit segment ID {segment_id}")
            start, end = record.get("exact_start_timecode"), record.get("exact_end_timecode")
            for field, value in (("exact_start_timecode", start), ("exact_end_timecode", end)):
                if not isinstance(value, str) or _TIMECODE.fullmatch(value) is None:
                    errors.append(f"source_context.locked_duration_evidence.{index}.{field}: exact timecode must be well-formed")
            if isinstance(start, str) and isinstance(end, str) and _TIMECODE.fullmatch(start) and _TIMECODE.fullmatch(end) and tuple(map(int, end.split(":"))) <= tuple(map(int, start.split(":"))):
                errors.append(f"source_context.locked_duration_evidence.{index}: exact end timecode must be later than exact start timecode")

    spotting = payload.get("spotting")
    cues = payload.get("cues")
    if not isinstance(spotting, list) or not isinstance(cues, list):
        return errors
    spot_ids: set[str] = set()
    spotted_segments: set[str] = set()
    covered: set[str] = set()
    score_cue_ids: set[str] = set()
    has_unscored = False
    item_pattern = re.compile(rf"{re.escape(unit_id)}-MU{_POSITIVE_ID}")
    for index, decision in enumerate(spotting):
        if not isinstance(decision, Mapping):
            continue
        location = f"spotting.{index}"
        item_id = decision.get("spotting_id")
        if isinstance(item_id, str):
            if item_id in spot_ids:
                errors.append(f"{location}.spotting_id: duplicate spotting item ID {item_id}")
            spot_ids.add(item_id)
            if item_pattern.fullmatch(item_id) is None:
                errors.append(f"{location}.spotting_id: {item_id!r} must match {unit_id}-MU###")
        segment_id = decision.get("edit_segment_id")
        if isinstance(segment_id, str):
            if segment_id not in segments:
                errors.append(f"{location}.edit_segment_id: unknown edit segment ID {segment_id}")
            else:
                covered.add(segment_id)
                if segment_id in spotted_segments:
                    errors.append(f"{location}.edit_segment_id: duplicate/conflicting spotting decision for edit segment {segment_id}")
                spotted_segments.add(segment_id)
        if decision.get("decision") == "unscored":
            has_unscored = True
            if decision.get("cue_id") is not None:
                errors.append(f"{location}.cue_id: unscored spotting decision must not carry a cue ID")
            purpose = decision.get("narrative_purpose")
            normalized_purpose = "".join(char for char in unicodedata.normalize("NFKC", purpose or "").casefold() if char.isalnum()) if isinstance(purpose, str) else ""
            if normalized_purpose in {"", "tbd", "pending", "unknown", "none", "na", "notapplicable"}:
                errors.append(f"{location}.narrative_purpose: intentional unscored decision requires a non-placeholder purpose")
        purpose = decision.get("narrative_purpose")
        if isinstance(purpose, str):
            _reject_prohibited_prose(f"{location}.narrative_purpose", purpose, None, errors)
            if _TIMECODE.search(purpose) or _EXACT_DURATION.search(purpose):
                errors.append(f"{location}.narrative_purpose: exact duration/timecode claims are allowed only through bound locked-duration evidence")
        if decision.get("decision") == "scored" and isinstance(decision.get("cue_id"), str):
            score_cue_ids.add(decision["cue_id"])
    for segment_id in sorted(segments - covered):
        errors.append(f"source_context.edit_segments: declared edit segment {segment_id} is not covered by an explicit spotting decision")
    if not has_unscored:
        errors.append("spotting: at least one explicit unscored decision with narrative purpose is required")

    cue_ids: set[str] = set()
    protected_by_segment: dict[str, set[str]] = {}
    for record in context.get("protected_dialogue", []):
        if isinstance(record, Mapping) and isinstance(record.get("edit_segment_id"), str) and isinstance(record.get("dialogue_id"), str):
            protected_by_segment.setdefault(record["edit_segment_id"], set()).add(record["dialogue_id"])
    for index, cue in enumerate(cues):
        if not isinstance(cue, Mapping):
            continue
        location = f"cues.{index}"
        cue_id = cue.get("cue_id")
        if isinstance(cue_id, str):
            if cue_id in cue_ids:
                errors.append(f"{location}.cue_id: duplicate cue ID {cue_id}")
            cue_ids.add(cue_id)
            if item_pattern.fullmatch(cue_id) is None:
                errors.append(f"{location}.cue_id: {cue_id!r} must match {unit_id}-MU###")
            if cue_id not in score_cue_ids:
                errors.append(f"{location}.cue_id: cue must be referenced by one scored spotting decision")
        cue_segments = {value for value in cue.get("edit_segment_ids", []) if isinstance(value, str)}
        cue_spotted_segments = {decision.get("edit_segment_id") for decision in spotting if isinstance(decision, Mapping) and decision.get("decision") == "scored" and decision.get("cue_id") == cue_id}
        for decision in spotting:
            if isinstance(decision, Mapping) and decision.get("decision") == "scored" and decision.get("cue_id") == cue_id and decision.get("edit_segment_id") not in cue_segments:
                errors.append(f"{location}.edit_segment_ids: scored spotting cue {cue_id} must cover its spotting edit segment {decision.get('edit_segment_id')}")
        for segment_id in sorted(cue_segments - cue_spotted_segments):
            errors.append(f"{location}.edit_segment_ids: cue must not cover unscored or differently scored edit segment {segment_id}")
        for segment_id in cue_segments - segments:
            errors.append(f"{location}.edit_segment_ids: unknown edit segment ID {segment_id}")
        _validate_bindings(cue, characters, themes, location, errors)
        _validate_dialogue(cue, cue_segments, dialogue, protected_by_segment, location, errors)
        _validate_duration(cue, cue_segments, durations, location, errors)
        _validate_evidence(cue, evidence, location, errors)
        _validate_text(cue, location, evidence, errors)
    for cue_id in sorted(score_cue_ids - cue_ids):
        errors.append(f"spotting: scored decision references unknown cue ID {cue_id}")
    for evidence_id, record in evidence.items():
        for cue_id in record.get("cue_ids", []):
            if cue_id not in cue_ids:
                errors.append(f"source_context.review_rights_evidence: evidence {evidence_id} references unknown cue ID {cue_id}")
    for location, value in _strings({"assumptions": payload.get("assumptions"), "uncertainties": payload.get("uncertainties")}):
        _reject_prohibited_prose(location, value, None, errors)
        if _TIMECODE.search(value) or _BARE_DURATION.search(value):
            errors.append(f"{location}: exact duration/timecode claims are allowed only through bound locked-duration evidence")
    return errors


def _register(context: Mapping[str, Any], field: str, id_field: str, pattern: str, label: str, errors: list[str]) -> set[str]:
    return set(_register_records(context, field, id_field, pattern, label, errors))


def _register_records(context: Mapping[str, Any], field: str, id_field: str, pattern: str, label: str, errors: list[str]) -> dict[str, Mapping[str, Any]]:
    records: dict[str, Mapping[str, Any]] = {}
    values = context.get(field)
    if not isinstance(values, list):
        return records
    for index, record in enumerate(values):
        if not isinstance(record, Mapping) or not isinstance(record.get(id_field), str):
            continue
        value = record[id_field]
        if value in records:
            errors.append(f"source_context.{field}.{index}.{id_field}: duplicate declared {label} ID {value}")
        else:
            records[value] = record
        if re.fullmatch(pattern, value) is None:
            errors.append(f"source_context.{field}.{index}.{id_field}: {value!r} must belong to project/unit ownership")
    return records


def _validate_bindings(cue: Mapping[str, Any], characters: set[str], themes: set[str], location: str, errors: list[str]) -> None:
    for index, binding in enumerate(cue.get("leitmotif_bindings", [])):
        if not isinstance(binding, Mapping):
            continue
        binding_id, binding_type = binding.get("binding_id"), binding.get("binding_type")
        if binding_type == "character" and isinstance(binding_id, str) and binding_id not in characters:
            errors.append(f"{location}.leitmotif_bindings.{index}.binding_id: unknown character ID {binding_id}")
        if binding_type == "theme" and isinstance(binding_id, str) and binding_id not in themes:
            errors.append(f"{location}.leitmotif_bindings.{index}.binding_id: unknown theme ID {binding_id}")


def _validate_dialogue(cue: Mapping[str, Any], segments: set[str], dialogue: set[str], protected_by_segment: Mapping[str, set[str]], location: str, errors: list[str]) -> None:
    if "dialogue_interaction" in cue and "dialogue_interactions" in cue:
        errors.append(f"{location}.dialogue_interactions: singular and plural dialogue interactions are mutually exclusive")
    protected = {segment for segment in segments if segment in protected_by_segment}
    candidates = cue.get("dialogue_interactions")
    interactions = candidates if isinstance(candidates, list) else [cue.get("dialogue_interaction")]
    if protected and not any(isinstance(interaction, Mapping) for interaction in interactions):
        errors.append(f"{location}.dialogue_interaction: protected dialogue requires an explicit structured priority and interaction decision")
        return
    covered_dialogue: set[str] = set()
    seen_dialogue: set[str] = set()
    for interaction_index, interaction in enumerate(interactions):
        if not isinstance(interaction, Mapping):
            continue
        dialogue_id = interaction.get("dialogue_id")
        if isinstance(dialogue_id, str) and dialogue_id not in dialogue:
            errors.append(f"{location}.dialogue_interactions.{interaction_index}.dialogue_id: unknown protected dialogue ID {dialogue_id}")
        if isinstance(dialogue_id, str) and dialogue_id in seen_dialogue:
            errors.append(f"{location}.dialogue_interactions.{interaction_index}.dialogue_id: duplicate/conflicting dialogue binding {dialogue_id}")
        if isinstance(dialogue_id, str):
            seen_dialogue.add(dialogue_id)
            bound_segments = {segment for segment, ids in protected_by_segment.items() if dialogue_id in ids}
            if dialogue_id in dialogue and not bound_segments <= segments:
                errors.append(f"{location}.dialogue_interactions.{interaction_index}.dialogue_id: protected dialogue binding {dialogue_id} is outside cue edit segments")
        if interaction.get("priority") == "dialogue" and isinstance(dialogue_id, str):
            covered_dialogue.add(dialogue_id)
    required_dialogue = set().union(*(protected_by_segment[x] for x in protected)) if protected else set()
    if protected and not required_dialogue <= covered_dialogue:
        errors.append(f"{location}.dialogue_interaction: protected dialogue requires dialogue priority bound to the same segment")


def _validate_duration(cue: Mapping[str, Any], segments: set[str], durations: Mapping[str, Mapping[str, Any]], location: str, errors: list[str]) -> None:
    logic = cue.get("entry_exit_logic")
    exact = isinstance(logic, Mapping) and ("exact_start_timecode" in logic or "exact_end_timecode" in logic)
    evidence_ids = cue.get("locked_duration_evidence_ids")
    if isinstance(logic, Mapping):
        start, end = logic.get("exact_start_timecode"), logic.get("exact_end_timecode")
        if (start is None) != (end is None):
            errors.append(f"{location}.entry_exit_logic: exact start and end timecodes must be paired")
        if start is not None and (not isinstance(start, str) or _TIMECODE.fullmatch(start) is None):
            errors.append(f"{location}.entry_exit_logic.exact_start_timecode: exact timecode must be well-formed")
        if end is not None and (not isinstance(end, str) or _TIMECODE.fullmatch(end) is None):
            errors.append(f"{location}.entry_exit_logic.exact_end_timecode: exact timecode must be well-formed")
        if isinstance(start, str) and isinstance(end, str) and _TIMECODE.fullmatch(start) and _TIMECODE.fullmatch(end) and tuple(map(int, end.split(":"))) <= tuple(map(int, start.split(":"))):
            errors.append(f"{location}.entry_exit_logic: exact end timecode must be later than exact start timecode")
    if exact and (not isinstance(evidence_ids, list) or not evidence_ids):
        errors.append(f"{location}.locked_duration_evidence_ids: exact duration/timecode requires locked-duration evidence bound to the same cue segments")
    if isinstance(evidence_ids, list):
        for evidence_id in evidence_ids:
            record = durations.get(evidence_id) if isinstance(evidence_id, str) else None
            if record is None:
                errors.append(f"{location}.locked_duration_evidence_ids: unknown locked-duration evidence ID {evidence_id}")
            elif not segments <= set(record.get("edit_segment_ids", [])):
                errors.append(f"{location}.locked_duration_evidence_ids: evidence {evidence_id} does not cover every cue edit segment")
    if exact and isinstance(logic, Mapping) and isinstance(evidence_ids, list):
        for evidence_id in evidence_ids:
            record = durations.get(evidence_id) if isinstance(evidence_id, str) else None
            if record and (logic.get("exact_start_timecode") != record.get("exact_start_timecode") or logic.get("exact_end_timecode") != record.get("exact_end_timecode")):
                errors.append(f"{location}.entry_exit_logic: exact duration/timecode must match bound locked-duration evidence {evidence_id}")


def _validate_evidence(cue: Mapping[str, Any], evidence: Mapping[str, Mapping[str, Any]], location: str, errors: list[str]) -> None:
    state, cue_id = cue.get("state"), cue.get("cue_id")
    evidence_ids = cue.get("review_rights_evidence_ids")
    if state in _COMPLETED_STATES and (not isinstance(evidence_ids, list) or not evidence_ids):
        errors.append(f"{location}.review_rights_evidence_ids: {state} requires applicable named review/rights evidence")
    if isinstance(evidence_ids, list):
        applicable = False
        for evidence_id in evidence_ids:
            record = evidence.get(evidence_id) if isinstance(evidence_id, str) else None
            if record is None:
                errors.append(f"{location}.review_rights_evidence_ids: unknown review/rights evidence ID {evidence_id}")
            elif cue_id not in record.get("cue_ids", []):
                errors.append(f"{location}.review_rights_evidence_ids: evidence {evidence_id} is not applicable to cue {cue_id}")
            elif record.get("claim_type") == state:
                applicable = True
        if state in _COMPLETED_STATES and not applicable:
            errors.append(f"{location}.review_rights_evidence_ids: evidence must attest the {state} claim for this cue")


def _validate_text(cue: Mapping[str, Any], location: str, evidence: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    text_fields = ("thematic_role", "energy_curve", "instrumentation_intent", "transition", "silence_alternative", "source_assumption", "approval_boundary")
    prose: list[tuple[str, str]] = [(f"{location}.{field}", value) for field in text_fields if isinstance((value := cue.get(field)), str)]
    logic = cue.get("entry_exit_logic")
    if isinstance(logic, Mapping):
        prose.extend((f"{location}.entry_exit_logic.{field}", value) for field in ("entry", "exit") if isinstance((value := logic.get(field)), str))
    for binding_index, binding in enumerate(cue.get("leitmotif_bindings", [])):
        if isinstance(binding, Mapping) and isinstance(binding.get("transformation"), str):
            prose.append((f"{location}.leitmotif_bindings.{binding_index}.transformation", binding["transformation"]))
    interactions = cue.get("dialogue_interactions") if isinstance(cue.get("dialogue_interactions"), list) else [cue.get("dialogue_interaction")]
    for interaction_index, interaction in enumerate(interactions):
        if isinstance(interaction, Mapping) and isinstance(interaction.get("approach"), str):
            prose.append((f"{location}.dialogue_interactions.{interaction_index}.approach", interaction["approach"]))
    attested = {record.get("claim_type") for evidence_id in cue.get("review_rights_evidence_ids", []) if isinstance(evidence_id, str) and (record := evidence.get(evidence_id)) and cue.get("cue_id") in record.get("cue_ids", [])}
    for sublocation, value in prose:
        _reject_prohibited_prose(sublocation, value, attested, errors)
        if (_TIMECODE.search(value) or _BARE_DURATION.search(value)) and not sublocation.endswith(("exact_start_timecode", "exact_end_timecode")):
            errors.append(f"{sublocation}: exact duration/timecode claims are allowed only through bound locked-duration evidence")


def _reject_prohibited_prose(location: str, value: str, attested: set[Any] | None, errors: list[str]) -> None:
    style_reference = re.search(r"\bin the style of\s+([^.;,!]+)", value, re.I)
    generic_style = style_reference is not None and re.fullmatch(r"(?:the\s+)?(?:19|20)\d0s?(?:\s+[a-z-]+){0,3}", style_reference.group(1).strip(), re.I) is not None
    sound_reference = re.search(r"\bsound like\s+([^.;,!]+)", value, re.I)
    ordinary_sound = sound_reference is not None and re.search(r"\b(?:tape|machine|ocean|wind|room|metal|rain|texture)\b", sound_reference.group(1), re.I) is not None
    safety_text = re.sub(r"\bno\s+(?:artist\s+)?imitation\b|\bno\s+(?:existing[- ]song|melody)\s+copying\b", "", value, flags=re.I)
    if _IMITATION.search(safety_text) or (style_reference is not None and not generic_style) or (sound_reference is not None and not ordinary_sound):
        errors.append(f"{location}: living-artist imitation or copyrighted-song/melody copying is prohibited")
    normalized = {str(item).replace("-", "") for item in (attested or set())}
    clauses: list[str] = []
    for clause in re.split(r"[.;!?]+|\b(?:but|however|yet)\b", value, flags=re.I):
        leading = re.match(r"^\s*(?:although|while)\b[^,]*,\s*", clause, re.I)
        clauses.extend((clause[:leading.end()], clause[leading.end():]) if leading else (clause,))
    for clause in clauses:
        for match in _COMPLETION.finditer(clause):
            claim = re.sub(r"^picture[- ]", "", match.group(0).casefold()).replace(" ", "")
            if claim not in normalized and not _completion_is_qualified(clause, match.start()):
                errors.append(f"{location}: assertive completion claim requires named applicable evidence")
                return


def _completion_is_qualified(clause: str, claim_start: int) -> bool:
    """Return whether conditional or negative language governs this claim."""
    prefix = clause[:claim_start]
    return bool(
        re.search(r"\b(?:not|never)\s+(?:yet\s+)?(?:been\s+)?$", prefix, re.I)
        or re.search(r"\bno\s*$", prefix, re.I)
        or re.search(
            r"\b(?:not|never)\s+(?:yet\s+)?(?:been\s+)?"
            r"(?:approved|reviewed|licensed|cleared|delivered|recorded|composed|picture[- ]locked|locked)"
            r"\s+(?:and|or)\s*$",
            prefix,
            re.I,
        )
        or _scoped_negation_governs(prefix)
        or re.search(r"\bno\b(?:\s+[\w'-]+){0,5}\s+(?:is|was|has been|will be)\s*$", prefix, re.I)
        or re.search(r"\b(?:planned|proposed|awaiting|pending)\s+(?:to\s+be|being)\s*$", prefix, re.I)
        or re.search(r"\b(?:if|unless|until|after)\b(?:\s+[\w'-]+){0,4}\s*$", prefix, re.I)
    )


def _scoped_negation_governs(prefix: str) -> bool:
    match = re.search(r"\b(?:not|never)\b(?P<tail>[^,;.!?]*)$", prefix, re.I)
    if match is None:
        return False
    tail = match.group("tail")
    if len(re.findall(r"[\w'-]+", tail)) > 8:
        return False
    return re.search(r"\b(?:is|was|were|has|have|had)\b", tail, re.I) is None

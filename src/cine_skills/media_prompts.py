"""Semantic checks for vendor-neutral media prompt packages."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

_POSITIVE_ID = r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
_DOMAIN_FIELDS = {
    "video": ("scene_action", "identity_lock", "start_composition", "end_composition", "camera_movement", "trajectory", "direction", "speed", "subject_retention", "lens_depth_light_texture_mood", "performance_timing", "duration_assumption"),
    "image": ("subject_or_place", "composition", "view_or_scale", "light_material_mood", "identity_or_environment_lock"),
    "voice": ("speaker_or_source", "performance_intent", "delivery_timing", "originality_boundary"),
    "music": ("dramatic_function", "dialogue_policy", "entry_exit_shape", "instrumental_texture", "originality_boundary"),
    "sound": ("sound_source", "event_or_bed", "perspective", "timing_and_decay"),
}
_VENDORS = r"(?:midjourney|stable\s+diffusion|dall-?e|sora|runway|adobe\s+firefly)"
_AFFIRMATIVE_CLEARANCE = re.compile(
    r"\b(?:consent|permission|rights?|legal\s+clearance)\b"
    r"(?P<between>[^.;,]{0,45}?)\b(?:granted|confirmed|approved|cleared)\b",
    re.I,
)
_PRODUCTION_BOUNDARY = re.compile(
    r"\b(?:budget|schedule|casting|procurement|nle|dcc|legal\s+decisions?)\b",
    re.I,
)


def _iter_text(value: Any, path: str = "$"):
    """Yield strings without recursively descending untrusted nesting."""
    stack = [(path, value)]
    while stack:
        location, current = stack.pop()
        if isinstance(current, str):
            yield location, current
        elif isinstance(current, Mapping):
            for key, child in reversed(list(current.items())):
                stack.append((f"{location}.{key}", child))
        elif isinstance(current, list):
            for index in range(len(current) - 1, -1, -1):
                stack.append((f"{location}.{index}", current[index]))


def _prompt_texts(prompt: Mapping[str, Any]):
    """Return instructions, deliberately excluding source-path metadata."""
    for field in ("creative_content", "immutable_anchors", "allowed_variation", "technical_assumptions", "negative_constraints", "continuity_anchors", "acceptance_criteria"):
        yield from _iter_text(prompt.get(field), field)
    for domain, fields in _DOMAIN_FIELDS.items():
        value = prompt.get(domain)
        if isinstance(value, Mapping):
            for field in fields:
                yield from _iter_text(value.get(field), f"{domain}.{field}")


_SEMANTIC_BOUNDARY = re.compile(
    r"[.;]|\s*,\s*(?:but|however|yet)\b|\b(?:but|however|although|while)\b|(?<!not\s)\byet\s+(?=(?:still\s+)?(?:do\s+)?(?:match|replicate|recreate|clone|use)\b)",
    re.I,
)


def _semantic_segments(text: str) -> list[str]:
    """Split independent predicates without treating ordinary commas as clauses."""
    segments: list[str] = []
    start = 0
    for boundary in _SEMANTIC_BOUNDARY.finditer(text):
        segment = text[start:boundary.start()]
        if segment.strip():
            segments.append(segment)
        start = boundary.end()
    if text[start:].strip():
        segments.append(text[start:])
    return segments


def _predicate_prefix(text: str, start: int) -> str:
    """Return the local phrase governing a predicate at *start*."""
    segment_start = 0
    for boundary in _SEMANTIC_BOUNDARY.finditer(text):
        if boundary.start() >= start:
            break
        segment_start = boundary.end()
    return text[segment_start:start]


def _predicate_is_directly_negated(text: str, start: int) -> bool:
    prefix = _predicate_prefix(text, start)
    return bool(
        re.search(r"\b(?:do not|don't|never)\s+(?:[\w'-]+\s+){0,6}$", prefix, re.I)
        or re.search(r"\bno\s+$", prefix, re.I)
    )


def _leading_no_governs_review(segment: str, start: int) -> bool:
    """Return whether a leading No governs the review subject ending at *start*."""
    return bool(
        re.fullmatch(
            r"\s*no\b(?:\s+[\w'/-]+|,\s*(?:(?:and|or)\s+)?[\w'/-]+)*\s*",
            segment[:start],
            re.I,
        )
    )


def _has_affirmative_clearance(text: str) -> bool:
    for segment in re.split(r"[.;,]|\b(?:but|although|while)\b", text, flags=re.I):
        for match in _AFFIRMATIVE_CLEARANCE.finditer(segment):
            prefix = segment[:match.start()] + match.group("between")
            if not re.search(r"\b(?:no|not|without)\b", prefix, re.I):
                return True
    return False


def _review_bypass(text: str) -> bool:
    for segment in _semantic_segments(text):
        if re.search(r"\bno\b[^.;]{0,80}\breview\s+(?:is\s+)?(?:required|needed|necessary)\b", segment, re.I):
            return True
        for match in re.finditer(
            r"\breview\s+(?:is\s+)?(?P<predicate>not\s+required|not\s+needed|optional|skipped|bypassed|waived)\b",
            segment,
            re.I,
        ):
            predicate = match.group("predicate").casefold()
            if (
                predicate in {"optional", "skipped", "bypassed", "waived"}
                and _leading_no_governs_review(segment, match.start())
            ):
                continue
            return True
        if re.search(
            r"\b(?:generation|production|work)\s+may\s+proceed\s+(?:before|without)\b",
            segment,
            re.I,
        ):
            return True
        for match in re.finditer(
            r"\b(?:skip|bypass|waive)\s+(?:the\s+)?review\b", segment, re.I
        ):
            if not _predicate_is_directly_negated(segment, match.start()):
                return True
    return False


def _protected_production_ranges(segment: str) -> list[range]:
    return [
        range(match.start(), match.end())
        for pattern in (
            r"\b(?:do not|don't|never)\s+make\s+[^.;]*?\bdecisions?\b",
            r"^\s*no\b[^.;]*?\bdecisions?\b",
        )
        for match in re.finditer(pattern, segment, re.I)
    ]


def _has_affirmative_production_action(text: str) -> bool:
    for segment in _semantic_segments(text):
        protected = _protected_production_ranges(segment)
        for match in _PRODUCTION_BOUNDARY.finditer(segment):
            if any(match.start() in item for item in protected):
                continue
            if not _predicate_is_directly_negated(segment, match.start()):
                return True
    return False


def _real_person_modalities(text: str) -> set[str]:
    """Return real-person modalities described in a value-bearing instruction."""
    modalities: set[str] = set()
    person = r"(?:real|living|named|recognizable|specific)\s+(?:person|performer|human|actor)"
    patterns = {
        "likeness": rf"\b{person}(?:'s)?\s+(?:likeness|face)\b|\b{person}\s+reference\b[^.]{{0,80}}\b(?:likeness|face)\b|\b(?:match|replicate|recreate|clone)\b[^.]{{0,80}}\b(?:likeness|face)\b",
        "voice": rf"\b{person}(?:'s)?\s+voice\b|\b{person}\s+reference\b[^.]{{0,80}}\bvoice\b|\b(?:match|replicate|recreate|clone)\b[^.]{{0,80}}\bvoice\b",
    }
    for segment in _semantic_segments(text):
        for modality, pattern in patterns.items():
            for match in re.finditer(pattern, segment, re.I):
                if not _predicate_is_directly_negated(segment, match.start()):
                    modalities.add(modality)
    return modalities


def _forbidden_errors(path: str, text: str) -> list[str]:
    errors: list[str] = []
    if re.search(r"\b[a-z][a-z0-9+.-]*://", text, re.I):
        errors.append(f"{path}: URLs are not permitted")
    if re.search(r"\bdata:[^\s,]+;base64,|\bbase64\s*,|(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{64,}={0,2}(?![A-Za-z0-9+/])", text, re.I):
        errors.append(f"{path}: embedded media is not permitted")
    if re.search(r"\b(?:api[_ -]?key|secret|password|token)\s*(?:[:=]|is|equals)\s*['\"]?[A-Za-z0-9_./+=-]{4,}|\b(?:use|provide|set)\s+(?:an?\s+)?(?:api[_ -]?key|secret|password|token)\s+['\"]?[A-Za-z0-9_./+=-]{4,}", text, re.I):
        errors.append(f"{path}: secrets are not permitted")
    imitation = re.search(r"\b(?:in\s+the\s+exact\s+style\s+of|(?:copy|imitate|match|recreate)\b[^.]{0,60}\b(?:style|aesthetic|work)\b[^.]{0,60}\b(?:exactly|of)\b)", text, re.I)
    if imitation and not _predicate_is_directly_negated(text, imitation.start()):
        errors.append(f"{path}: living-artist imitation is not permitted")
    if re.search(rf"\b(?:use|using|with|via|on|in)\s+{_VENDORS}\b|\b{_VENDORS}\s+(?:settings?|parameters?|prompt|render|model)\b", text, re.I):
        errors.append(f"{path}: vendor or software prescriptions are not permitted")
    if re.search(r"(?:^|\s)--[a-z][\w-]*(?:\s|$)|\b(?:cfg|sampler|seed)\s*=", text, re.I):
        errors.append(f"{path}: vendor parameter syntax is not permitted")
    if _has_affirmative_production_action(text):
        errors.append(f"{path}: production, software-control, or legal-decision content is not permitted")
    return errors


def validate_media_prompt_package_contract(payload: Mapping[str, Any]) -> list[str]:
    """Validate IDs, exact provenance, review state, and portable instructions."""
    errors: list[str] = []
    project = payload.get("project_id")
    if not isinstance(project, str):
        return errors
    context = payload.get("source_context")
    if not isinstance(context, Mapping):
        return errors
    registries = context.get("registries")
    if not isinstance(registries, Mapping):
        return errors
    registry_for_kind = {"character": "character_ids", "scene": "scene_ids", "shot": "shot_ids", "asset": "asset_ids", "world": "world_ids", "beat": "beat_ids", "sound": "sound_ids"}
    registered: dict[str, set[str]] = {}
    for kind, field in registry_for_kind.items():
        ids: set[str] = set()
        if isinstance(registries.get(field), list):
            for index, identifier in enumerate(registries[field]):
                if not isinstance(identifier, str):
                    continue
                if not identifier.startswith(f"{project}-"):
                    errors.append(f"source_context.registries.{field}.{index}: {identifier!r} must belong to project {project}")
                if identifier in ids:
                    errors.append(f"source_context.registries.{field}.{index}: duplicate {kind} ID {identifier}")
                ids.add(identifier)
        registered[kind] = ids
    facts: dict[str, Mapping[str, Any]] = {}
    if isinstance(context.get("source_facts"), list):
        for index, fact in enumerate(context["source_facts"]):
            if not isinstance(fact, Mapping):
                continue
            fact_id, scope, subject_id = fact.get("fact_id"), fact.get("scope"), fact.get("subject_id")
            if not isinstance(fact_id, str):
                continue
            if re.fullmatch(rf"{re.escape(project)}-SF{_POSITIVE_ID}", fact_id) is None:
                errors.append(f"source_context.source_facts.{index}.fact_id: {fact_id!r} must match {project}-SF###")
            if fact_id in facts:
                errors.append(f"source_context.source_facts.{index}.fact_id: duplicate source fact ID {fact_id}")
            facts.setdefault(fact_id, fact)
            value = fact.get("value")
            if isinstance(value, str):
                errors.extend(_forbidden_errors(f"source_context.source_facts.{index}.value", value))
                if _has_affirmative_clearance(value):
                    errors.append(f"source_context.source_facts.{index}.value: artifact cannot assert consent, permission, rights, or legal clearance")
            if scope == "project" and subject_id != project:
                errors.append(f"source_context.source_facts.{index}.subject_id: project fact must bind exactly to project_id {project}")
            elif isinstance(scope, str) and scope != "project" and isinstance(subject_id, str) and subject_id not in registered.get(scope, set()):
                errors.append(f"source_context.source_facts.{index}.subject_id: unknown {scope} reference {subject_id}")
    ledger_specs = (("constraint", "supplied_constraints", "SC"), ("approved", "approval_evidence", "APR"), ("consent", "consent_evidence", "CON"))
    ledgers: dict[str, dict[str, Mapping[str, Any]]] = {name: {} for name, _, _ in ledger_specs}
    all_ledger_ids: set[str] = set()
    for status, field, suffix in ledger_specs:
        if isinstance(context.get(field), list):
            for index, record in enumerate(context[field]):
                if not isinstance(record, Mapping) or not isinstance(record.get("record_id"), str):
                    continue
                record_id = record["record_id"]
                if re.fullmatch(rf"{re.escape(project)}-{suffix}{_POSITIVE_ID}", record_id) is None:
                    errors.append(f"source_context.{field}.{index}.record_id: {record_id!r} must match {project}-{suffix}###")
                if record_id in all_ledger_ids:
                    errors.append(f"source_context.{field}.{index}.record_id: duplicate ID across provenance ledgers {record_id}")
                all_ledger_ids.add(record_id)
                if record_id in ledgers[status]:
                    errors.append(f"source_context.{field}.{index}.record_id: duplicate {status} record ID {record_id}")
                ledgers[status][record_id] = record
                value = record.get("value")
                if isinstance(value, str):
                    errors.extend(_forbidden_errors(f"source_context.{field}.{index}.value", value))
                    if _has_affirmative_clearance(value):
                        errors.append(f"source_context.{field}.{index}.value: artifact cannot assert consent, permission, rights, or legal clearance")
    prompts = payload.get("prompts")
    if not isinstance(prompts, list):
        return errors
    handoffs = payload.get("human_review_handoffs", [])
    handoffs_by_prompt: dict[str, list[Mapping[str, Any]]] = {}
    handoff_ids: set[str] = set()
    if isinstance(handoffs, list):
        for index, handoff in enumerate(handoffs):
            if not isinstance(handoff, Mapping):
                continue
            location = f"human_review_handoffs.{index}"
            if isinstance(handoff.get("handoff_id"), str):
                handoff_id = handoff["handoff_id"]
                if re.fullmatch(rf"{re.escape(project)}-HR{_POSITIVE_ID}", handoff_id) is None:
                    errors.append(f"{location}.handoff_id: {handoff_id!r} must match {project}-HR###")
                if handoff_id in handoff_ids:
                    errors.append(f"{location}.handoff_id: duplicate human review handoff ID {handoff_id}")
                handoff_ids.add(handoff_id)
            if isinstance(handoff.get("prompt_id"), str):
                handoffs_by_prompt.setdefault(handoff["prompt_id"], []).append(handoff)
            if handoff.get("review_action") != "require-qualified-human-consent-rights-review" or handoff.get("review_status") != "pending-qualified-human-review":
                errors.append(f"{location}: review_action and review_status must affirm a pending qualified-human review")
            review = handoff.get("review")
            if isinstance(review, str) and _has_affirmative_clearance(review):
                errors.append(f"{location}.review: handoff cannot assert consent, permission, rights, or legal clearance")
            if isinstance(review, str) and _review_bypass(review):
                errors.append(f"{location}.review: review bypass or waiver is not permitted")
            if isinstance(handoff.get("consent_evidence_ids"), list):
                for evidence_index, evidence_id in enumerate(handoff["consent_evidence_ids"]):
                    if isinstance(evidence_id, str) and evidence_id not in ledgers["consent"]:
                        errors.append(f"{location}.consent_evidence_ids.{evidence_index}: unknown consent evidence {evidence_id}")
    category_domain = {"video": "video", "character-image": "image", "environment-image": "image", "key-frame": "image", "voice": "voice", "dialogue": "voice", "music": "music", "ambience": "sound", "foley": "sound", "effect": "sound"}
    prompt_ids: set[str] = set()
    for index, prompt in enumerate(prompts):
        if not isinstance(prompt, Mapping):
            continue
        location, prompt_id = f"prompts.{index}", prompt.get("prompt_id")
        if isinstance(prompt_id, str):
            if re.fullmatch(rf"{re.escape(project)}-MP{_POSITIVE_ID}", prompt_id) is None:
                errors.append(f"{location}.prompt_id: {prompt_id!r} must match {project}-MP###")
            if prompt_id in prompt_ids:
                errors.append(f"{location}.prompt_id: duplicate prompt ID {prompt_id}")
            prompt_ids.add(prompt_id)
        texts = list(_prompt_texts(prompt))
        for path, text in texts:
            errors.extend(_forbidden_errors(f"{location}.{path}", text))
            if _has_affirmative_clearance(text):
                errors.append(f"{location}.{path}: artifact cannot assert consent, permission, rights, or legal clearance")
        category = prompt.get("category")
        expected_domain = category_domain.get(category) if isinstance(category, str) else None
        for domain in _DOMAIN_FIELDS:
            if domain != expected_domain and domain in prompt:
                errors.append(f"{location}.{domain}: {category} prompt cannot carry irrelevant {domain} structure")
        refs: dict[str, set[str]] = {}
        if isinstance(prompt.get("upstream_references"), list):
            for ref_index, reference in enumerate(prompt["upstream_references"]):
                if not isinstance(reference, Mapping):
                    continue
                kind, identifier = reference.get("kind"), reference.get("id")
                if isinstance(kind, str) and isinstance(identifier, str):
                    refs.setdefault(kind, set()).add(identifier)
                    if identifier not in registered.get(kind, set()):
                        errors.append(f"{location}.upstream_references.{ref_index}.id: {identifier} does not belong to {kind} registry")
                        if kind == "shot":
                            errors.append(f"{location}.upstream_references.{ref_index}.id: unknown shot reference {identifier}")
        cited_fact_ids: set[str] = set()
        for field in ("creative_content", "immutable_anchors", "allowed_variation", "technical_assumptions"):
            claims = prompt.get(field)
            if isinstance(claims, list):
                for claim in claims:
                    if isinstance(claim, Mapping) and isinstance(claim.get("provenance"), Mapping):
                        source_id = claim["provenance"].get("source_id")
                        if isinstance(source_id, str) and source_id in facts:
                            cited_fact_ids.add(source_id)
        if expected_domain and isinstance(prompt.get(expected_domain), Mapping):
            for field in _DOMAIN_FIELDS[expected_domain]:
                claim = prompt[expected_domain].get(field)
                if isinstance(claim, Mapping) and isinstance(claim.get("provenance"), Mapping):
                    source_id = claim["provenance"].get("source_id")
                    if isinstance(source_id, str) and source_id in facts:
                        cited_fact_ids.add(source_id)
        detected_modalities = set().union(*(_real_person_modalities(text) for _, text in texts))
        for fact_id in cited_fact_ids:
            value = facts[fact_id].get("value")
            if isinstance(value, str):
                detected_modalities.update(_real_person_modalities(value))
        declaration = prompt.get("real_person_use")
        declared_modalities = {
            "none": set(), "likeness": {"likeness"}, "voice": {"voice"},
            "likeness-and-voice": {"likeness", "voice"},
        }.get(declaration, set())
        if declaration not in {"none", "likeness", "voice", "likeness-and-voice"}:
            errors.append(f"{location}.real_person_use: structured real-person declaration is required")
        if not detected_modalities.issubset(declared_modalities):
            errors.append(f"{location}.real_person_use: real-person declaration cannot be none or omit a detected likeness or voice use")
        if (detected_modalities or declared_modalities) and not handoffs_by_prompt.get(prompt_id):
            errors.append(f"{location}: real-person likeness or voice request requires a structured qualified-human consent/rights review handoff")
        def validate_claim(claim: Any, claim_location: str) -> None:
            if not isinstance(claim, Mapping) or not isinstance(claim.get("provenance"), Mapping):
                errors.append(f"{claim_location}: provenance-bearing domain decision required")
                return
            provenance, value = claim["provenance"], claim.get("value")
            status, source_id = provenance.get("status"), provenance.get("source_id")
            if status == "supplied":
                source = facts.get(source_id) if isinstance(source_id, str) else None
                if not isinstance(source, Mapping) or source.get("value") != value:
                    errors.append(f"{claim_location}.value: supplied claim must exactly match value and source fact ledger")
                elif source.get("scope") == "project" and source.get("subject_id") != project:
                    errors.append(f"{claim_location}.provenance.source_id: project fact must bind exactly to project_id")
                elif source.get("scope") != "project" and source.get("subject_id") not in refs.get(source.get("scope"), set()):
                    errors.append(f"{claim_location}.provenance.source_id: supplied fact must bind its exact typed upstream ID")
            elif status in {"constraint", "approved"}:
                record = ledgers[status].get(source_id) if isinstance(source_id, str) else None
                if not isinstance(record, Mapping):
                    errors.append(f"{claim_location}.provenance.source_id: unknown {status} ledger record {source_id}")
                elif record.get("value") != value:
                    errors.append(f"{claim_location}.value: {status} claim must exactly match its external ledger record")
            elif status in {"proposed", "assumption", "uncertainty"}:
                source = facts.get(source_id) if isinstance(source_id, str) else None
                if source is None and source_id not in ledgers["constraint"]:
                    errors.append(f"{claim_location}.provenance.source_id: proposal, assumption, or uncertainty must cite an external source fact or supplied constraint")
                elif isinstance(source, Mapping) and source.get("scope") == "project" and source.get("subject_id") != project:
                    errors.append(f"{claim_location}.provenance.source_id: project fact must bind exactly to project_id")
                elif isinstance(source, Mapping) and source.get("scope") != "project" and source.get("subject_id") not in refs.get(source.get("scope"), set()):
                    errors.append(f"{claim_location}.provenance.source_id: fact-backed decision must bind its exact typed upstream ID")
        for field in ("creative_content", "immutable_anchors", "allowed_variation", "technical_assumptions"):
            if isinstance(prompt.get(field), list):
                for claim_index, claim in enumerate(prompt[field]):
                    validate_claim(claim, f"{location}.{field}.{claim_index}")
        if expected_domain and isinstance(prompt.get(expected_domain), Mapping):
            for field in _DOMAIN_FIELDS[expected_domain]:
                value = prompt[expected_domain].get(field)
                validate_claim(value, f"{location}.{expected_domain}.{field}")
                if field == "camera_movement" and isinstance(value, Mapping) and isinstance(value.get("value"), str) and re.search(r"\blocked[- ]off\b.*\b(?:orbit|track|pan)\b", value["value"], re.I):
                    errors.append(f"{location}.{expected_domain}.{field}.value: contradictory locked-off movement decision")
    for index, handoff in enumerate(handoffs if isinstance(handoffs, list) else []):
        if isinstance(handoff, Mapping) and isinstance(handoff.get("prompt_id"), str) and handoff["prompt_id"] not in prompt_ids:
            errors.append(f"human_review_handoffs.{index}.prompt_id: unknown prompt {handoff['prompt_id']}")
    return errors

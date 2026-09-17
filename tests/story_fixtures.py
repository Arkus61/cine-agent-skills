from __future__ import annotations

import copy
import json
from pathlib import Path

from tests.v1_fixtures import write_full_v1_package


STORY_ARTIFACTS = (
    ("story-concept.json", "story-concept"),
    ("story-structure.json", "story-structure"),
    ("character-arcs.json", "character-arcs"),
    ("world-bible.json", "world-bible"),
    ("season-arc.json", "season-arc"),
    ("story-manifest.json", "layer-manifest"),
)

SCRIPT_ARTIFACTS = (
    ("unit-outline.json", "unit-outline"),
    ("screenplay.fountain", "fountain"),
    ("screenplay-metadata.json", "screenplay-metadata"),
    ("script-revision-plan.json", "script-revision-plan"),
    ("scenes", "full-v1"),
    ("script-manifest.json", "layer-manifest"),
)


def _manifest(project_id: str, layer: str, artifacts: tuple[tuple[str, str], ...]):
    return {
        "schema_version": "2.0",
        "release_version": "2.0.0",
        "project_id": project_id,
        "layer": layer,
        "profile": "story-v2",
        "artifacts": [
            {
                "filename": filename,
                "schema_name": schema_name,
                "schema_version": "2.0",
                "dependency_order": order,
            }
            for order, (filename, schema_name) in enumerate(artifacts, start=1)
        ],
        "validation_status": "valid",
        "unresolved_questions": [],
    }


STORY_PAYLOADS: dict[str, object] = {
    "story-concept.json": {
        "schema_version": "2.0",
        "project_id": "EMBER",
        "project_format": "series",
        "production_modes": ["live-action"],
        "runtime_intent": "Two ten-minute episodes.",
        "audience_promise": "A clear mystery with a consequential answer.",
        "premise": "A courier finds a signal beneath a road checkpoint.",
        "logline": "A courier trades her map to expose a buried signal.",
        "central_dramatic_question": "Will Mara reveal what the road is hiding?",
        "themes": ["truth has a cost"],
        "genres": ["mystery"],
        "tone": ["tense"],
        "world_scope": "A salt road and its checkpoint.",
        "protagonist_focus": "Mara chooses between passage and evidence.",
        "supplied_constraints": [
            {
                "statement": "The story centers a courier, a map, and a road checkpoint.",
                "source_reference": "Test fixture brief, sentence 1.",
            }
        ],
        "success_criteria": ["Every episode advances the signal mystery."],
        "assumptions": ["The checkpoint remains the principal location."],
        "uncertainties": ["The signal source is intentionally unresolved."],
    },
    "story-structure.json": {
        "schema_version": "2.0",
        "project_id": "EMBER",
        "candidate_models": [
            {"name": "Three Act", "fit": "Causal turns.", "benefits": ["Clear escalation."], "risks": ["Can feel rigid."]},
            {"name": "Serial mystery", "fit": "Two linked reveals.", "benefits": ["Renewable questions."], "risks": ["Can defer answers."]},
        ],
        "selection_criteria": [{"criterion": "causality", "brief_evidence": "The signal changes Mara's goal.", "priority": "high"}],
        "selected_model": "Serial mystery",
        "hybrid_components": [],
        "selection_rationale": "The episodes resolve one question and open another.",
        "intentional_deviations": ["The first episode ends on a changed goal."],
        "plotlines": [{"plotline_id": "EMBER-PL01", "title": "The signal", "function": "Drive the investigation.", "progression": "Detection becomes response."}],
        "sequences": [
            {"sequence_id": "EMBER-SQ01", "title": "Detection", "purpose": "Plant the signal.", "plotline_ids": ["EMBER-PL01"], "event_ids": ["EMBER-EV001"]},
            {"sequence_id": "EMBER-SQ02", "title": "Response", "purpose": "Pay off the signal.", "plotline_ids": ["EMBER-PL01"], "event_ids": ["EMBER-EV002"]},
        ],
        "events": [
            {"event_id": "EMBER-EV001", "order": 1, "sequence_id": "EMBER-SQ01", "plotline_ids": ["EMBER-PL01"], "description": "Mara detects the signal.", "story_function": "setup", "causal_change": "She stops at the checkpoint.", "retention_effect": "Opens a concrete question."},
            {"event_id": "EMBER-EV002", "order": 2, "sequence_id": "EMBER-SQ02", "plotline_ids": ["EMBER-PL01"], "description": "The checkpoint answers the signal.", "story_function": "payoff", "causal_change": "The road becomes unsafe.", "retention_effect": "Answers and enlarges the question."},
        ],
        "setup_payoffs": [{"setup_event_id": "EMBER-EV001", "payoff_event_id": "EMBER-EV002", "relationship": "The detected pulse receives an answer."}],
        "assumptions": [],
        "uncertainties": [],
    },
    "character-arcs.json": {
        "schema_version": "2.0",
        "project_id": "EMBER",
        "characters": [
            {
                "character_id": "EMBER-CH001", "name": "Mara", "role": "Courier protagonist", "external_objective": "Cross the road.", "internal_need": "Share dangerous evidence.", "governing_tension": "Passage conflicts with disclosure.",
                "agency": {"capacity": "Can trade the map.", "constraints": ["The gate is locked."], "choices_under_pressure": ["Trades the map for access."]},
                "values": ["truth"], "relationships": [{"target_character_id": "EMBER-CH002", "dynamic": "Mara needs the Keeper's consent.", "arc": "Suspicion becomes cooperation."}], "arc_shape": "positive", "turning_event_ids": ["EMBER-EV001", "EMBER-EV002"], "behavioral_evidence": ["Mara shares the signal."], "contradictions": ["She protects evidence by hiding it."], "endpoint": "Mara chooses disclosure."
            },
            {
                "character_id": "EMBER-CH002", "name": "Keeper", "role": "Gatekeeper", "external_objective": "Protect the checkpoint.", "internal_need": "Accept outside evidence.", "governing_tension": "Secrecy conflicts with safety.",
                "agency": {"capacity": "Can open the gate.", "constraints": ["The signal threatens the road."], "choices_under_pressure": ["Opens the gate after the answer."]},
                "values": ["safety"], "relationships": [{"target_character_id": "EMBER-CH001", "dynamic": "The Keeper doubts Mara.", "arc": "Doubt becomes conditional trust."}], "arc_shape": "open", "turning_event_ids": ["EMBER-EV002"], "behavioral_evidence": ["The Keeper unlocks the gate."], "contradictions": ["He hides danger to keep travelers safe."], "endpoint": "The Keeper shares the road warning."
            },
        ],
        "assumptions": [],
        "uncertainties": [],
    },
    "world-bible.json": {
        "schema_version": "2.0", "project_id": "EMBER",
        "scope": {"story_boundary": "The salt road checkpoint.", "scales": ["local"], "excluded_or_unknown": []},
        "locations": [{"location_id": "EMBER-LO001", "name": "Salt checkpoint", "scale": "Roadside", "story_function": "Blocks passage.", "material_conditions": ["Salt wind corrodes metal."], "access_constraints": ["A keeper controls the gate."], "canon_status": "canon", "provenance": "supplied", "basis": "The brief supplies the checkpoint."}],
        "factions": [], "institutions": [], "history": [], "cultures": [],
        "systems": [{"name": "Buried signal", "system_type": "technology", "inputs": ["electrical pulse"], "outputs": ["answering pulse"], "dependencies": ["road conduit"], "rule_ids": ["EMBER-WR001"], "canon_status": "proposal", "provenance": "proposed", "basis": "A bounded mechanism for the supplied signal."}],
        "rules": [{"rule_id": "EMBER-WR001", "name": "Signal answer", "system_type": "technology", "statement": "A scan receives one delayed answer.", "cost": "The road conduit heats.", "limit": "Only one answer per scan.", "contradiction_checks": [{"scenario": "Two answers follow one scan.", "expected_behavior": "Only the first is genuine.", "resolution": "Treat the second as another source."}], "provenance": "proposed", "canon_status": "proposal", "basis": "Keeps the mechanism bounded.", "story_consequence": "Scanning alerts the checkpoint."}],
        "terminology": [],
        "production_assets": [{"asset_id": "EMBER-AS001", "name": "Courier map", "asset_type": "prop", "world_function": "Records passage.", "production_use": "Setup and trade object.", "canon_status": "canon", "provenance": "supplied", "basis": "The brief supplies the map."}],
        "assumptions": [], "uncertainties": [],
    },
}


def _episode(episode_id: str, number: int, event_id: str, next_id: str | None):
    return {
        "episode_id": episode_id, "episode_number": number, "title": f"Episode {number}", "episode_type": "premiere" if number == 1 else "finale", "episode_premise": "Mara follows the signal.",
        "cold_open": None, "act_outs": [{"position": "end", "turn": "The signal changes.", "pressure": "The road is unsafe."}],
        "plot_distribution": [{"slot": "A", "plotline_id": "EMBER-PL01", "event_ids": [event_id], "episode_engine": "Investigate the signal.", "advancement": "The signal advances."}],
        "local_resolution": "The episode's signal question is answered.", "escalation": "The answer increases danger.", "opening_hook": "A pulse interrupts passage.",
        "forward_hook": None if next_id is None else {"target_episode_id": next_id, "mechanism": "changed-goal", "promise": "Mara follows the answer."},
        "cliffhanger": None,
    }


STORY_PAYLOADS["season-arc.json"] = {
    "schema_version": "2.0", "project_id": "EMBER", "project_format": "series", "season_premise": "A courier traces an answering road signal.", "season_dramatic_question": "What is beneath the road?", "arc_strategy": "Two linked signal events.",
    "source_plotline_ids": ["EMBER-PL01"], "source_event_ids": ["EMBER-EV001", "EMBER-EV002"], "source_character_ids": ["EMBER-CH001", "EMBER-CH002"],
    "episodes": [_episode("EMBER-E01", 1, "EMBER-EV001", "EMBER-E02"), _episode("EMBER-E02", 2, "EMBER-EV002", None)],
    "character_progression": [{"character_id": "EMBER-CH001", "episode_ids": ["EMBER-E01", "EMBER-E02"], "event_ids": ["EMBER-EV001", "EMBER-EV002"], "progression": "Mara moves from concealment to disclosure.", "endpoint": "She shares the warning."}],
    "relationship_progression": [{"character_ids": ["EMBER-CH001", "EMBER-CH002"], "episode_ids": ["EMBER-E01", "EMBER-E02"], "event_ids": ["EMBER-EV001", "EMBER-EV002"], "progression": "Suspicion becomes cooperation.", "endpoint": "They share the road warning."}],
    "reveal_schedule": [{"event_id": "EMBER-EV002", "episode_id": "EMBER-E02", "reveal": "The road answers.", "audience_effect": "The threat becomes active."}],
    "season_setups": [{"setup_event_id": "EMBER-EV001", "episode_id": "EMBER-E01", "setup": "Mara sends a scan.", "intended_payoff": "The road answers."}],
    "finale_payoff": {"episode_id": "EMBER-E02", "setup_event_ids": ["EMBER-EV001"], "payoff_event_ids": ["EMBER-EV002"], "resolution": "The signal answers.", "consequence": "The road closes.", "season_question_status": "partially-answered"},
    "unresolved_threads": [{"plotline_id": "EMBER-PL01", "state": "The source remains buried.", "reason_retained": "A later unit may investigate it."}],
    "next_season_seeds": [], "assumptions": [], "uncertainties": [],
}
STORY_PAYLOADS["story-manifest.json"] = _manifest("EMBER", "story", STORY_ARTIFACTS)


def _unit_outline(unit_id: str, event_id: str, final: bool):
    scene_id = f"{unit_id}-SC001"
    return {
        "schema_version": "2.0", "project_id": "EMBER", "project_format": "series", "unit_id": unit_id, "runtime_seconds": 600, "runtime_basis": "Ten-minute episode.", "unit_objective": "Resolve one signal event.", "structural_model": "Serial mystery", "source_event_ids": [event_id], "source_plotline_ids": ["EMBER-PL01"],
        "opening_hook": {"scene_id": scene_id, "promise": "A pulse interrupts the road.", "function": "Orient the episode."},
        "scenes": [{"scene_id": scene_id, "scene_index": 1, "start_seconds": 0, "end_seconds": 600, "title": "Checkpoint", "summary": "Mara confronts the signal.", "story_function": "Advance the mystery.", "event_ids": [event_id], "plotline_ids": ["EMBER-PL01"], "evidence_status": "not-applicable", "retention_function": "Resolve the episode question."}],
        "event_coverage": [{"event_id": event_id, "scene_ids": [scene_id], "outcome": "The event changes the road."}],
        "plotline_coverage": [{"plotline_id": "EMBER-PL01", "scene_ids": [scene_id], "advancement": "The signal advances."}],
        "emotional_turns": [{"scene_id": scene_id, "from_state": "uncertainty", "to_state": "resolve", "change": "Mara chooses disclosure."}], "act_outs": [], "midpoint": None, "climax": {"scene_id": scene_id, "function": "The signal changes."}, "resolution": {"scene_id": scene_id, "outcome": "The local question is answered.", "unit_change": "The road status changes."},
        "forward_hook": None if final else {"scene_id": scene_id, "promise": "The answer changes Mara's goal.", "dependency": "The next episode follows the response."},
        "format_plan": {"mode": "series-episode", "episode_position": "finale" if final else "nonfinal", "local_resolution": "Resolve the local signal question.", "season_dependencies": [{"dependency": "The signal plot continues.", "carry_forward": "Carry the changed road status."}]},
        "assumptions": [], "uncertainties": [],
    }


def _revision(unit_id: str, scene_id: str):
    source_id = f"{scene_id}-A01"
    return {
        "schema_version": "2.0", "project_id": "EMBER", "unit_id": unit_id, "draft_version": "first", "project_format": "series", "revision_scope": "One scene pass.", "source_element_ids": [source_id], "approved_constraints": [],
        "diagnosis_items": [{"diagnosis_id": f"{unit_id}-RV001", "category": "pace", "affected_ids": [source_id], "evidence": [{"source_id": source_id, "observation": "The turn arrives late.", "effect": "The outcome is compressed."}], "diagnosis": "The scene delays its turn.", "priority": 1, "dependency_impact": "scene-engine", "dependency_rationale": "Scene order controls the turn.", "proposed_change": "Move the turn earlier.", "change_target_ids": [source_id], "execution_mode": "executable-change", "preserved_constraint_ids": [], "preservation_checks": [], "decision_request": None, "downstream_impact": ["Recheck dialogue."], "status": "proposed", "assumptions": [], "uncertainties": []}],
        "assumptions": [], "uncertainties": [],
    }


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def write_story_package(path: Path) -> None:
    path.mkdir(parents=True)
    for filename, payload in STORY_PAYLOADS.items():
        write_json(path / filename, copy.deepcopy(payload))


def write_script_package(path: Path, unit_id: str, event_id: str, final: bool) -> None:
    path.mkdir(parents=True)
    scene_id = f"{unit_id}-SC001"
    outline = _unit_outline(unit_id, event_id, final)
    metadata = {
        "schema_version": "2.0", "project_id": "EMBER", "unit_id": unit_id, "source_event_ids": [event_id],
        "scene_mappings": [{"scene_id": scene_id, "heading": "EXT. SALT ROAD - DUSK", "event_ids": [event_id], "character_ids": ["EMBER-CH001"], "location_id": "EMBER-LO001", "objective": "Mara secures passage.", "conflict": "The signal blocks the road.", "turn": "Mara shares the signal."}],
        "character_mappings": [{"character_id": "EMBER-CH001", "cue": "MARA"}], "location_mappings": [{"location_id": "EMBER-LO001", "name": "Salt checkpoint"}], "setup_payoffs": [], "assumptions": [], "uncertainties": [],
    }
    for filename, payload in {
        "unit-outline.json": outline,
        "screenplay-metadata.json": metadata,
        "script-revision-plan.json": _revision(unit_id, scene_id),
        "script-manifest.json": _manifest("EMBER", "script", SCRIPT_ARTIFACTS),
    }.items():
        write_json(path / filename, payload)
    (path / "screenplay.fountain").write_text(
        "Title: Ember Road\n\nEXT. SALT ROAD - DUSK\n\nWind drives salt over the gate.\n\nMARA\nOpen the road.\n",
        encoding="utf-8",
    )
    scenes = path / "scenes"
    scenes.mkdir()
    write_full_v1_package(scenes / scene_id, scene_id)


def write_story_project(root: Path) -> tuple[Path, Path]:
    story = root / "story"
    scripts = root / "scripts"
    write_story_package(story)
    write_script_package(scripts / "EMBER-E01", "EMBER-E01", "EMBER-EV001", False)
    write_script_package(scripts / "EMBER-E02", "EMBER-E02", "EMBER-EV002", True)
    return story, scripts

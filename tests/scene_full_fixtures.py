from __future__ import annotations

import json
from pathlib import Path


MANIFEST_ARTIFACTS = (
    "scene-beats.json",
    "directing-plan.json",
    "visual-language-plan.json",
    "blocking-plan.json",
    "camera-movement-plan.json",
    "shot-list.json",
    "lighting-plan.json",
    "sound-plan.json",
    "storyboard-plan.json",
    "production-breakdown.json",
    "continuity-plan.json",
)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def write_scene_full_package(package: Path, scene_id: str = "S01") -> None:
    package.mkdir(parents=True)
    (package / "source-scene.md").write_text(
        "# Scene\n\nNinel wakes, chooses to breathe, and studies the room.\n",
        encoding="utf-8",
    )
    beat_id = f"{scene_id}-B01"
    shot_id = f"{scene_id}-SH001"
    payloads: dict[str, object] = {
        "scene-beats.json": {
            "schema_version": "0.3.0",
            "scene_id": scene_id,
            "scene_objective": "Ninel wakes and orients herself.",
            "turn": "The quiet room becomes threatening.",
            "assumptions": [],
            "beats": [
                {
                    "beat_id": beat_id,
                    "evidence": "Ninel opens her eyes.",
                    "action": "She wakes.",
                    "tactic": "She listens.",
                    "value_shift": "calm to unease",
                    "visual_opportunity": "A close view of her eye.",
                }
            ],
        },
        "directing-plan.json": {
            "schema_version": "0.3.0",
            "scene_id": scene_id,
            "concept": "A waking mind tests whether the room is safe.",
            "point_of_view": "Stay with Ninel's incomplete perception.",
            "performance_notes": ["Keep the awakening restrained."],
            "visual_strategy": ["Begin close and reveal space only with her attention."],
            "rhythm": "Slow observation, then one clear turn.",
            "assumptions": [],
        },
        "visual-language-plan.json": {
            "schema_version": "0.3.0",
            "scene_id": scene_id,
            "assumptions": ["Delivery ratio requires confirmation."],
            "aspect_ratio": "Unconfirmed; preserve central safe composition.",
            "point_of_view": "Show only what Ninel can perceive.",
            "palette": ["charcoal", "desaturated cyan"],
            "contrast": "Deep blacks with retained subject detail.",
            "texture": "Controlled glass and condensation texture.",
            "lens_strategy": "Move from compressed detail to a neutral spatial view.",
            "visual_motifs": ["breath on glass", "machine rectangles"],
            "prohibited_defaults": ["unmotivated handheld"],
            "exceptions": [],
            "rules": [
                {
                    "rule_id": f"{scene_id}-V01",
                    "beat_ids": [beat_id],
                    "composition": "Hold Ninel within the chamber geometry.",
                    "camera_height": "Stay aligned with Ninel's eye line.",
                    "dramatic_purpose": "Make her first choice visually legible.",
                }
            ],
        },
        "blocking-plan.json": {
            "schema_version": "0.3.0",
            "scene_id": scene_id,
            "space": "A narrow medical bay.",
            "axis": "The chamber-to-monitor line.",
            "positions": ["Ninel begins inside the chamber."],
            "moves": [
                {
                    "beat_id": beat_id,
                    "character": "Ninel",
                    "start": "inside chamber",
                    "end": "seated at chamber edge",
                    "motivation": "She tests the room.",
                }
            ],
            "continuity_rules": ["Preserve the chamber-to-monitor axis."],
            "assumptions": [],
        },
        "camera-movement-plan.json": {
            "schema_version": "0.3.0",
            "scene_id": scene_id,
            "movement_philosophy": "Movement follows Ninel's access to space.",
            "moves": [
                {
                    "move_id": f"{scene_id}-M01",
                    "beat_ids": [beat_id],
                    "name_ru": "Медленный отъезд",
                    "name_en": "Slow dolly out",
                    "movement": "dolly out",
                    "direction": "away from Ninel",
                    "speed": "slow",
                    "framing": "close to medium",
                    "start": "Ninel's eye",
                    "end": "Ninel in the chamber geography",
                    "purpose": "Reveal only the space she can now inspect.",
                    "ai_video_prompt": "A slow controlled dolly out as Ninel wakes.",
                }
            ],
            "assumptions": [],
        },
        "shot-list.json": {
            "schema_version": "0.3.0",
            "scene_id": scene_id,
            "assumptions": [],
            "shots": [
                {
                    "shot_id": shot_id,
                    "beat_ids": [beat_id],
                    "size": "medium",
                    "angle": "eye-level",
                    "lens_mm": 50,
                    "camera_support": "slider",
                    "movement": "slow dolly out",
                    "subject": "Ninel",
                    "action": "opens her eyes and sits",
                    "composition": "centered within chamber geometry",
                    "dramatic_purpose": "establish chosen agency",
                    "audio": "low ship hum and first inhale",
                    "continuity": ["preserve chamber-to-monitor axis"],
                }
            ],
        },
        "lighting-plan.json": {
            "schema_version": "0.3.0",
            "scene_id": scene_id,
            "assumptions": ["Final fixtures and exposure require prelight."],
            "lighting_philosophy": "Let motivated chamber light reveal agency.",
            "setups": [
                {
                    "setup_id": f"{scene_id}-L01",
                    "beat_ids": [beat_id],
                    "shot_ids": [shot_id],
                    "environment_time_basis": "Interior medical bay at scripted night; the chamber diagnostic remains the active environmental source.",
                    "motivation": "The chamber diagnostic source remains active.",
                    "sources": ["chamber practical"],
                    "direction": "Top-side through chamber geometry.",
                    "quality": "Controlled and restrained.",
                    "color_intent": "Desaturated cool diagnostic light.",
                    "exposure_contrast": "Retain glass detail and deep background separation.",
                    "control": ["Keep spill off the monitor."],
                    "continuity": ["Record the approved practical state."],
                    "safety": ["Qualified crew approve rigging and electrical work."],
                    "dramatic_purpose": "Make the first breath legible without announcing it.",
                }
            ],
        },
        "sound-plan.json": {
            "schema_version": "0.3.0",
            "scene_id": scene_id,
            "assumptions": ["Location acoustics require a survey."],
            "sound_philosophy": "Let breath interrupt the machine-controlled room.",
            "cues": [
                {
                    "cue_id": f"{scene_id}-A01",
                    "beat_ids": [beat_id],
                    "shot_ids": [shot_id],
                    "category": "effects",
                    "source": "Ninel's first voluntary inhale",
                    "perspective": "Close and aligned with Ninel.",
                    "timing": "The inhale interrupts the diagnostic rhythm.",
                    "requirement": "Protect clean breath, chamber, and room states.",
                    "dramatic_purpose": "Make breath the first sound that belongs to Ninel.",
                }
            ],
        },
        "storyboard-plan.json": {
            "schema_version": "0.3.0",
            "scene_id": scene_id,
            "assumptions": ["The panel is a textual drawing instruction."],
            "storyboard_intent": "Make the chosen breath and space reveal drawable.",
            "panels": [
                {
                    "panel_id": f"{scene_id}-SB001",
                    "shot_id": shot_id,
                    "moment": "Ninel begins the first inhale.",
                    "framing": "Medium single inherited from the shot list.",
                    "camera_height": "At Ninel's eye line.",
                    "angle": "Level through chamber geometry.",
                    "foreground": "Chamber glass and frost.",
                    "midground": "Ninel's eye and face.",
                    "background": "Unresolved medical-bay darkness.",
                    "subject_placement": "Ninel remains centered in the machine geometry.",
                    "action_direction": "Frost moves across the glass as she rises.",
                    "movement_state": "Camera begins the approved dolly out.",
                    "lighting_note": "Cold chamber light retains glass detail.",
                    "audio_cue": "The first inhale interrupts the room hum.",
                    "continuity_note": "Match frost and eye line into the wider state.",
                    "dramatic_purpose": "Make chosen agency visible.",
                }
            ],
        },
        "production-breakdown.json": {
            "schema_version": "0.3.0",
            "scene_id": scene_id,
            "assumptions": ["Chamber implementation requires department review."],
            "breakdown_scope": "Scene-level requirements only.",
            "items": [
                {
                    "item_id": f"{scene_id}-PD001",
                    "category": "props",
                    "source_basis": "The scene and shot require a repeatable chamber edge.",
                    "beat_ids": [beat_id],
                    "shot_ids": [shot_id],
                    "requirement": "Provide a repeatable chamber action state.",
                    "continuity_reset": "Restore the chamber, frost, and hand start state.",
                    "assumptions": ["The practical method is unconfirmed."],
                    "risk_level": "medium",
                }
            ],
        },
        "continuity-plan.json": {
            "schema_version": "0.3.0",
            "scene_id": scene_id,
            "assumptions": ["Take-level records are added during photography."],
            "continuity_strategy": "Track chosen breath and chamber states.",
            "items": [
                {
                    "continuity_id": f"{scene_id}-CN001",
                    "shot_ids": [shot_id],
                    "category": "action",
                    "tracked_state": "Ninel starts still and ends seated.",
                    "required_transition": "The shot preserves the eye-open, inhale, and rise order.",
                    "reset_instruction": "Restore eye, body, chamber, and frost start states.",
                    "severity": "critical",
                }
            ],
        },
    }
    for filename, payload in payloads.items():
        write_json(package / filename, payload)

    manifest = {
        "release_version": "0.3.0",
        "profile": "scene-full",
        "scene_id": scene_id,
        "source_file": "source-scene.md",
        "artifacts": [
            {
                "filename": filename,
                "schema_version": "0.3.0",
                "dependency_order": order,
            }
            for order, filename in enumerate(MANIFEST_ARTIFACTS, start=1)
        ],
        "validation_status": "valid",
        "unresolved_questions": [],
    }
    write_json(package / "package-manifest.json", manifest)

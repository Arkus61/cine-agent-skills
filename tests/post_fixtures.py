from __future__ import annotations
import json
from pathlib import Path
from cine_skills.project_contracts import ProjectIndex, required_post_artifacts
from tests.test_artifacts import valid_edit_plan, valid_sound_post_plan
from tests.test_color_plans import planned_color_plan
from tests.test_music_plans import valid_music_plan
from tests.test_titles_captions import planned_titles_plan
from tests.test_vfx_post_plans import valid_planned_vfx_post_plan
from tests.test_mastering_qc import planned_mastering_plan

PROJECT, UNIT = "NINEL", "NINEL-U01"

def post_index() -> ProjectIndex:
    return ProjectIndex(project_id=PROJECT, project_format="short", production_modes=("hybrid",), unit_ids=frozenset({UNIT}), shot_ids=frozenset({f"{UNIT}-S01-SH001", f"{UNIT}-S01-SH002"}), media_ids=frozenset({f"{PROJECT}-MD001"}), edit_segment_ids=frozenset({f"{UNIT}-ED001", f"{UNIT}-ED002"}))

def _normalise(value: object) -> object:
    encoded = json.dumps(value)
    for source in ("SPARK", "DAY", "MORROW", "ORBIT", "LANTERN", "GLASS"):
        encoded = encoded.replace(source, PROJECT)
    return json.loads(encoded)

def valid_post_payloads() -> dict[str, dict[str, object]]:
    result = {name: _normalise(payload) for name, payload in {
        "edit-plan.json": valid_edit_plan(), "sound-post-plan.json": valid_sound_post_plan(),
        "music-plan.json": valid_music_plan(), "vfx-post-plan.json": valid_planned_vfx_post_plan(),
        "color-plan.json": planned_color_plan(), "titles-captions-plan.json": planned_titles_plan(),
    }.items()}
    for payload in result.values(): payload.update(project_id=PROJECT, unit_id=UNIT)
    result["mastering-qc-plan.json"] = _normalise(planned_mastering_plan())
    result["mastering-qc-plan.json"].update(project_id=PROJECT, unit_id=UNIT)
    # Every edit-dependent post plan declares both upstream segments, even when
    # the detailed work item currently targets only one of them.
    for name, payload in result.items():
        if name in {"edit-plan.json", "mastering-qc-plan.json"}:
            continue
        context = payload.get("source_context")
        if isinstance(context, dict) and isinstance(context.get("edit_segments"), list):
            if not any(isinstance(item, dict) and item.get("segment_id") == f"{UNIT}-ED002" for item in context["edit_segments"]):
                context["edit_segments"].append({"segment_id": f"{UNIT}-ED002", "source_reference": "post/edit-plan.json#/segments/1"})
    for item in result["sound-post-plan.json"].get("items", []):
        if isinstance(item, dict): item.setdefault("edit_segment_ids", []).append(f"{UNIT}-ED002")
    for item in result["vfx-post-plan.json"].get("items", []):
        if isinstance(item, dict): item.setdefault("edit_segment_ids", []).append(f"{UNIT}-ED002")
    return result

def write_post_package(directory: Path, *, extra: str | None = None) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    payloads = valid_post_payloads()
    payloads["post-manifest.json"] = {"schema_version":"0.3.0", "release_version":"0.3.0", "project_id":PROJECT, "layer":"post", "profile":"post", "artifacts":[{"filename":c.filename,"schema_name":c.schema_name,"schema_version":"0.3.0","dependency_order":c.dependency_order} for c in required_post_artifacts()], "validation_status":"valid", "unresolved_questions":[]}
    for name, payload in payloads.items(): (directory / name).write_text(json.dumps(payload), encoding="utf-8")
    if extra: (directory / extra).write_text("{}", encoding="utf-8")
    return directory

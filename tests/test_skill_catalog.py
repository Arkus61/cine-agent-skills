import json
from pathlib import Path

import yaml


V1_SKILLS = {
    "scene-beat-analyzer",
    "scene-director",
    "visual-language-designer",
    "blocking-designer",
    "camera-movement-designer",
    "shot-list-builder",
    "lighting-designer",
    "sound-designer",
    "storyboard-designer",
    "production-breakdown",
    "continuity-supervisor",
    "scene-preproduction-pipeline",
}

STORY_SPECIALIST_SKILLS = {
    "story-concept-designer",
    "story-structure-designer",
    "character-arc-designer",
    "worldbuilding-designer",
    "season-arc-designer",
    "episode-outline-builder",
    "screenplay-writer",
    "screenplay-reviser",
}

PRODUCTION_SPECIALIST_SKILLS = {
    "production-designer",
    "character-look-designer",
    "animation-director",
    "vfx-planner",
    "ai-media-prompt-designer",
    "media-review-supervisor",
}

PRODUCTION_PIPELINE_SKILLS = {"creative-production-pipeline"}

POSTPRODUCTION_SPECIALIST_SKILLS = {"film-editor", "sound-post-designer", "music-story-designer", "vfx-post-supervisor", "color-grading-designer", "titles-captions-designer", "mastering-qc-supervisor"}
POSTPRODUCTION_PIPELINE_SKILLS = {"postproduction-pipeline"}
FULL_PIPELINE_SKILLS = {"full-creative-pipeline"}

EXPECTED_SKILLS = V1_SKILLS | STORY_SPECIALIST_SKILLS | {
    "story-development-pipeline",
} | PRODUCTION_SPECIALIST_SKILLS | PRODUCTION_PIPELINE_SKILLS | POSTPRODUCTION_SPECIALIST_SKILLS | POSTPRODUCTION_PIPELINE_SKILLS | FULL_PIPELINE_SKILLS

CANONICAL_FULL_V1_FILES = (
    "source-scene.md",
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
    "package-manifest.json",
)

STORY_SERIES_DEPENDENCY_ORDER = (
    "story-concept.json",
    "story-structure.json",
    "character-arcs.json",
    "world-bible.json",
    "season-arc.json",
    "story-manifest.json",
)

SCRIPT_DEPENDENCY_ORDER = (
    "unit-outline.json",
    "screenplay.fountain",
    "screenplay-metadata.json",
    "script-revision-plan.json",
    "scenes",
    "script-manifest.json",
)


def test_catalog_is_exactly_the_thirty_seven_current_skills(repository_root: Path) -> None:
    root = repository_root / ".agents" / "skills"
    actual = {path.name for path in root.iterdir() if path.is_dir()}
    v2 = EXPECTED_SKILLS - V1_SKILLS

    assert len(V1_SKILLS) == 12
    assert len(v2) == 25
    assert len(EXPECTED_SKILLS) == 37
    assert actual == EXPECTED_SKILLS


def test_ai_media_prompt_designer_is_catalogued(
    repository_root: Path,
) -> None:
    assert "ai-media-prompt-designer" in EXPECTED_SKILLS
    assert (repository_root / ".agents" / "skills" / "ai-media-prompt-designer").is_dir()


def test_media_review_supervisor_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "media-review-supervisor"
    expected = {
        "SKILL.md",
        "agents/openai.yaml",
        "assets/media-review-report.template.json",
        "references/media-review-evidence.md",
        "references/shot-acceptance.md",
    }
    actual = {
        path.relative_to(skill).as_posix()
        for path in skill.rglob("*")
        if path.is_file()
    }

    assert actual == expected


def test_postproduction_pipeline_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "postproduction-pipeline"
    expected = {
        "SKILL.md",
        "agents/openai.yaml",
        "assets/post-package-checklist.md",
        "references/post-pipeline-contract.md",
    }
    actual = {path.relative_to(skill).as_posix() for path in skill.rglob("*") if path.is_file()}
    assert actual == expected


def test_postproduction_pipeline_contract_covers_order_and_handoffs(repository_root: Path) -> None:
    contract = (repository_root / ".agents/skills/postproduction-pipeline/references/post-pipeline-contract.md").read_text(encoding="utf-8")
    for required in (
        "edit-first", "sound", "music", "VFX", "color", "titles", "captions", "mastering", "validate-post",
        "earliest invalid", "preserves valid unaffected", "planned", "ready-for-master-review", "blocked",
        "never invent", "approval",
    ):
        assert required.lower() in contract.lower()


def test_full_creative_pipeline_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents/skills/full-creative-pipeline"
    expected = {"SKILL.md", "agents/openai.yaml", "assets/full-creative-checklist.md", "references/full-creative-contract.md"}
    actual = {path.relative_to(skill).as_posix() for path in skill.rglob("*") if path.is_file()}
    assert actual == expected


def test_full_creative_pipeline_contract_and_eval_are_observable(repository_root: Path) -> None:
    contract = (repository_root / ".agents/skills/full-creative-pipeline/references/full-creative-contract.md").read_text(encoding="utf-8")
    for required in ("story", "production", "post", "validate-project", "awaiting-media", "blocked", "preserve", "no media"):
        assert required.lower() in contract.lower()
    data = json.loads((repository_root / "evals/full-creative-pipeline.json").read_text(encoding="utf-8"))
    assert data["skill"] == "full-creative-pipeline"
    assert len(data["cases"]) >= 3
    observables = " ".join(item for case in data["cases"] for item in case["observables"]).lower()
    for required in ("story", "production", "post", "awaiting-media", "validate-project", "earliest-invalid"):
        assert required in observables


def test_postproduction_pipeline_eval_has_required_observables(repository_root: Path) -> None:
    data = json.loads((repository_root / "evals/postproduction-pipeline.json").read_text(encoding="utf-8"))
    assert data["skill"] == "postproduction-pipeline"
    assert len(data["cases"]) >= 2
    observables = " ".join(item for case in data["cases"] for item in case["observables"]).lower()
    for required in ("edit-first", "planned", "evidence", "earliest", "approval", "validate-post", "blocked"):
        assert required in observables


def test_original_twelve_v1_skills_remain_the_preserved_base(repository_root: Path) -> None:
    root = repository_root / ".agents" / "skills"
    actual = {path.name for path in root.iterdir() if path.is_dir()}

    assert len(V1_SKILLS) == 12
    assert V1_SKILLS <= actual
    assert actual - V1_SKILLS == STORY_SPECIALIST_SKILLS | {
        "story-development-pipeline",
    } | PRODUCTION_SPECIALIST_SKILLS | PRODUCTION_PIPELINE_SKILLS | POSTPRODUCTION_SPECIALIST_SKILLS | POSTPRODUCTION_PIPELINE_SKILLS | FULL_PIPELINE_SKILLS


def test_every_skill_has_openai_metadata(repository_root: Path) -> None:
    for name in EXPECTED_SKILLS:
        metadata_path = repository_root / ".agents" / "skills" / name / "agents" / "openai.yaml"
        data = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        assert data["interface"]["display_name"]
        assert 25 <= len(data["interface"]["short_description"]) <= 64
        assert f"${name}" in data["interface"]["default_prompt"]


def test_character_look_designer_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "character-look-designer"
    expected = {
        "SKILL.md",
        "agents/openai.yaml",
        "assets/character-look-bible.template.json",
        "references/character-visual-consistency.md",
        "references/look-development.md",
    }
    actual = {
        path.relative_to(skill).as_posix()
        for path in skill.rglob("*")
        if path.is_file()
    }

    assert actual == expected

    metadata = yaml.safe_load(
        (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
    )
    assert metadata["interface"] == {
        "display_name": "Character Look Designer",
        "short_description": "Design traceable continuity-safe character looks",
        "default_prompt": (
            "Use $character-look-designer to create a validated character look "
            "bible from these character and shot materials."
        ),
    }


def test_animation_director_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "animation-director"
    expected = {
        "SKILL.md",
        "agents/openai.yaml",
        "assets/animation-plan.template.json",
        "references/animation-performance.md",
        "references/animation-timing-motion.md",
    }
    actual = {
        path.relative_to(skill).as_posix()
        for path in skill.rglob("*")
        if path.is_file()
    }

    assert actual == expected

    metadata = yaml.safe_load(
        (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
    )
    assert metadata["interface"] == {
        "display_name": "Animation Director",
        "short_description": "Direct traceable shot-level animation performance",
        "default_prompt": (
            "Use $animation-director to create a validated animation plan from "
            "these character, directing, and shot materials."
        ),
    }


def test_vfx_planner_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "vfx-planner"
    expected = {
        "SKILL.md",
        "agents/openai.yaml",
        "assets/vfx-plan.template.json",
        "references/vfx-preproduction.md",
        "references/vfx-capture-elements.md",
    }
    actual = {
        path.relative_to(skill).as_posix()
        for path in skill.rglob("*")
        if path.is_file()
    }

    assert actual == expected

    metadata = yaml.safe_load(
        (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
    )
    assert metadata["interface"] == {
        "display_name": "VFX Planner",
        "short_description": "Plan traceable shot-level visual effects",
        "default_prompt": (
            "Use $vfx-planner to create a validated VFX plan from these "
            "scene, shot, camera, lighting, and performance materials."
        ),
    }


def test_visual_language_designer_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "visual-language-designer"
    expected = {
        "SKILL.md",
        "agents/openai.yaml",
        "references/visual-language.md",
        "assets/visual-language-plan.template.json",
    }
    actual = {
        path.relative_to(skill).as_posix()
        for path in skill.rglob("*")
        if path.is_file()
    }

    assert actual == expected

    metadata = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    assert metadata["interface"] == {
        "display_name": "Visual Language Designer",
        "short_description": "Define a coherent visual language for a scene",
        "default_prompt": "Use $visual-language-designer to define the visual language for this scene.",
    }


def test_lighting_designer_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "lighting-designer"
    expected = {
        "SKILL.md",
        "agents/openai.yaml",
        "references/lighting-design.md",
        "assets/lighting-plan.template.json",
    }
    actual = {
        path.relative_to(skill).as_posix()
        for path in skill.rglob("*")
        if path.is_file()
    }

    assert actual == expected

    metadata = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    assert metadata["interface"] == {
        "display_name": "Lighting Designer",
        "short_description": "Plan motivated lighting for every scene shot",
        "default_prompt": "Use $lighting-designer to create a motivated lighting plan for this scene.",
    }


def test_sound_designer_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "sound-designer"
    expected = {
        "SKILL.md",
        "agents/openai.yaml",
        "references/production-sound.md",
        "assets/sound-plan.template.json",
    }
    actual = {
        path.relative_to(skill).as_posix()
        for path in skill.rglob("*")
        if path.is_file()
    }

    assert actual == expected

    metadata = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    assert metadata["interface"] == {
        "display_name": "Sound Designer",
        "short_description": "Plan production sound and dramatic audio cues",
        "default_prompt": "Use $sound-designer to create a production sound plan for this scene.",
    }


def test_sound_post_designer_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "sound-post-designer"
    expected = {
        "SKILL.md",
        "agents/openai.yaml",
        "assets/sound-post-plan.template.json",
        "references/dialogue-adr-foley.md",
        "references/sound-edit-design-mix.md",
        "references/sound-delivery-assumptions.md",
    }
    actual = {
        path.relative_to(skill).as_posix()
        for path in skill.rglob("*")
        if path.is_file()
    }

    assert actual == expected

    metadata = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    assert metadata["interface"] == {
        "display_name": "Sound Post Designer",
        "short_description": "Plan source-bound dialogue, design, mix, and delivery",
        "default_prompt": "Use $sound-post-designer to create a validated sound post plan from this edit plan and supplied audio evidence.",
    }


def test_music_story_designer_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "music-story-designer"
    expected = {
        "SKILL.md", "agents/openai.yaml", "assets/music-plan.template.json",
        "references/music-spotting-story.md", "references/leitmotif-diegetic-silence.md",
    }
    actual = {path.relative_to(skill).as_posix() for path in skill.rglob("*") if path.is_file()}
    assert actual == expected
    metadata = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    assert metadata["interface"] == {
        "display_name": "Music Story Designer",
        "short_description": "Spot source-bound music with restraint and evidence",
        "default_prompt": "Use $music-story-designer to create a validated music plan from this edit plan and supplied music evidence.",
    }


def test_vfx_post_supervisor_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "vfx-post-supervisor"
    expected = {
        "SKILL.md", "agents/openai.yaml", "assets/vfx-post-plan.template.json",
        "references/vfx-turnover-compositing.md", "references/vfx-review-integration.md",
    }
    actual = {path.relative_to(skill).as_posix() for path in skill.rglob("*") if path.is_file()}
    assert actual == expected
    metadata = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    assert metadata["interface"] == {
        "display_name": "VFX Post Supervisor",
        "short_description": "Plan version-bound VFX turnover, review, and delivery",
        "default_prompt": "Use $vfx-post-supervisor to create a validated VFX post plan from these VFX, edit, media, and review records.",
    }


def test_color_grading_designer_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "color-grading-designer"
    expected = {
        "SKILL.md", "agents/openai.yaml", "assets/color-plan.template.json",
        "references/color-management-assumptions.md", "references/shot-matching-look.md",
        "references/color-story-arc.md",
    }
    actual = {path.relative_to(skill).as_posix() for path in skill.rglob("*") if path.is_file()}
    assert actual == expected
    metadata = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    assert metadata["interface"] == {
        "display_name": "Color Grading Designer",
        "short_description": "Plan source-bound color, matching, looks, and review",
        "default_prompt": "Use $color-grading-designer to create a validated color plan from this edit plan and supplied color evidence.",
    }


def test_titles_captions_designer_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "titles-captions-designer"
    expected = {
        "SKILL.md", "agents/openai.yaml", "assets/titles-captions-plan.template.json",
        "references/title-design-timing.md", "references/captions-readability-accessibility.md",
    }
    actual = {path.relative_to(skill).as_posix() for path in skill.rglob("*") if path.is_file()}
    assert actual == expected
    metadata = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    assert metadata["interface"] == {
        "display_name": "Titles and Captions Designer",
        "short_description": "Plan source-bound titles, captions, timing, and review",
        "default_prompt": "Use $titles-captions-designer to create a validated titles and captions plan from the current edit and supplied text, timing, and review records.",
    }


def test_mastering_qc_supervisor_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "mastering-qc-supervisor"
    expected = {
        "SKILL.md", "agents/openai.yaml", "assets/mastering-qc-plan.template.json",
        "references/mastering-deliverable-assumptions.md", "references/technical-qc.md",
    }
    actual = {path.relative_to(skill).as_posix() for path in skill.rglob("*") if path.is_file()}
    assert actual == expected
    metadata = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    assert metadata["interface"] == {
        "display_name": "Mastering and QC Supervisor",
        "short_description": "Plan version-bound mastering checks and delivery readiness",
        "default_prompt": "Use $mastering-qc-supervisor to create a validated mastering and QC plan from delivery specifications, the current post package, and supplied evidence.",
    }


def test_storyboard_designer_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "storyboard-designer"
    expected = {
        "SKILL.md",
        "agents/openai.yaml",
        "references/textual-storyboards.md",
        "assets/storyboard-plan.template.json",
    }
    actual = {
        path.relative_to(skill).as_posix()
        for path in skill.rglob("*")
        if path.is_file()
    }

    assert actual == expected

    metadata = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    assert metadata["interface"] == {
        "display_name": "Storyboard Designer",
        "short_description": "Turn shot lists into drawable storyboard panels",
        "default_prompt": "Use $storyboard-designer to create textual storyboard panels for this shot list.",
    }


def test_production_breakdown_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "production-breakdown"
    expected = {
        "SKILL.md",
        "agents/openai.yaml",
        "references/department-breakdown.md",
        "assets/production-breakdown.template.json",
    }
    actual = {
        path.relative_to(skill).as_posix()
        for path in skill.rglob("*")
        if path.is_file()
    }

    assert actual == expected

    metadata = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    assert metadata["interface"] == {
        "display_name": "Production Breakdown",
        "short_description": "Break scenes into department production needs",
        "default_prompt": "Use $production-breakdown to create a department-by-department scene breakdown.",
    }


def test_continuity_supervisor_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "continuity-supervisor"
    expected = {
        "SKILL.md",
        "agents/openai.yaml",
        "references/continuity-control.md",
        "assets/continuity-plan.template.json",
    }
    actual = {
        path.relative_to(skill).as_posix()
        for path in skill.rglob("*")
        if path.is_file()
    }

    assert actual == expected

    metadata = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    assert metadata["interface"] == {
        "display_name": "Continuity Supervisor",
        "short_description": "Track shot continuity states and required resets",
        "default_prompt": "Use $continuity-supervisor to create a continuity and reset plan for this scene.",
    }


def test_scene_pipeline_specifies_the_full_v1_contract(repository_root: Path) -> None:
    pipeline = repository_root / ".agents" / "skills" / "scene-preproduction-pipeline"
    skill_text = (pipeline / "SKILL.md").read_text(encoding="utf-8")
    contract_text = (pipeline / "references" / "pipeline-contract.md").read_text(
        encoding="utf-8"
    )
    checklist_text = (pipeline / "assets" / "scene-package-checklist.md").read_text(
        encoding="utf-8"
    )
    evaluation = json.loads(
        (repository_root / "evals" / "scene-preproduction-pipeline.json").read_text(
            encoding="utf-8"
        )
    )

    positions = [skill_text.index(filename) for filename in CANONICAL_FULL_V1_FILES]
    assert positions == sorted(positions)
    assert "--profile full-v1" in skill_text
    assert "earliest" in skill_text.lower()
    assert "downstream" in skill_text.lower()
    assert "package-manifest.json" in contract_text
    assert "source-scene.md" in contract_text
    assert "full-v1" in checklist_text

    observables = " ".join(
        observable
        for case in evaluation["cases"]
        for observable in case["observables"]
    ).lower()
    for required in (
        "thirteen",
        "dependency order",
        "full-v1",
        "downstream",
        "handoff",
    ):
        assert required in observables


def test_story_development_pipeline_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "story-development-pipeline"
    expected = {
        "SKILL.md",
        "agents/openai.yaml",
        "assets/story-package-checklist.md",
        "references/story-pipeline-contract.md",
    }
    actual = {
        path.relative_to(skill).as_posix()
        for path in skill.rglob("*")
        if path.is_file()
    }
    assert actual == expected

    metadata = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    assert metadata["interface"] == {
        "display_name": "Story Development Pipeline",
        "short_description": "Build and validate story and script packages",
        "default_prompt": "Use $story-development-pipeline to build a validated story and script package.",
    }


def test_story_pipeline_names_every_artifact_in_dependency_order(
    repository_root: Path,
) -> None:
    pipeline = repository_root / ".agents" / "skills" / "story-development-pipeline"
    skill_text = (pipeline / "SKILL.md").read_text(encoding="utf-8")
    contract_text = (pipeline / "references" / "story-pipeline-contract.md").read_text(
        encoding="utf-8"
    )

    specialist_positions = [
        skill_text.index(f"${name}")
        for name in (
            "story-concept-designer",
            "story-structure-designer",
            "character-arc-designer",
            "worldbuilding-designer",
            "season-arc-designer",
            "episode-outline-builder",
            "screenplay-writer",
            "screenplay-reviser",
        )
    ]
    assert specialist_positions == sorted(specialist_positions)

    artifact_positions = [
        contract_text.index(f"`{filename}`")
        for filename in STORY_SERIES_DEPENDENCY_ORDER + SCRIPT_DEPENDENCY_ORDER
    ]
    assert artifact_positions == sorted(artifact_positions)


def test_story_pipeline_observable_gate_covers_validation_repair_and_handoff(
    repository_root: Path,
) -> None:
    pipeline = repository_root / ".agents" / "skills" / "story-development-pipeline"
    skill_text = (pipeline / "SKILL.md").read_text(encoding="utf-8")
    contract_text = (pipeline / "references" / "story-pipeline-contract.md").read_text(
        encoding="utf-8"
    )
    checklist_text = (pipeline / "assets" / "story-package-checklist.md").read_text(
        encoding="utf-8"
    )
    evaluation = json.loads(
        (repository_root / "evals" / "story-development-pipeline.json").read_text(
            encoding="utf-8"
        )
    )

    assert "validate-story" in skill_text
    assert "If `project_format` is `series`" in skill_text
    assert "For every other format, do not create `season-arc.json`" in skill_text
    assert "earliest invalid" in contract_text.lower()
    assert "transitive downstream closure" in contract_text.lower()
    assert "Never declare the screenplay package valid without inspecting `screenplay.fountain`" in contract_text

    handoff_line = next(
        line for line in contract_text.splitlines() if line.startswith("Allowed handoff statuses:")
    )
    assert handoff_line == (
        "Allowed handoff statuses: `ready-for-preproduction`, `blocked`."
    )

    observables = " ".join(
        observable
        for case in evaluation["cases"]
        for observable in case["observables"]
    ).lower()
    for required in (
        "validate-story",
        "series-only",
        "no season-arc.json",
        "earliest invalid",
        "transitive downstream closure",
        "inspects screenplay.fountain",
        "ready-for-preproduction",
        "blocked",
    ):
        assert required in observables

    assert "validate-story" in checklist_text
    assert "screenplay.fountain" in checklist_text


def test_creative_production_pipeline_bundle_is_complete(repository_root: Path) -> None:
    skill = repository_root / ".agents" / "skills" / "creative-production-pipeline"
    expected = {
        "SKILL.md",
        "agents/openai.yaml",
        "assets/production-package-checklist.md",
        "references/production-pipeline-contract.md",
    }
    actual = {
        path.relative_to(skill).as_posix()
        for path in skill.rglob("*")
        if path.is_file()
    }
    assert actual == expected

    metadata = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    assert metadata["interface"] == {
        "display_name": "Creative Production Pipeline",
        "short_description": "Orchestrate validated creative production packages",
        "default_prompt": (
            "Use $creative-production-pipeline to assemble and validate a "
            "mode-selected creative production package."
        ),
    }


def test_creative_production_pipeline_declares_dependency_order_and_modes(
    repository_root: Path,
) -> None:
    skill = repository_root / ".agents" / "skills" / "creative-production-pipeline"
    skill_text = (skill / "SKILL.md").read_text(encoding="utf-8")
    contract_text = (skill / "references" / "production-pipeline-contract.md").read_text(
        encoding="utf-8"
    )

    specialists = (
        "production-designer",
        "character-look-designer",
        "animation-director",
        "vfx-planner",
        "ai-media-prompt-designer",
        "media-review-supervisor",
    )
    positions = [skill_text.index(f"${name}") for name in specialists]
    assert positions == sorted(positions)
    assert skill_text.index("validate-production") > positions[-1]

    assert "validated story/script package" in contract_text
    assert "full-v1 scene package" in contract_text
    for mode, expected, forbidden in (
        (
            "live-action-only",
            "`production-design-plan.json`, `character-look-bible.json`, `vfx-plan.json`, `media-review-report.json`, `production-manifest.json`",
            "`animation-plan.json` and `media-prompt-package.json`",
        ),
        (
            "animation-only",
            "`production-design-plan.json`, `character-look-bible.json`, `animation-plan.json`, `vfx-plan.json`, `media-review-report.json`, `production-manifest.json`",
            "`media-prompt-package.json`",
        ),
        (
            "ai-only",
            "`production-design-plan.json`, `character-look-bible.json`, `vfx-plan.json`, `media-prompt-package.json`, `media-review-report.json`, `production-manifest.json`",
            "`animation-plan.json`",
        ),
        (
            "hybrid",
            "`production-design-plan.json`, `character-look-bible.json`, `animation-plan.json`, `vfx-plan.json`, `media-prompt-package.json`, `media-review-report.json`, `production-manifest.json`",
            "none",
        ),
    ):
        line = next(line for line in contract_text.splitlines() if line.startswith(f"- `{mode}`:"))
        assert expected in line
        assert forbidden in line


def test_creative_production_pipeline_gates_repair_media_and_handoff(
    repository_root: Path,
) -> None:
    skill = repository_root / ".agents" / "skills" / "creative-production-pipeline"
    contract_text = (skill / "references" / "production-pipeline-contract.md").read_text(
        encoding="utf-8"
    )
    checklist_text = (skill / "assets" / "production-package-checklist.md").read_text(
        encoding="utf-8"
    )
    evaluation = json.loads(
        (repository_root / "evals" / "creative-production-pipeline.json").read_text(
            encoding="utf-8"
        )
    )

    for required in (
        "validate upstream",
        "earliest invalid",
        "transitive downstream closure",
        "Preserve valid unaffected",
        "awaiting-media",
        "blocked",
        "ready-for-post",
        "unseen media",
        "validate-production",
        "exit code 0",
    ):
        assert required.lower() in contract_text.lower()
    assert "validate-production" in checklist_text
    assert "ready-for-post" in checklist_text

    observables = " ".join(
        observable
        for case in evaluation["cases"]
        for observable in case["observables"]
    ).lower()
    for required in (
        "live-action-only",
        "ai-only",
        "awaiting-media",
        "validate-production",
        "earliest invalid",
        "preserves valid unaffected",
        "blocked",
        "ready-for-post",
    ):
        assert required in observables


def test_creative_production_pipeline_distinguishes_membership_labels_from_cli_modes(
    repository_root: Path,
) -> None:
    contract_text = (
        repository_root
        / ".agents"
        / "skills"
        / "creative-production-pipeline"
        / "references"
        / "production-pipeline-contract.md"
    ).read_text(encoding="utf-8")

    for membership_label, cli_mode in (
        ("live-action-only", "live-action"),
        ("animation-only", "animation"),
        ("ai-only", "ai"),
        ("hybrid", "hybrid"),
    ):
        assert f"`{membership_label}`: CLI mode `{cli_mode}`" in contract_text


def test_creative_production_pipeline_declares_stage_handoff_gates(
    repository_root: Path,
) -> None:
    """Removing a stage input, stop gate, or real validator must fail catalog review."""
    contract_text = (
        repository_root
        / ".agents"
        / "skills"
        / "creative-production-pipeline"
        / "references"
        / "production-pipeline-contract.md"
    ).read_text(encoding="utf-8")

    assert "## Stage handoff gates" in contract_text
    rows = {}
    for line in contract_text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 6:
            rows[cells[0]] = cells[1:]

    expected_stages = {
        "Production design": (
            ("validated story/script package", "validated full-v1 scene packages"),
            "production-design-plan.json",
            "Production Designer",
            "continue",
            "validate-artifact production-design-plan",
        ),
        "Character look": (
            ("validated story/script package", "validated full-v1 scene packages"),
            "character-look-bible.json",
            "Character Look Designer",
            "continue",
            "validate-artifact character-look-bible",
        ),
        "Animation": (
            ("production-design-plan.json", "character-look-bible.json"),
            "animation-plan.json",
            "Animation Director",
            "continue",
            "validate-artifact animation-plan",
        ),
        "VFX": (
            ("production-design-plan.json", "character-look-bible.json"),
            "vfx-plan.json",
            "VFX Planner",
            "continue",
            "validate-artifact vfx-plan",
        ),
        "Prompts": (
            ("vfx-plan.json", "character-look-bible.json"),
            "media-prompt-package.json",
            "AI Media Prompt Designer",
            "continue",
            "validate-artifact media-prompt-package",
        ),
        "Review": (
            ("media-prompt-package.json", "inspectable media or measurable metadata"),
            "media-review-report.json",
            "Media Review Supervisor",
            "awaiting-media",
            "validate-artifact media-review-report",
        ),
        "Manifest": (
            ("exact mode-selected artifacts",),
            "production-manifest.json",
            "Pipeline",
            "continue",
            "validate-artifact layer-manifest",
        ),
        "Validator": (
            ("production-manifest.json", "exact selected production modes"),
            "production-v2 validation evidence",
            "Production package validator",
            "ready-for-post",
            "validate-production",
        ),
    }
    assert set(expected_stages) <= rows.keys()

    for stage, (inputs, output, owner, allowed_status, validation_gate) in expected_stages.items():
        consumed, produced, actual_owner, control, validation = rows[stage]
        for required_input in inputs:
            assert required_input.lower() in consumed.lower()
        assert output in produced.replace("`", "")
        assert owner in actual_owner
        assert allowed_status in control
        assert "stop" in control
        assert validation_gate in validation

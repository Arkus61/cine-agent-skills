import pytest

from cine_skills.project_contracts import (
    FULL_CREATIVE_PROFILE,
    PROJECT_FORMATS,
    PRODUCTION_MODES,
    required_post_artifacts,
    required_production_artifacts,
    required_story_artifacts,
)


def filenames(contracts):
    return tuple(item.filename for item in contracts)


def test_v2_profiles_and_supported_variants_are_literal():
    assert FULL_CREATIVE_PROFILE == "full-creative-v2"
    assert PROJECT_FORMATS == (
        "feature", "short", "series", "documentary",
        "commercial", "music-video", "short-form",
    )
    assert PRODUCTION_MODES == ("live-action", "animation", "ai", "hybrid")


def test_series_story_requires_season_arc():
    assert filenames(required_story_artifacts("series")) == (
        "story-concept.json", "story-structure.json", "character-arcs.json",
        "world-bible.json", "season-arc.json", "story-manifest.json",
    )


def test_feature_story_does_not_require_season_arc():
    assert "season-arc.json" not in filenames(required_story_artifacts("feature"))


def test_hybrid_production_requires_animation_and_media_prompts():
    names = filenames(required_production_artifacts(("hybrid",)))
    assert "animation-plan.json" in names
    assert "media-prompt-package.json" in names


def test_combined_animation_and_ai_modes_require_both_conditional_artifacts():
    names = filenames(required_production_artifacts(("animation", "ai")))
    assert "animation-plan.json" in names
    assert "media-prompt-package.json" in names


def test_unknown_format_lists_sorted_allowed_values():
    with pytest.raises(ValueError, match="commercial.*documentary.*feature"):
        required_story_artifacts("podcast")


def test_unknown_production_mode_lists_sorted_allowed_values():
    with pytest.raises(ValueError, match="ai.*animation.*hybrid.*live-action"):
        required_production_artifacts(("stop-motion",))


def test_post_artifacts_follow_the_declared_dependency_order():
    assert filenames(required_post_artifacts()) == (
        "edit-plan.json",
        "sound-post-plan.json",
        "music-plan.json",
        "vfx-post-plan.json",
        "color-plan.json",
        "titles-captions-plan.json",
        "mastering-qc-plan.json",
        "post-manifest.json",
    )


@pytest.mark.parametrize("project_format", PROJECT_FORMATS)
def test_every_supported_format_has_a_story_contract(project_format):
    contracts = required_story_artifacts(project_format)

    assert contracts[-1].filename == "story-manifest.json"
    assert all(item.schema_name for item in contracts)


@pytest.mark.parametrize(
    ("modes", "conditional"),
    [
        (("live-action",), ()),
        (("animation",), ("animation-plan.json",)),
        (("ai",), ("media-prompt-package.json",)),
        (("hybrid",), ("animation-plan.json", "media-prompt-package.json")),
    ],
)
def test_each_production_mode_has_exact_conditional_artifacts(modes, conditional):
    names = filenames(required_production_artifacts(modes))

    assert tuple(name for name in ("animation-plan.json", "media-prompt-package.json") if name in names) == conditional

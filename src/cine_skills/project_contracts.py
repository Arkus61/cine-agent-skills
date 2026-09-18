from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass

STORY_PROFILE = "story"
PRODUCTION_PROFILE = "production"
POST_PROFILE = "post"
FULL_CREATIVE_PROFILE = "full-creative"

PROJECT_FORMATS = (
    "feature", "short", "series", "documentary",
    "commercial", "music-video", "short-form",
)
PRODUCTION_MODES = ("live-action", "animation", "ai", "hybrid")


@dataclass(frozen=True)
class ArtifactContract:
    filename: str
    schema_name: str
    dependency_order: int


@dataclass(frozen=True)
class LayerContract:
    profile: str
    directory_name: str
    base_artifacts: tuple[ArtifactContract, ...]


@dataclass(frozen=True)
class ProjectIndex:
    project_id: str
    project_format: str
    production_modes: tuple[str, ...]
    unit_ids: frozenset[str] = frozenset()
    scene_ids: frozenset[str] = frozenset()
    beat_ids: frozenset[str] = frozenset()
    shot_ids: frozenset[str] = frozenset()
    character_ids: frozenset[str] = frozenset()
    event_ids: frozenset[str] = frozenset()
    world_ids: frozenset[str] = frozenset()
    asset_ids: frozenset[str] = frozenset()
    sound_ids: frozenset[str] = frozenset()
    media_ids: frozenset[str] = frozenset()
    edit_segment_ids: frozenset[str] = frozenset()


def _contracts(items: tuple[tuple[str, str], ...]) -> tuple[ArtifactContract, ...]:
    return tuple(
        ArtifactContract(filename, schema_name, order)
        for order, (filename, schema_name) in enumerate(items, start=1)
    )


def _unknown_values(values: Collection[str], allowed: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(set(values).difference(allowed)))


def _unknown_value_error(kind: str, values: Collection[str], allowed: tuple[str, ...]) -> ValueError:
    unknown = _unknown_values(values, allowed)
    return ValueError(
        f"unknown {kind}: {', '.join(unknown)}; allowed values: {', '.join(sorted(allowed))}"
    )


def required_story_artifacts(project_format: str) -> tuple[ArtifactContract, ...]:
    if project_format not in PROJECT_FORMATS:
        raise _unknown_value_error("project format", (project_format,), PROJECT_FORMATS)

    items = (
        ("story-concept.json", "story-concept"),
        ("story-structure.json", "story-structure"),
        ("character-arcs.json", "character-arcs"),
        ("world-bible.json", "world-bible"),
    )
    if project_format == "series":
        items += (("season-arc.json", "season-arc"),)
    return _contracts(items + (("story-manifest.json", "layer-manifest"),))


def required_production_artifacts(
    production_modes: Collection[str],
) -> tuple[ArtifactContract, ...]:
    if unknown := _unknown_values(production_modes, PRODUCTION_MODES):
        raise _unknown_value_error("production mode", unknown, PRODUCTION_MODES)

    modes = frozenset(production_modes)
    items = (
        ("production-design-plan.json", "production-design-plan"),
        ("character-look-bible.json", "character-look-bible"),
    )
    if {"animation", "hybrid"}.intersection(modes):
        items += (("animation-plan.json", "animation-plan"),)
    items += (("vfx-plan.json", "vfx-plan"),)
    if {"ai", "hybrid"}.intersection(modes):
        items += (("media-prompt-package.json", "media-prompt-package"),)
    items += (
        ("media-review-report.json", "media-review-report"),
        ("production-manifest.json", "layer-manifest"),
    )
    return _contracts(items)


def required_post_artifacts() -> tuple[ArtifactContract, ...]:
    return _contracts(
        (
            ("edit-plan.json", "edit-plan"),
            ("sound-post-plan.json", "sound-post-plan"),
            ("music-plan.json", "music-plan"),
            ("vfx-post-plan.json", "vfx-post-plan"),
            ("color-plan.json", "color-plan"),
            ("titles-captions-plan.json", "titles-captions-plan"),
            ("mastering-qc-plan.json", "mastering-qc-plan"),
            ("post-manifest.json", "layer-manifest"),
        )
    )

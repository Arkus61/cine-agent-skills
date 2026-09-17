from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path

import pytest

from cine_skills.production_package import validate_production_package
from tests.production_fixtures import (
    PROJECT_ID,
    SCENE_ID,
    SHOT_IDS,
    production_payloads,
    read_payload,
    replace_payload,
    write_production_package,
)


@pytest.mark.parametrize(
    ("modes", "expected"),
    [
        (("live-action",), ("production-design-plan.json", "character-look-bible.json", "vfx-plan.json", "media-review-report.json", "production-manifest.json")),
        (("animation",), ("production-design-plan.json", "character-look-bible.json", "animation-plan.json", "vfx-plan.json", "media-review-report.json", "production-manifest.json")),
        (("ai",), ("production-design-plan.json", "character-look-bible.json", "vfx-plan.json", "media-prompt-package.json", "media-review-report.json", "production-manifest.json")),
        (("hybrid",), ("production-design-plan.json", "character-look-bible.json", "animation-plan.json", "vfx-plan.json", "media-prompt-package.json", "media-review-report.json", "production-manifest.json")),
    ],
)
def test_production_package_accepts_exact_mode_selected_inventory(
    repository_root: Path, tmp_path: Path, modes: tuple[str, ...], expected: tuple[str, ...]
) -> None:
    package = tmp_path / PROJECT_ID
    upstream = write_production_package(package, modes)

    assert tuple(sorted(path.name for path in package.iterdir())) == tuple(sorted(expected))
    assert validate_production_package(package, repository_root, modes, upstream) == []


def test_production_package_rejects_manifest_with_wrong_dependency_order(
    repository_root: Path, tmp_path: Path
) -> None:
    package = tmp_path / PROJECT_ID
    upstream = write_production_package(package, ("ai",))
    manifest = read_payload(package, "production-manifest.json")
    artifacts = manifest["artifacts"]
    assert isinstance(artifacts, list)
    artifacts[0], artifacts[1] = artifacts[1], artifacts[0]
    replace_payload(package, "production-manifest.json", manifest)

    assert validate_production_package(package, repository_root, ("ai",), upstream) == [
        "production-manifest.json: artifacts must match the exact dependency order: production-design-plan.json, character-look-bible.json, vfx-plan.json, media-prompt-package.json, media-review-report.json, production-manifest.json"
    ]


def test_production_package_rejects_foreign_project_and_out_of_index_shot(
    repository_root: Path, tmp_path: Path
) -> None:
    package = tmp_path / PROJECT_ID
    upstream = write_production_package(package, ("live-action",))
    manifest = read_payload(package, "production-manifest.json")
    manifest["project_id"] = "OTHER"
    replace_payload(package, "production-manifest.json", manifest)
    design = read_payload(package, "production-design-plan.json")
    coverage = design["coverage"]
    assert isinstance(coverage, list) and isinstance(coverage[0], dict)
    coverage[0]["shot_id"] = "NINEL-U01-S01-SH999"
    replace_payload(package, "production-design-plan.json", design)

    errors = validate_production_package(package, repository_root, ("live-action",), upstream)
    assert "production-manifest.json: project_id OTHER does not match NINEL" in errors
    assert any("coverage.0.shot_id" in error and "SH999" in error for error in errors)


def test_production_package_requires_declared_shot_coverage_and_vfx_effect_coverage(
    repository_root: Path, tmp_path: Path
) -> None:
    package = tmp_path / PROJECT_ID
    upstream = write_production_package(package, ("live-action",))
    design = read_payload(package, "production-design-plan.json")
    coverage = design["coverage"]
    assert isinstance(coverage, list)
    design["coverage"] = coverage[:-1]
    replace_payload(package, "production-design-plan.json", design)
    vfx = read_payload(package, "vfx-plan.json")
    applicability = vfx["applicability"]
    assert isinstance(applicability, list)
    vfx["applicability"] = applicability[:-1]
    replace_payload(package, "vfx-plan.json", vfx)

    errors = validate_production_package(package, repository_root, ("live-action",), upstream)
    assert any("NINEL-U01-S01-SH004" in error and "coverage" in error for error in errors)
    assert any("vfx-plan.json" in error and "applicability" in error for error in errors)


def test_production_package_compares_every_department_to_authoritative_upstream_shots(
    repository_root: Path, tmp_path: Path
) -> None:
    package = tmp_path / PROJECT_ID
    upstream = write_production_package(package, ("hybrid",))
    missing_shot = "NINEL-U01-S01-SH005"
    authoritative = replace(upstream, shot_ids=frozenset((*SHOT_IDS, missing_shot)))

    errors = validate_production_package(package, repository_root, ("hybrid",), authoritative)

    assert f"production-design-plan.json: missing coverage for upstream shot {missing_shot}" in errors
    assert f"character-look-bible.json: missing shot coverage for upstream shot {missing_shot}" in errors
    assert f"animation-plan.json: missing shot-character plan for upstream shot {missing_shot}" in errors
    assert f"vfx-plan.json: missing applicability for upstream shot {missing_shot}" in errors
    assert f"media-prompt-package.json: missing prompt coverage for upstream shot {missing_shot}" in errors
    assert f"media-review-report.json: missing reviewed media coverage for upstream shot {missing_shot}" in errors


def test_production_package_requires_design_to_carry_upstream_asset_continuity(
    repository_root: Path, tmp_path: Path
) -> None:
    package = tmp_path / PROJECT_ID
    upstream = write_production_package(package, ("live-action",))
    authoritative = replace(upstream, asset_ids=frozenset({"NINEL-AS999"}))

    assert validate_production_package(package, repository_root, ("live-action",), authoritative) == [
        "production-design-plan.json: missing declared continuity asset NINEL-AS999"
    ]


def test_production_package_requires_exact_world_and_character_continuity_context(
    repository_root: Path, tmp_path: Path
) -> None:
    package = tmp_path / PROJECT_ID
    upstream = write_production_package(package, ("live-action",))
    authoritative = replace(
        upstream,
        character_ids=frozenset({"NINEL-CH001", "NINEL-CH999"}),
        world_ids=frozenset({"NINEL-LO001", "NINEL-WR001", "NINEL-WR002", "NINEL-WR999"}),
    )

    errors = validate_production_package(package, repository_root, ("live-action",), authoritative)

    assert "production-design-plan.json: source_context.world_ids: missing upstream world NINEL-WR999" in errors
    assert "character-look-bible.json: source_context.character_ids: missing upstream character NINEL-CH999" in errors


def test_production_package_accepts_authoritative_sound_references(
    repository_root: Path, tmp_path: Path
) -> None:
    package = tmp_path / PROJECT_ID
    upstream = write_production_package(package, ("ai",))
    prompt = read_payload(package, "media-prompt-package.json")
    prompt_context = prompt["source_context"]
    assert isinstance(prompt_context, dict)
    registries = prompt_context["registries"]
    prompts = prompt["prompts"]
    assert isinstance(registries, dict) and isinstance(prompts, list)
    assert isinstance(prompts[0], dict)
    registries["sound_ids"] = ["NINEL-SD001"]
    prompt_references = prompts[0]["upstream_references"]
    assert isinstance(prompt_references, list)
    prompt_references.append({"kind": "sound", "id": "NINEL-SD001"})
    replace_payload(package, "media-prompt-package.json", prompt)
    review = read_payload(package, "media-review-report.json")
    context = review["source_context"]
    assert isinstance(context, dict)
    review_registries = context["registries"]
    prompt_packages = context["prompt_packages"]
    items = review["items"]
    assert isinstance(review_registries, dict) and isinstance(prompt_packages, list)
    assert isinstance(prompt_packages[0], dict) and isinstance(items, list)
    assert isinstance(items[0], dict)
    review_registries["sound_ids"] = ["NINEL-SD001"]
    prompt_packages[0]["upstream_references"].append(
        {"kind": "sound", "id": "NINEL-SD001"}
    )
    items[0]["upstream_references"].append({"kind": "sound", "id": "NINEL-SD001"})
    replace_payload(package, "media-review-report.json", review)
    authoritative = replace(upstream, sound_ids=frozenset({"NINEL-SD001"}))

    assert validate_production_package(package, repository_root, ("ai",), authoritative) == []


def test_production_package_binds_review_to_in_package_prompt_and_evidence(
    repository_root: Path, tmp_path: Path
) -> None:
    package = tmp_path / PROJECT_ID
    upstream = write_production_package(package, ("ai",))
    prompt = read_payload(package, "media-prompt-package.json")
    prompts = prompt["prompts"]
    assert isinstance(prompts, list) and isinstance(prompts[0], dict)
    prompts[0]["prompt_id"] = "NINEL-MP999"
    replace_payload(package, "media-prompt-package.json", prompt)

    errors = validate_production_package(package, repository_root, ("ai",), upstream)
    assert "media-review-report.json: source_context.prompt_packages.0.prompt_id: unknown in-package prompt NINEL-MP001" in errors


def test_production_package_requires_review_to_bind_every_in_package_criterion(
    repository_root: Path, tmp_path: Path
) -> None:
    package = tmp_path / PROJECT_ID
    upstream = write_production_package(package, ("ai",))
    review = read_payload(package, "media-review-report.json")
    context = review["source_context"]
    assert isinstance(context, dict)
    packages = context["prompt_packages"]
    assert isinstance(packages, list) and isinstance(packages[0], dict)
    criteria = packages[0]["acceptance_criteria"]
    assert isinstance(criteria, list)
    removed = criteria.pop()
    assert isinstance(removed, dict)
    criterion_id = removed["criterion_id"]
    items = review["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    item = items[0]
    evidence = item["inspection_evidence"]
    outcomes = item["criterion_outcomes"]
    assert isinstance(evidence, list) and isinstance(outcomes, list)
    item["inspection_evidence"] = [
        record for record in evidence if record.get("criterion_id") != criterion_id
    ]
    item["criterion_outcomes"] = [
        record for record in outcomes if record.get("criterion_id") != criterion_id
    ]
    replace_payload(package, "media-review-report.json", review)

    assert validate_production_package(package, repository_root, ("ai",), upstream) == [
        "media-review-report.json: source_context.prompt_packages.0.acceptance_criteria: must exactly match in-package prompt NINEL-MP001"
    ]


def test_production_package_rejects_approved_media_without_evidence(
    repository_root: Path, tmp_path: Path
) -> None:
    package = tmp_path / PROJECT_ID
    upstream = write_production_package(package, ("ai",))
    review = read_payload(package, "media-review-report.json")
    items = review["items"]
    assert isinstance(items, list) and isinstance(items[0], dict)
    items[0]["inspection_evidence"] = []
    replace_payload(package, "media-review-report.json", review)

    errors = validate_production_package(package, repository_root, ("ai",), upstream)
    assert "media-review-report.json: items.0.inspection_evidence: [] should be non-empty" in errors


def test_production_package_reports_inventory_and_malformed_json_without_traceback(
    repository_root: Path, tmp_path: Path
) -> None:
    package = tmp_path / PROJECT_ID
    upstream = write_production_package(package, ("live-action",))
    (package / "generated-media").mkdir()
    (package / "vfx-plan.json").write_text('{"project_id":', encoding="utf-8")

    errors = validate_production_package(package, repository_root, ("live-action",), upstream)
    assert errors == sorted(errors)
    assert "generated-media: unexpected entry for production-v2 package" in errors
    assert any(error.startswith("vfx-plan.json: invalid JSON") for error in errors)


def test_production_package_reports_wrong_file_type_and_unreadable_directory_safely(
    repository_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    package = tmp_path / PROJECT_ID
    upstream = write_production_package(package, ("live-action",))
    (package / "vfx-plan.json").unlink()
    (package / "vfx-plan.json").mkdir()

    assert "vfx-plan.json: required file is missing" in validate_production_package(
        package, repository_root, ("live-action",), upstream
    )

    def denied(_path: Path):
        raise PermissionError("denied")

    monkeypatch.setattr(Path, "iterdir", denied)
    assert validate_production_package(package, repository_root, ("live-action",), upstream) == [
        f"{package}: unable to inspect production-v2 package directory: denied"
    ]


def test_production_fixture_payloads_are_literal_and_do_not_compute_contracts() -> None:
    assert set(production_payloads(("hybrid",))) == {
        "production-design-plan.json", "character-look-bible.json", "animation-plan.json",
        "vfx-plan.json", "media-prompt-package.json", "media-review-report.json",
        "production-manifest.json",
    }

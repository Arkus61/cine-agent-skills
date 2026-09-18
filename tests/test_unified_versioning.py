from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_active_release_and_profiles_use_one_prerelease_version(repository_root: Path) -> None:
    from cine_skills import __version__
    from cine_skills.package import CORE_PROFILE, FULL_PROFILE
    from cine_skills.project_contracts import (
        FULL_CREATIVE_PROFILE,
        POST_PROFILE,
        PRODUCTION_PROFILE,
        STORY_PROFILE,
    )

    assert __version__ == "0.3.0"
    assert (CORE_PROFILE, FULL_PROFILE) == ("scene-core", "scene-full")
    assert (STORY_PROFILE, PRODUCTION_PROFILE, POST_PROFILE, FULL_CREATIVE_PROFILE) == (
        "story",
        "production",
        "post",
        "full-creative",
    )
    manifest = json.loads((repository_root / "system-manifest.json").read_text(encoding="utf-8"))
    assert manifest["release_version"] == __version__


def test_active_schemas_use_system_version(repository_root: Path) -> None:
    from cine_skills import __version__

    mismatches: list[str] = []
    for path in sorted((repository_root / "schemas").glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        for property_name in ("schema_version", "release_version"):
            constraint = schema.get("properties", {}).get(property_name, {})
            if "const" in constraint and constraint["const"] != __version__:
                mismatches.append(f"{path.name}:{property_name}")
    assert mismatches == []


def test_legacy_profile_flag_is_rejected_and_neutral_profile_is_accepted(
    repository_root: Path,
) -> None:
    command = [sys.executable, "-m", "cine_skills", "validate-package", "examples/scene-core/scenes/S01"]
    legacy = subprocess.run(
        [*command, "--profile", "full-v1"],
        cwd=repository_root,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": "src"},
    )
    assert legacy.returncode == 2
    neutral = subprocess.run(
        [*command, "--profile", "scene-core", "--format", "json"],
        cwd=repository_root,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": "src"},
    )
    assert neutral.returncode == 0
    assert json.loads(neutral.stdout)["profile"] == "scene-core"

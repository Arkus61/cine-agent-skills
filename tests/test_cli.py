import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.scene_full_fixtures import write_scene_full_package
from tests.story_fixtures import write_json, write_story_package
from tests.production_fixtures import (
    PROJECT_ID,
    read_payload,
    replace_payload,
    write_production_package,
)
from tests.post_fixtures import write_post_package


def test_validate_project_unknown_profile_is_malformed_invocation(repository_root: Path) -> None:
    result = run_cli(repository_root, "validate-project", "examples/ninel", "--profile", "unknown")
    assert result.returncode == 2
    assert "invalid choice" in result.stderr
    assert "Traceback" not in result.stdout + result.stderr


def test_cli_exposes_validate_post() -> None:
    from cine_skills.__main__ import build_parser
    args = build_parser().parse_args(["validate-post", "post", "--root", ".", "--format", "json"])
    assert args.command == "validate-post"


def test_validate_post_json_report_is_valid_for_complete_package(
    repository_root: Path, tmp_path: Path
) -> None:
    package = write_post_package(tmp_path / "post")
    result = run_cli(
        repository_root, "validate-post", str(package), "--root", str(repository_root),
        "--format", "json",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stderr == ""
    assert json.loads(result.stdout) == {
        "command": "validate-post", "errors": [], "profile": "post", "system_version": "0.3.0", "valid": True
    }


def test_validate_post_rejects_invalid_package_without_traceback(
    repository_root: Path, tmp_path: Path
) -> None:
    package = write_post_package(tmp_path / "post", extra="unexpected.txt")
    result = run_cli(repository_root, "validate-post", str(package), "--root", str(repository_root))
    assert_rejected_without_traceback(result, "unexpected.txt: unexpected entry")


def run_cli(repository_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ | {"PYTHONPATH": str(repository_root / "src")}
    return subprocess.run(
        [sys.executable, "-m", "cine_skills", *args],
        cwd=repository_root,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def run_make(repository_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ | {"PYTHONPATH": str(repository_root / "src")}
    return subprocess.run(
        ["make", f"PYTHON={sys.executable}", *args],
        cwd=repository_root,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def assert_rejected_without_traceback(
    result: subprocess.CompletedProcess[str], *diagnostics: str
) -> None:
    assert result.returncode == 1
    output = result.stdout + result.stderr
    assert "Traceback" not in output
    for diagnostic in diagnostics:
        assert diagnostic in output


def test_validate_production_json_report_is_literal_and_mode_repeated(
    repository_root: Path, tmp_path: Path
) -> None:
    package = tmp_path / PROJECT_ID
    write_production_package(package, ("animation", "ai"))

    result = run_cli(
        repository_root,
        "validate-production",
        str(package),
        "--root",
        str(repository_root),
        "--production-mode",
        "animation",
        "--production-mode",
        "ai",
        "--format",
        "json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stderr == ""
    assert result.stdout == (
        '{"command":"validate-production","errors":[],"profile":"production",'
        '"system_version":"0.3.0","valid":true}\n'
    )


def test_validate_production_allows_manifest_selected_nested_layer(
    repository_root: Path,
) -> None:
    result = run_cli(
        repository_root,
        "validate-production",
        "examples/ninel/production",
        "--root",
        str(repository_root),
        "--production-mode",
        "animation",
        "--production-mode",
        "ai",
        "--allow-nested",
        "--format",
        "json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["errors"] == []


def test_validate_production_returns_one_for_validation_failure_without_traceback(
    repository_root: Path, tmp_path: Path
) -> None:
    package = tmp_path / PROJECT_ID
    write_production_package(package, ("live-action",))
    (package / "unexpected.txt").write_text("not part of the package", encoding="utf-8")

    result = run_cli(
        repository_root,
        "validate-production",
        str(package),
        "--root",
        str(repository_root),
        "--production-mode",
        "live-action",
    )

    assert_rejected_without_traceback(result, "unexpected.txt: unexpected entry")


def test_validate_production_invalid_mode_is_usage_error_without_traceback(
    repository_root: Path, tmp_path: Path
) -> None:
    package = tmp_path / PROJECT_ID
    write_production_package(package, ("live-action",))

    result = run_cli(
        repository_root,
        "validate-production",
        str(package),
        "--root",
        str(repository_root),
        "--production-mode",
        "stop-motion",
    )

    assert result.returncode == 2
    assert "Traceback" not in result.stdout + result.stderr
    assert "invalid choice" in result.stderr


def test_validate_production_derives_declared_beat_context_for_ai_package(
    repository_root: Path, tmp_path: Path
) -> None:
    package = tmp_path / PROJECT_ID
    write_production_package(package, ("ai",))
    prompt = read_payload(package, "media-prompt-package.json")
    prompt_context = prompt["source_context"]
    assert isinstance(prompt_context, dict)
    registries = prompt_context["registries"]
    prompts = prompt["prompts"]
    assert isinstance(registries, dict) and isinstance(prompts, list)
    assert isinstance(prompts[0], dict)
    registries["beat_ids"] = ["NINEL-B001"]
    prompt_references = prompts[0]["upstream_references"]
    assert isinstance(prompt_references, list)
    prompt_references.append({"kind": "beat", "id": "NINEL-B001"})
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
    review_registries["beat_ids"] = ["NINEL-B001"]
    prompt_packages[0]["upstream_references"].append(
        {"kind": "beat", "id": "NINEL-B001"}
    )
    items[0]["upstream_references"].append({"kind": "beat", "id": "NINEL-B001"})
    replace_payload(package, "media-review-report.json", review)

    result = run_cli(
        repository_root,
        "validate-production",
        str(package),
        "--root",
        str(repository_root),
        "--production-mode",
        "ai",
        "--format",
        "json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["errors"] == []


def test_validate_production_derives_declared_sound_context_for_ai_package(
    repository_root: Path, tmp_path: Path
) -> None:
    package = tmp_path / PROJECT_ID
    write_production_package(package, ("ai",))
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

    result = run_cli(
        repository_root,
        "validate-production",
        str(package),
        "--root",
        str(repository_root),
        "--production-mode",
        "ai",
        "--format",
        "json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["errors"] == []


def test_validate_story_json_report_is_exact(repository_root: Path, tmp_path: Path) -> None:
    story = tmp_path / "story"
    write_story_package(story)

    result = run_cli(
        repository_root,
        "validate-story",
        str(story),
        "--project-format",
        "series",
        "--format",
        "json",
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == (
        '{"command":"validate-story","errors":[],"profile":"story",'
        '"system_version":"0.3.0","valid":true}\n'
    )


def test_validate_story_text_report_is_backward_compatible_in_shape(
    repository_root: Path, tmp_path: Path
) -> None:
    story = tmp_path / "story"
    write_story_package(story)

    result = run_cli(
        repository_root,
        "validate-story",
        str(story),
        "--project-format",
        "series",
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == "Story package validation passed.\n"


def test_validate_story_malformed_json_has_no_traceback(
    repository_root: Path, tmp_path: Path
) -> None:
    story = tmp_path / "story"
    write_story_package(story)
    (story / "story-concept.json").write_text('{"project_id":', encoding="utf-8")

    result = run_cli(
        repository_root,
        "validate-story",
        str(story),
        "--project-format",
        "series",
        "--format",
        "json",
    )

    assert_rejected_without_traceback(result, "story-concept.json", "invalid JSON")
    report = json.loads(result.stdout)
    assert report["command"] == "validate-story"
    assert report["profile"] == "story"
    assert report["valid"] is False


@pytest.mark.parametrize("invalid_provenance", [[], {}], ids=["array", "object"])
def test_validate_story_schema_invalid_canon_provenance_has_no_traceback(
    repository_root: Path,
    tmp_path: Path,
    invalid_provenance: object,
) -> None:
    story = tmp_path / "story"
    write_story_package(story)
    world_path = story / "world-bible.json"
    world = json.loads(world_path.read_text(encoding="utf-8"))
    rules = world["rules"]
    assert isinstance(rules, list) and isinstance(rules[0], dict)
    rules[0]["canon_status"] = "canon"
    rules[0]["provenance"] = invalid_provenance
    write_json(world_path, world)

    result = run_cli(
        repository_root,
        "validate-story",
        str(story),
        "--project-format",
        "series",
        "--format",
        "json",
    )

    assert_rejected_without_traceback(
        result, "world-bible.json", "rules.0.provenance", "not one of"
    )


def test_validate_story_malformed_invocation_exits_two_without_traceback(
    repository_root: Path,
) -> None:
    result = run_cli(repository_root, "validate-story")

    assert result.returncode == 2
    assert "Traceback" not in result.stdout + result.stderr
    assert "the following arguments are required" in result.stderr


@pytest.mark.parametrize(
    ("target", "variables", "success_message"),
    [
        (
            "validate-artifact",
            [
                "SCHEMA_NAME=shot-list",
                "ARTIFACT_FILE=examples/scene-core/scenes/S01/shot-list.json",
            ],
            "Artifact validation passed.",
        ),
        (
            "validate-package",
            ["PACKAGE_DIR=examples/scene-core/scenes/S01"],
            "Scene package validation passed.",
        ),
    ],
)
def test_make_validation_targets_use_configured_python(
    repository_root: Path,
    target: str,
    variables: list[str],
    success_message: str,
) -> None:
    result = run_make(repository_root, target, *variables)

    assert result.returncode == 0, result.stdout + result.stderr
    assert success_message in result.stdout


@pytest.mark.parametrize(
    ("target", "expected_output"),
    [
        ("validate-scene-core-example", "Scene package validation passed."),
        ("validate-scene-full-example", '"profile": "scene-full"'),
    ],
)
def test_documented_example_targets_pass(
    repository_root: Path, target: str, expected_output: str
) -> None:
    result = run_make(repository_root, target)

    assert result.returncode == 0, result.stdout + result.stderr
    assert expected_output in result.stdout
    if target == "validate-scene-full-example":
        assert '"valid": true' in result.stdout


@pytest.mark.parametrize(
    ("package_dir", "expected_report"),
    [
        (
            "examples/scene-core/scenes/S01",
            '{"command": "validate-package", "errors": [], "profile": "scene-core", "system_version": "0.3.0", "valid": true}\n',
        ),
        (
            "examples/scene-full/scenes/S01",
            '{"command": "validate-package", "errors": [], "profile": "scene-full", "system_version": "0.3.0", "valid": true}\n',
        ),
    ],
)
def test_canonical_packages_emit_literal_json_reports(
    repository_root: Path, package_dir: str, expected_report: str
) -> None:
    result = run_cli(
        repository_root,
        "validate-package",
        package_dir,
        "--root",
        str(repository_root),
        "--format",
        "json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == expected_report
    assert result.stderr == ""


def test_validate_artifact_cli_accepts_valid_file(
    tmp_path: Path, repository_root: Path
) -> None:
    artifact_path = tmp_path / "shot-list.json"
    artifact_path.write_text(
        json.dumps(
            {
                "schema_version": "0.3.0",
                "scene_id": "S01",
                "assumptions": [],
                "shots": [
                    {
                        "shot_id": "S01-SH001",
                        "beat_ids": ["S01-B01"],
                        "size": "medium",
                        "angle": "eye-level",
                        "lens_mm": 50,
                        "camera_support": "tripod",
                        "movement": "static",
                        "subject": "Ninel",
                        "action": "opens her eyes",
                        "composition": "centered medium single",
                        "dramatic_purpose": "establish disorientation",
                        "audio": "low ship hum",
                        "continuity": ["screen direction neutral"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    result = run_cli(
        repository_root,
        "validate-artifact",
        "shot-list",
        str(artifact_path),
        "--root",
        str(repository_root),
    )

    assert result.returncode == 0


def write_valid_package(package: Path) -> None:
    package.mkdir()
    files = {
        "scene-beats.json": {
            "schema_version": "0.3.0",
            "scene_id": "S01",
            "scene_objective": "Ninel wakes.",
            "turn": "Silence becomes threatening.",
            "assumptions": [],
            "beats": [
                {
                    "beat_id": "S01-B01",
                    "evidence": "Ninel opens her eyes.",
                    "action": "She wakes.",
                    "tactic": "She listens.",
                    "value_shift": "calm to unease",
                    "visual_opportunity": "A close view of her eyes.",
                }
            ],
        },
        "directing-plan.json": {
            "schema_version": "0.3.0",
            "scene_id": "S01",
            "concept": "A waking mind finds danger in silence.",
            "point_of_view": "Ninel",
            "performance_notes": ["Keep the awakening restrained."],
            "visual_strategy": ["Hold close to Ninel."],
            "rhythm": "Slow and attentive.",
            "assumptions": [],
        },
        "blocking-plan.json": {
            "schema_version": "0.3.0",
            "scene_id": "S01",
            "space": "A narrow cabin.",
            "axis": "The bunk-to-door line.",
            "positions": ["Ninel begins in the bunk."],
            "moves": [],
            "continuity_rules": ["Preserve the bunk-to-door axis."],
            "assumptions": [],
        },
        "camera-movement-plan.json": {
            "schema_version": "0.3.0",
            "scene_id": "S01",
            "movement_philosophy": "Let stillness create pressure.",
            "moves": [],
            "assumptions": [],
        },
        "shot-list.json": {
            "schema_version": "0.3.0",
            "scene_id": "S01",
            "assumptions": [],
            "shots": [
                {
                    "shot_id": "S01-SH001",
                    "beat_ids": ["S01-B01"],
                    "size": "medium",
                    "angle": "eye-level",
                    "lens_mm": 50,
                    "camera_support": "tripod",
                    "movement": "static",
                    "subject": "Ninel",
                    "action": "opens her eyes",
                    "composition": "centered medium single",
                    "dramatic_purpose": "establish disorientation",
                    "audio": "low ship hum",
                    "continuity": ["screen direction neutral"],
                }
            ],
        },
    }
    for name, value in files.items():
        (package / name).write_text(json.dumps(value), encoding="utf-8")


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
@pytest.mark.parametrize("command", ["validate-artifact", "validate-package"])
def test_validation_cli_rejects_nonstandard_json_constants(
    tmp_path: Path, repository_root: Path, command: str, constant: str
) -> None:
    package = tmp_path / "S01"
    write_valid_package(package)
    artifact = package / "shot-list.json"
    document = artifact.read_text(encoding="utf-8")
    assert '"lens_mm": 50' in document
    artifact.write_text(
        document.replace('"lens_mm": 50', f'"lens_mm": {constant}'),
        encoding="utf-8",
    )
    if command == "validate-artifact":
        args = (
            command,
            "shot-list",
            str(artifact),
            "--root",
            str(repository_root),
        )
    else:
        args = (command, str(package), "--root", str(repository_root))

    result = run_cli(repository_root, *args)

    assert_rejected_without_traceback(
        result, "shot-list.json", "non-standard JSON constant", constant
    )


@pytest.mark.parametrize(
    "context",
    ["artifact-document", "package-document", "artifact-schema", "repository-schema"],
)
def test_validation_cli_reports_invalid_utf8(
    tmp_path: Path, repository_root: Path, context: str
) -> None:
    package = tmp_path / "S01"
    write_valid_package(package)
    artifact = package / "shot-list.json"
    validation_root = repository_root

    if context == "artifact-document":
        artifact.write_bytes(b"\xff")
        args = (
            "validate-artifact",
            "shot-list",
            str(artifact),
            "--root",
            str(validation_root),
        )
        qualified_file = str(artifact)
    elif context == "package-document":
        artifact.write_bytes(b"\xff")
        args = (
            "validate-package",
            str(package),
            "--root",
            str(validation_root),
        )
        qualified_file = str(artifact)
    else:
        validation_root = tmp_path / "repository"
        shutil.copytree(repository_root / "schemas", validation_root / "schemas")
        schema = validation_root / "schemas" / "shot-list.schema.json"
        schema.write_bytes(b"\xff")
        qualified_file = str(schema)
        if context == "artifact-schema":
            args = (
                "validate-artifact",
                "shot-list",
                str(artifact),
                "--root",
                str(validation_root),
            )
        else:
            args = ("validate", str(validation_root))

    result = run_cli(repository_root, *args)

    assert_rejected_without_traceback(result, qualified_file, "UTF-8")


@pytest.mark.parametrize("damaged_file", ["SKILL.md", "agents/openai.yaml"])
def test_validate_repository_cli_reports_invalid_utf8_skill_file_as_json(
    tmp_path: Path, repository_root: Path, damaged_file: str
) -> None:
    validation_root = tmp_path / "repository"
    skill = validation_root / ".agents" / "skills" / "scene-director"
    skill.mkdir(parents=True)
    skill_file = skill / "SKILL.md"
    metadata_file = skill / "agents" / "openai.yaml"
    if damaged_file == "SKILL.md":
        skill_file.write_bytes(b"\xff")
        damaged_path = skill_file
    else:
        skill_file.write_text(
            "---\nname: scene-director\n"
            "description: Use for directing a scripted scene.\n"
            "---\n\n# Scene Director\n",
            encoding="utf-8",
        )
        metadata_file.parent.mkdir()
        metadata_file.write_bytes(b"\xff")
        damaged_path = metadata_file

    result = run_cli(
        repository_root,
        "validate",
        str(validation_root),
        "--format",
        "json",
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["valid"] is False
    assert any(
        str(damaged_path) in error and "UTF-8" in error
        for error in payload["errors"]
    )


def test_validate_repository_cli_reports_symlink_loop_as_json(
    tmp_path: Path, repository_root: Path
) -> None:
    validation_root = tmp_path / "repository"
    skill = validation_root / ".agents" / "skills" / "scene-director"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: scene-director\n"
        "description: Use for directing a scripted scene.\n"
        "---\n\n# Scene Director\n\nRead [loop](loop/file.md).\n",
        encoding="utf-8",
    )
    metadata = skill / "agents" / "openai.yaml"
    metadata.parent.mkdir()
    metadata.write_text(
        "interface:\n"
        "  display_name: Scene Director\n"
        "  short_description: Plan a scripted scene for production\n"
        "  default_prompt: Use $scene-director to direct this scene.\n",
        encoding="utf-8",
    )
    os.symlink("loop", skill / "loop")

    result = run_cli(
        repository_root,
        "validate",
        str(validation_root),
        "--format",
        "json",
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["valid"] is False
    assert any(
        "cannot resolve relative reference: loop/file.md" in error
        for error in payload["errors"]
    )


@pytest.mark.parametrize(
    "context",
    [
        "artifact-document",
        "artifact-schema",
        "repository-schema",
        "skill-frontmatter",
        "openai-metadata",
    ],
)
def test_validation_cli_reports_excessive_parser_nesting_as_json(
    tmp_path: Path, repository_root: Path, context: str
) -> None:
    validation_root = tmp_path / "repository"
    deep_json = "[" * 10_000 + "0" + "]" * 10_000
    deep_yaml = "[" * 1_200 + "0" + "]" * 1_200

    def write_valid_skill() -> tuple[Path, Path]:
        skill = validation_root / ".agents" / "skills" / "scene-director"
        skill.mkdir(parents=True)
        skill_file = skill / "SKILL.md"
        skill_file.write_text(
            "---\nname: scene-director\n"
            "description: Use for directing a scripted scene.\n"
            "---\n\n# Scene Director\n",
            encoding="utf-8",
        )
        metadata_file = skill / "agents" / "openai.yaml"
        metadata_file.parent.mkdir()
        metadata_file.write_text(
            "interface:\n"
            "  display_name: Scene Director\n"
            "  short_description: Plan a scripted scene for production\n"
            "  default_prompt: Use $scene-director to direct this scene.\n",
            encoding="utf-8",
        )
        return skill_file, metadata_file

    if context == "artifact-document":
        damaged_path = tmp_path / "deep.json"
        damaged_path.write_text('{"value":' + deep_json + "}", encoding="utf-8")
        args = (
            "validate-artifact",
            "shot-list",
            str(damaged_path),
            "--root",
            str(repository_root),
            "--format",
            "json",
        )
    elif context in {"artifact-schema", "repository-schema"}:
        schema_dir = validation_root / "schemas"
        schema_dir.mkdir(parents=True)
        damaged_path = schema_dir / "shot-list.schema.json"
        damaged_path.write_text(deep_json, encoding="utf-8")
        if context == "artifact-schema":
            artifact = tmp_path / "artifact.json"
            artifact.write_text("{}", encoding="utf-8")
            args = (
                "validate-artifact",
                "shot-list",
                str(artifact),
                "--root",
                str(validation_root),
                "--format",
                "json",
            )
        else:
            write_valid_skill()
            args = ("validate", str(validation_root), "--format", "json")
    else:
        skill_file, metadata_file = write_valid_skill()
        if context == "skill-frontmatter":
            skill_file.write_text(
                "---\nname: scene-director\ndescription: "
                + deep_yaml
                + "\n---\n\n# Scene Director\n",
                encoding="utf-8",
            )
            damaged_path = skill_file
        else:
            metadata_file.write_text("interface: " + deep_yaml, encoding="utf-8")
            damaged_path = metadata_file
        args = ("validate", str(validation_root), "--format", "json")

    result = run_cli(repository_root, *args)

    assert result.returncode == 1
    assert "Traceback" not in result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["valid"] is False
    assert any(
        str(damaged_path) in error and "nesting" in error
        for error in payload["errors"]
    )


@pytest.mark.parametrize("command", ["validate-artifact", "validate"])
def test_validation_cli_reports_excessively_deep_valid_schema_as_json(
    tmp_path: Path, repository_root: Path, command: str
) -> None:
    validation_root = tmp_path / "repository"
    schema_dir = validation_root / "schemas"
    schema_dir.mkdir(parents=True)
    schema_path = schema_dir / "deep.schema.json"
    nested_schema = (
        '{"type":"array","items":' * 1_500
        + '{"type":"number"}'
        + "}" * 1_500
    )
    schema_path.write_text(nested_schema, encoding="utf-8")
    if command == "validate-artifact":
        artifact = tmp_path / "artifact.json"
        artifact.write_text("{}", encoding="utf-8")
        args = (
            command,
            "deep",
            str(artifact),
            "--root",
            str(validation_root),
            "--format",
            "json",
        )
    else:
        skill = validation_root / ".agents" / "skills" / "scene-director"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: scene-director\n"
            "description: Use for directing a scripted scene.\n"
            "---\n\n# Scene Director\n",
            encoding="utf-8",
        )
        metadata = skill / "agents" / "openai.yaml"
        metadata.parent.mkdir()
        metadata.write_text(
            "interface:\n"
            "  display_name: Scene Director\n"
            "  short_description: Plan a scripted scene for production\n"
            "  default_prompt: Use $scene-director to direct this scene.\n",
            encoding="utf-8",
        )
        args = (command, str(validation_root), "--format", "json")

    result = run_cli(repository_root, *args)

    assert result.returncode == 1
    assert "Traceback" not in result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert any(
        str(schema_path) in error and "nesting" in error
        for error in payload["errors"]
    )


def test_validate_artifact_cli_reports_excessive_validation_nesting_as_json(
    tmp_path: Path, repository_root: Path
) -> None:
    validation_root = tmp_path / "repository"
    schema_dir = validation_root / "schemas"
    schema_dir.mkdir(parents=True)
    schema_path = schema_dir / "deep.schema.json"
    schema_path.write_text(
        json.dumps(
            {
                "$defs": {
                    "node": {
                        "anyOf": [
                            {"type": "integer"},
                            {
                                "type": "array",
                                "items": {"$ref": "#/$defs/node"},
                            },
                        ]
                    }
                },
                "type": "object",
                "required": ["value"],
                "properties": {"value": {"$ref": "#/$defs/node"}},
            }
        ),
        encoding="utf-8",
    )
    artifact = tmp_path / "artifact.json"
    artifact.write_text(
        '{"value":' + "[" * 500 + "0" + "]" * 500 + "}",
        encoding="utf-8",
    )

    result = run_cli(
        repository_root,
        "validate-artifact",
        "deep",
        str(artifact),
        "--root",
        str(validation_root),
        "--format",
        "json",
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert any(
        str(schema_path) in error and "nesting" in error
        for error in payload["errors"]
    )


@pytest.mark.parametrize(
    ("schema_document", "diagnostic"),
    [
        (
            '{"$schema": "https://json-schema.org/draft/2020-12/schema", '
            '"type": "cinematic"}',
            "invalid schema",
        ),
        (
            '{"$schema": "https://json-schema.org/draft/2020-12/schema", '
            '"$ref": "#/$defs/missing"}',
            "schema reference",
        ),
    ],
)
@pytest.mark.parametrize("command", ["validate-artifact", "validate-package"])
def test_artifact_and_package_cli_report_schema_failures(
    tmp_path: Path,
    repository_root: Path,
    command: str,
    schema_document: str,
    diagnostic: str,
) -> None:
    package = tmp_path / "S01"
    write_valid_package(package)
    validation_root = tmp_path / "repository"
    shutil.copytree(repository_root / "schemas", validation_root / "schemas")
    schema = validation_root / "schemas" / "shot-list.schema.json"
    schema.write_text(schema_document, encoding="utf-8")
    if command == "validate-artifact":
        args = (
            command,
            "shot-list",
            str(package / "shot-list.json"),
            "--root",
            str(validation_root),
        )
    else:
        args = (command, str(package), "--root", str(validation_root))

    result = run_cli(repository_root, *args)

    assert_rejected_without_traceback(result, str(schema), diagnostic)


def test_validate_package_cli_accepts_valid_package(
    tmp_path: Path, repository_root: Path
) -> None:
    package = tmp_path / "S01"
    write_valid_package(package)

    result = run_cli(
        repository_root,
        "validate-package",
        str(package),
        "--root",
        str(repository_root),
    )

    assert result.returncode == 0


def test_validate_package_json_report_is_machine_readable(
    repository_root: Path,
) -> None:
    result = run_cli(
        repository_root,
        "validate-package",
        "examples/scene-core/scenes/S01",
        "--profile",
        "scene-core",
        "--format",
        "json",
    )

    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "command": "validate-package",
        "errors": [],
        "profile": "scene-core",
        "system_version": "0.3.0",
        "valid": True,
    }


def test_validate_full_package_json_report_is_machine_readable(
    tmp_path: Path, repository_root: Path
) -> None:
    package = tmp_path / "S01"
    write_scene_full_package(package)

    result = run_cli(
        repository_root,
        "validate-package",
        str(package),
        "--profile",
        "scene-full",
        "--format",
        "json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout) == {
        "command": "validate-package",
        "errors": [],
        "profile": "scene-full",
        "system_version": "0.3.0",
        "valid": True,
    }


def test_validate_package_json_report_sorts_errors(
    tmp_path: Path, repository_root: Path
) -> None:
    package = tmp_path / "S01"
    write_valid_package(package)
    (package / "shot-list.json").unlink()
    (package / "blocking-plan.json").unlink()

    result = run_cli(
        repository_root,
        "validate-package",
        str(package),
        "--root",
        str(repository_root),
        "--format",
        "json",
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["valid"] is False
    assert payload["profile"] == "scene-core"
    assert payload["errors"] == sorted(payload["errors"])
    assert len(payload["errors"]) == 2


def test_installed_console_entry_validates_core_package(
    repository_root: Path,
) -> None:
    executable = Path(sys.executable).parent / "cine-skills"
    assert executable.is_file()

    result = subprocess.run(
        [
            str(executable),
            "validate-package",
            "examples/scene-core/scenes/S01",
            "--profile",
            "scene-core",
        ],
        cwd=repository_root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == "Scene package validation passed.\n"


def test_validate_package_cli_rejects_inconsistent_package(
    tmp_path: Path, repository_root: Path
) -> None:
    package = tmp_path / "S01"
    write_valid_package(package)
    directing_plan_path = package / "directing-plan.json"
    directing_plan = json.loads(directing_plan_path.read_text(encoding="utf-8"))
    directing_plan["scene_id"] = "S02"
    directing_plan_path.write_text(json.dumps(directing_plan), encoding="utf-8")

    result = run_cli(
        repository_root,
        "validate-package",
        str(package),
        "--root",
        str(repository_root),
    )

    assert result.returncode == 1
    assert "directing-plan.json" in result.stdout
    assert "scene_id" in result.stdout


def test_validate_package_cli_rejects_missing_package_file(
    tmp_path: Path, repository_root: Path
) -> None:
    package = tmp_path / "S01"
    write_valid_package(package)
    (package / "shot-list.json").unlink()

    result = run_cli(
        repository_root,
        "validate-package",
        str(package),
        "--root",
        str(repository_root),
    )

    assert result.returncode == 1
    assert "shot-list.json" in result.stdout

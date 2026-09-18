from importlib.metadata import version
from pathlib import Path

from cine_skills import __version__
from cine_skills.validator import validate_repository


EXPECTED_V1_SCHEMAS = {
    "scene-beats.schema.json",
    "directing-plan.schema.json",
    "visual-language-plan.schema.json",
    "blocking-plan.schema.json",
    "camera-movement-plan.schema.json",
    "shot-list.schema.json",
    "lighting-plan.schema.json",
    "sound-plan.schema.json",
    "storyboard-plan.schema.json",
    "production-breakdown.schema.json",
    "continuity-plan.schema.json",
    "package-manifest.schema.json",
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_release_version_is_0_3_0() -> None:
    assert __version__ == "0.3.0"
    assert version("cine-agent-skills") == "0.3.0"


def test_scene_schema_catalog_is_present(repository_root: Path) -> None:
    actual = {
        path.name for path in (repository_root / "schemas").glob("*.schema.json")
    }
    assert EXPECTED_V1_SCHEMAS <= actual


def test_repository_reports_skills_directory_inspection_error(
    tmp_path: Path, monkeypatch
) -> None:
    skills_root = tmp_path / ".agents" / "skills"
    skills_root.mkdir(parents=True)
    original_iterdir = Path.iterdir

    def deny_skills_listing(path: Path):
        if path == skills_root:
            raise PermissionError("skills denied")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", deny_skills_listing)

    errors = validate_repository(tmp_path)

    assert errors == [
        f"{skills_root}: cannot inspect skills directory: skills denied"
    ]


def test_repository_reports_schema_directory_inspection_error(
    tmp_path: Path, monkeypatch
) -> None:
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    skill = tmp_path / ".agents" / "skills" / "scene-director"
    write(
        skill / "SKILL.md",
        "---\nname: scene-director\n"
        "description: Use for directing a scripted scene.\n"
        "---\n\n# Scene Director\n",
    )
    write(
        skill / "agents" / "openai.yaml",
        "interface:\n"
        "  display_name: Scene Director\n"
        "  short_description: Plan a scripted scene for production\n"
        "  default_prompt: Use $scene-director to direct this scene.\n",
    )
    original_iterdir = Path.iterdir

    def deny_schema_listing(path: Path):
        if path == schema_dir:
            raise PermissionError("schemas denied")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", deny_schema_listing)

    errors = validate_repository(tmp_path)

    assert errors == [
        f"{schema_dir}: cannot inspect schema directory: schemas denied"
    ]


def test_valid_repository_has_no_errors(tmp_path: Path) -> None:
    skill = tmp_path / ".agents" / "skills" / "scene-director"
    write(
        skill / "SKILL.md",
        "---\nname: scene-director\ndescription: Creates a directing plan. Use for directing a scripted scene.\n---\n\n# Scene Director\n",
    )
    write(
        skill / "agents" / "openai.yaml",
        'interface:\n  display_name: "Scene Director"\n  short_description: "Plan a scene for production"\n  default_prompt: "Use $scene-director to direct this scene."\n',
    )

    assert validate_repository(tmp_path) == []


def test_directory_name_must_match_frontmatter_name(tmp_path: Path) -> None:
    skill = tmp_path / ".agents" / "skills" / "scene-director"
    write(
        skill / "SKILL.md",
        "---\nname: wrong-name\ndescription: Creates a directing plan. Use for directing a scripted scene.\n---\n",
    )

    errors = validate_repository(tmp_path)

    assert any("must match directory" in error for error in errors)


def test_description_must_not_exceed_1024_characters(tmp_path: Path) -> None:
    skill = tmp_path / ".agents" / "skills" / "scene-director"
    write(
        skill / "SKILL.md",
        f"---\nname: scene-director\ndescription: {'x' * 1025}\n---\n",
    )

    errors = validate_repository(tmp_path)

    assert any("1024" in error for error in errors)


def test_openai_default_prompt_mentions_skill(tmp_path: Path) -> None:
    skill = tmp_path / ".agents" / "skills" / "scene-director"
    write(
        skill / "SKILL.md",
        "---\nname: scene-director\ndescription: Creates a directing plan. Use for directing a scripted scene.\n---\n",
    )
    write(
        skill / "agents" / "openai.yaml",
        'interface:\n  display_name: "Scene Director"\n  short_description: "Plan a scene for production"\n  default_prompt: "Direct this scene."\n',
    )

    errors = validate_repository(tmp_path)

    assert any("$scene-director" in error for error in errors)


def test_broken_markdown_reference_is_reported(tmp_path: Path) -> None:
    skill = tmp_path / ".agents" / "skills" / "scene-director"
    write(
        skill / "SKILL.md",
        "---\nname: scene-director\ndescription: Creates a directing plan. Use for directing a scripted scene.\n---\n\nRead [missing](references/missing.md).\n",
    )

    errors = validate_repository(tmp_path)

    assert any("missing relative reference" in error for error in errors)


def test_repository_reports_malformed_json_schema(tmp_path: Path) -> None:
    write(tmp_path / "schemas" / "broken.schema.json", "{not JSON")

    errors = validate_repository(tmp_path)

    assert any(
        "broken.schema.json" in error and "invalid JSON schema" in error
        for error in errors
    )


def test_repository_rejects_nonstandard_json_constant_in_schema(tmp_path: Path) -> None:
    write(
        tmp_path / "schemas" / "nonstandard.schema.json",
        '{"$schema": "https://json-schema.org/draft/2020-12/schema", '
        '"type": "number", "maximum": NaN}',
    )

    errors = validate_repository(tmp_path)

    assert any(
        "nonstandard.schema.json" in error
        and "invalid JSON schema" in error
        and "NaN" in error
        for error in errors
    )


def test_repository_reports_invalid_json_schema_keyword(tmp_path: Path) -> None:
    skill = tmp_path / ".agents" / "skills" / "scene-director"
    write(
        skill / "SKILL.md",
        "---\nname: scene-director\ndescription: Creates a directing plan. Use for directing a scripted scene.\n---\n\n# Scene Director\n",
    )
    write(
        skill / "agents" / "openai.yaml",
        'interface:\n  display_name: "Scene Director"\n  short_description: "Plan a scene for production"\n  default_prompt: "Use $scene-director to direct this scene."\n',
    )
    write(
        tmp_path / "schemas" / "invalid.schema.json",
        '{"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "cinematic"}',
    )

    errors = validate_repository(tmp_path)

    assert any(
        "invalid.schema.json" in error and "invalid JSON schema" in error
        for error in errors
    )

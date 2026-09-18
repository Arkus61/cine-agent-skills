from __future__ import annotations

import hashlib
from pathlib import Path

import pytest


def _skill(root: Path, name: str, body: str = "# Body\n") -> Path:
    skill = root / name
    (skill / "agents").mkdir(parents=True)
    (skill / "references").mkdir()
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Describe {name}\n---\n{body}",
        encoding="utf-8",
    )
    (skill / "agents/openai.yaml").write_text("interface: {}\n", encoding="utf-8")
    (skill / "references/guide.md").write_text("guide\n", encoding="utf-8")
    return skill


def test_registry_returns_discovery_metadata_without_instruction_body(tmp_path: Path) -> None:
    from cine_skills.runtime.skill_registry import build_skill_registry

    _skill(tmp_path, "camera-movement-designer", "# secret body\nDo not expose this.\n")
    records = build_skill_registry(tmp_path)

    assert records[0]["name"] == "camera-movement-designer"
    assert records[0]["description"] == "Describe camera-movement-designer"
    assert records[0]["path"] == "camera-movement-designer"
    assert "secret body" not in records[0]
    assert records[0]["digest"] == hashlib.sha256(
        b"SKILL.md\x00---\nname: camera-movement-designer\n"
        b"description: Describe camera-movement-designer\n---\n"
        b"# secret body\nDo not expose this.\n"
        b"\x00agents/openai.yaml\x00interface: {}\n"
        b"\x00references/guide.md\x00guide\n"
    ).hexdigest()


def test_registry_uses_conditional_reference_rules_from_config(repository_root: Path) -> None:
    from cine_skills.runtime.skill_registry import build_skill_registry

    records = build_skill_registry(repository_root / ".agents/skills")
    camera = next(item for item in records if item["name"] == "camera-movement-designer")

    assert camera["required_refs"] == []
    assert camera["conditional_refs"] == [
        {
            "path": "references/camera-movement-taxonomy.md",
            "when": "movement-family-selection",
        }
    ]
    assert len(records) == 37
    assert all("body" not in record for record in records)


def test_registry_digest_changes_when_reference_changes(tmp_path: Path) -> None:
    from cine_skills.runtime.skill_registry import build_skill_registry

    skill = _skill(tmp_path, "scene-planner")
    before = build_skill_registry(tmp_path)[0]["digest"]
    (skill / "references/guide.md").write_text("changed\n", encoding="utf-8")

    after = build_skill_registry(tmp_path)[0]["digest"]

    assert after != before


def test_registry_rejects_malformed_frontmatter(tmp_path: Path) -> None:
    from cine_skills.runtime.skill_registry import build_skill_registry

    skill = _skill(tmp_path, "scene-planner")
    (skill / "SKILL.md").write_text("# no frontmatter\n", encoding="utf-8")

    with pytest.raises(ValueError, match="frontmatter"):
        build_skill_registry(tmp_path)

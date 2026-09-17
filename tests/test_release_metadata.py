from __future__ import annotations

import tomllib
from pathlib import Path

from cine_skills import __version__


def read(repository_root: Path, relative: str) -> str:
    return (repository_root / relative).read_text(encoding="utf-8")


def test_release_metadata_is_synchronised(repository_root: Path) -> None:
    metadata = tomllib.loads(read(repository_root, "pyproject.toml"))
    assert metadata["project"]["version"] == "2.0.0"
    assert __version__ == "2.0.0"


def test_readme_describes_v2_profiles_and_migration(repository_root: Path) -> None:
    readme = read(repository_root, "README.md")
    for profile in ("story-v2", "production-v2", "post-v2", "full-creative-v2"):
        assert profile in readme
    assert "migration-v1-to-v2.md" in readme


def test_release_docs_describe_boundaries(repository_root: Path) -> None:
    agents = read(repository_root, "AGENTS.md")
    schemas = read(repository_root, "schemas/README.md")
    migration = read(repository_root, "docs/migration-v1-to-v2.md")
    changelog = read(repository_root, "CHANGELOG.md")
    assert "2026-09-13-cine-direction.md" in agents
    assert "creative-manifest.schema.json" in schemas
    assert "No migration command fabricates" in migration
    assert "## 2.0.0" in changelog


def test_makefile_exposes_v2_and_archive_gates(repository_root: Path) -> None:
    makefile = read(repository_root, "Makefile")
    assert "validate-story-example:" in makefile
    assert "validate-production-example:" in makefile
    assert "validate-post-example:" in makefile
    assert "validate-v2-example:" in makefile
    assert "release-archive:" in makefile

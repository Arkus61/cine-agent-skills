# Active Versioning Policy

The active Cine Agent Skills system has one prerelease label: **0.3**. Machine-readable fields use **0.3.0**. These are two spellings of one version, not independent counters.

## Source of truth

`[project].version` in `pyproject.toml` is the only hand-edited version source. Run:

```bash
PYTHONPATH=src python scripts/sync_versions.py --root . --check
PYTHONPATH=src python scripts/sync_versions.py --root . --write
make check-version
```

The synchronizer updates and checks the allowlisted derived values in `src/cine_skills/__init__.py`, `system-manifest.json`, active schemas, evaluations, examples, and skill templates. It is text-preserving for JSON so a version bump does not reformat unrelated creative content. Release archives derive their filename from the same project version.

## Functional profiles

| Historical name | Active profile |
|---|---|
| `core-v0.1` | `scene-core` |
| `full-v1` | `scene-full` |
| `story-v2` | `story` |
| `production-v2` | `production` |
| `post-v2` | `post` |
| `full-creative-v2` | `full-creative` |
| `auto` | `auto` |

The active CLI exposes only the right-hand names. Old generation-named flags are rejected with exit code `2`, with the replacement named in the diagnostic. This avoids hidden aliases and makes new requests unambiguous.

## Older data

Validation is read-only and never changes a supplied project. A package containing historical schema/profile values must go through the explicit migration command:

```bash
PYTHONPATH=src python scripts/migrate_project.py \
  --root . --source path/to/legacy-package --output path/to/new-package \
  --dry-run --format json
```

The command recognizes only the known legacy scene and layered-project shapes. It writes a new output directory, preserves source bytes, IDs, approvals, facts, uncertainty, and media revisions, changes only the allowlisted version/profile fields, validates the candidate, and reports `ready`, `migrated`, or `blocked` instead of guessing. A blocked migration never publishes a partial output.

The repository's migration guides, historical plans, forward reports, and changelog entries retain the version numbers that were true at the time. See the [historical index](history/README.md). They are historical evidence, not active contracts. Do not copy their generation-named profiles into new artifacts.

## What is not versioned here

Do not change Python or dependency versions, JSON Schema's `$schema`, stable entity IDs, draft/edit/revision numbers, source dates, or media identifiers as part of a system version bump. Do not create per-skill counters or numbered duplicate directories.

## Review checklist

- `pyproject.toml` contains the intended version.
- `make check-version` passes.
- All active schemas, templates, evals, examples, and manifests carry `0.3.0`.
- JSON reports include `system_version: "0.3.0"` and a neutral functional profile.
- Old flags fail with code `2`; old data is not silently accepted as current.
- `make check`, all neutral example targets, `make release-archive`, and `git diff --check` pass.

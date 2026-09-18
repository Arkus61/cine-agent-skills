# Unified Versioning Design

## Decision

Cine Agent Skills has one active prerelease version, `0.3` (machine value `0.3.0`). The value is edited only in `[project].version` in `pyproject.toml`; runtime metadata, active schemas, templates, evaluations, examples, manifests, reports, and release archive names are derived or checked from it.

Package completeness is represented by neutral functional profiles:

| Profile | Responsibility |
|---|---|
| `scene-core` | Minimal scene package |
| `scene-full` | Complete scene package |
| `story` | Story and screenplay layer |
| `production` | Production planning layer |
| `post` | Postproduction planning layer |
| `full-creative` | Complete layered project |
| `auto` | Select scene completeness by manifest presence |

Generation-named flags are historical inputs, not active aliases. The CLI rejects them with code `2`. Validation is read-only. Legacy packages are converted only by `scripts/migrate_project.py`, which writes a new directory, changes an allowlisted set of metadata/profile fields, validates the candidate, and returns `ready`, `migrated`, or `blocked`.

## Invariants

- Stable IDs, authored facts, assumptions, uncertainties, approvals, and media revisions are unchanged by a version bump or migration.
- Subject schemas remain separate; a common version does not create a universal artifact schema.
- Historical plans, reports, migration guides, and changelog entries retain their original numbers and are marked as history.
- Core validation remains offline and does not require the optional runtime, a provider, Blender, or network access.
- The optional runtime reuses community libraries and standard MCP. The user's configured Blender MCP is the only Blender integration boundary; no custom connector or protocol is part of this design.
- Unknown versions, mixed contracts, unsafe paths, symlinks, malformed JSON, and invalid candidates block migration without publishing partial output.

## Verification

The version gate is `make check-version`. The acceptance gate runs `make check`, all neutral example targets, `make release-archive`, and `git diff --check`. Archive output is derived from the same source version and is deterministic for a fixed tracked tree.

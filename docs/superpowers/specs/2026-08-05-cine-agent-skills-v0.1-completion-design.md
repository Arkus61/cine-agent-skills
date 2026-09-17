# Cine Agent Skills v0.1 Completion Design

## Status and intent

The imported starter repository already contains the six approved skills and five artifact schemas. This completion pass turns that starter into a reproducible v0.1 release without expanding the product boundary.

## Approaches considered

### Repackage the starter unchanged

This is the smallest option, but it does not prove that a generated scene package is internally consistent. It also leaves artifact validation available only as a Python function.

### Harden the approved pipeline (selected)

Keep the exact six-skill catalog and five-artifact flow. Add deterministic artifact and scene-package validation, a canonical split-file example, end-to-end tests, reproducible setup instructions, and release checks.

### Add storyboarding and camera-angle skills

This would more closely match the long-term roadmap, but it changes the approved v0.1 boundary. Those skills remain candidates for v0.2 or a separately approved release.

## Product boundary

Version 0.1 ends at a production-ready shot list. It contains no image or video generation, external generation APIs, MCP server, DaVinci Resolve or Blender control, production scheduling, budgeting, casting, or web UI.

The exact skill catalog remains:

1. `scene-beat-analyzer`
2. `scene-director`
3. `blocking-designer`
4. `camera-movement-designer`
5. `shot-list-builder`
6. `scene-preproduction-pipeline`

## Canonical scene package

The pipeline writes one directory:

```text
projects/<project-slug>/scenes/<scene-id>/
├── source-scene.md
├── scene-beats.json
├── directing-plan.json
├── blocking-plan.json
├── camera-movement-plan.json
└── shot-list.json
```

Each JSON file must pass its schema. Package-level validation additionally checks:

- every artifact has the same non-empty `scene_id`;
- beat, movement, and shot identifiers are unique and use the package scene prefix;
- every beat reference in blocking, camera movement, and shots resolves to a declared beat;
- every dramatic beat has at least one shot;
- required files exist and contain JSON objects;
- schema and cross-artifact errors identify the file and field involved.

Static scenes may have zero camera moves. Blocking may also contain zero character moves when motivated stillness is selected.

## Command-line interface

The repository exposes three commands:

```bash
python -m cine_skills validate .
python -m cine_skills validate-artifact shot-list path/to/shot-list.json
python -m cine_skills validate-package path/to/scene-package
```

All commands return `0` on success, `1` for validation failures, and `2` for malformed invocation. Validation output is deterministic and actionable.

## Example and evaluation

The Ninel example becomes a canonical scene package under `examples/ninel/scenes/S01/`. The existing aggregate example remains as a convenient readable showcase, while tests prove it matches the split files.

The pipeline skill receives three evaluation scenarios covering dialogue pressure, physical action with geography, and intentional ambiguity. Evaluations describe observable expected behavior rather than exact prose.

## Testing strategy

- Unit tests cover JSON loading, schema selection, validation errors, ID checks, dangling references, and coverage gaps.
- CLI tests invoke the real module entry point and assert exit codes and user-visible diagnostics.
- Catalog tests preserve the exact six-skill boundary and verify OpenAI metadata.
- End-to-end tests validate the complete Ninel package and aggregate equivalence.
- Repository validation checks that every JSON schema is itself a valid Draft 2020-12 schema.

## Release criteria

- `make check` exits `0` in an installed development environment.
- All six skills pass repository validation.
- All five Ninel artifacts pass schema and package validation.
- The CLI succeeds on valid inputs and rejects malformed or inconsistent inputs.
- Documentation shows installation, specialist invocation, package generation, and validation.
- The release archive excludes `.git`, caches, local environments, and build artifacts.


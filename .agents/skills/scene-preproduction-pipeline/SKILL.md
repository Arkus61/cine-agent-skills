---
name: scene-preproduction-pipeline
description: Use when a user provides one scripted scene or scene brief and needs a complete, validated full-v1 preproduction package with coordinated creative and production handoff.
---

# Scene Preproduction Pipeline

Build one canonical thirteen-file `full-v1` package. Run specialist skills in dependency order, preserve stable identifiers, validate the package as a whole, and hand off only a passing result.

## Pipeline

1. Save the supplied scene and context without rewriting them as `source-scene.md`.
2. Use `$scene-beat-analyzer` to create `scene-beats.json`.
3. Use `$scene-director` to create `directing-plan.json`.
4. Use `$visual-language-designer` to create `visual-language-plan.json`.
5. Use `$blocking-designer` to create `blocking-plan.json`.
6. Use `$camera-movement-designer` to create `camera-movement-plan.json`.
7. Use `$shot-list-builder` to create `shot-list.json`.
8. Once shots are stable, use `$lighting-designer` to create `lighting-plan.json`.
9. Use `$sound-designer` to create `sound-plan.json`.
10. Use `$storyboard-designer` to create `storyboard-plan.json`.
11. Use `$production-breakdown` to create `production-breakdown.json` from the source and all selected plans.
12. Use `$continuity-supervisor` to create `continuity-plan.json` from the final shot-level plans.
13. Assemble `package-manifest.json` last. Use release version `1.0.0`, package profile `full-v1`, and the exact eleven-artifact inventory in the contract.
14. Validate the complete package:

```bash
PYTHONPATH=src .venv/bin/python -m cine_skills validate-package projects/<project-slug>/scenes/<scene-id> --profile full-v1 --format json
```

15. If validation fails, repair the earliest invalid artifact in dependency order. Regenerate only its downstream dependants, then rewrite the manifest when any inventoried artifact changed and rerun the same command. Do not regenerate valid upstream artifacts.
16. Hand off only after the command exits successfully and reports `valid: true`.

## Execution rules

- Preserve one non-empty `scene_id` and stable scene-prefixed beat, movement, shot, storyboard-panel, breakdown-item, and continuity-item IDs.
- Treat every source omission as an explicit assumption or uncertainty. Never promote an assumption to fact downstream.
- Resolve all beat and shot references. Cover every beat with a shot and every shot with lighting, sound, storyboard, production-breakdown, and continuity planning.
- A later artifact may refine an earlier decision but must not silently contradict it. Record unresolved conflicts in the handoff.
- Prefer one coherent, shootable primary plan over maximum coverage. Keep alternatives separate.
- The manifest is an inventory and validation claim, not a substitute for validation.
- Do not add generated images, audio, video, budgets, schedules, casting, or vendor-specific service calls to this package.

## Output layout

```text
projects/<project-slug>/scenes/<scene-id>/
├── source-scene.md
├── scene-beats.json
├── directing-plan.json
├── visual-language-plan.json
├── blocking-plan.json
├── camera-movement-plan.json
├── shot-list.json
├── lighting-plan.json
├── sound-plan.json
├── storyboard-plan.json
├── production-breakdown.json
├── continuity-plan.json
└── package-manifest.json
```

## Handoff

Return the package path, profile, exact validation command and result, files repaired during validation, labeled assumptions, and unresolved creative or production conflicts. State that the package is ready for human review, not that it is ready to shoot without departmental approval.

Read [pipeline contract](references/pipeline-contract.md) before execution or repair. Use [the scene package checklist](assets/scene-package-checklist.md) before handoff.

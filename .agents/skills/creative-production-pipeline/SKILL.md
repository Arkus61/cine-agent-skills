---
name: creative-production-pipeline
description: Use when validated story and scene-full scene packages must become an exact mode-selected production package with evidence-based media review and a postproduction handoff.
---

# Creative Production Pipeline

Orchestrate existing specialist contracts into one `production` package. This skill coordinates dependencies and validation; specialists retain their own creative theory, and no step creates or approves unseen media.

## Inputs and preparation

Read the selected project format and exact production modes from the validated story/script package. Before production work, validate the story/script package and every selected `scene-full` scene package. Read [the production pipeline contract](references/production-pipeline-contract.md), then use [the production package checklist](assets/production-package-checklist.md) before handoff.

## Pipeline

The [stage handoff gates](references/production-pipeline-contract.md#stage-handoff-gates) are binding: each selected stage consumes only its listed current inputs, produces its listed handoff, and must pass its listed direct validation gate before the next selected stage uses it. At the first missing or invalid input, stop there with its repair instruction; preserve valid unaffected records. Do not turn a conditional stage into a placeholder.

1. Use `$production-designer` for `production-design-plan.json`, then `$character-look-designer` for `character-look-bible.json` from the current validated upstream inventories.
2. For `animation` or `hybrid`, use `$animation-director` for `animation-plan.json`. Then use `$vfx-planner` for `vfx-plan.json` in every mode.
3. For `ai` or `hybrid`, use `$ai-media-prompt-designer` for `media-prompt-package.json`; do not create that file for the other modes.
4. Use `$media-review-supervisor` for `media-review-report.json`. With no directly inspectable media or measurable metadata, return `awaiting-media`; do not infer approval from prompts, filenames, or claims. `awaiting-media` stops release, while an explicit review blocker stops processing.
5. Assemble `production-manifest.json` from the exact mode-selected inventory, validate its `layer-manifest` schema, and run the hard gate:

```bash
.venv/bin/python -m cine_skills validate-production <project>/production --production-mode <mode> --format json
```

Pass every selected mode as a separate `--production-mode` argument. `ready-for-post` is allowed only after this command exits 0 with `"profile":"production"`, `"valid":true`, and no errors.

Use only validator mode values: a live-action-only inventory uses `--production-mode live-action`; animation-only uses `animation`; AI-only uses `ai`; hybrid uses `hybrid`. The `-only` labels describe exclusive artifact membership, not CLI arguments.

6. On any error, stop at the earliest invalid dependency. Preserve valid unaffected artifacts and their stable IDs; invalidate and regenerate only the transitive downstream closure, rebuild the manifest if its inventory changed, and rerun affected validation. Never replace specialist decisions with generic prose.

## Handoff

Return one status from `awaiting-media`, `blocked`, or `ready-for-post`, with the package path, exact modes and inventory, current commands and outputs, earliest repair or blocker, invalidated closure, preserved records, assumptions, and unresolved questions. `awaiting-media` and `blocked` are non-release states. See the contract for exact membership and ownership.

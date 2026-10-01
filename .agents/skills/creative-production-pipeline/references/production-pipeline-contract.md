# Creative Production Pipeline Contract

## Preconditions and order

The input is a validated story/script package and every selected validated scene-full scene package. First validate upstream story/script and scene packages; do not begin a production specialist while an earlier prerequisite is invalid or absent.

Run the relevant concrete upstream gates before starting production. A nonzero result is the earliest stop: repair that package before opening a production stage.

```bash
PYTHONPATH=src .venv/bin/python -m cine_skills validate-story <project>/story --project-format <format> --format json
PYTHONPATH=src .venv/bin/python -m cine_skills validate-package <project>/scenes/<scene-id> --profile scene-full --root <repository> --format json
```

Run the production nodes in this exact dependency order:

1. `production-design-plan.json` — owner: Production Designer; output: design assets, coverage, and reset context.
2. `character-look-bible.json` — owner: Character Look Designer; output: source-bound character visual continuity.
3. `animation-plan.json` — owner: Animation Director; output: shot performance; selected only for animation or hybrid.
4. `vfx-plan.json` — owner: VFX Planner; output: VFX capture and continuity plan.
5. `media-prompt-package.json` — owner: AI Media Prompt Designer; output: source-bound prompt package; selected only for AI or hybrid.
6. `media-review-report.json` — owner: Media Review Supervisor; output: evidence-based review status.
7. `production-manifest.json` — owner: pipeline; output: exact inventory claim.
8. `validate-production` — owner: production package validator; output: current `production` validation evidence.
9. Handoff — owner: pipeline; output: exactly one allowed status.

## Stage handoff gates

The table is the operational contract. `continue` means the next selected stage may consume the produced artifact only after the named command exits 0 and reports `valid: true`. Every `stop` preserves valid unaffected records and reports the earliest missing or invalid input with its direct repair; it does not create a substitute artifact or continue downstream.

| Stage | Consumes | Produces | Owner | Allowed status / stop condition | Direct validation gate |
| --- | --- | --- | --- | --- | --- |
| Production design | Current validated story/script package; validated scene-full scene packages | `production-design-plan.json` | Production Designer | `continue`; missing or invalid upstream input, or a failing artifact gate: `blocked` and stop | `PYTHONPATH=src .venv/bin/python -m cine_skills validate-artifact production-design-plan <project>/production/production-design-plan.json --root <repository> --format json` |
| Character look | Current validated story/script package; validated scene-full scene packages; current `production-design-plan.json` | `character-look-bible.json` | Character Look Designer | `continue`; missing or invalid required input, or a failing artifact gate: `blocked` and stop | `PYTHONPATH=src .venv/bin/python -m cine_skills validate-artifact character-look-bible <project>/production/character-look-bible.json --root <repository> --format json` |
| Animation | Current `production-design-plan.json`; current `character-look-bible.json`; validated upstream inventories | `animation-plan.json` only for animation or hybrid | Animation Director | `continue` when selected and valid; skip when unselected; missing or invalid selected input, or a failing artifact gate: `blocked` and stop | `PYTHONPATH=src .venv/bin/python -m cine_skills validate-artifact animation-plan <project>/production/animation-plan.json --root <repository> --format json` |
| VFX | Current `production-design-plan.json`; current `character-look-bible.json`; current `animation-plan.json` when selected; validated upstream inventories | `vfx-plan.json` | VFX Planner | `continue`; missing or invalid required input, or a failing artifact gate: `blocked` and stop | `PYTHONPATH=src .venv/bin/python -m cine_skills validate-artifact vfx-plan <project>/production/vfx-plan.json --root <repository> --format json` |
| Prompts | Current `character-look-bible.json`; current `vfx-plan.json`; selected animation plan when present; validated upstream inventories | `media-prompt-package.json` only for AI or hybrid | AI Media Prompt Designer | `continue` when selected and valid; skip when unselected; missing or invalid selected input, or a failing artifact gate: `blocked` and stop | `PYTHONPATH=src .venv/bin/python -m cine_skills validate-artifact media-prompt-package <project>/production/media-prompt-package.json --root <repository> --format json` |
| Review | Exact selected production artifacts, including `media-prompt-package.json` when selected; inspectable media or measurable metadata when supplied | `media-review-report.json` | Media Review Supervisor | `continue` with evidence-complete review; absent inspectable media or measurable metadata: `awaiting-media`, which stops release; an unresolved review blocker or failing artifact gate: `blocked` and stop | `PYTHONPATH=src .venv/bin/python -m cine_skills validate-artifact media-review-report <project>/production/media-review-report.json --root <repository> --format json` |
| Manifest | Exact mode-selected artifacts and their current validation evidence | `production-manifest.json` | Pipeline | `continue`; missing, extra, stale, or invalid selected artifact, or a failing manifest gate: `blocked` and stop | `PYTHONPATH=src .venv/bin/python -m cine_skills validate-artifact layer-manifest <project>/production/production-manifest.json --root <repository> --format json` |
| Validator | Current exact selected production artifacts; `production-manifest.json`; exact selected production modes | `production` validation evidence | Production package validator | `ready-for-post` only on clean validation and no unresolved review blocker; `awaiting-media` stops release; invalid package or unresolved blocker: `blocked` and stop | `PYTHONPATH=src .venv/bin/python -m cine_skills validate-production <project>/production --production-mode <mode> [--production-mode <mode> ...] --root <repository> --format json` |

## Exact production-mode membership

The declared modes are exact project data. Select these files and no extras:

- `live-action-only`: CLI mode `live-action`; `production-design-plan.json`, `character-look-bible.json`, `vfx-plan.json`, `media-review-report.json`, `production-manifest.json`; never create `animation-plan.json` and `media-prompt-package.json`.
- `animation-only`: CLI mode `animation`; `production-design-plan.json`, `character-look-bible.json`, `animation-plan.json`, `vfx-plan.json`, `media-review-report.json`, `production-manifest.json`; never create `media-prompt-package.json`.
- `ai-only`: CLI mode `ai`; `production-design-plan.json`, `character-look-bible.json`, `vfx-plan.json`, `media-prompt-package.json`, `media-review-report.json`, `production-manifest.json`; never create `animation-plan.json`.
- `hybrid`: CLI mode `hybrid`; `production-design-plan.json`, `character-look-bible.json`, `animation-plan.json`, `vfx-plan.json`, `media-prompt-package.json`, `media-review-report.json`, `production-manifest.json`; forbidden extras: none.

`live-action-only`, `animation-only`, and `ai-only` mean their single matching mode. `hybrid` is the one matching hybrid mode; do not substitute a different combination because a file happens to exist.

## Validation, repair, and evidence

Validate upstream before orchestration. On any diagnostic, identify the earliest invalid node in the order above. Stop there, give an actionable repair instruction, and invalidate its transitive downstream closure. Preserve valid unaffected artifacts, independent siblings, stable IDs, supplied facts, and still-current evidence. Regenerate only the affected closure, then refresh its manifest and validation evidence.

Media review is an evidence gate, not a prompt check. Unseen media, inaccessible media, or absent applicable measurement produces `awaiting-media`, never an approval. An unresolved evidence, subjective, rights, or safety decision produces `blocked`. Do not invent inspection, fingerprints, observations, or specialist theory.

Run this hard gate after exact package assembly:

```bash
.venv/bin/python -m cine_skills validate-production <project>/production --production-mode <mode> [--production-mode <mode> ...] --format json
```

Record the exact selected modes, command, exit code, profile, `valid` value, and errors. The only release-ready status is `ready-for-post`, and it requires exit code 0, profile `production`, `valid: true`, no errors, and a media report with no unresolved blocker. A passing specialist, manifest field, earlier command, or file presence cannot replace `validate-production`.

Allowed handoff statuses: `awaiting-media`, `ready-for-post`, `blocked`.

## Boundaries

The pipeline does not generate media, approve unseen output, change specialist semantics, select vendors or software, invoke external services, estimate budget or schedule, make casting/procurement decisions, or make legal, rights, safety, credential, or release decisions.

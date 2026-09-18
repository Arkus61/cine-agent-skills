# Production Package Checklist

## Preconditions and selection

- [ ] The story/script package and every selected scene-full scene package have current passing validation evidence.
- [ ] Project ID, selected modes, upstream IDs, supplied constraints, assumptions, and unresolved questions are carried forward without replacement.
- [ ] The exact mode inventory from the production pipeline contract is selected; absent conditional files are not placeholders.
- [ ] Validator arguments use only `live-action`, `animation`, `ai`, or `hybrid`; an `-only` inventory label is never passed as a CLI mode.

## Specialist order

- [ ] Production design and character look are validated before animation, VFX, prompts, or review use their records.
- [ ] Animation is present only for animation or hybrid; VFX is present for every mode.
- [ ] Media prompts are present only for AI or hybrid.
- [ ] Media review contains only direct inspection or supplied measurable evidence. No media or applicable measurement means `awaiting-media`.

## Repair and handoff

- [ ] An invalid upstream or specialist artifact stopped the pipeline at the earliest invalid dependency.
- [ ] Only the transitive downstream closure was regenerated; valid unaffected artifacts, IDs, facts, and current evidence were preserved.
- [ ] `production-manifest.json` inventories exactly the mode-selected files.
- [ ] The current `validate-production` command ran with every selected `--production-mode` and reports profile `production`, `valid: true`, no errors, and exit code 0.
- [ ] The handoff is exactly `awaiting-media`, `blocked`, or `ready-for-post`.
- [ ] `ready-for-post` is used only after the hard validation gate and a media report with no unresolved blocker.

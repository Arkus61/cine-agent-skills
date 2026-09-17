# Story and Script Package Checklist

## Selection and story layer

- [ ] The creative brief, selected format, production modes, unit scope, and every supplied constraint are recorded with exact source references, separately from assumptions and unresolved questions.
- [ ] `story-concept.json`, `story-structure.json`, `character-arcs.json`, and `world-bible.json` exist in dependency order and pass their artifact contracts.
- [ ] A series includes `season-arc.json` and selects units only from its episode inventory.
- [ ] A non-series package has no `season-arc.json` and uses the canonical `<project>-U01` unit.
- [ ] `story-manifest.json` lists the exact format-selected inventory in dependency order.
- [ ] The literal `validate-story` command exits zero and its current output reports `valid: true` with profile `story-v2`.

## Each script unit

- [ ] `unit-outline.json`, `screenplay.fountain`, `screenplay-metadata.json`, `script-revision-plan.json`, `scenes`, and `script-manifest.json` exist in exact dependency order.
- [ ] The outline belongs to the selected episode or canonical non-series unit and references only valid story IDs.
- [ ] `screenplay.fountain` was inspected; every heading and unique character cue corresponds one-to-one with `screenplay-metadata.json`.
- [ ] The revision plan diagnoses the actual draft, preserves approved constraints, and does not masquerade as an executed rewrite.
- [ ] Every metadata scene has one valid full-v1 package under `scenes/<scene-id>/`.
- [ ] The real script-package validator and full project-index validator both exit zero with no errors.

## Repair and handoff

- [ ] Repair began at the earliest invalid dependency and invalidated only its transitive downstream closure.
- [ ] Valid upstream artifacts and independent siblings were preserved; affected manifests and evidence were refreshed.
- [ ] Validation evidence records exact commands, exit codes, outputs, profile, and errors without invented success.
- [ ] The handoff is exactly `ready-for-preproduction` or `blocked`.
- [ ] `ready-for-preproduction` is used only when every selected package has current passing evidence.
- [ ] `blocked` includes the errors, earliest repair decision, invalidated closure, and unresolved questions.

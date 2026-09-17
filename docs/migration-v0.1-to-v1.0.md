# Migrating a Core v0.1 Package to Full v1

Version 1.0 keeps valid v0.1 packages working unchanged. Migration is optional and additive: it adds six reviewed creative artifacts and one manifest without rewriting the source or the five existing artifacts.

## Before migrating

Validate the existing package explicitly:

```bash
cine-skills validate-package projects/<project>/scenes/<scene-id> --profile core-v0.1 --format json
```

Resolve core validation errors first. Preserve surviving scene, beat, movement, and shot IDs because the new artifacts reference them.

## Add the v1 artifacts

Run specialists in this dependency order:

1. `$visual-language-designer` creates `visual-language-plan.json` after the directing plan.
2. `$lighting-designer` creates `lighting-plan.json` after the shot list is stable.
3. `$sound-designer` creates `sound-plan.json` from the source and stable shots.
4. `$storyboard-designer` creates `storyboard-plan.json` from the stable shot list.
5. `$production-breakdown` creates `production-breakdown.json` from the source and selected plans.
6. `$continuity-supervisor` creates `continuity-plan.json` from the final shot-level plans.

Review every proposal and keep source omissions labeled as assumptions or uncertainties. Migration does not include a command that invents missing creative decisions.

## Create the manifest last

Create `package-manifest.json` with release `1.0.0`, profile `full-v1`, the shared `scene_id`, and the exact eleven-artifact inventory defined by its schema. The source and manifest are control files, so they are not repeated in that creative-artifact inventory.

## Validate and repair

```bash
cine-skills validate-package projects/<project>/scenes/<scene-id> --profile full-v1 --format json
```

On failure, repair the earliest affected artifact in dependency order, regenerate only semantically affected downstream artifacts, and rewrite the manifest when an inventoried file changes. Repeat until the command returns exit status `0` and `valid: true`.

The resulting package is ready for human departmental review. Schema validity does not replace creative, safety, legal, or departmental approval.

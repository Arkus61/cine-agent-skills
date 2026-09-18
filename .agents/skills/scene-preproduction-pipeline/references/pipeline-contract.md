# Scene-Full Pipeline Contract

## Canonical dependency order

Use this order for creation, validation triage, and repair:

```text
source scene
  → scene beats
  → directing plan
  → visual language plan
  → blocking plan
  → camera movement plan
  → shot list
  → lighting plan
  → sound plan
  → storyboard plan
  → production breakdown
  → continuity plan
  → package manifest
```

Lighting, sound, and storyboard planning are independent siblings once the shot list is stable. Their canonical file order remains lighting, sound, then storyboard so generation and validation are deterministic.

## Canonical package

Write exactly these thirteen files in one scene directory:

```text
source-scene.md
scene-beats.json
directing-plan.json
visual-language-plan.json
blocking-plan.json
camera-movement-plan.json
shot-list.json
lighting-plan.json
sound-plan.json
storyboard-plan.json
production-breakdown.json
continuity-plan.json
package-manifest.json
```

The manifest inventory contains exactly these eleven creative artifacts, in this order:

```text
scene-beats.json
directing-plan.json
visual-language-plan.json
blocking-plan.json
camera-movement-plan.json
shot-list.json
lighting-plan.json
sound-plan.json
storyboard-plan.json
production-breakdown.json
continuity-plan.json
```

The source scene and manifest are package control files and therefore are not repeated in the creative-artifact inventory.

## Validation gate

Run:

```bash
PYTHONPATH=src .venv/bin/python -m cine_skills validate-package <package-dir> --profile scene-full --format json
```

The validator checks exact package membership, all twelve JSON schemas, one shared `scene_id`, identifier contracts, resolved beat and shot references, full coverage, and the manifest contract. A package is handoff-ready only when the command exits zero and returns `valid: true`.

Keep `source-scene.md` as the supplied scene and context, not a rewritten screenplay. Treat schema success as a minimum contract; humans still approve creative and departmental decisions.

## Earliest-failure repair

When validation returns more than one error:

1. identify the earliest affected artifact in canonical dependency order;
2. fix its schema, references, or creative contradiction;
3. regenerate only semantically affected downstream artifacts;
4. preserve valid upstream artifacts and surviving identifiers;
5. regenerate the manifest if any inventoried file changed;
6. rerun the complete `scene-full` validation command.

Repeat until it passes. A formatting-only schema repair does not trigger creative regeneration unless it changes meaning or a reference.

## Invalidation map

- Source change: regenerate every JSON artifact.
- Beat change: regenerate directing and everything downstream.
- Directing change: regenerate visual language and everything downstream.
- Visual-language change: regenerate blocking and everything downstream.
- Blocking change: regenerate camera movement and everything downstream.
- Camera-movement change: regenerate affected shots and all shot-dependent artifacts.
- Shot-list change: regenerate lighting, sound, storyboard, production breakdown, continuity, and manifest.
- Lighting, sound, or storyboard change: regenerate affected production-breakdown and continuity entries, then the manifest.
- Production-breakdown change: regenerate affected continuity entries and the manifest.
- Continuity change: regenerate only the manifest.
- Manifest-only change: regenerate no creative artifact.

## Stable identifiers

Never renumber surviving items because another item was removed. Assign the next unused ID to new items. This keeps review notes and cross-artifact references durable.

## Conflict and handoff report

For each unresolved conflict state the earlier decision, later contradiction, production impact, recommended resolution, and affected files. The final handoff states:

- package path and `scene-full` profile;
- exact validation command, exit result, and `valid` result;
- repairs and regenerated downstream files;
- assumptions and uncertainties still requiring confirmation;
- unresolved conflicts;
- readiness for human departmental review.

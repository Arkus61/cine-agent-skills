# Color Grading Designer forward-application report

## Scope and method

This trial applied only the current Color Grading Designer skill, its three references and template, the supplied `schemas/color-plan.schema.json`, and the public validation command. No media was available or inspected, no image operations were performed, and no inspection, measurement, match, or approval evidence was fabricated.

Artifacts:

- Final DAY plan: `docs/color-forward-daylight.json`
- Preserved first DAY output: `docs/color-forward-daylight-first.json`
- Final INK plan: `docs/color-forward-animation.json`
- Preserved first INK output: `docs/color-forward-animation-first.json`

## Scenario 1 — DAY daylight sequence

The plan registers both exact segment IDs and supplied edit-plan references. It treats the producer's `Log` filename claim as a lead only: input encoding remains `unknown`, with no metadata records, source versions, or evidence invented. A scene-referred wide-gamut working environment is proposed but deliberately does not imply an input transform or output display.

The two segments receive distinct treatments rather than a mechanical match. The exterior wide favors restrained golden warmth, open shadows, natural skin, and retained sky/foliage/neutral separation. The shaded close-up keeps the face as the continuity anchor while retaining motivated cool shade; facial shadows, complexion variation, and eye/hair/wardrobe identity are protected. The story arc moves from expansive sunlit warmth into intimate shade without turning the lighting-zone change into an accidental color jump.

Because there is no media, graded output, display specification, or inspection record, both match states are `awaiting-media`. The requested same-day approvals are `pending`, with empty evidence arrays: nothing is represented as matched or approved. Display-specific trims remain conditional, and no display target is invented.

## Scenario 2 — INK animation/VFX sequence

The plan registers both exact edit segment IDs, both supplied edit-plan references, and VFX item `INK-U01-FX001` with its supplied VFX-plan reference. ACEScg is recorded only as a `proposed` working space. Input encodings stay `unknown`; VFX render space, range, premultiplication, configuration version, and exact source/render versions must be obtained independently before normalization.

The first segment establishes restrained cool-cyan industrial ambience with dimensional metal and shadow texture. The doorway reveal introduces controlled amber-gold warmth while retaining cool industrial shadows. Cyan eyes and silver-white hair are explicit recognition anchors across both items: planned selective work protects cyan hue/readability and hair neutrality/detail without erasing motivated environmental reflections or warm edge light.

`INK-U01-FX001` is linked to the industrial-interior color item. Its handoff calls for edge, matte contamination, black-level, grain/noise, metallic/hair highlight, cyan-eye, gamut, and temporal-stability review on an exact graded output.

P3-D65 ST 2084 is included only as a `proposed` HDR planning target. The target explicitly leaves mastering-display capabilities and surround undeclared. Both items are `awaiting-media`, approvals are `pending`, evidence is empty, and the requested “approved HDR match” is not accepted as fact. HDR trims and certification remain gated on verified transforms, a declared mastering path, exact-output sequence inspection, and matching human approval evidence.

## First validation and repair record

Both initial JSON outputs were preserved byte-for-byte before repair. The commands used were:

```text
PYTHONPATH=src .venv/bin/python -m cine_skills validate-artifact color-plan docs/color-forward-daylight.json --root . --format json
PYTHONPATH=src .venv/bin/python -m cine_skills validate-artifact color-plan docs/color-forward-animation.json --root . --format json
```

DAY first validation exit code: `1`

Exact output:

```json
{"command": "validate-artifact", "errors": ["color_management.working_space: Additional properties are not allowed ('metadata_record_ids' was unexpected)", "items.0.observed_input: 'source_version_id' is a required property", "items.1.observed_input: 'source_version_id' is a required property"], "valid": false}
```

INK first validation exit code: `1`

Exact output:

```json
{"command": "validate-artifact", "errors": ["color_management.working_space: Additional properties are not allowed ('metadata_record_ids' was unexpected)", "items.0.observed_input: 'source_version_id' is a required property", "items.1.observed_input: 'source_version_id' is a required property"], "valid": false}
```

The minimal repair removed `metadata_record_ids` from `color_management.working_space` and added `source_version_id: null` to every uninspected `observed_input`. No creative claims, evidence states, approval states, or source assertions were changed.

The chronology matters: the schema and template read for the initial draft still showed the earlier working-space/observation shapes, but the controller applied the source-inspection and working-space contract correction during this run, after the initial stable signal and before validation. The first validation failures therefore record a real mid-run contract transition; they do **not** demonstrate a persistent schema/CLI mismatch. The preserved first artifacts and exact failures above remain part of the trial evidence.

After the controller correction, the current sources agree with the CLI and with the repaired plans. The template now gives `working_space` only `value` and `state`, and supplies `observed_input.source_version_id: null`. The schema now routes `color_management.working_space` through a dedicated `workingSpace` definition requiring only `value` and `state`, while `observation` requires nullable `source_version_id`. The final artifacts follow this corrected, consistently expressed contract.

## Final validation

DAY repaired validation exit code: `0`

Exact output:

```json
{"command": "validate-artifact", "errors": [], "valid": true}
```

INK repaired validation exit code: `0`

Exact output:

```json
{"command": "validate-artifact", "errors": [], "valid": true}
```

The final plans are structurally valid according to the requested CLI and remain intentionally provisional wherever media, metadata, display definition, inspection, or human approval is absent.

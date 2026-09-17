---
name: color-grading-designer
description: Use when an edit plan needs a validated, source-aware color-plan.json covering color management, matching, look, VFX handoff, display intent, trims, and review.
---

# Color Grading Designer

Create `color-plan.json`; do not grade, render, encode, upload, deliver, inspect unavailable media, or approve on another person's behalf.

1. Copy the exact project and unit IDs. Register edit segments as `<UNIT>-ED###`, optional VFX post items as `<UNIT>-FX###`, media as `<PROJECT>-MD###`, versions as `<MEDIA>-v###`, metadata as `<PROJECT>-CM###`, evidence as `<PROJECT>-CE###`, display targets as `<PROJECT>-DT###`, and color items as `<UNIT>-CL###`. Numbers start at 001; `###` means at least three digits. Every populated reference must resolve, including in planned or provisional states.
2. Keep observed input separate from desired look. Uninspected input has no findings; each inspected finding equals the value in inspection evidence bound to its exact source version, item, and complete segment set. A filename, plausible path, verbal label, or requested working space does not establish source encoding. A `declared` input encoding needs applicable metadata for every linked source-version/segment pair, bound to the `input-encoding` field and declared value. Otherwise use `unknown` or `proposed`. Read [color-management assumptions](references/color-management-assumptions.md).
3. Give every item substantive decisions for normalization prerequisites, balance and shot matching, exposure and contrast, palette, protected colors, selective treatment, and VFX handoff. Preserve motivated differences rather than forcing mechanical uniformity. Read [shot matching and look](references/shot-matching-look.md).
4. State the unit's emotional color progression and connect local choices to it. Protect recognition-critical skin, costume, product, or character colors. Read [color story arc](references/color-story-arc.md).
5. Distinguish input encoding, working-space assumption, and output/display intent. Keep working space `unknown` or `proposed`; this contract does not certify it from metadata. Select only a constrained display standard; record its viewing environment and whether the target is proposed or declared. Record actual display review as exact evidence on the color item, not as an unsupported target state. Keep trims conditional until the destination and review evidence support them.
6. Bind inspection and approval evidence to the exact color item, complete segment set, graded output version, claim, and claimed value. `approved` matching requires current-output inspection. Approval additionally requires human approval whose value matches the inspection claim. A source reference is provenance, not independent proof that evidence is authentic; cross-artifact authenticity remains a later integration responsibility.
7. Validate against `schemas/color-plan.schema.json`. With no media, keep encodings unknown, matching planned or awaiting media, evidence empty, approval not requested or pending, and still provide useful creative and review plans.

Record assumptions and uncertainties explicitly. Do not invent measurements, timing, transform settings, inspection, approval, or QC.

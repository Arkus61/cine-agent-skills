---
name: visual-language-designer
description: Use when a scripted scene, directing plan, or beat sheet needs a coherent aspect ratio, point of view, palette, contrast, texture, lens, composition, camera-height, motif, and exception system before blocking, shot listing, lighting, or storyboarding.
---

# Visual Language Designer

Define a repeatable visual grammar, not a list of attractive images. Make every rule traceable to a dramatic beat and state what the production should avoid.

## Inputs

Use the source scene, `scene-beats.json`, `directing-plan.json`, known format or delivery constraints, available locations, and confirmed camera limits. Label every missing production fact as an assumption.

## Workflow

1. State the scene point of view and the viewer information boundary.
2. Select an aspect ratio only when it supports subject relationships, geography, or delivery needs.
3. Define one coherent strategy for palette, contrast, texture, and lens behavior.
4. Translate the strategy into stable `<scene>-V##` rules. Give every rule non-empty beat references, composition, camera height, and dramatic purpose.
5. Define motifs that may recur, default choices to reject, and the exact dramatic condition that permits each exception.
6. Check that the rules can coexist with blocking, lighting, camera movement, coverage, and continuity.
7. Produce JSON conforming to `schemas/visual-language-plan.schema.json`.

## Output contract

| Layer | Required decision |
|---|---|
| Frame | Aspect ratio and point-of-view boundary |
| Look | Palette, contrast, and texture |
| Optics | Lens strategy, stated as behavior rather than unsupported equipment fact |
| Grammar | Stable rules with beat IDs, composition, height, and purpose |
| Control | Motifs, prohibited defaults, motivated exceptions, and assumptions |

## Quality gate

- Preserve ambiguity when the script does not settle reality.
- Treat low/high angles, symmetry, negative space, focal length, and movement as choices with consequences, not emotional shortcuts.
- Keep physical camera movement in `camera-movement-plan.json`; describe here only the visual rule that constrains it.
- Do not prescribe unavailable equipment as fact.
- Do not add lighting setups, shot coverage, storyboard panels, or generation prompts to this artifact.

Read [visual language](references/visual-language.md) when selecting frame, angle, composition, lens behavior, or exceptions. Copy [the complete template](assets/visual-language-plan.template.json) for the output shape.

---
name: storyboard-designer
description: Use when a source scene and stable shot list need a textual, drawable storyboard plan with one or more ordered panels per shot, explicit frame layers, subject placement, action direction, movement, lighting, audio, continuity, and dramatic purpose.
---

# Storyboard Designer

Translate approved shot decisions into panels another artist or department can draw and review. This skill creates structured text only; it does not generate, embed, or link images.

## Inputs

Use the source scene, beats, directing plan, visual-language plan, blocking, camera movement, shot list, lighting plan, sound plan, confirmed art/wardrobe facts, and delivery aspect ratio. Record missing facts as assumptions.

## Workflow

1. State one storyboard intent that explains what the board must make clear.
2. Follow shot-list order. Create at least one stable `<scene>-SB###` panel for every supplied shot.
3. Add a second panel only when a single drawing cannot communicate a meaningful action, camera, reveal, or end-state transition.
4. For each panel select the precise moment and inherit framing, camera height, angle, and movement from approved upstream artifacts.
5. Describe foreground, midground, background, subject placement, action direction, and movement state so the panel is drawable without a reference image.
6. Add the lighting state, relevant audio cue, continuity note, and dramatic purpose.
7. Produce JSON conforming to `schemas/storyboard-plan.schema.json`.

## Panel test

A useful panel answers all of these:

- What exact moment is frozen?
- What occupies each depth layer?
- Where is the subject in the frame?
- What direction does action travel?
- What is moving, what is still, and what comes next?
- Which light, sound, and continuity state must match?
- Why does this panel exist?

## Quality gate

- Do not invent aspect ratio, lens, duration, timecode, safe area, production design, VFX method, or performance detail that upstream artifacts do not confirm.
- Do not redesign the shot list. If a conflict makes a shot unboardable, record the conflict as an assumption and preserve the shot reference.
- Do not add `image_url`, base64, generation prompts, binary assets, or external image dependencies.
- Preserve point of view and ambiguity. A board must not objectively show information the directing or visual plan withholds.
- Make directional language relative to the frame or established screen direction, not an invented stage coordinate system.

Read [textual storyboards](references/textual-storyboards.md) for panel selection, composition, action, and continuity reasoning. Copy [the complete template](assets/storyboard-plan.template.json) for output.

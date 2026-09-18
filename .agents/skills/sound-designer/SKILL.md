---
name: sound-designer
description: Use when a scene with stable beats and shot IDs needs a production-sound plan that connects dialogue, effects, ambience, silence, transitions, and music intent to timing, listening perspective, capture requirements, and dramatic purpose.
---

# Sound Designer

Turn the scene's listening point of view into concise, traceable production requirements. Plan what must be heard and protected without inventing an unconfirmed equipment package or extending into postproduction delivery.

## Inputs

Use the source scene, beats, directing plan, visual rules, blocking, camera movement, shot list, confirmed location acoustics, performer constraints, practical effects, and production limits. Record missing facts as assumptions.

## Workflow

1. State one sound philosophy: whose listening perspective leads, what changes, and where restraint or silence matters.
2. Inventory story sources before adding designed sound. Separate dialogue, effects, ambience, silence, transitions, and optional music intent.
3. Create stable `<scene>-A##` cues. Give every cue non-empty beat and shot references.
4. For every cue record source, perspective, timing, production requirement, and dramatic purpose.
5. Cover every supplied shot and preserve clean dialogue, room tone, practical states, wild elements, and repeatable timing where the scene needs them.
6. Flag noise, wardrobe, reflections, camera movement, playback, performer comfort, access, and location-acoustic questions as assumptions or survey needs.
7. Produce JSON conforming to `schemas/sound-plan.schema.json`.

## Cue reasoning

| Question | Record |
|---|---|
| What is heard? | Category and source |
| From whose position? | Perspective |
| When does it change? | Timing |
| What must production protect or capture? | Requirement |
| Why does it matter? | Dramatic purpose |

## Quality gate

- Do not use a sting, pulse, or voice treatment to prove an event the scene keeps ambiguous.
- Do not prescribe microphone models, recorder settings, frequencies, decibels, channel layouts, loudness targets, licensed recordings, or final delivery formats unless the production confirms them.
- For music, describe only dramatic function, entry/exit behavior, texture, or the choice to use no music. Never select a copyrighted track.
- Keep the artifact within scene preproduction. Do not create an editorial, mixing, mastering, or delivery workflow.
- Keep performer-mounted capture, playback, hearing levels, cabling, practical noise, and access subject to performer consent and qualified sound/safety review.

Read [production sound](references/production-sound.md) for perspective, capture, continuity, and safety reasoning. Copy [the complete template](assets/sound-plan.template.json) for output.

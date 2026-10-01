---
name: sound-post-designer
description: Use when a source-bound edit plan must become a validated sound-post-plan.json covering dialogue, design, mix, accessibility, and delivery assumptions.
---

# Sound Post Designer

Create `sound-post-plan.json`; do not record, edit, repair, mix, master, measure, approve, or deliver audio. Never invent production audio, takes, sync, defects, ADR need, Foley performances, measurements, delivery specifications, approval, or compliance.

## Ground the handoff

1. Copy one project and exact `<PROJECT>-U##` or `<PROJECT>-E##` unit from the edit plan. Register every declared `<UNIT>-ED###` once and bind each sound-post item only to that register. Register supplied inspection evidence as `<PROJECT>-IN###` with a source reference and kind before any item is `inspected`.
2. Give every item a unique positive `<UNIT>-PS###` ID, responsibility, dramatic purpose, structured listener perspective, state, and conditional instruction. Perspective is `{ "mode", "intent" }`: choose one of `objective`, `subjective`, `spatial-focus`, `dialogue-focus`, `accessibility`, or `not-applicable-from-supplied-material`, then state a real intent rather than a placeholder. Cover every declared edit segment exactly through the item bindings.
3. Create typed ownership for dialogue edit, repair, ADR, Foley, ambience, effects, sound design, transition, intentional silence, premix, automation, mix priority, accessibility, loudness assumption, and mastering. A dialogue-free unit still records the dialogue/ADR decision as conditional or not applicable from supplied material; it does not invent a voice track.
4. Put observed measurement values and units only in `numeric_measurements`. Copy category, metric, value, and unit exactly from a supplied `measurement_evidence` record; do not reuse an ID for another metric. A provisional numeric target may appear only in `delivery_assumption` on `loudness-assumption`; it remains a declared assumption until the distributor specification and final measurement are supplied.

## Plan the work

1. Use [dialogue, ADR, and Foley](references/dialogue-adr-foley.md) to preserve dialogue intelligibility, identify repair or ADR only after source review, and make Foley performance serve action and perspective.
2. Use [sound edit, design, and mix](references/sound-edit-design-mix.md) to establish room tone, ambience, effects, subjective perspective, transitions, silence, premix ownership, dynamics, and automation without masking story-critical speech.
3. Use [delivery assumptions](references/sound-delivery-assumptions.md) to state accessibility handoffs, a provisional delivery target, required supplied inputs, and mastering checks. Do not call an unmeasured plan compliant.

## Validate and hand off

Validate against `schemas/sound-post-plan.schema.json`. Keep source inputs, measurements, decisions, and delivery requirements explicit. Do not hide completed measurement, approval, compliance, master, or delivery claims in prose; use negative or conditional language for unresolved work. `planned` and `awaiting-input` cannot bind inspection evidence or imply review. `inspected` requires named, responsibility-applicable supplied evidence and never means that a mix, master, approval, or delivery specification exists.

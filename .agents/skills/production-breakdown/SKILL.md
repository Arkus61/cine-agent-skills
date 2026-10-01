---
name: production-breakdown
description: Use when an approved scene package needs a traceable department-by-department inventory of cast, set, props, wardrobe, hair/makeup, camera/grip, lighting, sound, practical effects, visual effects, art, safety, and open-question requirements before scheduling or budgeting.
---

# Production Breakdown

Convert approved scene facts into department requirements that production can review. Keep every item tied to evidence, beats or shots, a reset instruction, explicit assumptions, and a qualitative risk.

## Inputs

Use the source scene and every approved scene artifact available. Prefer the most specific source: shot requirements over inference, and source text over convention. Treat conflicts and omissions as open questions.

## Workflow

1. State the breakdown scope. Do not widen it into a project schedule, budget, or vendor plan.
2. Walk the source scene, beats, blocking, shot list, lighting, sound, storyboard, and continuity facts in order.
3. Create stable `<scene>-PD###` items. Choose one normalized category per item.
4. Record the exact source basis in original paraphrase, then link all relevant beat and shot IDs. Every item needs at least one of those references.
5. Describe the observable requirement rather than a shopping solution.
6. State how its action/state must reset or be documented between takes.
7. Separate unconfirmed implementation from the requirement in item assumptions.
8. Assign `low`, `medium`, or `high` risk based on story loss, safety, repeatability, interdepartment dependency, or irreversible reset.
9. Produce JSON conforming to `schemas/production-breakdown.schema.json`.

## Category routing

Use exactly one of: `cast`, `location-set`, `props`, `wardrobe`, `hair-makeup`, `camera-grip`, `lighting`, `sound`, `practical-effects`, `visual-effects`, `art`, `safety`, `open-question`.

When multiple departments share one requirement, route it to the department that owns the physical or recorded result and name collaborating departments in the requirement. Split the item only when the teams have independently resettable deliverables.

## Quality gate

- Do not invent an object, costume, effect, crew role, location feature, or technical method merely because it is common on films.
- Do not include cost, price, quantity pricing, vendor, booking, hire duration, shoot date, call time, or schedule fields.
- Do not treat risk level as a safety approval. Hazardous work requires qualified department review and the production's formal risk process.
- Keep `source_basis` concrete enough that a reviewer can find the fact or inference in the supplied scene package.
- Use `open-question` for a real decision that blocks a department requirement; do not hide unknowns inside confident prose.

Read [department breakdown](references/department-breakdown.md) for traceability, ownership, reset, and risk reasoning. Copy [the complete template](assets/production-breakdown.template.json) for output.

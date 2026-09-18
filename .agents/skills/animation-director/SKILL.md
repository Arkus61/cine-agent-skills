---
name: animation-director
description: Use when animated or hybrid character shots need traceable acting beats, poses, staging, timing, motion, facial or lip-sync applicability, simulation assumptions, continuity, camera coordination, and review criteria derived from supplied directing, scene, character, and shot materials.
---

# Animation Director

Turn supplied shot and performance intent into a reviewable animation-plan.json. Preserve intent and identity while making pose, timing, motion, and continuity decisions explicit.

## Inputs

Consume available directing, scene, shot-list, character-look, production-design, and continuity material. Copy exact project, character, scene, shot, duration, timebase, camera-intent, and performance-intent records into source_context. Inventory each value and source-reference pair that a downstream decision will repeat as supplied, scoped either to the shot or to one character in that shot.

## Required preparation

Read both references before drafting:

- [Animation performance](references/animation-performance.md) for acting beats, readable poses, staging, face and mouth applicability, camera coordination, and review.
- [Animation timing and motion](references/animation-timing-motion.md) for timing, spacing, arcs, weight, anticipation, overlap, holds, simulation assumptions, and stylization.

Copy [the strict JSON template](assets/animation-plan.template.json) and preserve its field names.

## Workflow

1. Bind every supplied shot to its exact scene, duration, timing basis, camera intent, applicable character IDs, directing-performance intent, and scoped `supplied_facts` ledger. Use shot scope only for the camera relationship; use shot-character scope for performance, action, pose, expression, lip-sync, and continuity claims.
2. Create exactly one shot-character plan for every applicable character in every supplied shot. Multiple characters in one shot receive separate plans.
3. Give every plan and nested beat, pose, hold, simulation, and continuity record a unique positive project-derived ID.
4. Divide the full shot into ordered, non-overlapping, nonempty acting beats. Require `start < end` for every beat and hold, keep all numeric timing nonnegative and inside the supplied duration, and retain key poses as instants.
5. Define readable key poses and purposeful holds inside their owning beat. State staging, timing, spacing, arcs, weight, anticipation, follow-through, overlap, and camera relationship.
6. Declare facial performance and lip-sync as specified, none, or not-applicable according to the subject and supplied dialogue. Do not force human anatomy onto a nonhuman subject.
7. Separate physically credible behavior from intentional stylization. Give each consequential choice supplied, inferred, proposed, or approved provenance with purpose, basis, and source reference.
8. Keep every unconfirmed simulation method an assumption or uncertainty. Never mark an unconfirmed method confirmed or approved.
9. Link ordered continuity states and write observable acceptance criteria that preserve supplied performance intent.
10. Validate against schemas/animation-plan.schema.json and repair graph, timing, lineage, source-binding, ownership, and certainty errors.

## Boundaries

- Do not prescribe software, vendors, model parameters, rigs, solvers, render settings, or DCC/NLE operations.
- Do not emit or embed media, URLs, base64, secrets, or credentials.
- Do not make budget, schedule, casting, procurement, legal, medical, engineering, or safety decisions.
- Do not invent dialogue, anatomy, mechanics, duration, performance approval, or simulation certainty.

## Quality gate

- Every supplied shot-character pair is covered once with exact lineage and source intent.
- Every downstream claim marked supplied exactly matches one applicable `supplied_facts` value and source-reference pair; never reuse a shot fact across shots or a character fact across characters.
- Beats, poses, holds, and continuity links resolve to the same owning plan and character.
- Timing is explicit, ordered, nonnegative, nonempty for beats and holds, and bounded by the supplied duration.
- Pose readability, staging, motion principles, subject-appropriate face/lip handling, camera relationship, continuity, and acceptance criteria are observable.
- Physical realism and intentional stylization are distinguished without making either universally preferable.
- Missing facts remain assumptions or uncertainties.

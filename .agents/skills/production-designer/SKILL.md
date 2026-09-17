---
name: production-designer
description: Use when story, screenplay, world, visual-language, shot-list, or continuity material needs a production design plan for environments, sets, props, materials, graphics, palette, scale, wear, cultural logic, motifs, shot coverage, practical-digital assumptions, and reset continuity before production or media planning.
---

# Production Designer

Turn dramatic function into a bounded, traceable design system. Design only what the story and supplied coverage need; do not make an unconfirmed fabrication or digital method sound decided.

## Inputs

Consume available story concept, structure, screenplay metadata, world bible, visual-language plans, shot lists, and continuity plans. Preserve exact project, world, scene, and shot IDs. Copy the supplied world, scene, and shot inventories into required `source_context`; do not fabricate missing IDs. Each shot ID keeps its supplied scene prefix so lineage can be checked.

## Required preparation

Read both references before drafting:

- [Production design language](references/production-design-language.md) for story function, environments, form, material, palette, scale, wear, graphics, cultural logic, and motifs.
- [Environment and prop continuity](references/environment-prop-continuity.md) for causal assets, scene/shot coverage, provenance, state changes, resets, and department handoffs.

Copy [the strict JSON template](assets/production-design-plan.template.json) and preserve its field names.

## Workflow

1. Build a source ledger. Separate supplied, inferred, proposed, and approved decisions. Record identity provenance on every asset. Separately record purpose and provenance inside every asset's `design` block for its new form, material, graphic, palette, scale, wear, cultural, and motif decisions. A supplied object does not make its proposed treatment supplied.
2. State the story function before choosing a look. Describe the action, knowledge, relationship, tension, or scale change the environment must make visible.
3. Define one economical design system: shape language, material behavior, palette roles, scale, wear, cultural logic, graphics, and recurring motifs. Do not add detail that has no dramatic or spatial job.
4. Declare only production-relevant environments, sets, props, materials, and graphics. Give every asset one unique exact positive `<project>-AS###` ID, identity purpose and provenance, upstream references, and a complete design block with its own non-empty purpose and provenance.
5. Treat every practical, digital, hybrid, or undetermined implementation as an `assumption`. State the rationale and departments that must test or decide it. A creative plan does not prove a build, playback, extension, or VFX method.
6. Create one coverage entry for every supplied shot. Use the scene that owns that supplied shot. Make asset-shot links exact in both views: every `asset.shot_ids` declaration appears in that shot's coverage, and every coverage asset declares that shot. State why the minimum asset set matters; do not hide an uncovered shot behind scene-level prose.
7. Create asset-linked continuity states for every object or surface that opens, breaks, empties, fills, moves, changes graphics, accumulates wear, or must match. Record entry state, exit state, reset target, reset actions, shot IDs, and purpose.
8. Record cross-department dependencies with affected asset, scene, and shot IDs. Use `confirmed`, `assumption`, or `unresolved`; never convert another department's open decision into fact.
9. Put missing dimensions, materials, methods, approvals, references, and upstream decisions in `assumptions` or `uncertainties`. Remove decorative inventions that exist only to make the plan feel complete.
10. Produce only `production-design-plan.json`. Validate against `schemas/production-design-plan.schema.json`, then repair duplicate IDs, cross-project IDs, dangling references, missing coverage, and undeclared fields.

## Decision gate

| Decision | Required evidence |
|---|---|
| Keep an element | It changes action, knowledge, relationship, tension, orientation, or continuity. |
| Assign an asset ID | A department must design, represent, test, track, or reset it. |
| Claim a material or finish | Supplied/approved evidence, or explicit proposed provenance. |
| Select practical or digital | Always an assumption pending the relevant test or approval. |
| Add cultural detail | Bounded evidence and a material or social function; never aesthetic stereotyping. |
| Repeat a motif | Each recurrence has a changed dramatic job. |

## Boundaries

- Do not name vendors, suppliers, products, facilities, or procurement actions.
- Do not estimate cost, labor, quantities, schedule, build duration, or budget.
- Do not make legal, rights, clearance, engineering, rigging, or safety approvals.
- Do not generate or embed images, video, audio, models, plates, or other media.
- Do not invent architecture, cultural history, branding, deterioration, technology, or fabrication detail as fact.
- Do not duplicate lighting, camera, VFX, costume, sound, or animation plans; state the design dependency and its purpose.

## Quality gate

- The visual concept begins with story function and remains legible without style adjectives.
- Every asset identity and every design treatment has its own purpose and provenance; neither record stands in for the other.
- Asset IDs are exact, positive, unique, project-derived, and stable.
- Environment, set, prop, material, graphic, palette, scale, wear, cultural logic, and motif decisions are present where relevant and intentionally absent where irrelevant.
- Every supplied world, scene, shot, and asset reference resolves; every supplied shot has explicit coverage in its supplied scene; asset-shot declarations and coverage links match exactly.
- Practical/digital language is labelled as assumption, including apparently obvious build choices.
- State-changing assets have usable reset continuity.
- Assumptions and uncertainties expose missing facts instead of concealing them with detail.

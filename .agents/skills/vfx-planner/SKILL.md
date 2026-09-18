---
name: vfx-planner
description: Use when planning shot-level visual effects, invisible cleanup, practical/digital integration, capture or authored elements, simulations, or explicit no-VFX applicability from supplied scene and shot materials.
---

# VFX Planner

Create a source-bound `vfx-plan.json` that makes each effect reviewable before capture or animation. Describe required evidence and visible results without selecting a vendor, software, production resource, or operational method.

## Establish source truth

Consume available source scenes, shot lists, visual-language, camera-movement, lighting, directing-performance, production-design, character-look, animation, and continuity records. Stop when project, scene, or shot lineage is absent or contradictory.

Copy every supplied scene into `source_context.scenes` with its exact `scene_id` and `source_reference`, then copy every supplied shot into `source_context.shots`. Scene and shot IDs must belong to the declared project, and every shot ID must encode its declared scene as `<SCENE>-SH###`. For each shot, record exact visual, camera, lens, lighting, and performance `(category, value, source_reference)` facts. Scope that ledger to the shot: a fact from one shot cannot authorize a supplied claim in another.

For every effect shot, include exactly one camera, lens, and lighting metadata claim. A `supplied` claim repeats the full source triple exactly. An `approved` claim names an `approval_id` and exactly matches its structured root-level `approval_evidence` record. Keep inferred, proposed, and approved decisions distinct; planning never upgrades an assumption or uncertainty to approval.

## Approval evidence shapes

Put approval records only in root `approval_evidence`. The record type is exact:

```json
{
  "approval_id": "ORBIT-APR001",
  "kind": "metadata",
  "effect_id": "ORBIT-FX001",
  "shot_id": "ORBIT-S01-SH001",
  "category": "camera",
  "value": "The supplied camera makes a slow push.",
  "source_reference": "SRC-APPROVED-CAMERA"
}
```

```json
{
  "approval_id": "ORBIT-APR002",
  "kind": "simulation",
  "effect_id": "ORBIT-FX001",
  "shot_ids": ["ORBIT-S01-SH001"],
  "requirements": ["Preserve the approved energy flow and dissipation."],
  "source_reference": "SRC-APPROVED-SIMULATION"
}
```

```json
{
  "approval_id": "ORBIT-APR003",
  "kind": "practical-digital-boundary",
  "effect_id": "ORBIT-FX001",
  "shot_ids": ["ORBIT-S01-SH001"],
  "practical_scope": "Use only the approved interactive light.",
  "digital_scope": "Render the map volume digitally.",
  "source_reference": "SRC-APPROVED-BOUNDARY"
}
```

For a confirmed simulation, copy the evidence `requirements` array exactly into
`simulation.requirements`. For a confirmed boundary, copy both approved scope
strings exactly into `practical_digital_boundary`.

When the supplied source itself establishes an all-authored or no-practical
boundary, use root `supplied_boundary_evidence` instead of `approval_evidence`:

```json
{
  "supplied_evidence_id": "ORBIT-SBE001",
  "effect_id": "ORBIT-FX001",
  "shot_ids": ["ORBIT-S01-SH001"],
  "practical_scope": "No photographed practical element applies.",
  "digital_scope": "The energy effect is fully animated.",
  "source_reference": "SRC-S01"
}
```

`source_reference` must already appear in `source_context.scenes` or a supplied
shot fact. Copy the evidence ID into
`practical_digital_boundary.supplied_evidence_id` with `uncertainty_id: null`.
A confirmed boundary uses exactly one path: this supplied evidence or approved
boundary evidence, never both. Use neither path for an unresolved boundary.

## Build the plan

Copy [the strict template](assets/vfx-plan.template.json) and preserve its fields. Read [VFX preproduction](references/vfx-preproduction.md) before decomposing effects and [capture elements](references/vfx-capture-elements.md) before specifying plates, tracking, metadata, references, interaction, or simulation.

1. Classify every supplied shot exactly once as `effect` or `no-vfx`. A no-VFX shot has no effect IDs. An effect-classified shot has at least one inverse-linked effect.
2. Give every effect one exact positive `<PROJECT>-FX###` ID, applicable shot IDs, distinct dramatic and visual purposes, and an observable component decomposition.
3. Record practical/digital boundary status and scope. Link every unresolved boundary to a project-owned uncertainty; never mark an untested boundary confirmed. A `confirmed` simulation names exact structured `approval_evidence`; a confirmed boundary names either exact approved boundary evidence or exact supplied boundary evidence, never both. Each record binds its complete shot set, source reference, and identical approved or supplied scopes/requirements.
4. Make structured decisions for clean plates and tracking. Record shot-scoped camera, lens, and lighting metadata; mattes or holdouts; reference capture; practical interaction; capture or authored generation elements; and integration assumptions.
5. State simulation status and visible requirements. An unresolved simulation links to an uncertainty; `not-required` carries no requirements. Do not force photographic capture or plates onto a fully animated effect.
6. Add continuity states, dependency owners, a qualified human-safety review handoff, and observable acceptance criteria. When `human_safety_handoff.required` is true, its review explicitly states qualified human review and never guarantees outcomes, calls a method risk-free, or waives specialist review.
7. Put missing methods, capture choices, source facts, and approvals in structured uncertainties with exact effect and shot ownership. List every applicable uncertainty on the effect's `uncertainty_ids` and list the same effect and exact owned shots on the uncertainty. Ensure every effect-to-uncertainty link is bidirectional, including a fully animated effect's unresolved density or continuity question.

Support conspicuous effects, invisible cleanup, and complete no-VFX inventories without inventing extra work. Preserve supplied performance, framing, lens character, light relationships, contact, shadows, occlusion, and continuity unless an upstream decision explicitly changes them.

## Validate and deliver

Produce only English `vfx-plan.json`. Validate against `schemas/vfx-plan.schema.json`, then repair schema errors, malformed nodes, IDs, source binding, lineage, applicability, inverse references, uncertainty ownership, state contradictions, and forbidden operational content.

Do not include generated or embedded media, URLs, encoded payloads, credentials, vendor or software prescriptions, NLE/DCC control, budgets, schedules, casting, procurement, or legal decisions.

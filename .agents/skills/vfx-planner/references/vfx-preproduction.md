# VFX preproduction

## Purpose, source, and applicability

A VFX plan is a shot-owned graph of visible work, evidence, dependencies, uncertainties, and acceptance criteria. It does not decide how a facility executes the work. Give every effect a **dramatic purpose**—the story, performance, or causal result—and a separate **visual purpose** describing what the viewer must perceive. This keeps a visible effect from becoming unmotivated spectacle and keeps invisible cleanup from disappearing from the plan.

The supplied scene and shot inventories are authoritative. Record every scene with its source reference, then retain only project-owned shot IDs that encode their declared scene. Copy exact visual, camera, lens, lighting, and performance `(category, value, source_reference)` facts into each shot’s ledger. A `supplied` downstream claim repeats the complete triple exactly. Every effect shot carries exactly one camera, lens, and lighting claim. `inferred` decisions state their basis; `proposed` decisions await review; `approved` names structured approval evidence with the same effect, shot, category, value, and source reference. Never reuse a fact across shots or use a downstream claim to manufacture a source record.

Classify every source shot exactly once as `effect` or `no-vfx`. An effect-classified shot lists at least one effect; a no-VFX shot lists none. Each effect lists its shots, and each applicable shot lists the effect back. Use exact positive project IDs such as `ORBIT-FX001`. One effect may span shots only when purpose, boundary, behavior, and continuity genuinely belong to the same designed phenomenon.

## Decompose visible relationships

Decompose only far enough to expose integration and ownership. Applicable components can include a created subject; photographed foreground and background; revealed cleanup area; contact, shadow, reflection, illumination, or displacement; depth ordering and holdouts; atmosphere or dynamic behavior; a transformation or glitch; and lens, focus, motion-blur, exposure, color, texture, and temporal relationships.

Use only applicable components. Cable removal may need revealed background, retained key edges and shadow, and temporal stability but no simulation. A fully animated energy effect may need stylization, holdouts, authored light response, simulation, and cross-shot continuity but no live plate.

## Practical/digital boundary and integration

Record practical and digital scope plus `confirmed` or `unresolved` status. An unresolved boundary links to a structured uncertainty containing the same effect and shots and naming a human owner, with neither approval nor supplied-boundary evidence. A confirmed boundary either names source-bound approval evidence or a `supplied_boundary_evidence` record, never both. Both records exactly own the effect and complete shot set and repeat its exact `practical_scope` and `digital_scope`; supplied-boundary evidence also repeats an existing source-context reference rather than inventing one. Prose in a dependency or assumption does not prove confirmation. Planning cannot confirm an emitter, practical debris, performer-contact proxy, digital interaction light, or another untested method.

Describe how elements must read together: stable position, scale, orientation and parallax; correct occlusion; coherent contact, reaction and eyeline; motivated shadow, reflection and illumination; compatible focus, depth of field, blur, exposure, texture and color; preserved performance timing and framing. Do not claim physical accuracy when mass, geometry, material, or environmental facts are absent.

The [ScreenSkills VFX supervisor profile](https://www.screenskills.com/job-profiles/browse/visual-effects-vfx/on-set/vfx-supervisor/) describes the role as a liaison across creative and production stakeholders. The planning consequence is to expose boundaries and owner decisions clearly enough for relevant human leads to resolve them, without impersonating their approval.

## Simulation, continuity, and review

Simulation applies when dynamic behavior—particles, fluid, cloth, hair, crowds, debris, or another stateful system—is required. The Visual Effects Society’s [19th Annual Awards definitions](https://vesglobal.org/previous-awards/19th-annual-ves-awards/) describe simulated effects through dynamic behavior and interaction with characters, sets, and environments across photoreal and animated work. Plan the visible system, influences or contact, continuity state, and evidence, not software or a solver.

Use `confirmed` only for source-bound approved behavior, with nonempty requirements and no uncertainty. A confirmed simulation names matching approval evidence with the identical ordered `requirements` array; it is not confirmed merely because a plan describes it confidently. Use `unresolved` when behavior or dependencies remain open and link the uncertainty. Use `not-required` with no requirements.

Continuity identifies observable state: position, scale, design version, phase, density, damage, light response, cleanup extent, or timing. Dependencies name both prerequisite and human owner. List every unresolved state on both the effect and the uncertainty record; its owned shots exactly equal the linked effect shots. Acceptance criteria must be visible: stable placement, correct occlusion, preserved contact shadow, synchronized reaction, absence of cleanup residue, coherent light/lens response, or exact cross-shot state.

VES [23rd Annual Awards material](https://vesglobal.org/previous-awards/23rd-annual-ves-awards/) asks breakdowns to demonstrate integration of elements and recognizes both practical-plate and animated environments. Plan mode-appropriate review evidence; do not force live-action evidence onto animation.

## Human-safety boundary

Markers, practical interaction, light, atmosphere, rigs, performers, animals, vehicles, water, fire, or debris that could affect people receive a qualified human-review handoff. When the structured handoff is required, explicitly state qualified human review. Never guarantee an outcome, call a method risk-free, waive specialist review, or declare a method safe, cleared, certified, or approved. This artifact supplies creative and evidence requirements only.

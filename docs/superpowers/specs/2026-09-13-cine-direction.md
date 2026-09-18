# Cine Direction Amendment — 2026-09-13

## Decision

The user authorized the audit's proposed rebaseline: preserve the planning core, reopen unsupported integration acceptance, prioritize a demonstrable Ninel workflow, and design Blender as a separate extension. This amends sequencing and acceptance; it does not authorize silently replacing the August artifact contracts.

## Product layers

1. Portable planning core: story, screenplay, scene, production and post plans, with deterministic schema/reference checks.
2. Change tracking: explicit provenance and freshness of dependent results, distinct from creative approval.
3. Optional execution adapters: tool-specific operations and observed outputs. They cannot become mandatory dependencies of the core.

The planning core remains offline-capable. Blender execution, image/video generation and publication are not claimed as current capabilities. The pilot design is at `2026-09-13-blender-pilot.md` in this directory.

## Readiness semantics

- Structural validity means declared contracts and references pass checks.
- Creative acceptance requires a recorded review of story and production choices.
- Freshness compares the current sources with those used to create a result.
- Media readiness requires supplied inspection evidence; planned metadata is not an observed measurement.

None implies the others. In particular, a valid project may be awaiting media, and a schema-valid result may be stale.

## Evidence and source discipline

Ninel's canonical integration target remains `series` with `animation` and `ai`. Existing fixture text is not user-approved story canon. Any new demonstration content must be labeled as such. An incomplete example must fail a visible gate rather than carry an unsupported acceptance label.

The exact 37-skill catalog is a compatibility and packaging target, not a measure of practical success. Retain the implemented specialists; prioritize a complete pilot and one meaningful revision over adding more roles.

## Supersession

`../plans/2026-09-13-cine-rebaseline.md` is the current execution plan. Earlier plans remain historical and provide detailed artifact requirements where not contradicted by this amendment. No v2 release date or readiness claim follows from this decision.

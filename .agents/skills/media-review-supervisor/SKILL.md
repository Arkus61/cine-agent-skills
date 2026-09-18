---
name: media-review-supervisor
description: Use when supplied media or measurable metadata must be reviewed against source-bound prompt acceptance criteria without inventing observations or making release decisions.
---

# Media Review Supervisor

Create `media-review-report.json`; never create media or make a release, legal, rights, safety, casting, budget, schedule, procurement, vendor, API, NLE, or DCC decision.

## Prepare

Copy the strict template. Declare exact project registries, prompt IDs, prompt references, and each acceptance criterion's exact statement and source reference. Use `media-prompt-package.json#/prompts/<PROMPT_ID>/acceptance_criteria/<zero-based-index>` exactly: `<PROMPT_ID>` replaces the numeric prompts-array position, while the criterion index remains zero-based. If no inspectable media or measurable metadata exists, return `awaiting-media` with zero items and explicit missing inputs and criteria.

## Review

1. Give every inspected item a unique positive `<PROJECT>-MD###` ID and bind it exactly to one prompt, its scene/shot/asset references, and one inspected input with identity plus full SHA-256 fingerprint.
2. Record only direct inspection or supplied measurable metadata as evidence. A filename, path, URI, prompt, creator description, or expected result is context, never evidence.
3. Bind each evidence claim to its exact input and named criterion. Inspect composition, performance, identity, action, movement, light, continuity, sound, artifacts, and declared criteria when applicable. Use [media review evidence](references/media-review-evidence.md) and [shot acceptance](references/shot-acceptance.md).
4. A still can prove static visible criteria only; motion, timing, temporal artifacts, synchronization, and sound need applicable motion or audio evidence. Metadata proves only its named measurement.
5. Record every criterion outcome, deviation, bounded repair scope, and reviewer uncertainty. Use `repair` only for localized correctable deviation, `regenerate` for foundational mismatch, and `human-review` only for subjective, rights, or safety judgment with a handoff. `approved` needs applicable evidence, passed outcomes, and no unresolved deviation.
6. Use `blocked` only with an explicit evidence, subjective, rights, or safety blocker. Validate against `schemas/media-review-report.schema.json` before delivery.

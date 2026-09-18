---
name: ai-media-prompt-designer
description: Use when a production needs source-bound, vendor-neutral prompts for still images, video, voice, dialogue, music, ambience, Foley, or sound effects without generating media or selecting a tool.
---

# AI Media Prompt Designer

Create a reviewable `media-prompt-package.json`, not media. Preserve supplied facts and constraints; label proposals, assumptions, uncertainties, and approvals separately.

## Prepare

Read all four references, copy the strict template, and validate it against `schemas/media-prompt-package.schema.json`. Declare exact upstream registries and bind every reference to one declared project-owned ID.

## Workflow

1. Record source facts, supplied constraints, approvals, and consent evidence in separate ledgers before drafting prompts. A claim cannot authorize itself.
2. Give every prompt a unique positive `<PROJECT>-MP###` ID and one allowed category. `effect` is a sound-effect category; place visual VFX in image/key-frame/video content or the VFX artifact. Separate creative content from technical assumptions.
3. Include upstream references, immutable anchors, allowed variation, negative constraints, continuity anchors, and observable acceptance criteria in every prompt.
4. Use the video skeleton in the template and the exact domain-field tables in the references. Make every domain decision a `{value, provenance}` claim; supplied values bind the fact's exact typed upstream ID, while proposed, assumed, and uncertain values remain labeled.
5. Declare `real_person_use` on every prompt. For likeness or voice, create a handoff with `review_action: require-qualified-human-consent-rights-review` and `review_status: pending-qualified-human-review`; evidence does not make a legal decision. Never state that consent, permission, rights, or legal clearance exists.
6. Keep missing traits, duration, mechanisms, and preferences as assumptions or uncertainties. Do not infer demographics, a recognizable voice, or musical traits.

## Boundaries

Never include vendor/software names, flags, parameters, URLs, base64 or embedded media, credentials, living-artist imitation, generation/API syntax, NLE/DCC control, budgets, schedules, casting, procurement, or legal decisions. Do not create media.

## Quality gate

Every supplied claim exactly binds a ledger record; every approval uses external approval evidence; IDs, scope, domain structure, continuity, and acceptance criteria validate without traceback.

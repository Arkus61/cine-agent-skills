---
name: vfx-post-supervisor
description: Use when an edit plan and preproduction VFX records need a validated, version-aware vfx-post-plan.json for turnover, compositing, review, and delivery handoff.
---

# VFX Post Supervisor

Create `vfx-post-plan.json`; do not operate an NLE or DCC, create media, render, upload, deliver, or approve work.

1. Copy the exact project and unit IDs. Register supplied preproduction effects as `<PROJECT>-FX###`, edit segments as `<UNIT>-ED###`, media as `<PROJECT>-MD###`, and each media version as `<MEDIA_ID>-v###`. Give versions one or more constrained roles: `source`, `plate`, or `output`. A prior output reused downstream has both `source` and `output` roles. Create distinct post items as `<UNIT>-FX###`. Every post item links at least one preproduction effect and one edit segment.
2. Treat pulls, frame ranges, handles, plate identity, lens data, color encoding, and grain as assumptions until supplied metadata or inspected media establishes them. A filename or verbal report is not inspection evidence.
3. For each item, add only applicable workstreams and give each a concrete action and explicit assumption. Plan plates, tracking, roto, keying, cleanup, compositing, simulation, lens/defocus/grain integration, color handoff, and final verification as the shot requires. Read [turnover and compositing](references/vfx-turnover-compositing.md) when decomposing this work.
4. Express cross-item prerequisites as ordered dependency records. Every edge names existing upstream and downstream items, appears in the downstream item's `dependency_ids`, follows execution order, and keeps the graph acyclic.
5. Keep review version-specific. `candidate` and `changes-requested` require a known current version with the `output` role. `approved` additionally requires inspection and human-approval evidence bound to that exact item and output version. A completed workstream likewise requires inspection evidence for that item and output version. Read [review and integration](references/vfx-review-integration.md) for iteration and final checks.
6. A verified delivery names a declared target and delivery-verification evidence bound to the exact item, version, and target. Otherwise leave delivery planned, candidate, or not planned and state unresolved handoff assumptions.
7. Validate against `schemas/vfx-post-plan.schema.json` before handoff. Preserve valid planning without media by using awaiting-input or planned states and keeping evidence arrays empty.

Keep creative intent, inspected evidence, technical assumptions, uncertainties, and human approval distinct. Later post decisions may refine upstream intent but may not silently contradict it.

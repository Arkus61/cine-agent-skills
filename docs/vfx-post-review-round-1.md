### Spec Compliance

- ❌ Issues found: the artifact cannot structurally distinguish source plates from VFX output versions, despite Task 4 requiring both source versions and plates (`docs/superpowers/plans/2026-08-06-cine-agent-skills-v2.0-postproduction.md:135`; `schemas/vfx-post-plan.schema.json:27-30`). It also permits version-specific review states without a current output version (`schemas/vfx-post-plan.schema.json:67,70`; `src/cine_skills/vfx_post_plans.py:121-140`).
- ⚠️ Cannot verify from this task diff: authoritative upstream source authenticity is intentionally deferred to Task 8, and no ProjectIndex VFX registry expansion belongs in Task 4 (`docs/vfx-post-resume-evidence.md:23`).

### Strengths

- The schema fixes `schema_version` at `"2.0"`, requires project/unit context, and provides distinct source, evidence, item, dependency, assumption, and uncertainty structures (`schemas/vfx-post-plan.schema.json:7,85-103`).
- The semantic validator enforces project-derived preproduction, edit, media/version, post-item, evidence, delivery-target, and dependency namespaces and rejects unknown populated references (`src/cine_skills/vfx_post_plans.py:19-60,62-77,90-95,121-155`).
- Approval requires inspection plus human approval bound to the exact current item/version, verified delivery additionally binds a declared target, and completed workstreams require current-version inspection evidence (`src/cine_skills/vfx_post_plans.py:130-155`).
- Dependencies require existing endpoints, downstream backlinks, unique ascending order, topological order, and an acyclic graph (`src/cine_skills/vfx_post_plans.py:79-115,156-159`).
- The skill guidance preserves creative intent, inspected evidence, assumptions, uncertainty, and human approval, while explicitly excluding media/VFX/render/upload/delivery operation (`.agents/skills/vfx-post-supervisor/SKILL.md:6-18`).
- Fresh forward evidence was honest: GLASS rejected stale approval and only passed after repairing media/version IDs; WOOD passed first attempt while leaving verbal completion, review, and delivery unresolved (`docs/vfx-post-forward-report.md:13-47,53-74`).

### Issues

#### Critical (Must Fix)

- None.

#### Important (Should Fix)

- `schemas/vfx-post-plan.schema.json:27-30`; `src/cine_skills/vfx_post_plans.py:29-38,121-140` — A media-version record has no role or kind that identifies a plate/source versus a VFX output. Consequently `current_output_version_id` can point at any registered media version, and inspection/approval evidence can approve that record even if it is actually a plate. This misses the required plate/output structure and weakens the exact-version approval gate. Add a constrained media role (at minimum source/plate versus output), require `source_version_ids` to reference source-capable records, and require `current_output_version_id` plus review/delivery evidence to reference an output-capable record.
- `schemas/vfx-post-plan.schema.json:67,70`; `src/cine_skills/vfx_post_plans.py:121-140` — `candidate` and `changes-requested` are version-specific review states, but both validate with `current_output_version_id: null`; only `approved` requires a current registered version. A plan can therefore claim review of no identifiable output, contrary to the version-aware-status requirement. Require a known current output version for `candidate` and `changes-requested` (and preserve `planned`/`awaiting-media` as the no-media states); add focused negative tests for both null-version states.

#### Minor (Nice to Have)

- `.agents/skills/vfx-post-supervisor/SKILL.md:7`; `docs/vfx-post-forward-report.md:27-39` — The skill tells the agent to register media versions but does not state the exact `<PROJECT>-MD###-v###` contract. The GLASS forward used descriptive IDs and failed before repair. State the media and version ID formats alongside the effect/edit/post formats so the contract is usable without inferring it from the template or validation error.

### Assessment

**Task quality:** Needs fixes

**Reasoning:** The implementation is conservative, well-tested, and strong on ownership, dependency, and exact evidence binding. However, version-specific review can exist without a version, and the data model cannot prove that an approved current version is a VFX output rather than a source plate, so the core version-aware approval contract is not yet trustworthy.

**Check run:** No test suite was rerun; the controller supplied the implementer's report of 1077 passing tests, and the fresh forward report records one repaired GLASS validation and one first-pass WOOD validation (`docs/vfx-post-forward-report.md:27-47,68-74`).

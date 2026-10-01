# Color Grading Designer — Task 5 execution brief

Base: `7d6f460`. Requirements derive from the approved v2 postproduction plan, Task 5.

## Required deliverables

- Complete `.agents/skills/color-grading-designer/` bundle: SKILL.md, agents/openai.yaml, assets/color-plan.template.json, references/color-management-assumptions.md, shot-matching-look.md and color-story-arc.md.
- `schemas/color-plan.schema.json`, `evals/color-grading-designer.json`, source-register entry, minimal artifact/catalog registration and template-validity test.
- Focused `src/cine_skills/color_plans.py` and `tests/test_color_plans.py`; do not expand monolithic artifact semantics or create post-package CLI here.
- Produce `color-plan.json` with schema_version 2.0, exact project/unit ownership, `<unit>-CL###` items, edit segments, input/color-space assumptions, balance and shot matching, exposure/contrast, palette, protected colors, selective treatment, VFX handoff, display targets, trim assumptions, evidence and approval state.

## Behavior and tests

Separate desired look from observed input and supplied metadata. Reject declared input color space without applicable metadata, approved shot match without inspection, unknown edit/VFX references, and unsupported display target values. Bind evidence to exact item/segment/media version and claimed value; a plausible source path is not independent proof of authenticity. Preserve useful no-media planning and evidence-backed safe counterexamples.

Use explicit source/evidence records and constrained state/target fields. Define names/ID formats clearly in the contract reference, not just in validation errors. All populated references resolve even in provisional states. Distinguish input encoding, working-space assumption and output/display intent rather than treating them as interchangeable. Do not build a universal prose parser.

Teach conceptual color management, input uncertainty, normalization, balance/matching, exposure/contrast, palette, protection of skin and character colors, localized treatment, emotional progression, VFX integration, display assumptions, trims and review. No mandatory vendor/runtime dependency, no NLE/color/VFX/render/encode/upload/delivery automation, no invented inspection, exact timing, measurements, approval or QC.

Authoritative cross-artifact authenticity belongs to later Task 8, not this standalone schema. Reuse accepted VFX media/version roles where useful, but do not extend ProjectIndex here. Preserve legacy profiles and pre-existing uv.lock.

## Evidence and handoff

Baseline is recorded separately before implementation. Write tests first and record exact failing output before code. Run focused, full `make PYTHON=.venv/bin/python check`, core/full legacy, and diff checks. Save report at `docs/color-task-5-report.md` and commit task files only. Controller runs independent daylight/animation forwards and read-only review after implementation.

## Verified primary-source pointers

- [ACES system overview](https://docs.acescentral.com/background/overview/): distinguishes input, color-space, look and output transforms.
- [ACES output transforms](https://docs.acescentral.com/system-components/output-transforms/): output transforms target a display and viewing conditions.
- [OpenColorIO conceptual overview](https://opencolorio.readthedocs.io/en/latest/concepts/overview/overview.html): pipeline color management concepts.

Use brief original paraphrases and register sources; do not reproduce documentation or prescribe current software settings as verified facts.

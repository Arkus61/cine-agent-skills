# Mastering and QC Supervisor — Task 7 execution brief

Derived from approved postproduction plan Task 7. Preparation only: do not start implementation before Titles/Captions acceptance.

## Required deliverables

- Complete `.agents/skills/mastering-qc-supervisor/` bundle: SKILL.md, agents/openai.yaml, assets/mastering-qc-plan.template.json, references/mastering-deliverable-assumptions.md and technical-qc.md.
- `schemas/mastering-qc-plan.schema.json`, `evals/mastering-qc-supervisor.json`, source-register entries, minimal artifact/catalog registration and template-validity test.
- Separate `src/cine_skills/mastering_qc.py` and `tests/test_mastering_qc.py`; do not extend monolithic semantics or implement Task 8/ProjectIndex here.
- `schema_version: "2.0"`, exact project/unit ownership, `<unit>-QC###` checks, expected resolution/frame rate/aspect/duration/audio layout, sync, missing/duplicate/black frames, levels/clipping, captions/titles, artifacts, deliverable inventory, evidence, result `planned|pass|fail|human-review`, unresolved assumptions and readiness.

## Behavior and tests

Begin with RED. Baseline: `docs/mastering-baseline-2026-09-08.md`. Include both useful specs-only planning and supplied measurable metadata positive cases. Reject pass/fail without applicable inspection/measurement evidence, numeric measured values without source, unknown title/sound/color references, and ready/valid-for-delivery claims while required checks remain unresolved. A schema-valid planned artifact is not a passed master: keep artifact validity distinct from delivery readiness.

Use structured, exact records for criterion/expected value, observed value and units, master version, source reference, check result and evidence applicability. A requirement is not a measurement; a filename is not an inspection; a report for one version cannot verify another. All references resolve and every record is internally consistent even when unused. Constrain IDs, duplicate detection, scope, result values and source kinds. Keep standalone internal integrity separate from future authoritative upstream validation.

Bind measured/observed evidence to the exact check, criterion and current master version. The claimed value must match its evidence, and pass/fail must agree with the applicable criterion where machine-comparable. Keep richer qualitative judgments explicit and evidence-backed; do not build a universal prose parser or a broad standards engine. Reusing a measurement for another metric/unit or a metadata-only report for sync/visual QC must fail. Sample peak is not true peak or loudness; channel count is not channel layout. Do not infer complete-master readiness from a partial report.

Represent substantive required checks and deliverables, not empty ready plans. Required unresolved/planned/human-review checks and failed required checks block readiness; deleting required coverage must not manufacture readiness. Bind any human approval to the exact current master/version and relevant review scope. Preserve supplied historical records honestly if supported; never transfer approval automatically.

Teach specification freeze, sync, frame integrity, intentional versus accidental black, channel/layout, clipping/levels, caption/title presence and readability, safe-area review, artifacts, VFX/color completion, deliverable inventory and result evidence. No rendering, encoding, external measurement execution, upload, distribution or media processing. Measurements may be recorded from supplied reports; never claim this agent performed them without access. Vendor settings/thresholds remain explicit supplied requirements or assumptions, not universal defaults. Preserve legacy profiles and pre-existing uv.lock.

## Verified primary references

- [EBU R 128](https://tech.ebu.ch/publications/r128), checked 2026-09-08: distinguishes programme loudness, loudness range and maximum true-peak descriptors. Use the concepts, not an unrequested universal project target.
- [W3C WAI captions/subtitles](https://www.w3.org/WAI/media/av/captions/), checked 2026-09-07: relevant speech/nonspeech caption content and accuracy review. Do not equate metadata presence with verified accessibility.

Register short original paraphrases and sources; do not copy documentation. The EBU general quality-control landing page could not be retrieved; do not claim to have verified it or cite it as consulted.

## Verification and handoff

Write `docs/mastering-task-7-report.md` with exact RED/GREEN, focused/full `make PYTHON=.venv/bin/python check`, both legacy and diff checks. Commit scoped files only. Freeze schema/template/instructions before controller's fresh specs-only and measurable-metadata forwards. Independent read-only review and blocking-finding closure precede acceptance.

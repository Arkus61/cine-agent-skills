# Titles and Captions Designer — Task 6 execution brief

Requirements derive from the approved v2 postproduction plan, Task 6. This brief is preparation; implementation starts only after Color Task 5 acceptance.

## Deliverables

- Complete `.agents/skills/titles-captions-designer/` bundle: concise SKILL.md, agents/openai.yaml, assets/titles-captions-plan.template.json, references/title-design-timing.md and captions-readability-accessibility.md.
- `schemas/titles-captions-plan.schema.json`, `evals/titles-captions-designer.json`, source-register entries, minimal artifact/catalog registration and template-validity test.
- Focused `src/cine_skills/titles_captions.py` and `tests/test_titles_captions.py`. Do not grow the monolithic artifact validator with department semantics or implement validate-post here.
- Artifact schema version `2.0`, exact project/unit ownership, `<unit>-TT###` items, type, edit segment, text source, placement, timing intent, safe-area assumption, typography intent, readability, language, speaker identification, sound description, burn-in/sidecar assumption and approval.

## Contract and test requirements

Start from test failures, not product code. Include useful vertical short-form and widescreen feature planning, plus evidence-backed valid cases. Reject missing caption language, dialogue caption without a source reference, unsafe placement without exception rationale, exact timing without applicable current locked-edit metadata, and final approval without applicable review evidence.

Use explicit structured states and source/evidence registries, not a universal prose parser. Make every ID shape and CLI invocation clear in the skill/reference/template. All populated references must resolve even in draft states; every registry record must itself be internally consistent even when unused. Reject duplicate or cross-project/unit IDs and cross-item/segment/version evidence wiring.

Distinguish creative timing intent from exact supplied timing. No exact-looking placeholder timestamps without metadata. A lock label on its own cannot establish cue timing; exact values must match supplied records for the same current edit version, item and segment, with a declared timebase and valid ordered bounds. Do not conflate source-media timecodes with output-timeline timecodes. Existing edit lock decisions use project `LK###` IDs and reference segment/source media; reuse that relationship where applicable, without claiming those records contain an output timeline they do not provide.

Source text is provenance, not proof of performed speech. Preserve supplied dialogue and its source pointer; keep translation and editorial captioning explicit proposals until reviewed. Unknown credit names, organizations and rights clearance remain unresolved, never fabricated. Review/approval must bind the exact current item content/revision and edit context, not simply a nonempty evidence list. Do not let stale or unrelated review approve changed text, timing or placement. Standalone validation establishes internal consistency; authoritative upstream authenticity belongs to Task 8.

Teach hierarchy, rhythm, typography as creative intent, placement relative to active picture/platform UI, contrast on changing backgrounds, credits scope without clearance claims, subtitles versus accessibility captions, relevant speaker/nonspeech information, language/localization, semantic line breaks, reading speed/line length as proposed targets, and burn-in versus sidecar tradeoffs. No universal safe-area percentage, font, reading-speed limit or delivery standard asserted without an applicable specification. Preserve substantive decisions while media is unavailable.

No NLE, caption rendering, transcription service, encode, upload or delivery automation. No invented timecodes, inspection, measured readability, QC pass or human approval. Preserve v0.1/v1 profiles and pre-existing uv.lock. Do not extend ProjectIndex in this specialist.

## Sources and evidence

Independent baseline and analysis: `docs/titles-baseline-2026-09-07.md`. It was honest about approval/credits, but supplied exact-looking provisional timestamps, ad-hoc IDs and no structured source bindings. Classify as output-contract/reference improvement, not a fabricated safety failure.

Primary references verified 2026-09-07:

- [W3C WAI captions/subtitles](https://www.w3.org/WAI/media/av/captions/): captions carry speech plus relevant nonspeech information; terminology varies; open/closed presentation differs; automatic captions need accuracy review.
- [W3C understanding prerecorded captions](https://www.w3.org/WAI/WCAG22/Understanding/captions-prerecorded.html): accessibility rationale and caption content context.

Paraphrase briefly, register sources, and avoid claiming generic guidance proves project compliance. These are references, not new runtime dependencies or permission to reproduce source text.

Write `docs/titles-task-6-report.md` with exact RED/GREEN evidence, focused/full `make PYTHON=.venv/bin/python check`, core/full legacy and diff checks. Commit scoped task files only. Controller owns independent forward trials after the contract is frozen and the read-only review gate.

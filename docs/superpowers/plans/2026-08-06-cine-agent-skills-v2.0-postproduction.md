# Cine Agent Skills v2.0 Postproduction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add validated editorial, sound-post, music, VFX-post, color, titles/captions, mastering, and QC planning from reviewed media or explicit pre-media assumptions.

**Architecture:** `edit-plan.json` is the postproduction spine. Sound, music, VFX post, and color reference stable edit segments; titles/captions and mastering/QC depend on the current post state. A plan may be created before media exists, but exact takes, timecodes, and approvals require supplied media evidence or metadata.

**Tech Stack:** Python 3.11+, Markdown, YAML, JSON Schema Draft 2020-12, pytest, Agent Skills.

## Global Constraints

- Complete foundation, story, and production plans first.
- New artifacts use `schema_version: "2.0"` and exact project/unit-derived IDs.
- No NLE, DAW, color, VFX, render, encode, upload, or delivery automation.
- Never invent a selected take, exact timecode, loudness measurement, color-space reading, sync result, or QC pass.
- Vendor-specific settings are assumptions or human handoff notes, never required runtime dependencies.
- Each specialist completes baseline → implementation → forward-test before the next specialist.
- Preserve the distinction between creative intent, inspected evidence, technical assumption, unresolved question, and human approval.

---

## File map

- `schemas/edit-plan.schema.json`
- `schemas/sound-post-plan.schema.json`
- `schemas/music-plan.schema.json`
- `schemas/vfx-post-plan.schema.json`
- `schemas/color-plan.schema.json`
- `schemas/titles-captions-plan.schema.json`
- `schemas/mastering-qc-plan.schema.json`
- `src/cine_skills/post_package.py`
- `tests/post_fixtures.py`
- `tests/test_post_package.py`
- `.agents/skills/<post-skill>/...`
- `evals/<post-skill>.json`

### Task 1: Film Editor

**Files:**
- Create complete `film-editor` bundle with template `edit-plan.template.json`.
- Create references: `cut-motivation.md`, `continuity-discontinuity-montage.md`, `editorial-rhythm-by-format.md`, `edit-workflow.md`.
- Create: `schemas/edit-plan.schema.json`
- Create: `evals/film-editor.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Consumes: screenplay metadata, v1 shot plans, production plans, and media review when available.
- Produces: `edit-plan.json` with `<unit>-ED###` segments, assembly order, source media/shot IDs, dramatic purpose, in/out intent, cut motivation, transition, eye trace, motion, continuity, rhythm, dialogue/sound bridge, temporal treatment, alternatives, evidence status, and lock status.

- [ ] **Step 1: RED baseline and schema tests**

Ask a fresh agent to plan a tense dialogue and an action reveal. Record arbitrary transitions, no cut motivation, confusion between continuity and montage, invented timecodes, and no sound bridges. Schema tests reject duplicate segment IDs, unknown media/shot IDs, nonascending assembly order, `picture-locked` without inspected evidence, and exact timecodes when `evidence_status` is `planned`.

- [ ] **Step 2: Implement schema and theory bundle**

Cover cut motivation through emotion, story, rhythm, eye trace, screen plane, movement, and sound; continuity/discontinuity; Kuleshov and associative montage; match cut, jump cut, cutaway, reaction, J-cut, L-cut, sound bridge, parallel/cross-cutting, ellipsis, temporal compression/expansion; dialogue, comedy, action, horror, documentary, music-video, commercial, and short-form pacing; rough cut, fine cut, picture lock, and revision discipline.

- [ ] **Step 3: Forward-test and commit**

Forward-test a documentary sequence with incomplete coverage and a 30-second music video. Confirm the skill proposes alternatives without inventing media.

```bash
git add .agents/skills/film-editor schemas/edit-plan.schema.json evals/film-editor.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add film editor"
```

### Task 2: Sound Post Designer

**Files:**
- Create complete `sound-post-designer` bundle with template `sound-post-plan.template.json`.
- Create references: `dialogue-adr-foley.md`, `sound-edit-design-mix.md`, `sound-delivery-assumptions.md`.
- Create: `schemas/sound-post-plan.schema.json`
- Create: `evals/sound-post-designer.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Produces: `sound-post-plan.json` with `<unit>-PS###` items for dialogue edit, repair, ADR, Foley, ambience, effects, sound design, transitions, premix groups, automation intent, mix priorities, accessibility, loudness assumptions, and master requirements.

- [ ] **Step 1: RED baseline and schema tests**

Baseline plans sound for one interior dialogue and one subjective reveal. Record generic “add ambience,” missing perspective, no dialogue priority, no ADR/Foley distinction, and invented loudness compliance. Reject unknown edit segments, measured values without evidence, uncovered edit segments, and a silence item with no stated dramatic purpose.

- [ ] **Step 2: Implement bundle**

Teach production sound handoff, dialogue assembly/repair, ADR decision criteria, Foley performance, room tone/ambience, perspective, subjective design, transitions, premix groups, dynamics, intelligibility, intentional silence, accessibility, loudness target as a declared delivery assumption, final mix, and mastering handoff.

- [ ] **Step 3: Forward-test and commit**

Forward-test a dialogue-free animated short and an interview-led documentary.

```bash
git add .agents/skills/sound-post-designer schemas/sound-post-plan.schema.json evals/sound-post-designer.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add sound post designer"
```

### Task 3: Music Story Designer

**Files:**
- Create complete `music-story-designer` bundle with template `music-plan.template.json`.
- Create references: `music-spotting-story.md` and `leitmotif-diegetic-silence.md`.
- Create: `schemas/music-plan.schema.json`
- Create: `evals/music-story-designer.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Produces: `music-plan.json` with `<unit>-MU###` cues, edit-segment references, thematic role, leitmotif, entry/exit logic, energy curve, instrumentation intent, diegetic status, dialogue interaction, transition, silence alternative, source assumption, and approval state.

- [ ] **Step 1: RED baseline and schema tests**

Require a spotting plan that leaves one scene unscored. Reject living-artist imitation, unknown edit segments/characters/themes, music under protected dialogue without an interaction decision, and exact duration claims without locked edit evidence.

- [ ] **Step 2: Implement bundle**

Teach spotting, thematic function, leitmotif transformation, harmony/timbre/rhythm as narrative choices, diegetic versus nondiegetic source, entry/exit, dialogue competition, transitions, restraint, and silence. Avoid copyrighted melody or artist imitation.

- [ ] **Step 3: Forward-test and commit**

Forward-test horror restraint and a performance-led commercial.

```bash
git add .agents/skills/music-story-designer schemas/music-plan.schema.json evals/music-story-designer.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add music story designer"
```

### Task 4: VFX Post Supervisor

**Files:**
- Create complete `vfx-post-supervisor` bundle with template `vfx-post-plan.template.json` and references `vfx-turnover-compositing.md` and `vfx-review-integration.md`.
- Create: `schemas/vfx-post-plan.schema.json`
- Create: `evals/vfx-post-supervisor.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Produces: `vfx-post-plan.json` with `<unit>-FX###` items, preproduction VFX references, edit segments, source versions, plates, tracking, roto, keying, compositing, simulation, cleanup, lens/grain integration, dependencies, evidence, review status, and final assumptions.

- [ ] **Step 1: RED baseline and schema tests**

Reject missing preproduction VFX links, unknown edit segments/media, final approval without inspection evidence, and delivery claims without a declared target. Require version-aware status and dependency order.

- [ ] **Step 2: Implement bundle**

Teach turnover, pulls and handles as assumptions until media metadata exists, plates, tracking, roto, keying, cleanup, compositing, simulations, grain/lens/defocus integration, color handoff, version review, and final verification.

- [ ] **Step 3: Forward-test and commit**

Forward-test a screen replacement and a creature composite.

```bash
git add .agents/skills/vfx-post-supervisor schemas/vfx-post-plan.schema.json evals/vfx-post-supervisor.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add VFX post supervisor"
```

### Task 5: Color Grading Designer

**Files:**
- Create complete `color-grading-designer` bundle with template `color-plan.template.json`.
- Create references: `color-management-assumptions.md`, `shot-matching-look.md`, `color-story-arc.md`.
- Create: `schemas/color-plan.schema.json`
- Create: `evals/color-grading-designer.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Produces: `color-plan.json` with `<unit>-CL###` items, edit segments, input/color-space assumptions, balance and shot matching, exposure/contrast, palette, protected colors, selective treatment, VFX handoff, display targets, trim assumptions, evidence, and approval state.

- [ ] **Step 1: RED baseline and schema tests**

Baseline distinguishes intended look from measured input. Reject claimed input color space without metadata, approved shot match without inspection evidence, unknown edit/VFX references, and unsupported display target values.

- [ ] **Step 2: Implement bundle**

Teach color management conceptually, input uncertainty, normalization, balancing, shot matching, exposure/contrast, palette, skin/character-color protection, localized treatment, emotional color progression, VFX integration, target display assumptions, trims, and review.

- [ ] **Step 3: Forward-test and commit**

Forward-test a live-action daylight scene and stylized animation.

```bash
git add .agents/skills/color-grading-designer schemas/color-plan.schema.json evals/color-grading-designer.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add color grading designer"
```

### Task 6: Titles and Captions Designer

**Files:**
- Create complete `titles-captions-designer` bundle with template `titles-captions-plan.template.json`.
- Create references: `title-design-timing.md` and `captions-readability-accessibility.md`.
- Create: `schemas/titles-captions-plan.schema.json`
- Create: `evals/titles-captions-designer.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Produces: `titles-captions-plan.json` with `<unit>-TT###` items, type, edit segment, text source, placement, timing intent, safe-area assumption, typography intent, readability, language, speaker identification, sound description, burn-in/sidecar assumption, and approval.

- [ ] **Step 1: RED baseline and schema tests**

Reject captions with no language, dialogue captions with no source reference, unsafe placement with no exception rationale, exact timing without locked edit metadata, and final approval without review evidence.

- [ ] **Step 2: Implement bundle**

Teach hierarchy, title rhythm, typography as creative intent, safe areas, contrast/readability, credits scope without legal clearance, subtitles versus captions, speaker IDs, nonspeech descriptions, line length, reading speed as a target assumption, and burn-in/sidecar tradeoffs.

- [ ] **Step 3: Forward-test and commit**

Forward-test a vertical short-form project and widescreen feature titles.

```bash
git add .agents/skills/titles-captions-designer schemas/titles-captions-plan.schema.json evals/titles-captions-designer.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add titles and captions designer"
```

### Task 7: Mastering and QC Supervisor

**Files:**
- Create complete `mastering-qc-supervisor` bundle with template `mastering-qc-plan.template.json`.
- Create references: `mastering-deliverable-assumptions.md` and `technical-qc.md`.
- Create: `schemas/mastering-qc-plan.schema.json`
- Create: `evals/mastering-qc-supervisor.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Produces: `mastering-qc-plan.json` with `<unit>-QC###` checks, expected resolution/frame rate/aspect/duration/audio layout, sync, missing/duplicate/black frames, levels/clipping, captions/titles, artifacts, deliverable inventory, evidence, result (`planned`, `pass`, `fail`, `human-review`), and unresolved assumptions.

- [ ] **Step 1: RED baseline and schema tests**

Baseline receives specifications but no master file. It must return planned checks, never `pass`. Reject pass/fail without inspection evidence, numeric measurements with no source, unknown title/sound/color references, and a project marked valid while required checks are unresolved.

- [ ] **Step 2: Implement bundle**

Teach specification freeze, sync, frame integrity, intentional versus accidental black, audio channel/layout, clipping/levels, caption/title presence, safe-area review, compression artifacts, VFX/color completion, deliverable inventory, and result evidence. Explicitly exclude rendering, encoding, upload, and distribution.

- [ ] **Step 3: Forward-test and commit**

Forward-test once with specs only and once with supplied measurable QC metadata.

```bash
git add .agents/skills/mastering-qc-supervisor schemas/mastering-qc-plan.schema.json evals/mastering-qc-supervisor.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add mastering and QC supervisor"
```

### Task 8: Post Package Validation and CLI

**Files:**
- Create: `src/cine_skills/post_package.py`
- Create: `tests/post_fixtures.py`
- Create: `tests/test_post_package.py`
- Modify: `src/cine_skills/__main__.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Produces: `validate_post_package(package_dir: Path, root: Path, upstream: ProjectIndex) -> list[str]`.
- Adds CLI: `validate-post PATH --format text|json` with profile `post-v2`.

- [ ] **Step 1: Write failing package tests**

Assert exact eight-file membership, manifest order, project/unit equality, all ID/reference categories, edit assembly order, shot/media resolution, post coverage of edit segments, evidence gates for take/timecode/approval/measurement, and QC result consistency. Add unexpected directory, unreadable directory, malformed JSON, and invalid UTF-8 cases.

- [ ] **Step 2: Verify RED**

Run: `.venv/bin/python -m pytest tests/test_post_package.py tests/test_cli.py -k post -q`

Expected: missing validator and command failures.

- [ ] **Step 3: Implement schema-first validator and CLI**

Compose foundation primitives, skip cross-checks for schema-invalid files, return sorted diagnostics, and emit literal JSON:

```json
{"command":"validate-post","errors":[],"profile":"post-v2","valid":true}
```

- [ ] **Step 4: Run post and compatibility tests**

Run: `.venv/bin/python -m pytest tests/test_post_package.py tests/test_cli.py tests/test_package.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/cine_skills/post_package.py src/cine_skills/__main__.py tests/post_fixtures.py tests/test_post_package.py tests/test_cli.py
git commit -m "feat: validate v2 post packages"
```

### Task 9: Postproduction Pipeline

**Files:**
- Create complete `postproduction-pipeline` bundle with checklist `post-package-checklist.md` and reference `post-pipeline-contract.md`.
- Create: `evals/postproduction-pipeline.json`
- Modify: `tests/test_skill_catalog.py`

**Interfaces:**
- Consumes: validated scene/production packages and media-review state.
- Produces: exact post package and handoff `planned`, `ready-for-master-review`, or `blocked`.

- [ ] **Step 1: RED baseline and catalog tests**

Baseline asks for a complete Ninel pilot post plan before media exists. Tests require edit-first order, downstream dependency flow, explicit planned/evidence state, earliest-invalid repair, no invented approvals, `validate-post`, and a blocked or planned handoff instead of false finality.

- [ ] **Step 2: Implement lean orchestrator**

Invoke editor first; sound/music/VFX/color next; titles/captions after current edit; mastering/QC last. Revalidate after each repair and preserve unaffected reviewed items.

- [ ] **Step 3: Forward-test and commit**

Forward-test a documentary with incomplete media and a fully metadata-described short. Verify different handoff states.

```bash
git add .agents/skills/postproduction-pipeline evals/postproduction-pipeline.json tests/test_skill_catalog.py
git commit -m "feat: orchestrate v2 postproduction"
```

## Post subsystem completion gate

Run:

```bash
make check
.venv/bin/python -m pytest tests/test_post_package.py -q
make validate-core-example
make validate-full-example
git diff --check
```

Expected: all commands pass and a post package can be valid as a plan without claiming unobserved completion.

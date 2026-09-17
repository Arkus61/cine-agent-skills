# Cine Agent Skills v2.0 Creative Production Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add production design, character consistency, animation, VFX, vendor-neutral media prompts, evidence-based media review, and an independently validated creative-production package.

**Architecture:** Preserve v1 scene packages as the shot-level source of truth. New production artifacts reference approved project, unit, scene, beat, shot, character, world, and asset IDs. Conditional membership is derived only from declared production modes: animation/hybrid require animation planning; AI/hybrid require media prompts.

**Tech Stack:** Python 3.11+, Markdown, YAML, JSON Schema Draft 2020-12, pytest, Agent Skills.

## Global Constraints

- Complete foundation and story plans first.
- New artifacts use `schema_version: "2.0"`; preserved scene artifacts remain `"1.0"`.
- No generated or embedded media, model API, vendor-specific parameter, credential, NLE/DCC control, budget, schedule, casting, or procurement.
- A media item can be approved only when inspectable evidence is supplied; otherwise package status is `awaiting-media`.
- Character identity anchors and approved canon are distinct from scene-specific variation.
- Every consequential production decision references its dramatic and visual purpose.
- Each skill completes baseline → implementation → forward-test before the next skill.
- Detailed theory is paraphrased into focused references and registered in `docs/source-register.md`.

---

## File map

- `schemas/production-design-plan.schema.json`
- `schemas/character-look-bible.schema.json`
- `schemas/animation-plan.schema.json`
- `schemas/vfx-plan.schema.json`
- `schemas/media-prompt-package.schema.json`
- `schemas/media-review-report.schema.json`
- `src/cine_skills/production_package.py`
- `tests/production_fixtures.py`
- `tests/test_production_package.py`
- `.agents/skills/<production-skill>/...`
- `evals/<production-skill>.json`

### Task 1: Production Designer

**Files:**
- Create complete `production-designer` bundle with template `production-design-plan.template.json` and references `production-design-language.md` and `environment-prop-continuity.md`.
- Create: `schemas/production-design-plan.schema.json`
- Create: `evals/production-designer.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Consumes: story, screenplay metadata, world bible, visual language, shot list, and continuity plans.
- Produces: `production-design-plan.json` with visual concept, `<project>-AS###` assets, environments, sets, props, materials, graphics, palette, scale, wear, cultural logic, motifs, scene/shot coverage, practical/digital assumptions, continuity states, cross-department dependencies, assumptions, and uncertainties.

- [ ] **Step 1: RED baseline and schema tests**

Give a fresh agent the Ninel pilot scene and world rules; record decorative invention, missing provenance, no continuity state, and no shot coverage. Test a valid payload, then reject duplicate asset IDs, unknown world/scene/shot references, missing purpose, and unlabelled build-versus-digital claims.

- [ ] **Step 2: Implement schema and skill bundle**

Teach design from story function, shape/material/palette systems, environment storytelling, prop causality, cultural logic, scale, wear, graphics, practical/digital boundary as an assumption, and reset continuity. Explicitly exclude estimates, vendors, and procurement.

- [ ] **Step 3: Forward-test and commit**

Forward-test a contemporary one-room drama to prove the skill does not overdesign. Run schema and repository validation before commit.

```bash
git add .agents/skills/production-designer schemas/production-design-plan.schema.json evals/production-designer.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add production designer"
```

### Task 2: Character Look Designer

**Files:**
- Create complete `character-look-designer` bundle with template `character-look-bible.template.json` and references `character-visual-consistency.md` and `look-development.md`.
- Create: `schemas/character-look-bible.schema.json`
- Create: `evals/character-look-designer.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Produces: `character-look-bible.json` with character ID, immutable identity anchors, permitted variation, proportions, face/body descriptors, silhouette, palette, hair/makeup, wardrobe states, expression and pose ranges, required views, prohibited drift, scene continuity changes, reference needs, assumptions, and uncertainties.

- [ ] **Step 1: RED baseline and schema tests**

Baseline asks for a reproducible Ninel visual identity across five shots. Reject a character absent from `character-arcs.json`, duplicate state IDs, an immutable anchor contradicted by a scene state, and an appearance claim with no supplied/proposed provenance.

- [ ] **Step 2: Implement bundle**

Teach recognition anchors, silhouette, proportions, controlled variation, turnaround/view coverage, expression range, wardrobe states, material response, damage/wear progression, and AI consistency constraints. Do not infer ethnicity, disability, age, or body detail that the brief does not establish.

- [ ] **Step 3: Forward-test and commit**

Forward-test a live-action wardrobe/makeup continuity case and an animated nonhuman character.

```bash
git add .agents/skills/character-look-designer schemas/character-look-bible.schema.json evals/character-look-designer.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add character look designer"
```

### Task 3: Animation Director

**Files:**
- Create complete `animation-director` bundle with template `animation-plan.template.json` and references `animation-performance.md` and `animation-timing-motion.md`.
- Create: `schemas/animation-plan.schema.json`
- Create: `evals/animation-director.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Produces: `animation-plan.json` with shot-linked acting beats, key poses, staging, timing, spacing, arcs, weight, anticipation, overlap, holds, facial performance, lip-sync intent, camera relationship, simulation assumptions, continuity, and review criteria.

- [ ] **Step 1: RED baseline and schema tests**

Require an acting plan for one restrained awakening and one fast mechanical action. Reject uncovered shots, unknown character/shot IDs, a timing range with end before start, and simulation certainty when the method is unconfirmed.

- [ ] **Step 2: Implement bundle**

Teach pose readability, timing and spacing, arcs, anticipation, follow-through/overlap, weight, holds, staging, facial acting, lip-sync intention, camera coordination, and difference between physical realism and stylized motion. Preserve performance intent from `scene-director`.

- [ ] **Step 3: Forward-test and commit**

Forward-test a dialogue close-up and a creature locomotion shot. Verify different motion reasoning.

```bash
git add .agents/skills/animation-director schemas/animation-plan.schema.json evals/animation-director.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add animation director"
```

### Task 4: VFX Planner

**Files:**
- Create complete `vfx-planner` bundle with template `vfx-plan.template.json` and references `vfx-preproduction.md` and `vfx-capture-elements.md`.
- Create: `schemas/vfx-plan.schema.json`
- Create: `evals/vfx-planner.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Produces: `vfx-plan.json` with `<project>-FX###` items, purpose, shot references, practical/digital boundary, plates, tracking, mattes, references, simulations, capture/generation elements, integration assumptions, continuity, dependencies, and acceptance criteria.

- [ ] **Step 1: RED baseline and schema tests**

Test one hologram, one invisible-effect cleanup, and one no-VFX shot. Reject unknown shots, missing clean-plate decision, unresolved practical/digital boundary not placed in uncertainties, and an effect with no dramatic purpose.

- [ ] **Step 2: Implement bundle**

Teach effect decomposition, clean plates, reference capture, tracking markers, lens and lighting metadata, mattes, holdouts, practical interaction, simulation dependencies, integration, continuity, and human safety handoff. Do not prescribe vendor software.

- [ ] **Step 3: Forward-test and commit**

Forward-test a live-action creature extension and a fully animated energy effect.

```bash
git add .agents/skills/vfx-planner schemas/vfx-plan.schema.json evals/vfx-planner.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add VFX planner"
```

### Task 5: AI Media Prompt Designer

**Files:**
- Create complete `ai-media-prompt-designer` bundle with template `media-prompt-package.template.json`.
- Create references: `vendor-neutral-image-prompts.md`, `vendor-neutral-video-prompts.md`, `voice-music-sound-prompts.md`, `prompt-continuity.md`.
- Create: `schemas/media-prompt-package.schema.json`
- Create: `evals/ai-media-prompt-designer.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Produces: `media-prompt-package.json` with `<project>-MP###` prompts categorized as `character-image`, `environment-image`, `key-frame`, `video`, `voice`, `dialogue`, `music`, `ambience`, `foley`, or `effect`.
- Every prompt carries upstream IDs, content, immutable anchors, allowed variation, technical assumptions, negative constraints, continuity anchors, and acceptance criteria.

- [ ] **Step 1: RED baseline and schema tests**

Baseline requests one image, one shot video, one voice, one music, and one sound-effect prompt. Record fused scene/camera instructions, character drift, tool-specific flags, artist imitation, missing negative constraints, and no acceptance criteria. Schema tests reject vendor parameter fields, URLs, base64, secrets, living-artist imitation requests, unsupported categories, and unknown upstream IDs.

- [ ] **Step 2: Implement bundle**

For video, require separate scene/action, identity lock, start/end composition, named movement, trajectory, direction, speed, subject retention, lens/depth/light/texture/mood, performance timing, duration assumption, continuity anchors, negative constraints, and acceptance criteria. Apply equivalent domain contracts to image, voice, music, ambience, Foley, and effects. Surface real-person likeness/voice for human consent review without making a legal decision.

- [ ] **Step 3: Forward-test and commit**

Forward-test a live-action previs package, a stylized animation shot, and a dialogue-free music cue. Confirm vendor neutrality.

```bash
git add .agents/skills/ai-media-prompt-designer schemas/media-prompt-package.schema.json evals/ai-media-prompt-designer.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add vendor-neutral AI media prompts"
```

### Task 6: Media Review Supervisor

**Files:**
- Create complete `media-review-supervisor` bundle with template `media-review-report.template.json` and references `media-review-evidence.md` and `shot-acceptance.md`.
- Create: `schemas/media-review-report.schema.json`
- Create: `evals/media-review-supervisor.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Produces: `media-review-report.json` with package status `awaiting-media`, `reviewed`, or `blocked`; inspected entries use `<project>-MD###` media IDs and item status `approved`, `repair`, `regenerate`, or `human-review`; every entry records evidence, inspected input, upstream IDs, deviations, repair scope, and reviewer uncertainty.

- [ ] **Step 1: RED baseline and schema tests**

Baseline asks an agent to approve a shot described only by a filename. Record invented inspection. Schema rules prohibit item-level approval without non-empty `inspection_evidence`, prohibit reviewed status with zero items, and permit an empty `awaiting-media` report.

- [ ] **Step 2: Implement bundle**

Teach review against composition, performance, identity, action, movement, light, continuity, sound, artifacts, and declared acceptance criteria. Require direct inspection or supplied measurable metadata. Choose `repair` for localized correctable deviation, `regenerate` for foundational mismatch, and `human-review` for subjective/rights/safety decisions.

- [ ] **Step 3: Forward-test and commit**

Forward-test once with no media and once with an attached still plus prompt package. Verify the first stays `awaiting-media`.

```bash
git add .agents/skills/media-review-supervisor schemas/media-review-report.schema.json evals/media-review-supervisor.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add evidence-based media review"
```

### Task 7: Production Package Validation and CLI

**Files:**
- Create: `src/cine_skills/production_package.py`
- Create: `tests/production_fixtures.py`
- Create: `tests/test_production_package.py`
- Modify: `src/cine_skills/__main__.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Produces: `validate_production_package(package_dir: Path, root: Path, production_modes: Collection[str], upstream: ProjectIndex) -> list[str]`.
- Adds CLI: `validate-production PATH --production-mode MODE [--production-mode MODE ...] --format text|json`.
- Produces JSON profile `production-v2`.

- [ ] **Step 1: Write failing package tests**

Using literal expected filenames, assert exact conditional membership for live-action, animation, AI, and hybrid; manifest order; project ID consistency; all ID/reference categories; shot coverage; character/world/asset continuity; VFX coverage; prompt coverage for declared AI outputs; and evidence gate for media approval. Test unexpected directories and unreadable packages.

- [ ] **Step 2: Verify RED**

Run: `.venv/bin/python -m pytest tests/test_production_package.py tests/test_cli.py -k production -q`

Expected: missing validator and CLI command failures.

- [ ] **Step 3: Implement schema-first validator and CLI**

Compose foundation helpers. Do not require `animation-plan.json` for live-action-only, and do not require `media-prompt-package.json` unless modes include `ai` or `hybrid`. Return deterministic text/JSON diagnostics and exit codes 0/1/2.

- [ ] **Step 4: Run production and v1 regressions**

Run: `.venv/bin/python -m pytest tests/test_production_package.py tests/test_cli.py tests/test_package.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/cine_skills/production_package.py src/cine_skills/__main__.py tests/production_fixtures.py tests/test_production_package.py tests/test_cli.py
git commit -m "feat: validate v2 production packages"
```

### Task 8: Creative Production Pipeline

**Files:**
- Create complete `creative-production-pipeline` bundle with checklist `production-package-checklist.md` and reference `production-pipeline-contract.md`.
- Create: `evals/creative-production-pipeline.json`
- Modify: `tests/test_skill_catalog.py`

**Interfaces:**
- Consumes: validated story/script packages and v1 scene packages.
- Produces: exact mode-selected production package and handoff `awaiting-media`, `ready-for-post`, or `blocked`.

- [ ] **Step 1: RED baseline and catalog tests**

Baseline asks for a hybrid Ninel production package. Tests require exact dependency order, conditional artifacts, upstream validation, earliest-invalid repair, media evidence gate, downstream invalidation, and `validate-production` before handoff.

- [ ] **Step 2: Implement lean orchestrator**

Invoke production design and character look first, then animation/VFX, then prompts, then media review. Preserve valid unaffected items. Do not let the orchestrator invent specialist theory or approve unseen media.

- [ ] **Step 3: Forward-test and commit**

Forward-test live-action-only and AI-only briefs to verify membership differs correctly.

```bash
git add .agents/skills/creative-production-pipeline evals/creative-production-pipeline.json tests/test_skill_catalog.py
git commit -m "feat: orchestrate v2 creative production"
```

## Production subsystem completion gate

Run:

```bash
make check
.venv/bin/python -m pytest tests/test_production_package.py -q
make validate-core-example
make validate-full-example
git diff --check
```

Expected: all commands pass and production packages are independently usable for all four production modes.

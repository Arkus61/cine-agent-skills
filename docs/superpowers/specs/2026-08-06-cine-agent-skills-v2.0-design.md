# Cine Agent Skills v2.0 Design Specification

## Status

Approved product direction. Version 2.0 expands Cine Agent Skills from scene preproduction into a portable, validated creative-production system spanning story development, screenplay development, preproduction, production planning, AI-media instructions, and postproduction planning.

The system remains a knowledge and planning product. It does not generate, edit, render, mix, grade, or distribute media directly.

## Goal

Turn a creative brief into coherent, reviewable production instructions for a feature, short, series, documentary, commercial, music video, or short-form project. Support live-action, animation, AI, and hybrid production while preserving the existing v0.1 and v1.0 contracts unchanged.

Version 2.0 is complete when a user can:

1. choose a project format and production mode;
2. develop a story with an explicitly selected dramatic model;
3. produce structured outlines and a Fountain screenplay;
4. reuse the v1 scene-preproduction pipeline;
5. produce design, animation, VFX, and vendor-neutral AI-media instructions;
6. plan editing, sound post, music, VFX post, color, titles, captions, mastering, and QC;
7. validate every package and cross-project reference deterministically;
8. run each phase independently or invoke one full creative orchestrator.

## Approved constraints

- All repository content and examples are written in English.
- `SKILL.md` files remain concise; detailed theory lives in directly linked `references/` files.
- The system uses no paid API and does not require network access at runtime.
- AI prompts are vendor-neutral and never claim unsupported tool capabilities.
- The system supports `live-action`, `animation`, `ai`, and `hybrid` production modes.
- The system supports `feature`, `short`, `series`, `documentary`, `commercial`, `music-video`, and `short-form` project formats.
- Producer operations are excluded: budgets, schedules, call sheets, casting selection, crew management, bookings, and rights clearance.
- Existing `core-v0.1` and `full-v1` packages remain valid without migration or rewriting.

## Approaches considered

### Modular layered expansion (selected)

Add independent story, creative-production, and postproduction packages with their own orchestrators and manifests. Connect them through stable identifiers and a top-level creative manifest. This keeps contexts bounded, makes partial workflows useful, and allows later phases to be regenerated without rewriting unaffected upstream work.

### One monolithic full-v2 package

Keep every artifact in one directory and validate it as one contract. Invocation would be simple, but a feature or series package would become too large, conditional membership would be fragile, and small revisions would invalidate unrelated work.

### Independent skills without an integrated contract

Ship only specialist skills. This maximizes selective use but cannot guarantee that screenplay, scene planning, generated assets, editing, sound, VFX, and color refer to the same creative decisions.

## Product architecture

Version 2.0 has four connected layers:

1. **Story Development** — concept, format, genre, structure, characters, world, season, episode or unit outline, screenplay, and revision.
2. **Preproduction** — the complete v1 scene package plus production design, character look development, animation direction, and VFX planning.
3. **Creative Production Planning** — vendor-neutral instructions for captured, animated, or AI-generated media and evidence-based review of supplied media.
4. **Postproduction Planning** — edit, dialogue and sound post, music, VFX post, color, titles, captions, mastering, and technical QC.

The existing `scene-preproduction-pipeline` remains the scene-level preproduction orchestrator. New layer orchestrators own only their layer, and `full-creative-pipeline` coordinates the complete dependency graph.

## Skill catalog

Version 2.0 retains the twelve v1 skills and adds twenty-five skills, for thirty-seven total.

### Preserved v1 skills

1. `scene-beat-analyzer`
2. `scene-director`
3. `visual-language-designer`
4. `blocking-designer`
5. `camera-movement-designer`
6. `shot-list-builder`
7. `lighting-designer`
8. `sound-designer`
9. `storyboard-designer`
10. `production-breakdown`
11. `continuity-supervisor`
12. `scene-preproduction-pipeline`

### Story Development

1. `story-concept-designer`
2. `story-structure-designer`
3. `character-arc-designer`
4. `worldbuilding-designer`
5. `season-arc-designer`
6. `episode-outline-builder`
7. `screenplay-writer`
8. `screenplay-reviser`
9. `story-development-pipeline`

### Creative Production

10. `production-designer`
11. `character-look-designer`
12. `animation-director`
13. `vfx-planner`
14. `ai-media-prompt-designer`
15. `media-review-supervisor`
16. `creative-production-pipeline`

### Postproduction

17. `film-editor`
18. `sound-post-designer`
19. `music-story-designer`
20. `vfx-post-supervisor`
21. `color-grading-designer`
22. `titles-captions-designer`
23. `mastering-qc-supervisor`
24. `postproduction-pipeline`

### Full orchestration

25. `full-creative-pipeline`

Each specialist is independently invokable when its declared prerequisites are available. An orchestrator may request missing upstream work but must never fabricate an upstream artifact silently.

## Dramaturgy knowledge model

### Structural models

The theory base covers, in paraphrased form:

- Three-Act Structure;
- Five-Act Structure;
- Hero's Journey;
- Heroine's Journey;
- Eight-Sequence Structure;
- Story Circle;
- Save the Cat beat logic;
- Freytag's Pyramid;
- Kishotenketsu;
- episodic, circular, nonlinear, anthology, and frame structures;
- ensemble, multiple-protagonist, and parallel-plot structures.

No model is treated as universally correct. `story-structure-designer` must:

1. analyze format, runtime, genre, tonal promise, protagonist agency, chronology, plot count, and serialization;
2. propose two or three plausible models;
3. compare their benefits and failure modes for the supplied project;
4. select one model or a compatible hybrid;
5. explain the choice and any intentional deviations;
6. map story events to the selected model without inventing missing creative decisions.

### Genre and format routing

The reference system contains focused guidance for:

- fantasy, science fiction, adventure, quest, action, war, and heist;
- mystery, detective, procedural, thriller, horror, and survival;
- romance, comedy, tragedy, and drama;
- documentary, interview-led, observational, essay, and investigative nonfiction;
- commercials, music videos, Reels, and other short-form work.

Format profiles change the decision rules. A documentary prioritizes evidence, provenance, uncertainty, participant context, and ethical representation. A commercial prioritizes audience tension, claim, proof, brand action, and runtime. A music video may use narrative, performance, conceptual, or hybrid organization. Short-form work requires immediate orientation, retention turns, and a payoff appropriate to its duration.

### Story and event techniques

The theory base covers setup and payoff, planting, reveal, reversal, escalation, dilemma, ticking clock, dramatic irony, red herring, false victory and false defeat, midpoint shift, delayed information, parallel action, flashback and flashforward, unreliable narration, in medias res, ellipsis, contrast, motif, callback, suspense, surprise, and cliffhanger.

The story validator checks structural claims that can be expressed mechanically, including referenced event order, unresolved setup/payoff pairs, duplicated IDs, missing unit coverage, and dangling plotline references. It does not declare a story artistically good or bad.

### Series-specific theory

Series references cover season premise, season question, character and relationship arcs, A/B/C stories, serialization versus episodic reset, cold opens, act-outs, episode hooks, midpoint turns, finales, cliffhangers, bottle episodes, mythology episodes, and setup for the next episode. A season model and an episode model may differ but must not contradict each other silently.

## Canonical project layout

```text
projects/<project-slug>/
├── story/
│   ├── story-concept.json
│   ├── story-structure.json
│   ├── character-arcs.json
│   ├── world-bible.json
│   ├── season-arc.json                 # required for series
│   └── story-manifest.json
├── scripts/
│   └── <unit-id>/
│       ├── unit-outline.json
│       ├── screenplay.fountain
│       ├── screenplay-metadata.json
│       ├── script-revision-plan.json
│       ├── script-manifest.json
│       └── scenes/
│           └── <scene-id>/             # existing full-v1 package
├── production/
│   ├── production-design-plan.json
│   ├── character-look-bible.json
│   ├── animation-plan.json             # required for animation/hybrid
│   ├── vfx-plan.json
│   ├── media-prompt-package.json       # required for ai/hybrid
│   ├── media-review-report.json
│   └── production-manifest.json
├── post/
│   ├── edit-plan.json
│   ├── sound-post-plan.json
│   ├── music-plan.json
│   ├── vfx-post-plan.json
│   ├── color-plan.json
│   ├── titles-captions-plan.json
│   ├── mastering-qc-plan.json
│   └── post-manifest.json
└── creative-manifest.json
```

`<unit-id>` represents an episode for a series and the primary authored unit for other formats. The project manifest declares format, production modes, unit inventory, package locations, release version, validation status, and unresolved questions.

Conditional artifacts are selected only from manifest-declared format and production modes. A validator computes the exact required membership for that declared profile and rejects undeclared extras.

## Versioning and compatibility

- Repository release version: `2.0.0`.
- New v2 artifacts use `schema_version: "2.0"`.
- Preserved v0.1 and v1 artifacts retain `schema_version: "1.0"`.
- Preserved package profiles remain `core-v0.1` and `full-v1`.
- New layer profiles are `story-v2`, `production-v2`, `post-v2`, and `full-creative-v2`.
- Existing CLI invocations, schemas, examples, filenames, accepted payloads, and profile selection remain unchanged.

No migration command may fabricate creative content. Migration documentation explains how to create new v2 packages around an existing v1 scene package.

## Common v2 artifact rules

Every creative v2 JSON artifact contains:

- `schema_version: "2.0"`;
- a non-empty `project_id`;
- the applicable `unit_ids`, `scene_ids`, or shot references;
- an `assumptions` array;
- an `uncertainties` array;
- only fields declared by its schema;
- stable identifiers using the project or unit prefix;
- explicit creative or production purpose for consequential decisions.

Source facts, supplied constraints, assumptions, uncertainties, interpretations, and creative proposals remain distinguishable. For nonfiction, a claim cannot be converted into a fact without a source reference supplied or verified for that project.

## Stable identifiers

New identifiers use exact full-match validation and derive from the declared project or unit context.

| Entity | Suffix | Example |
|---|---|---|
| Character | `CH###` | `NINEL-CH001` |
| Plotline | `PL##` | `NINEL-PL01` |
| Story event | `EV###` | `NINEL-EV001` |
| Sequence | `SQ##` | `NINEL-SQ01` |
| Unit or episode | `U##` or `E##` | `NINEL-E01` |
| Asset | `AS###` | `NINEL-AS001` |
| Media prompt | `MP###` | `NINEL-MP001` |
| Media item | `MD###` | `NINEL-MD001` |
| Edit segment | `ED###` | `NINEL-E01-ED001` |
| Post-sound item | `PS###` | `NINEL-E01-PS001` |
| Music item | `MU###` | `NINEL-E01-MU001` |
| VFX item | `FX###` | `NINEL-E01-FX001` |
| Color item | `CL###` | `NINEL-E01-CL001` |
| Title or caption item | `TT###` | `NINEL-E01-TT001` |
| QC item | `QC###` | `NINEL-E01-QC001` |

Scene IDs include their unit when a project has multiple units, such as `NINEL-E01-S01`. Existing scene-relative IDs remain valid because the v1 contracts derive beat, movement, shot, panel, breakdown, and continuity IDs from the complete scene ID.

## New artifact contracts

### Story concept

Defines project format, production modes, runtime intent, audience promise, premise, logline, central dramatic question, theme, genre, tone, world scope, protagonist focus, supplied constraints, and success criteria.

### Story structure

Records candidate models, comparison criteria, selected model or compatible hybrid, intentional deviations, plotlines, sequences, ordered events, setup/payoff links, revelations, reversals, escalation, climax, resolution, and format-specific retention logic.

### Character arcs

Defines character function, external objective, internal need, misbelief or governing tension, agency, relationships, values, positive/flat/negative arc shape, turning events, behavioral evidence, contradictions, and endpoint. It avoids clinical diagnosis unless supplied by a qualified source as a story fact.

### World bible

Defines locations, cultures, institutions, technology or magic rules, history, factions, terminology, constraints, causal rules, and known unknowns. Each canon rule has an ID and provenance. Proposed worldbuilding remains separate from approved canon.

### Season arc

Defines season premise, season question, episode inventory, A/B/C plotline distribution, character and relationship progression, mythology reveals, escalation, episode hooks, cliffhangers, finale payoff, unresolved threads, and next-season seeds.

### Episode or unit outline

`unit-outline.json` defines unit objective, runtime, structural model, scenes, event coverage, plotline progress, emotional turns, act-outs when applicable, opening hook, midpoint, climax, resolution, and forward hook. For a series, a unit is an episode; other formats use the same filename and contract with format-specific fields.

### Fountain screenplay and metadata

`screenplay.fountain` is the human-readable screenplay. `screenplay-metadata.json` maps unit, scene, character, event, setup/payoff, and location IDs to screenplay elements so the validator can check coverage without forcing machine fields into the script text.

### Script revision plan

Records diagnosis and proposed changes for structure, causality, character agency, subtext, dialogue, exposition, pace, tone, continuity, format, production feasibility, and unresolved creative decisions. It never silently rewrites approved story canon.

### Production design plan

Defines visual concept, environments, sets, props, materials, graphic elements, palette, scale, wear, cultural logic, visual motifs, scene and shot coverage, build-versus-digital assumptions, continuity states, and cross-department dependencies. It is creative planning, not budgeting or procurement.

### Character look bible

Defines stable identity anchors, proportions, face and body descriptors, silhouette, palette, hair, makeup, wardrobe states, expressions, pose ranges, view requirements, prohibited drift, continuity changes, and reference needs. It must distinguish immutable identity from scene-specific variation.

### Animation plan

Defines acting beats, key poses, staging, timing, spacing, arcs, weight, anticipation, overlap, holds, facial performance, lip-sync intent, camera relationship, simulations, continuity, and review criteria. It does not assume a specific animation package.

### VFX plan

Defines required effects, purpose, shots, capture or generation elements, clean plates, tracking, mattes, references, simulations, integration assumptions, practical/digital boundary, continuity, dependencies, and review criteria.

### Media prompt package

Defines vendor-neutral prompts for character and environment images, key frames, video shots, voices, dialogue, music, ambience, Foley, and effects. Each prompt separates creative content from model or tool assumptions and records scene, shot, character, asset, continuity, and review references.

### Media review report

Records only media the agent has actually been given access to inspect. Each item records evidence and receives `approved`, `repair`, `regenerate`, or `human-review`. Missing media produces an explicit `awaiting-media` package status; it never receives invented approval.

### Edit plan

Defines editorial intent, assembly order, edit segments, source media references, shot purpose, in/out intent when known, cut motivation, transition, eye trace, motion, continuity, rhythm, dialogue and sound bridges, temporal treatment, alternate options, and lock status.

### Sound post plan

Defines dialogue edit, noise and repair needs, ADR intent, Foley, ambience, effects, sound design, perspective, transitions, premix groups, automation intent, mix priorities, accessibility considerations, loudness target assumptions, and mastering requirements.

### Music plan

Defines spotting, thematic roles, leitmotifs, entry and exit logic, dialogue interaction, energy curve, instrumentation intent, diegetic status, transitions, silence, source assumptions, and required human approval. It never requests imitation of a living artist.

### VFX post plan

Defines turnovers, version references, plates, tracking, rotoscoping, keying, compositing, simulations, cleanup, integration, grain and lens treatment, review status, dependencies, and final delivery assumptions.

### Color plan

Defines color-management assumptions, input uncertainty, scene balance, shot matching, exposure and contrast intent, palette, skin or character-color protection, selective treatments, VFX handoff, display targets, trim assumptions, and creative approval status.

### Titles and captions plan

Defines title hierarchy, placement, timing, safe areas, typography intent, credits scope, subtitles, captions, speaker identification, sound descriptions, readability, language inventory, and burn-in versus sidecar assumptions.

### Mastering and QC plan

Defines expected resolution, frame rate, aspect ratio, duration, audio layout, synchronization, missing or duplicate frame checks, black-frame intent, illegal level or clipping checks, subtitle and caption checks, title-safe checks, artifact review, deliverable inventory, and unresolved technical assumptions. It plans a master but does not render or distribute one.

## AI and animation prompt design

Every video prompt separates:

- scene and action;
- character identity locks and permitted variation;
- opening and ending composition;
- exact camera movement, trajectory, direction, and speed;
- subject retention and framing behavior;
- lens, depth, light, texture, and mood;
- action timing and performance beats;
- duration and declared technical assumptions;
- continuity anchors;
- negative constraints and prohibited drift;
- acceptance criteria.

Image, voice, music, ambience, Foley, and effect prompts use equivalent domain-specific contracts. Prompts never embed secrets, paid-service credentials, or unsupported parameters. Real-person likeness or voice use is surfaced for human rights and consent review; the system does not make a legal clearance decision.

## Editing and postproduction theory

### Editing

The film-editing reference covers cut motivation through emotion, story, rhythm, eye trace, screen plane, movement, and sound; continuity and discontinuity editing; Kuleshov and associative montage; match cuts, jump cuts, cutaways, reactions, J-cuts, L-cuts, and sound bridges; parallel and cross-cutting; ellipsis; temporal compression and expansion; dialogue, comedy, action, horror, documentary, music-video, and short-form pacing; rough cut, fine cut, picture lock, and revision discipline.

The skill distinguishes an intended edit plan from an evidence-based edit decision. It may provide editorial alternatives before media exists, but it cannot claim a selected take or exact timecode without supplied media metadata or direct inspection.

### Sound, music, VFX, color, titles, and QC

Post references cover dialogue edit, ADR, Foley, ambience, sound design, premix, final mix, and mastering; music spotting and leitmotif; VFX turnover and compositing; color management, matching, and emotional color arcs; title and caption timing and readability; and final technical quality control.

Every post decision resolves to a unit, scene, shot, media item, or edit segment. Later departments may refine earlier intent but cannot silently contradict it.

## Dependency flow and invalidation

1. Story concept establishes format, modes, constraints, and promise.
2. Structure, character arcs, and world bible develop from the concept.
3. Series projects add a season arc.
4. Unit outlines depend on applicable story artifacts.
5. Screenplays and metadata depend on approved unit outlines.
6. Revision plans audit the screenplay against approved upstream decisions.
7. Scene packages use the preserved v1 pipeline.
8. Production design and character look depend on story, screenplay, and scene packages.
9. Animation, VFX, and AI-media prompts depend on production design and stable scene/shot IDs.
10. Media review depends on supplied media or metadata and declares `awaiting-media` otherwise.
11. Edit planning depends on shot plans and, when available, reviewed media.
12. Sound post, music, VFX post, and color depend on the edit plan.
13. Titles, captions, mastering, and QC depend on the current post package.
14. The full manifest records validation and unresolved questions.

Changing an upstream artifact invalidates only its declared downstream dependency closure. A structure change invalidates outlines, screenplays, scene packages, production, and post. A character-look change invalidates affected asset prompts, reviewed media, affected edit segments, VFX, and color, but need not invalidate unrelated story events. Orchestrators regenerate from the earliest invalid dependency and preserve unaffected reviewed work.

## Validation model

Validation is schema-first. Cross-artifact checks run only for artifacts that load successfully and pass their own schema.

The v2 validator checks:

- strict UTF-8 standards-compliant JSON objects;
- JSON Schema Draft 2020-12 validity;
- exact package membership computed from format and production mode;
- manifest inventory and dependency order;
- stable identifier format and uniqueness;
- project, unit, scene, beat, shot, asset, prompt, media, edit, and post references;
- setup/payoff and plotline reference integrity;
- event-to-unit, unit-to-scene, beat-to-shot, and shot-to-production coverage;
- post coverage for declared edit segments;
- character, world, prop, wardrobe, spatial, visual, sound, and state continuity;
- media-review evidence and prohibition on unseen approval;
- explicit assumptions and unresolved conflicts;
- compatibility of the selected story format and production modes.

Diagnostics are deterministic, sorted, file-specific, field-specific, and available as text or JSON. Malformed input, unreadable files, invalid UTF-8, recursion depth, invalid schemas, symlink errors, disappearing directories, and reference failures never emit a Python traceback.

Creative heuristics remain evaluations rather than hard schema errors unless the artifact explicitly claims completion. For example, a missing midpoint is not inherently invalid, but a selected structure that declares a midpoint event must reference an existing event.

## CLI and profiles

Existing CLI behavior remains available. Additive commands support layer and project validation:

```bash
cine-skills validate-package PATH --profile core-v0.1|full-v1
cine-skills validate-story PATH --format text|json
cine-skills validate-production PATH --format text|json
cine-skills validate-post PATH --format text|json
cine-skills validate-project PATH --profile full-creative-v2 --format text|json
```

Exit codes remain `0` for valid, `1` for validation failure, and `2` for malformed invocation. The installed `cine-skills` entry point and `python -m cine_skills` remain equivalent.

## Source policy

- Use open, public, authoritative professional, educational, academic, and standards sources.
- Prefer primary or institutional material for technical claims.
- Paraphrase principles; do not copy course lessons, screenplay pages, book chapters, proprietary breakdowns, or paywalled teaching material.
- Record source title, organization or author, exact URL, access date, applied principles, and licensing or quotation limits in `docs/source-register.md`.
- Separate established practice, project convention, and creative recommendation.
- Keep detailed theory in focused references directly linked from the relevant `SKILL.md`.

## Testing and evaluation

### Skill development

Each new skill is developed and released independently before work begins on the next skill:

1. run a realistic baseline task without the new skill;
2. record observable omissions or failures;
3. write the minimal skill, reference, template, and evaluation contract that address those failures;
4. run the same scenario with the skill;
5. forward-test on a distinct project or format;
6. close discovered gaps and re-run validation.

Evaluations assert observable artifact shape, reference integrity, explicit assumptions, format-appropriate decisions, and decision rationale. They do not require identical prose.

### Code and schema development

- Write failing tests before Python behavior or schema constraints.
- Test format and mode profile selection.
- Test exact membership and manifests.
- Test strict IDs, dangling references, coverage, continuity, and invalidation.
- Test Fountain metadata mapping and malformed text handling.
- Test text and JSON CLI output and exit codes.
- Test malformed and adversarial user input without tracebacks.
- Run the unchanged v0.1 and v1.0 examples in every full check.

### Examples

The canonical full example is the Ninel series in `series + animation + ai` mode. It contains a season-level story package and one complete pilot unit carried through screenplay, v1 scene planning, production design, character look, animation, VFX, vendor-neutral media prompts, media-review state, edit, post sound, music, VFX post, color, titles, captions, mastering, and QC.

Compact fixtures cover feature, short, documentary, commercial, music-video, short-form, live-action, and hybrid profile behavior without duplicating a full creative project for every combination.

## Documentation and release artifacts

- Rewrite the README for the layered v2 workflow while preserving v0.1 and v1.0 instructions.
- Add a v1-to-v2 migration guide.
- Update Codex start instructions, schema documentation, source register, AGENTS instructions, and changelog.
- Document every format and production-mode profile.
- Build `cine-agent-skills-v2.0.0.zip` from tracked release files only.
- Record the release commit and SHA-256 digest.
- Verify a single archive prefix and exclusion of Git metadata, environments, caches, temporary media, and internal work logs.

## Explicit exclusions

Version 2.0 does not include:

- direct image, video, voice, music, or sound generation;
- paid APIs or vendor-specific API clients;
- NLE, DAW, color, 3D, animation, DCC, or render-farm control;
- automatic editing, mixing, grading, compositing, rendering, or delivery;
- budgets, schedules, call sheets, casting selection, crew management, bookings, or procurement;
- legal or rights clearance decisions;
- databases, MCP servers, hosted services, or web interfaces;
- distribution, marketing operations, or revenue planning.

Vendor integrations may be proposed only in a future specification. Their absence must not prevent any v2 planning or validation workflow.

## Release criteria

Version 2.0 is releasable only when:

1. the repository version is exactly `2.0.0`;
2. all thirty-seven project-local skills validate and match the approved catalog;
3. every new specialist has a baseline, forward evaluation, schema, template, and focused theory reference;
4. every new schema passes Draft 2020-12 validation;
5. `core-v0.1` and `full-v1` packages validate unchanged;
6. all v2 format and production-mode profile fixtures pass;
7. the Ninel pilot passes the complete `full-creative-v2` pipeline;
8. every cross-artifact reference, coverage rule, manifest, and invalidation rule passes automated tests;
9. malformed inputs return deterministic diagnostics without tracebacks;
10. `make setup` followed by the complete check suite succeeds from a clean tracked-only copy;
11. documentation contains no unsupported automation claims or stale product boundaries;
12. the release archive passes path, content, integrity, and clean-bootstrap checks.

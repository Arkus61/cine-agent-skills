# Cine Agent Skills v2.0 Story Development Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a validated story-development system that selects format- and genre-appropriate dramatic models, develops characters and worlds, produces unit outlines and Fountain screenplays, and preserves creative provenance through revision.

**Architecture:** Each specialist owns one v2 artifact schema, template, concise `SKILL.md`, focused theory references, UI metadata, and behavioral evaluation. `story_package.py` validates exact package membership and cross-references; `story-development-pipeline` coordinates specialists and downstream repair without absorbing their theory.

**Tech Stack:** Python 3.11+, Markdown, YAML, JSON Schema Draft 2020-12, Fountain plain text, pytest, Agent Skills.

## Global Constraints

- Complete the v2 foundation plan first.
- New artifacts use `schema_version: "2.0"` and exact project-derived IDs.
- Repository content, skills, theory, metadata, templates, evaluations, and examples are English-only.
- `SKILL.md` stays below 500 lines and links directly to detailed `references/`.
- Each new skill must complete baseline → minimal instructions → forward-test before the next skill begins.
- Theory is paraphrased from registered open sources; do not copy book chapters, courses, screenplays, or proprietary beat sheets.
- A structural model is an analytical option, not a mandatory formula.
- Preserve `core-v0.1`, `full-v1`, and the twelve v1 skills unchanged.
- Do not add generation APIs, budgets, schedules, casting, rights clearance, databases, MCP, or web UI.

---

## File map

- `schemas/story-concept.schema.json` — project format, mode, premise, promise, genre, tone, theme, and constraints.
- `schemas/story-structure.schema.json` — candidate models, selection, plotlines, events, setup/payoff, and intentional deviations.
- `schemas/character-arcs.schema.json` — character objectives, agency, relationships, turns, and arc evidence.
- `schemas/world-bible.schema.json` — canon rules, locations, factions, systems, terms, and provenance.
- `schemas/season-arc.schema.json` — series episode inventory, plot distribution, progression, hooks, and finale.
- `schemas/unit-outline.schema.json` — unit structure and scene inventory for every approved format.
- `schemas/screenplay-metadata.schema.json` — ID mapping from Fountain elements to story contracts.
- `schemas/script-revision-plan.schema.json` — diagnosis, proposed revisions, preservation constraints, and approval state.
- `src/cine_skills/fountain.py` — safe minimal Fountain structure inspection.
- `src/cine_skills/story_package.py` — story/script membership, schema, IDs, references, and coverage validation.
- `tests/test_fountain.py`, `tests/test_story_package.py`, `tests/story_fixtures.py` — story behavior and fixtures.
- `.agents/skills/<name>/` — one bundle per approved story skill.
- `evals/<name>.json` — observable behavior contracts.

## Mandatory bundle contract

Every specialist task creates exactly:

```text
.agents/skills/<skill>/SKILL.md
.agents/skills/<skill>/agents/openai.yaml
.agents/skills/<skill>/assets/<artifact>.template.json
.agents/skills/<skill>/references/<topic>.md
evals/<skill>.json
schemas/<artifact>.schema.json
```

`screenplay-writer` replaces the JSON template with `screenplay.template.fountain` plus `screenplay-metadata.template.json`. Every frontmatter contains only `name` and `description`; the directory and frontmatter name match.

### Task 1: Story Concept Designer

**Files:**
- Create: `.agents/skills/story-concept-designer/SKILL.md`
- Create: `.agents/skills/story-concept-designer/agents/openai.yaml`
- Create: `.agents/skills/story-concept-designer/assets/story-concept.template.json`
- Create: `.agents/skills/story-concept-designer/references/concept-format-genre.md`
- Create: `schemas/story-concept.schema.json`
- Create: `evals/story-concept-designer.json`
- Modify: `tests/test_artifacts.py`
- Modify: `docs/source-register.md`

**Interfaces:**
- Consumes: user brief and confirmed constraints.
- Produces: `story-concept.json` with required `schema_version`, `project_id`, `project_format`, `production_modes`, `runtime_intent`, `audience_promise`, `premise`, `logline`, `central_dramatic_question`, `themes`, `genres`, `tone`, `world_scope`, `protagonist_focus`, `success_criteria`, `assumptions`, and `uncertainties`.

- [ ] **Step 1: Run a RED baseline**

Dispatch a fresh agent without the skill: `Develop a reusable story concept package from this brief: an android explorer becomes stranded in a fantasy world while an underground hive intelligence expands. The target is a serialized animated AI production. Return structured JSON and label unknowns.` Record whether it omits format/mode, audience promise, central question, theme, or uncertainty separation.

- [ ] **Step 2: Write and run failing schema tests**

Assert a complete literal NINEL payload validates; delete `audience_promise` and expect a required-property error; set `project_format` to `podcast` and expect an enum error; add an undeclared field and expect an additional-properties error.

Run: `.venv/bin/python -m pytest tests/test_artifacts.py -k story_concept -q`

Expected: RED because the schema is missing.

- [ ] **Step 3: Implement the schema and skill bundle**

Use exact enums from `PROJECT_FORMATS` and `PRODUCTION_MODES`, non-empty strings, unique non-empty arrays, `schema_version: "2.0"`, and `additionalProperties: false`. The skill workflow must extract supplied facts, ask or label missing format decisions, distinguish premise from plot summary, and never claim audience research that was not supplied.

- [ ] **Step 4: Validate and forward-test**

Run repository validation and the focused schema tests. Then dispatch a fresh agent with the skill on a documentary brief about a closed factory. Verify the output switches to nonfiction evidence/uncertainty reasoning and does not force a hero arc.

- [ ] **Step 5: Commit**

```bash
git add .agents/skills/story-concept-designer schemas/story-concept.schema.json evals/story-concept-designer.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add story concept designer"
```

### Task 2: Story Structure Designer

**Files:**
- Create: `.agents/skills/story-structure-designer/SKILL.md`
- Create: `.agents/skills/story-structure-designer/agents/openai.yaml`
- Create: `.agents/skills/story-structure-designer/assets/story-structure.template.json`
- Create: `.agents/skills/story-structure-designer/references/structure-models.md`
- Create: `.agents/skills/story-structure-designer/references/genre-format-routing.md`
- Create: `.agents/skills/story-structure-designer/references/story-events-retention.md`
- Create: `schemas/story-structure.schema.json`
- Create: `evals/story-structure-designer.json`
- Modify: `tests/test_artifacts.py`
- Modify: `docs/source-register.md`

**Interfaces:**
- Consumes: valid `story-concept.json`.
- Produces: `story-structure.json` with `candidate_models`, `selection_criteria`, `selected_model`, `hybrid_components`, `selection_rationale`, `intentional_deviations`, `plotlines`, `sequences`, `events`, `setup_payoffs`, `assumptions`, and `uncertainties`.
- Stable IDs: `<project>-PL##`, `<project>-SQ##`, `<project>-EV###`.

- [ ] **Step 1: Run a RED baseline**

Prompt a fresh agent to choose a structure for the Ninel series concept while comparing Hero's Journey, Three-Act, and at least one serial alternative. Record forced-template behavior, lack of comparison, unmotivated hybridization, missing cliffhanger logic, and missing deviations.

- [ ] **Step 2: Write failing structure and exact-ID tests**

Create a valid payload with three candidates, one selected compatible hybrid, two plotlines, two sequences, three ordered events, and one setup/payoff pair. Assert schema success. Assert failures for one candidate, duplicate event IDs, `NINEL-EV001-extra`, a payoff pointing to an unknown event, and a sequence referencing another project.

Run: `.venv/bin/python -m pytest tests/test_artifacts.py -k story_structure -q`

Expected: RED because the schema and identifier contract are absent.

- [ ] **Step 3: Implement the detailed theory and output contract**

Cover Three-Act, Five-Act, Hero's Journey, Heroine's Journey, Eight-Sequence, Story Circle, Save the Cat beat logic, Freytag, Kishotenketsu, episodic, circular, nonlinear, anthology, frame, ensemble, multi-protagonist, and parallel structures. Cover setup/payoff, reveal, reversal, escalation, dilemma, ticking clock, dramatic irony, red herring, false victory/defeat, midpoint, delayed information, parallel action, flashback/forward, unreliable narration, in medias res, ellipsis, suspense, surprise, and cliffhanger. The selection workflow must propose 2–3 candidates, compare benefits and risks against observable format/genre criteria, select or hybridize, and state deviations.

- [ ] **Step 4: Validate and forward-test format routing**

Forward-test independently on: a 45-second commercial, a mystery short, and a performance-led music video. Each must select different structure logic and must not copy the Ninel solution.

- [ ] **Step 5: Commit**

```bash
git add .agents/skills/story-structure-designer schemas/story-structure.schema.json evals/story-structure-designer.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add adaptive story structure designer"
```

### Task 3: Character Arc Designer

**Files:**
- Create the complete `character-arc-designer` bundle using artifact `character-arcs` and reference `character-arc-agency.md`.
- Create: `schemas/character-arcs.schema.json`
- Create: `evals/character-arc-designer.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Consumes: story concept and structure.
- Produces: `character-arcs.json` containing characters with `<project>-CH###` IDs, role, external objective, internal need, governing tension, agency, values, relationships, arc shape (`positive`, `flat`, `negative`, `open`), turning event IDs, behavioral evidence, contradictions, endpoint, assumptions, and uncertainties.

- [ ] **Step 1: RED baseline and schema test**

Baseline prompt: develop Ninel, Argo, and one fantasy-world ally without diagnosing them. Schema tests reject duplicate IDs, an unsupported clinical diagnosis field, an unknown turning event, and a relationship target not declared in the character set.

- [ ] **Step 2: Implement bundle and cross-reference rules**

Teach want versus need, agency, choice under pressure, relationship arcs, positive/flat/negative/open arcs, contradiction, behavior instead of labels, ensemble function, and serial arc pacing. Add exact ID validation and event/relationship resolution to the later story validator fixture now as failing expectations.

- [ ] **Step 3: Forward-test and commit**

Forward-test a flat-arc detective and a negative-arc tragic protagonist. Commit only after schema, repository validation, and both forward cases pass.

```bash
git add .agents/skills/character-arc-designer schemas/character-arcs.schema.json evals/character-arc-designer.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add character arc designer"
```

### Task 4: Worldbuilding Designer

**Files:**
- Create the complete `worldbuilding-designer` bundle using artifact `world-bible` and references `worldbuilding-causality.md` and `speculative-systems.md`.
- Create: `schemas/world-bible.schema.json`
- Create: `evals/worldbuilding-designer.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Produces: `world-bible.json` with locations, factions, institutions, history, cultures, technology or magic systems, rules, costs, limits, terminology, canon status, provenance, story consequences, assumptions, and uncertainties. Canon entities use `<project>-AS###` only when they are production assets; world rules use `<project>-WR###` and locations `<project>-LO###`.

- [ ] **Step 1: RED baseline and schema tests**

Test a science-fantasy world where technology and magic coexist. Require costs, limits, contradiction checks, provenance (`supplied`, `inferred`, `proposed`, `approved`), and story consequence for every rule. Reject a canon rule with no consequence and duplicate location/rule IDs.

- [ ] **Step 2: Implement theory and bundle**

Teach causal systems, constraints before decoration, social consequences, scale, terminology, power limits, ecological and material logic, and canon/proposal separation. Do not turn an aesthetic list into unapproved canon.

- [ ] **Step 3: Forward-test and commit**

Forward-test a contained contemporary drama to prove the skill scales down and does not invent fantasy systems.

```bash
git add .agents/skills/worldbuilding-designer schemas/world-bible.schema.json evals/worldbuilding-designer.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add worldbuilding designer"
```

### Task 5: Season Arc Designer

**Files:**
- Create the complete `season-arc-designer` bundle using artifact `season-arc` and reference `serialized-story-design.md`.
- Create: `schemas/season-arc.schema.json`
- Create: `evals/season-arc-designer.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Consumes: series story concept, structure, character arcs, and world bible.
- Produces: `season-arc.json` with season premise/question, `<project>-E##` units, A/B/C plot distribution, character and relationship progression, reveal schedule, escalation, episode hooks, cliffhangers, finale payoff, unresolved threads, and next-season seeds.

- [ ] **Step 1: RED baseline and schema tests**

Require at least two episodes for a series fixture, exact episode IDs, plotline/event resolution, every episode to advance at least one plotline, and every nonfinal episode to declare a forward hook. Reject a finale payoff referencing an undeclared setup.

- [ ] **Step 2: Implement bundle**

Teach episodic versus serialized balance, cold open, act-out, bottle and mythology episodes, escalation across episodes, finale responsibility, and cliffhanger variety. Do not demand a cliffhanger for non-series formats because this schema is series-only.

- [ ] **Step 3: Forward-test and commit**

Forward-test a six-episode mystery and a mostly episodic procedural. Verify distinct arc strategies.

```bash
git add .agents/skills/season-arc-designer schemas/season-arc.schema.json evals/season-arc-designer.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add season arc designer"
```

### Task 6: Episode Outline Builder

**Files:**
- Create the complete `episode-outline-builder` bundle using artifact `unit-outline` and references `unit-outlining.md` and `short-form-outlining.md`.
- Create: `schemas/unit-outline.schema.json`
- Create: `evals/episode-outline-builder.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Produces: `unit-outline.json` for all formats with unit ID, runtime, structural model, opening hook, scene inventory, event and plotline coverage, emotional turns, act-outs when applicable, midpoint, climax, resolution, and forward hook when applicable.

- [ ] **Step 1: RED baseline and schema tests**

Use a series episode fixture and a short-form fixture. Reject missing event coverage, duplicate scene IDs, scene IDs without the unit prefix, out-of-order scene indexes, and a claimed midpoint pointing to an unknown scene.

- [ ] **Step 2: Implement bundle**

Route fields by the project format. Series logic preserves episode/season dependencies; feature and short logic treats the unit as the whole authored script; documentary logic marks planned versus discovered material; commercial and short-form logic enforce runtime-aware orientation and payoff without forcing a three-act label.

- [ ] **Step 3: Forward-test and commit**

Forward-test a documentary unit and a 60-second Reel; verify that evidence and retention are handled differently.

```bash
git add .agents/skills/episode-outline-builder schemas/unit-outline.schema.json evals/episode-outline-builder.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add format-aware unit outline builder"
```

### Task 7: Screenplay Writer and Fountain Validation

**Files:**
- Create: `.agents/skills/screenplay-writer/SKILL.md`
- Create: `.agents/skills/screenplay-writer/agents/openai.yaml`
- Create: `.agents/skills/screenplay-writer/assets/screenplay.template.fountain`
- Create: `.agents/skills/screenplay-writer/assets/screenplay-metadata.template.json`
- Create: `.agents/skills/screenplay-writer/references/screenplay-craft.md`
- Create: `.agents/skills/screenplay-writer/references/fountain-format.md`
- Create: `schemas/screenplay-metadata.schema.json`
- Create: `evals/screenplay-writer.json`
- Create: `src/cine_skills/fountain.py`
- Create: `tests/test_fountain.py`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Produces: `screenplay.fountain` and `screenplay-metadata.json`.
- Produces: `inspect_fountain(document: str, filename: str = "screenplay.fountain") -> tuple[FountainSummary | None, list[str]]`.
- `FountainSummary` exposes ordered scene headings and normalized character cues; it is not a complete Fountain renderer.

- [ ] **Step 1: RED baseline and parser tests**

Require a fresh agent to write one outlined scene with action, playable behavior, subtext, and restrained exposition. Parser tests cover title page, `INT./EXT.` scene headings, character cues, dialogue, transitions, empty input, invalid UTF-8 at file load, and 100,000 nested formatting markers without recursion or traceback.

- [ ] **Step 2: Implement safe minimal Fountain inspection**

Use line iteration, bounded line length, anchored heading and character-cue regexes, and no recursive parser. Return deterministic errors for empty scripts, no scene headings, duplicate metadata scene mapping, and metadata headings not present in the Fountain summary.

- [ ] **Step 3: Implement screenplay skill and metadata schema**

Teach visual action, scene objective, conflict, turn, subtext, playable verbs, dialogue economy, exposition through pressure, rhythm, format-specific conventions, and revision-friendly IDs. Metadata maps unit, scene, event, character, location, setup/payoff, and heading text without injecting JSON into screenplay prose.

- [ ] **Step 4: Forward-test and commit**

Forward-test one fantasy scene and one interview-led documentary sequence. Run parser, schema, repository, and malformed-input tests before commit.

```bash
git add .agents/skills/screenplay-writer schemas/screenplay-metadata.schema.json evals/screenplay-writer.json src/cine_skills/fountain.py tests/test_fountain.py tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add Fountain screenplay writer"
```

### Task 8: Screenplay Reviser

**Files:**
- Create the complete `screenplay-reviser` bundle using artifact `script-revision-plan` and reference `screenplay-revision.md`.
- Create: `schemas/script-revision-plan.schema.json`
- Create: `evals/screenplay-reviser.json`
- Modify: `tests/test_artifacts.py`, `docs/source-register.md`

**Interfaces:**
- Produces: `script-revision-plan.json` with diagnosis items, evidence, affected IDs, priority, proposed change, preserved constraint, downstream impact, status, assumptions, and uncertainties.

- [ ] **Step 1: RED baseline and schema tests**

Provide a screenplay with weak causality and expository dialogue but one approved ambiguity. Require evidence-linked notes and preservation of that ambiguity. Reject generic notes with no affected ID/evidence and proposed changes that silently rewrite approved canon.

- [ ] **Step 2: Implement bundle**

Cover structure, causality, agency, stakes, setup/payoff, subtext, dialogue, exposition, pace, tone, continuity, format, and production feasibility. Separate diagnosis from rewrite and rank changes by dependency impact.

- [ ] **Step 3: Forward-test and commit**

Forward-test a comedy short and a serialized drama scene; ensure notes are format-sensitive.

```bash
git add .agents/skills/screenplay-reviser schemas/script-revision-plan.schema.json evals/screenplay-reviser.json tests/test_artifacts.py docs/source-register.md
git commit -m "feat: add screenplay reviser"
```

### Task 9: Story and Script Package Validation

**Files:**
- Create: `src/cine_skills/story_package.py`
- Create: `tests/story_fixtures.py`
- Create: `tests/test_story_package.py`
- Modify: `src/cine_skills/__main__.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Produces: `validate_story_package(story_dir: Path, root: Path, project_format: str) -> list[str]`.
- Produces: `validate_script_package(script_dir: Path, root: Path, project_id: str, project_format: str) -> list[str]`.
- Produces: `build_story_index(story_dir: Path, scripts_dir: Path, root: Path) -> tuple[ProjectIndex | None, list[str]]` for production and project validators.
- Adds CLI: `validate-story PATH --project-format <enum> --format text|json`.

- [ ] **Step 1: Write complete failing package tests**

Use literal fixtures, not production registry helpers, to assert exact story membership, season conditionality, project ID equality, all ID categories, plot/event/character/world references, setup/payoff resolution, episode inventory, unit event coverage, Fountain/metadata mapping, and manifest order. Add unexpected directory and unreadable directory tests.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_story_package.py tests/test_cli.py -k story -q`

Expected: failures for missing validators and command.

- [ ] **Step 3: Implement validators and CLI**

Compose foundation primitives, call cross-artifact checks only for schema-valid payloads, keep diagnostics sorted, and render JSON exactly as:

```json
{"command":"validate-story","errors":[],"profile":"story-v2","valid":true}
```

- [ ] **Step 4: Run story, malformed-input, and v1 regression tests**

Run: `.venv/bin/python -m pytest tests/test_story_package.py tests/test_cli.py tests/test_package.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/cine_skills/story_package.py src/cine_skills/__main__.py tests/story_fixtures.py tests/test_story_package.py tests/test_cli.py
git commit -m "feat: validate v2 story packages"
```

### Task 10: Story Development Pipeline

**Files:**
- Create: `.agents/skills/story-development-pipeline/SKILL.md`
- Create: `.agents/skills/story-development-pipeline/agents/openai.yaml`
- Create: `.agents/skills/story-development-pipeline/assets/story-package-checklist.md`
- Create: `.agents/skills/story-development-pipeline/references/story-pipeline-contract.md`
- Create: `evals/story-development-pipeline.json`
- Modify: `tests/test_skill_catalog.py`

**Interfaces:**
- Consumes: creative brief and selected format/modes.
- Produces: valid story and script packages, a handoff status, earliest-invalid repair decision, and downstream invalidation list.

- [ ] **Step 1: RED pipeline baseline**

Ask a fresh agent to produce the Ninel season concept and pilot story package using only the eight specialist outputs by name. Record omissions in dependency order, manifest, Fountain metadata, validation, and downstream repair.

- [ ] **Step 2: Write failing catalog and observable tests**

Assert the pipeline names every story artifact in dependency order, invokes `validate-story`, distinguishes series-only season work, repairs the earliest invalid dependency, and never declares an unseen screenplay package valid.

- [ ] **Step 3: Implement the lean orchestrator bundle**

Keep theory in specialists. The orchestrator selects required artifacts from the manifest-declared format, invokes specialists in order, validates, regenerates only the invalid dependency closure, and emits `ready-for-preproduction` or `blocked` with unresolved questions.

- [ ] **Step 4: Forward-test and commit**

Forward-test on a non-series short to prove `season-arc.json` is not created. Run all story tests and repository validation.

```bash
git add .agents/skills/story-development-pipeline evals/story-development-pipeline.json tests/test_skill_catalog.py
git commit -m "feat: orchestrate v2 story development"
```

## Story subsystem completion gate

Run:

```bash
make check
.venv/bin/python -m pytest tests/test_story_package.py tests/test_fountain.py -q
make validate-core-example
make validate-full-example
git diff --check
```

Expected: all commands pass and the story subsystem is independently usable before creative-production work begins.

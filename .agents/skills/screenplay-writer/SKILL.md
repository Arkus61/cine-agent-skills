---
name: screenplay-writer
description: Use when drafting or rewriting an approved unit outline as a Fountain screenplay with separate, validation-ready story metadata for fiction, documentary, commercial, music-video, or short-form work.
---

# Screenplay Writer

## Purpose

Turn an approved `unit-outline.json` into two sibling files:

- `screenplay.fountain`: human-readable dramatic or nonfiction screen text;
- `screenplay-metadata.json`: exact revision and provenance mappings.

Keep IDs and JSON out of screenplay prose. Do not silently add events, canon, evidence, claims, access, or interview answers.

## Required inputs

Read the approved unit outline and applicable story structure, character, world, and season contracts. Record supplied facts, approved proposals, assumptions, and uncertainties before drafting. Stop and ask when a missing choice would materially alter authorship; otherwise label the uncertainty.

Read [screenplay-craft.md](references/screenplay-craft.md) for scene construction and format routing. Read [fountain-format.md](references/fountain-format.md) before writing or validating Fountain. Start from both files in `assets/` and replace every generic value.

## Workflow

1. Build a scene ledger in outline order. For each exact scene ID, retain its event IDs, participating character IDs, location ID, objective, conflict, and irreversible turn.
2. Decide what the audience can see or hear. Express intention through playable behavior: conceal, test, corner, deflect, bargain, expose, refuse, or another specific tactic.
3. Draft each scene around objective, opposing pressure, changing tactics, and a turn. Enter late, leave after the changed condition is legible, and preserve required setups and payoffs.
4. Write concise present-tense action. Prefer observable action, sound, spatial consequence, and meaningful objects over explanation, internal labels, shot lists, or unfilmable biography.
5. Give dialogue a task. Let characters pursue, evade, probe, or reframe; remove greetings, repeated information, and lines that merely name visible emotion. Put exposition under pressure and distribute only what the current choice needs.
6. Control rhythm with action paragraph length, silence, interruptions, reversals, and sentence shape. Use parentheticals only when action or delivery would otherwise be unclear.
7. Apply the format route in the craft reference. For documentary, never fabricate participant words, factual narration, access, or outcomes: write confirmed material, questions, evidence handling, and explicitly conditional planned passages.
8. Create `screenplay-metadata.json` separately. Copy exact upstream project, unit, scene, event, character, and location IDs. Copy each Fountain heading byte-for-byte into its scene mapping. Map setup/payoff relationships without placing IDs in dialogue or action.
9. Validate the metadata schema, inspect Fountain, and compare metadata to the returned summary. Repair the earliest error and re-run both checks.
10. Read the screenplay aloud. Cut redundant dialogue, convert abstract intent into behavior, verify each scene turns, and ensure revisions did not drift from approved IDs or evidence.

## Output contract

`screenplay.fountain` must use a plain-text title page, uppercase standard `INT.`, `EXT.`, `INT./EXT.`, `EXT./INT.`, or `I/E.` headings, action, character cues, dialogue, sparing parentheticals, and transitions only when useful. The repository inspector extracts only ordered standard headings and normalized character cues; it is not a renderer.

`screenplay-metadata.json` must be a strict schema-version `0.3.0` object containing:

- exact `project_id`, `unit_id`, and source event inventory;
- one unique mapping per scene with exact heading text, event and character references, location, objective, conflict, and turn;
- unique character ID-to-normalized-cue and location ID-to-name mappings;
- setup/payoff event and scene mappings, with `null` payoff fields only for an intentionally unresolved setup;
- assumptions and uncertainties.

Do not paste Fountain text, alternate dialogue, notes, or screenplay prose into the JSON.

## Validation

Run repository artifact validation on `screenplay-metadata.json`. Then call `inspect_fountain_file` and `validate_screenplay_metadata` from `cine_skills.fountain`. A valid handoff has no schema errors, no inspection errors, no duplicate scene mapping, no missing heading, and no unmapped spoken cue.

## Final checks

- Every scene has a playable objective, live conflict, changed tactic, and turn.
- Action is visual or audible; dialogue carries pressure and subtext.
- Exposition changes a present choice instead of pausing the scene.
- Format conventions fit the project rather than forcing feature-fiction habits.
- Documentary uncertainty and source status remain visible.
- Fountain and JSON are separate, original, English-only deliverables.
- No wording, scene, character, or dialogue is copied from a proprietary screenplay.

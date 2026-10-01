---
name: film-editor
description: Use when screenplay metadata, shot plans, production plans, or reviewed media must become a source-bound edit-plan.json with motivated cuts, format-aware rhythm, alternatives, and evidence-gated lock or timecode claims.
---

# Film Editor

Create `edit-plan.json`; do not edit, render, conform, mix, grade, distribute, or operate an NLE. Never invent media, takes, timecodes, coverage, continuity observations, measurements, approvals, or picture lock.

## Ground the plan

1. Copy the strict template and declare one project, one exact `<PROJECT>-U##` or `<PROJECT>-E##` unit, its format, exact upstream file references, every supplied shot ID, and only media IDs present in a supplied media-review report. Bind each shot to its encoded scene; a shared prefix is not ownership.
2. Separate screenplay and shot-plan intent from inspected evidence. With no reviewed media, keep `source_media_ids` empty, use `evidence_status: planned`, describe event-based in/out intent, and keep the segment unlocked.
3. Copy exact source boundaries only into a `timing_evidence` record bound to one reviewed media ID. A segment may use those boundaries only by naming that record and that media; do not repeat unsupported timecode syntax in rhythm, motion, transition, or other prose.
4. State the unit's editorial strategy from supplied dramatic changes. For documentary material, preserve provenance, participant context, uncertainty, and the distinction between allegation, verification, and open question.

## Build the assembly

1. Give each segment a unique positive `<UNIT>-ED###` ID and strictly ascending assembly order. Reference only declared shot and media IDs.
2. State dramatic purpose before choosing a transition. Motivate each cut through one or more of emotion, story, rhythm, eye trace, screen plane, movement, or sound. Use [cut motivation](references/cut-motivation.md).
3. Record in/out intent, transition, eye trace, motion, continuity, rhythm, dialogue or sound bridge, temporal treatment, and bounded alternatives per segment. Use [continuity, discontinuity, and montage](references/continuity-discontinuity-montage.md).
4. Shape pace for the declared project rather than applying a universal shot length. Use [editorial rhythm by format](references/editorial-rhythm-by-format.md).
5. When coverage is incomplete, preserve the gap and propose alternatives using only registered shots or media. Each alternative media ID must belong to a shot named by that same alternative. An alternative may change structure, omit a beat, retain uncertainty, use supplied sound, or request missing input; it may not create a cutaway, reaction, performance, or take that was not supplied.

## Revise and deliver

Follow [edit workflow](references/edit-workflow.md). Exact source in/out timecodes require a matching source-bound timing-evidence record. `picture-locked` requires inspected approved media plus an explicit supplied current lock decision bound to the exact segment and exact media set; inspection alone does not establish creative approval or lock. Keep assumptions and uncertainties explicit, validate against `schemas/edit-plan.schema.json`, and resolve every diagnostic before delivery.

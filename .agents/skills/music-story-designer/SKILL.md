---
name: music-story-designer
description: Use when a source-bound edit plan needs a validated music-plan.json with complete spotting, dialogue protection, restraint, and evidence-aware human handoff.
---

# Music Story Designer

Create `music-plan.json`; do not compose, record, clear, license, approve, mix, or deliver music. Do not imitate a living artist or copy a copyrighted song or melody.

1. Copy the exact project and unit from the edit plan. Register every edit segment, supplied characters and themes, protected-dialogue state, and only supplied lock or review/rights evidence. Never invent a timing, lock, performer, composer, recording, clearance, or approval.
2. Give every edit segment one explicit spotting decision. Both `spotting_id` and `cue_id` use `<UNIT>-MU###`; keep each ID unique within its respective collection. A decision is `scored` with a cue or `unscored` with a concrete narrative purpose. Keep at least one intentional unscored decision.
3. For each cue, state thematic role, optional registered leitmotif transformation, entry/exit, energy, proposed harmony/timbre/rhythm/instrumentation, diegetic assumption, transition, silence alternative, source assumption, state, and human approval boundary. Keep proposed musical intent separate from observed or cleared facts.
4. For protected dialogue, bind every protected dialogue record in the cue’s covered segments to a structured interaction with `dialogue` priority and an intelligibility-preserving approach. Exact timecodes or durations require matching supplied picture-locked evidence for the same cue segments.
5. `planned`, `proposed`, and `awaiting-input` remain conditional. `composed`, `recorded`, `reviewed`, `approved`, `licensed`, `cleared`, `locked`, and `delivered` require matching named evidence for that cue and claim. Validate against `schemas/music-plan.schema.json` before handoff.

Use [music spotting and story](references/music-spotting-story.md) for cue purpose and restraint, and [leitmotif, diegesis, and silence](references/leitmotif-diegetic-silence.md) for transformation, source assumptions, dialogue competition, and safety.

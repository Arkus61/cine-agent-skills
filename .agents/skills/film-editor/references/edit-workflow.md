# Edit workflow

## Evidence states

`planned` means editorial intent is based on supplied screenplay, shot, or production records. It permits event-based in/out intent and registered-shot alternatives, but no selected take, inspected continuity claim, exact source timecode, measured duration, or picture lock.

`inspected` means each segment names at least one media ID from the supplied media-review report. Exact timecode requires a `timing_evidence` record that names that media and establishes the same structured in/out pair. Bind the segment with `timing_evidence_id`; do not smuggle a different timecode into free prose. Qualitative cues such as “after the full answer” or “on the next inspected gesture” remain valid without exact timing evidence.

Inspection makes a claim possible; it does not itself provide creative approval, rights clearance, safety clearance, or lock. A `human-review`, `repair`, or `regenerate` media item cannot support picture lock.

## Passes

1. **Source inventory:** normalize exact unit, scene, shot, and reviewed-media IDs; record missing coverage and conflicting upstream decisions.
2. **Assembly:** place story events in ascending segment order using registered sources. Optimize for complete dramatic causality before polish.
3. **Rough cut:** compare structural alternatives, remove repetition, test clarity, and preserve useful handles or options. Keep evidence state attached to every segment.
4. **Fine cut:** refine eye trace, motion, reaction timing, dialogue overlaps, sound bridges, rhythm, and transitions against inspected media.
5. **Picture lock:** copy a supplied current decision into `lock_decisions` with one stable ID, the exact segment ID, the exact approved media-ID set, `decision: picture-locked`, `current: true`, and its source reference. The locked segment names that record with `lock_decision_id`. Do not silently alter locked segment order, source choice, media set, or exact boundaries; reopen the affected revision explicitly.

## Revision discipline

- Give a revision one named problem and an observable review question.
- Preserve an alternative until its tradeoff has been reviewed; do not overwrite the evidence for the rejected option.
- When upstream shots, media, timing evidence, or lock decisions change, mark dependent segments for review. Do not carry forward a stale inspected, boundary, or lock claim.
- Compare picture without sound and sound without picture when useful, but never infer missing tracks from the intended result.
- Separate creative preference from continuity defect, evidence gap, and technical defect.

## Incomplete coverage

Use the smallest honest repair:

1. restructure with registered material;
2. omit an unsupported beat while protecting meaning;
3. use supplied sound across a registered image;
4. retain uncertainty or discontinuity openly;
5. request the missing media or metadata.

Do not name a hypothetical take or coverage item as if it exists. Alternatives reference only IDs declared in `source_context`; a request for missing input belongs in uncertainty, not `source_media_ids`.

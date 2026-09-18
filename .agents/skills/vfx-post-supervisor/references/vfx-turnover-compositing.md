# VFX Turnover and Compositing

## Turn over known sources

Bind each post item to the preproduction effect and current edit segments that authorize it. Register every supplied plate or output as a media/version pair with explicit `source`, `plate`, or `output` roles. A version can carry both `source` and `output` when a prior-stage result becomes this item's input. Describe pulls, cut ranges, handles, scans, lens data, camera data, mattes, clean plates, color encoding, and naming as requested or supplied facts; leave each unknown explicit. A planned pull is not a retrieved plate.

## Decompose visible work

Use only the workstreams the result needs:

| Workstream | Concrete planning question |
|---|---|
| Plate | Which source and coverage must be confirmed? |
| Tracking | What movement, perspective, scale, or distortion must hold? |
| Rotoscoping or keying | Which occlusions, edges, transparency, spill, or motion detail need isolation? |
| Cleanup | What supplied unwanted element is removed while preserving texture and continuity? |
| Compositing | How do depth, light, shadow, reflection, atmosphere, and black level integrate? |
| Simulation | What visible behavior and interaction must be reviewed? |
| Lens, defocus, grain | Which plate characteristics must the output match after inspection? |
| Color handoff | Which version, color assumption, mattes, and review context move downstream? |

Set a workstream to `not-applicable` with a reason when its omission matters. Use `awaiting-input`, `planned`, or `in-progress` without claiming a result. Use `complete` only with inspection evidence for the current output version.

## Preserve source intent

Maintain supplied framing, performance, timing intent, light direction, contact, shadows, occlusion, lens character, and continuity. When post treatment changes upstream intent, record the decision for human review rather than silently rewriting the source.

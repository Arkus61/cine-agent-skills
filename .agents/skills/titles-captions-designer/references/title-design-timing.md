# Title design and timing

## Hierarchy and rhythm

Define what the audience should notice first, how long each idea needs, and how titles relate to cuts, performance, music, silence, and changes in visual density. Opening titles, intertitles, lower thirds, and end credits have different narrative jobs. Use typography as creative intent: describe hierarchy, weight, scale, spacing, alignment, motion restraint, and contrast without pretending a typeface is licensed or approved.

For credits, record only supplied names, roles, ordering, organizations, marks, and legal text. A useful draft can define categories and pacing while every unknown remains unresolved. It cannot claim contractual order, rights clearance, or legal approval.

## Placement and changing pictures

Describe placement relative to active picture, important action, faces, existing graphics, and anticipated platform controls. Do not apply a universal safe-area percentage. Mark a placement as specification-backed only when the applicable specification is cited; otherwise keep it proposed or unknown. An intentional exception records why the overlap is necessary and what review it needs.

Contrast is temporal: a title may begin legibly and cross into a busy or similarly valued background. Plan review across the entire interval and propose relocation, backing, outline, shadow, or picture treatment only as needed.

## Exact timing contract

Creative rhythm is `creative-intent` and contains prose, not exact-looking timestamps. Exact timing is `exact-supplied` and cites one `<PROJECT>-TM###` record. That record belongs to the same `<UNIT>-TT###` item and `<UNIT>-ED###` segment, names the supplied locked `<PROJECT>-EV###` edit version and existing `<PROJECT>-LK###` lock decision, declares a timebase, and stores ordered frame and timecode bounds in `output-timeline` coordinates.

Source-media timecode locates material inside a source. Output-timeline timecode locates the assembled cue. Never substitute one for the other. A lock decision that references segments or sources does not invent an output timeline; exact cue values require their own supplied metadata.

For integer non-drop timebases, each frame component must be lower than the nominal frames per second and each timecode must equal its declared frame count. Fractional and drop-frame records remain explicit supplied metadata and require downstream technical verification; do not derive or fabricate them in a creative plan.

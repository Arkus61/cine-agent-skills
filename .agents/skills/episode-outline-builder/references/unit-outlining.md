# Unit Outlining

Use a unit outline to bridge approved project structure and screenplay pages. The outline is not a prose synopsis: it is an ordered, time-bounded account of what each scene changes and which source decision it realizes.

## Contents

- [Unit boundary](#unit-boundary)
- [Source-to-scene translation](#source-to-scene-translation)
- [Scene inventory](#scene-inventory)
- [Structural landmarks](#structural-landmarks)
- [Format routing](#format-routing)
- [Audits](#audits)
- [Source boundaries](#source-boundaries)

## Unit boundary

Define the unit before inventing scenes.

| Input | Decision |
|---|---|
| Project format | Episode, complete authored script, documentary unit, spot, music video, or short-form video |
| Approved runtime | Integer seconds available to the complete unit |
| Structural model | The upstream event logic to realize, not a label to rediscover |
| Source events | Exact declared events assigned to this unit |
| Source plotlines | Exact declared tracks that change in this unit |
| Series assignment | Episode number, position, local responsibility, and carried season dependencies |
| Evidence status | Authored fact, planned documentary encounter, discovered material, or unresolved access/outcome |

A series episode is one renewable unit inside a larger arc. A feature or short is the entire authored work even when its structure contains sequences. Do not call one sequence a unit merely because outlining the whole work is harder.

## Source-to-scene translation

An event ID does not describe its own content. Read the source event object and preserve its description, function, causal change, and uncertainty. Do not supply characters, outcomes, locations, causes, or claims from the ID spelling.

Translate each assigned event through four questions:

1. What can an audience see or hear?
2. What changes because it occurs?
3. Which declared plotline moves, and how?
4. Which next scene becomes possible, necessary, newly doubtful, or differently interpreted?

One event may span several scenes when investigation, attempt, and consequence need separation. One scene may realize several events when their collision is the change. The coverage tables state this many-to-many mapping explicitly.

## Scene inventory

### Identity and order

Use the unit ID as the scene namespace. Scene index `1` is `<unit>-SC001`, index `2` is `<unit>-SC002`, and so on. Never recycle an ID after reordering; renumber the final approved order and update every reference together.

### Runtime

Record integer start and end seconds. Each scene starts at or after the prior scene ends, ends after it starts, and ends no later than `runtime_seconds`. A duration budget is a diagnostic allocation, not a claim about final edit precision.

If the assigned material cannot fit, expose the collision. Compress repeated function, combine compatible events, narrow the unit objective, or request a runtime/source reassignment. Do not hide overflow by omitting event coverage.

### Scene function

Each scene states one dominant story function and an observable change. Useful functions include orientation, attempt, complication, evidence test, discovery, reversal, decision, relationship renegotiation, demonstration, performance escalation, contrast, culmination, and consequence.

The `retention_function` states why the audience can reasonably continue. Examples include watching a test develop, anticipating a declared consequence, comparing evidence, following visible progress, waiting for musical release, or seeing a relationship decision land. "Keeps viewers engaged" names no mechanism.

### Emotional turn

Emotional turns describe a changed state caused by scene events. Use specific playable or perceivable movement: guarded to willing to test, confidence to doubt, isolation to mutual reliance, tension to relief, or curiosity to reappraisal. Avoid free-floating mood adjectives that do not affect action or audience interpretation.

## Structural landmarks

### Opening hook

Attach the opening hook to an inventory scene. State the promise and its function. A hook may orient an objective, subject, process, performance, pattern, image, conflict, or fair evidence gap. Confusion without a legible promise is not a hook.

### Act-out

Use act-outs only where presentation boundaries exist or are intentionally designed. An act-out changes pressure across the boundary by closing an option, exposing evidence, forcing choice, reversing leverage, changing the goal, or making consequence unavoidable. Page arithmetic alone is not an act-out.

### Midpoint

A midpoint is functional, not merely central in elapsed time. Claim one only when an identifiable scene changes goal, strategy, knowledge, agency, or interpretation of the first movement. Use `null` when the selected model has no central reorientation.

### Climax

A climax can be a decisive action, choice, discovery, evidence confrontation, demonstration result, performance peak, final contrast, or culminating image. Some observational or open nonfiction units have no defensible climax; use `null` instead of manufacturing one.

### Resolution

Every unit resolves the promise at its proper scale. Resolution can be success, failure, compromise, verified result, decision, answer, completed demonstration, performance release, or a bounded statement of what the inquiry established and did not establish. Open reality does not excuse an unfinished unit.

### Forward hook

A nonfinal series episode carries an approved changed promise after its local resolution. The hook names a season dependency; it does not reopen the episode's completed objective. Features, shorts, documentaries, spots, music videos, and short-form units use `null` unless the supplied project genuinely authorizes continuation.

## Format routing

### Series

Read the season episode assignment before outlining. Preserve assigned A/B/C emphasis, events, character progress, reveal schedule, setup/payoff responsibility, and later dependencies. Resolve the episode-sized objective. Do not spend a future episode's reveal or reset a prior change for convenience.

### Feature and short

Treat the unit as the entire authored script. The upstream structural model may be causal, episodic, circular, nonlinear, associative, ensemble, or contrast-led. A short benefits from event economy and one dominant effect; it is not obligated to imitate a feature's number of turns.

### Documentary

Outline access and editorial purpose without scripting reality. A planned interview, observation, archive request, experiment, or journey is a production intention, not a discovered result. A discovered record or captured moment can be stated as evidence with its basis. Preserve allegations, contradictions, inaccessible records, disputed chronology, and unknown outcomes.

Documentary retention comes from evidence access, competing interpretation, process, chronology, testimony, discovery, and honest uncertainty. Never label an outcome as the climax before it occurs merely because the treatment wants a decisive ending.

### Commercial

Fit approved subject recognition, problem or desire, response, and communication payoff inside the runtime. Claims must come from supplied approved material. Demonstration, contrast, testimonial, transformation, or associative brand-image logic may work without three acts.

### Music video

Map scenes to audible and performative changes: sections, energy, rhythm, motif, choreography, image recurrence, performer-camera relationship, or compact narrative. The climax may be musical or visual release. Do not invent dialogue scenes or a protagonist quest when the track supplies another engine.

### Short-form

Use a question/answer, demonstration, transformation, list escalation, loop, reveal, micro-story, or direct-address frame that fits the supplied duration. Orient quickly enough for the payoff to remain legible. Retention is earned by value and progress, not by hiding the subject or delaying the result beyond runtime.

## Audits

### Coverage audit

- Every source event appears exactly once in `event_coverage` and at least once in scene `event_ids`.
- Every source plotline appears exactly once in `plotline_coverage` and at least once in scene `plotline_ids`.
- Coverage outcomes describe what changes; they do not merely repeat scene summaries.
- No coverage entry invents meaning when the source supplied only an ID or unresolved assignment.

### Reference audit

- All scene pointers resolve to declared scene IDs.
- All event and plotline references resolve to their source catalogs.
- Scene IDs use the exact unit prefix and positive three-digit suffix matching index.
- Midpoint, climax, resolution, hook, act-out, and emotional-turn references survive reordering.

### Promise audit

- The opening promise is understandable in the first scene.
- The final scene fulfills or deliberately transforms that promise.
- Unit-scale resolution occurs before any forward hook.
- A series hook carries changed consequence; a documentary unknown remains unknown; a runtime-led payoff lands before the deadline.

## Source boundaries

John Reich's openly licensed film text distinguishes story action from plot arrangement; this guide applies that distinction to source-event and scene-order mapping with new operational language. Jason Mittell's open-access television research informs the separate responsibilities of episode closure and serial accumulation. PBS transparency standards support making significant documentary evidence and editorial limits evaluable. The University of Hamburg's open narratology handbook informs the distinction among suspense, curiosity, and surprise. See `docs/source-register.md` for exact pages, access date, rights notes, and repository paraphrases.

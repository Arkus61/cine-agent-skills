# Short-Form Outlining

Use this guide for `commercial`, `music-video`, and `short-form` units. Build from the supplied runtime, subject, track, claims, platform constraints, and audience promise. Do not assume a three-act model or a platform-specific duration that the brief does not supply.

## Contents

- [Clock-first design](#clock-first-design)
- [Orientation](#orientation)
- [Progress and retention](#progress-and-retention)
- [Payoff](#payoff)
- [Commercial routing](#commercial-routing)
- [Music-video routing](#music-video-routing)
- [Short-form routing](#short-form-routing)
- [Runtime audit](#runtime-audit)

## Clock-first design

Convert the approved duration to integer seconds before writing scenes. Reserve time for both the promised payoff and any required end information. Allocate by function rather than equal blocks:

1. orientation makes the subject, activity, question, pattern, or sensory premise legible;
2. development shows progress, variation, evidence, process, escalation, contrast, or performance change;
3. payoff fulfills or deliberately transforms the opening promise;
4. close allows the result to register and carries only an approved invitation, credit, disclosure, or loop.

Do not solve overflow by moving the payoff outside the unit, accelerating unreadable information, or converting omitted context into a mystery hook.

## Orientation

Orientation answers enough of "what am I seeing, why does it matter, and what result or experience is promised?" for the selected format. It need not explain outcome, cause, or every participant.

| Format | Useful early orientation | Misrouting |
|---|---|---|
| Commercial | Subject or brand context, approved need/desire, demonstration premise, or sensory proposition | Hiding the advertised subject until the final seconds without a supplied strategy |
| Music video | Performer, sonic/visual rule, motif, choreography, place, energy, or narrative relation | Exposition unrelated to the track's first meaningful change |
| Short-form | Question, before state, task, value, pattern, claim boundary, or direct-address premise | "Wait for it" language with no concrete promise |

Set `orientation_by_seconds` from the actual brief and content density. It is a deadline for legibility, not a universal platform metric.

## Progress and retention

Retention names the audience experience created by scene-to-scene change:

- a demonstration exposes diagnosis, attempt, correction, and result;
- a transformation makes before, intermediate change, and after comparable;
- a list varies or escalates value rather than repeating one fact;
- a question gains evidence before its answer;
- a performance changes energy, staging, intimacy, scale, rhythm, or motif;
- a loop returns to the opening with changed meaning or seamless rhythmic function;
- a micro-story changes objective, expectation, relationship, or consequence.

Do not confuse retention with ignorance. Basic orientation can coexist with curiosity about method, result, evidence, variation, or consequence. Every scene's `retention_function` should state the particular reason to continue.

## Payoff

The payoff is the promised communication, sensory, evidentiary, emotional, performance, or narrative result. Place it early enough that the audience can perceive it before any closing information.

Examples of payoff functions include:

- the repaired object visibly or audibly works;
- the approved product behavior is demonstrated without expanding the claim;
- a contrast completes and changes interpretation;
- a visual motif returns at the musical release;
- the answer follows fair evidence;
- a practical instruction produces the shown result;
- a loop reveals why the opening action occurred.

`payoff_by_seconds` is the latest arrival of the payoff, not the end of its duration. If the result needs comparison, reaction, legibility, or disclosure, budget those seconds too.

## Commercial routing

Use only approved claims. Separate observable demonstration from voiceover or copy assertions. A product or organization can be oriented through use, context, image, testimony, comparison, or direct presentation, but the final communication effect must be identifiable.

The structural model can be problem/response/payoff, demonstration, contrast, transformation, testimonial/frame, or associative progression. Do not label all three movements as acts unless the supplied structure selected that model for a reason.

An invitation or call to action does not replace payoff. First fulfill the communication promise; then present the approved next step with enough time to read or hear it.

## Music-video routing

Start from the exact track version and runtime. Map section changes and audible events before assigning scenes. Possible engines include:

- performance escalation;
- motif cycle and return;
- choreography development;
- parallel performance and narrative;
- visual transformation;
- tableau or anthology progression;
- associative contrast;
- compact causal story.

State what changes at each music boundary. Cutting to every beat creates activity without progression. Let selected accents, phrases, drops, holds, and releases organize meaningful changes.

The payoff may be a final performance release, choreographic convergence, motif transformation, narrative consequence, or image/music collision. Dialogue-plot suspense should not compete with the track unless explicitly supplied.

## Short-form routing

Choose one dominant value proposition or experience. A 60-second demonstration does not have room for unrelated backstory, multiple false endings, or a feature-scale subplot. Compress repetition before compressing comprehension.

For factual or instructional short-form work:

- show what is verified or demonstrated;
- label assumptions and unknowns;
- do not imply one example proves universal performance;
- preserve required safety, access, sponsorship, or claim disclosures;
- make the invitation truthful and subordinate to the delivered value.

For fiction or comedy, orient the governing rule quickly enough that variation, reversal, or punch line can be understood. For loops, ensure the return adds rhythm or changed meaning rather than removing closure.

## Runtime audit

Run these checks in order:

1. Scene IDs and indexes form one exact ordered sequence.
2. Scene start/end seconds do not overlap and the last end does not exceed `runtime_seconds`.
3. `orientation_by_seconds <= payoff_by_seconds <= runtime_seconds`.
4. The scene containing orientation begins before the orientation deadline.
5. The scene containing payoff reaches the result no later than the payoff deadline.
6. Required closing information remains legible after payoff.
7. Every assigned event and plotline still has complete coverage after compression.
8. The opening promise and final result are materially connected.

When the audit fails, remove duplicate function, narrow the promise, simplify the number of independent turns, or request a different runtime. Do not hide the failure with faster prose.

## Source boundaries

The University of Hamburg's open narratology handbook supports distinguishing suspense, curiosity, and surprise instead of treating withheld context as universal retention. John Reich's openly licensed film text supports separating story events from their presentation order. This reference's deadline, runtime-allocation, orientation, progress, payoff, and format-routing tests are original operational synthesis, not platform claims or a copied branded formula. See `docs/source-register.md`.

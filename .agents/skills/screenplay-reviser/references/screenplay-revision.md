# Screenplay Revision

Use this reference to diagnose a completed draft without substituting a new draft for the writer's decisions. Revision is dependency management: repair causes before symptoms, preserve approved invariants, and make each recommendation traceable to the current page.

## Diagnosis grammar

A useful diagnosis has three layers:

1. **Evidence:** identify the exact source element and describe what is present without guessing intention.
2. **Effect:** state how that element changes comprehension, pressure, agency, rhythm, continuity, format delivery, or feasibility.
3. **Operation:** propose the relationship or function to change, not replacement prose.

Weak: “The dialogue is on the nose.”

Actionable: “Both siblings name information they already share in the same exchange, so the decision pauses for explanation; put only the fact needed for the present choice under pressure and let their opposing tactics expose the rest.”

The actionable version still requires exact source IDs in the artifact. Do not quote more text than the evidence explanation needs, and do not recreate copyrighted pages.

## Source and constraint ledger

Reuse upstream project, unit, scene, event, character, location, and setup/payoff IDs. A Fountain draft normally keeps IDs outside the prose. When revision requires action- or dialogue-level precision, derive an ordered local ledger from the current draft, such as `<scene>-A01` for action and `<scene>-D01` for dialogue. Do not renumber unaffected elements during the diagnosis pass.

For every approved invariant, record:

- whether it is canon, an approved ambiguity, a format boundary, or a production boundary;
- the exact source IDs where a proposal could alter it;
- a preservation test that another reader can apply after a later rewrite.

An approved ambiguity is a designed range of interpretations, not missing information to solve. Revision may clarify why characters care, change their tactics around the uncertainty, or rebalance when evidence appears. It must not add evidence that decides the interpretation, make one character the authorial answer, or remove a viable reading.

If a requested fix conflicts with approved canon, stop treating it as a normal note. Record the conflict as an uncertainty or request an upstream decision. A constraint reference makes the preservation obligation visible; it does not authorize changing the constraint.

### Structured execution boundary

Keep three scopes distinct:

- `affected_ids`: every source element needed to prove and understand the diagnosis;
- `change_target_ids`: only elements a later rewrite is authorized to alter directly;
- `preservation_checks`: one exact snapshot per preserved constraint, including the declared protected IDs in their original order, an invariant, and a verification assertion.

Free-text intent is not machine-verifiable. Retaining a constraint ID beside “change the established fact” does not make that operation safe. If any direct target is protected, either remove it from the targets and redesign the operation around unprotected material, or mark the item `blocked-upstream-decision`. A blocked item uses status `blocked` and a structured `decision_request` whose conflict IDs exactly match the protected targets; its question and uncertainty tell the story owner what must be decided. Never encode this gate through keyword matching or claims about what a proposal “really means.”

Diagnosis IDs are positional, not merely unique. The first item is `<unit>-RV001`, the second is `<unit>-RV002`, and so on without gaps or reordering.

## Dependency-first audit

Read the complete draft once for experience before itemizing. On later passes, ask whether each problem is a cause or a symptom. Rank the earliest dependency that can remove the most downstream symptoms.

| Impact | Typical question | Revise before |
|---|---|---|
| `upstream-story` | Does the event chain, premise, choice, or approved story fact support what follows? | scenes, pacing, dialogue, format polish |
| `scene-engine` | Does a scene have a present objective, resistance, changing tactic, and consequential turn? | individual lines and presentation |
| `line-craft` | Do action and dialogue carry behavior, subtext, necessary information, and distinct voices? | typography and production simplification |
| `presentation-production` | Is the current expression legible, continuous, format-correct, and feasible inside supplied bounds? | final handoff only |

Do not classify by surface alone. A repeated exposition line may be a line-craft problem, or it may be a symptom of missing causal setup. A costly location may be a production note, or removing it may break an upstream event. Rank by dependency effect and explain the choice.

## Audit lenses

### Structure

Test the supplied model and format promise rather than imposing a favorite template. Identify missing, duplicated, misplaced, or disproportionate event functions. A short may need one compact movement; a series scene may serve a continuing dependency without completing the whole arc.

### Causality

Trace because/therefore relationships. A new beat should result from a choice, obstacle, discovery, or consequence, not merely happen next. Check whether setup information changes later action and whether coincidence removes a choice the story needs.

### Agency

Ask who makes the consequential decision, what options they perceive, what tactic they change, and what cost follows. Constraint does not eliminate agency; a character can choose how to respond inside limited options. Flag rescues or revelations that solve the conflict without the focal character's behavior when the approved design promises their agency.

### Stakes

Make the consequence specific, current, and connected to behavior. Separate what can be lost, why it matters to this character, and what action makes the risk grow. Do not inflate stakes with unsupported danger when a relational or moral cost is already active.

### Setup and payoff

Check that a setup is legible enough to be remembered, that intervening action preserves its relevance, and that the payoff changes meaning or consequence. A callback without change is repetition. Do not “fix” an intentionally unresolved setup when continuation is approved.

### Subtext

Compare literal topic with practical aim. Behavior, avoidance, object handling, silence, status, and timing may carry a second layer, but opacity is not automatically depth. Preserve enough context for the audience to follow the decision.

### Dialogue

Give each exchange a task: probe, recruit, stall, threaten, soothe, bargain, conceal, expose, or reframe. Test voice through priority, syntax, rhythm, and attention. Remove lines that only repeat visible action, label emotion, or restate another line. A proposal names the dialogue function; it does not draft alternate dialogue.

### Exposition

Ask whether the information is new to the listener and necessary for a present choice. Put required information into conflict, evidence, instruction, or consequence. Do not hide basic orientation solely to manufacture a reveal.

### Pace

Pace is the rate of meaningful change. Locate beats that repeat a tactic or conclusion without changing leverage, knowledge, relationship, risk, or available action. Protect pauses that create pressure, comedy timing, grief, observation, or a fair inference.

### Tone

Track the project's declared tonal range across behavior, consequence, image, and rhythm. A tonal turn can be intentional if prepared and consequential. Flag jokes, sentiment, violence, or spectacle that cancel the promised stakes rather than complicate them.

### Continuity

Track chronology, geography, entrances, exits, knowledge, injuries, props, wardrobe, time, weather, and character commitments. State the exact before/after contradiction and which later elements depend on it. Do not silently select one version when canon is unresolved.

### Format

Check runtime, whole-unit completion, episode boundaries, nonfiction evidence status, commercial claims, music-video logic, and short-form payoff against supplied requirements. Formatting polish cannot repair a missing format responsibility.

### Production feasibility

Identify the creative demand first: performers, locations, night work, weather, animals, vehicles, stunts, water, children, crowds, practical or visual effects, specialized props, playback, or sound conditions. State a bounded creative alternative that preserves story function. Do not estimate budget or schedule, select vendors or equipment, or claim clearance and safety approval.

## Format-sensitive revision

### Comedy short

Protect the compact causal engine. Test premise orientation, setup clarity, escalation through changed tactics, reversals, rule-of-three only when earned, reaction time, silence, consequence, and the final button or payoff. Do not judge by jokes per page. A funny detour that does not change the next beat may be the pacing problem; an apparently slow hold may be necessary timing.

### Serialized drama

Separate three scales: what the current scene turns, what the episode must resolve, and what the season deliberately carries. Preserve exact continuing dependency IDs and approved mysteries. An act-out or tag must change pressure or interpretation, not merely stop. Do not solve the serial engine to strengthen one scene, and do not use continuation to excuse missing local consequence.

### Feature or whole short

Audit cumulative causality, escalation, character choices, setup/payoff distance, and ending responsibility across the complete work. Fit notes to the selected structural model rather than percentage targets.

### Documentary and interview-led work

Separate verified fact, participant assertion, question, interpretation, planned access, and unknown outcome. A revision may strengthen comparison, context, follow-up logic, or transparency; it must not fabricate answers, causation, access, actuality, or a predetermined reveal.

### Commercial, music video, and short-form

For a commercial, test the supplied claim, proof, audience tension, and action inside runtime without inventing performance evidence. For a music video, revise performance, motif, spatial, rhythmic, conceptual, or narrative progression without forcing dialogue or a feature arc. For short-form, make orientation and payoff timely without confusing withholding with retention.

## Diagnosis is not rewrite

`script-revision-plan.json` ends before page work begins. Keep out:

- rewritten scenes, action paragraphs, dialogue, transitions, or alternate endings;
- a Fountain document or screenplay text field;
- speculative canon presented as the solution;
- approvals that the user did not give.

A proposed change should be testable after rewriting. “Shorten the scene” is not testable enough. “Remove the repeated refusal beat while preserving the first refusal and the later concession, then verify that the concession still follows the discovered cost” identifies an operation and a preservation check without authoring the scene.

After review, a separate rewrite task consumes only items whose status is `approved`. Deferred and rejected items remain visible. Revalidate source mappings, constraint tests, setup/payoff links, continuity, and downstream artifacts after the rewrite.

## Sources

- ACMI, [Screenwriting](https://www.acmi.net.au/education/school-program-and-resources/film-it-screenwriting/) and [Script to storyboard](https://www.acmi.net.au/education/school-program-and-resources/script-storyboard/): public educational guidance on visible action, setting, objects, dialogue, character behavior, and scenes advancing screen story.
- Academy of Motion Picture Arts and Sciences, [Screenwriting Resources](https://www.oscars.org/nicholl/screenwriting-resources): public professional resources for recognizable screenplay presentation and submission-script practice.
- PBS, [Editorial Standards](https://www.pbs.org/standards/), [Accuracy](https://www.pbs.org/standards/accuracy/), [Fairness](https://www.pbs.org/standards/fairness/), and [Transparency](https://www.pbs.org/standards/transparency/): public standards used to preserve evidence, context, participant representation, sourcing, and uncertainty in nonfiction revision.

All guidance above is a new operational synthesis. No source screenplay, course lesson, proprietary notes, or source prose is reproduced.

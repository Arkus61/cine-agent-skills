# Speculative systems

Use this reference when technology, magic, anomalous ecology, or a hybrid interaction changes what characters can do. A system is a causal contract, not a catalogue of impressive effects.

## 1. Decide whether a system is needed

Add a system when at least one of these is true:

- the brief explicitly supplies it;
- a declared story event depends on repeatable behavior;
- characters make consequential choices about access, use, failure, or interpretation;
- downstream writers need stable limits to avoid contradiction.

Do not add magic to fantasy-adjacent imagery, advanced technology to an ordinary contemporary tool, or an explanatory mechanism to deliberate ambiguity. A contained workplace drama may need locations, institutions, material access rules, and terminology while correctly leaving `systems` and `production_assets` empty.

## 2. Write the system contract

Define each system independently with:

| Part | Question |
|---|---|
| Input | What energy, material, information, state, skill, permission, or sacrifice is required? |
| Transformation | What repeatable relation changes the input? Keep unknown mechanisms unknown. |
| Output | What observable result occurs? |
| Dependency | What environment, device, organism, institution, or practice must remain available? |
| Cost | What is consumed, risked, damaged, owed, exposed, or displaced by use? |
| Limit | What can the system never do, where does it stop, or under what condition does it fail? |
| Evidence | What can characters actually observe, measure, remember, or dispute? |
| Consequence | What access, choice, conflict, knowledge, power, or outcome changes? |

The `systems` collection summarizes inputs, outputs, dependencies, and rule references. The `rules` collection holds the enforceable statement, cost, limit, contradiction checks, provenance, approval state, and story consequence.

## 3. Separate costs from limits

A cost permits use but makes it consequential. A limit defines inability or boundary.

Useful cost classes:

- depletion of energy, material, health, time, attention, memory, or opportunity;
- exposure to detection, pollution, retaliation, debt, obligation, or public scrutiny;
- maintenance, training, coordination, permission, or recovery;
- transfer of burden to another person, group, place, or later time.

Useful limit classes:

- range, duration, precision, capacity, compatibility, timing, or environmental condition;
- inability to distinguish cause, intention, identity, truth, or future outcome;
- dependence on a rare input, trained operator, institution, location, or prepared state;
- failure under overload, interference, contradiction, damage, or missing knowledge.

Avoid a cost that never affects behavior and a limit that disappears whenever the plot needs it. "It is tiring" is weak until the amount of lost capacity changes a choice. "It cannot solve the central problem" is too vague until the prohibited result or operating boundary is named.

## 4. Design power through access

For every capability, ask:

- Who can use it directly?
- Who supplies inputs, training, maintenance, permission, or interpretation?
- Who is excluded by cost, geography, law, body, language, or status?
- Can use be detected, audited, copied, blocked, countered, or monopolized?
- Who receives the benefit, and where do waste and risk go?
- What changes when access expands or fails?

Power is not balanced merely because an opposing power exists. Balance comes from specific asymmetries in information, timing, cost, vulnerability, scale, and legitimacy.

## 5. Make technology and magic coexist coherently

When two systems coexist, define each before their interface. Test the interaction matrix:

| Interaction | Required decision |
|---|---|
| Technology observes magic | State what the instrument measures and what it cannot infer. |
| Magic affects technology | State the affected component, range, cost, and failure behavior. |
| Technology reproduces magic | Decide whether it copies an output, a process, or only an appearance. |
| Magic replaces technology | Trace maintenance, access, labor, and institutional consequences. |
| Systems conflict | Name the condition and which rule takes precedence. |
| Systems amplify | Add a combined cost and limit; do not grant unlimited multiplication. |

A shared visual effect does not prove a shared mechanism. Correlation does not prove agency. One system's terminology must not silently redefine the other.

## 6. Write enforceable rules

Each `<project>-WR###` rule contains:

1. **Statement:** one repeatable relation in observable terms.
2. **Cost:** the consequence of attempting or completing use.
3. **Limit:** the boundary or impossible result.
4. **Contradiction check:** a scenario that would challenge the rule, the expected behavior, and the repair path.
5. **Provenance:** supplied, inferred, proposed, or approved.
6. **Canon status:** canon or proposal.
7. **Basis:** the source fact, reasoning, or approval record.
8. **Story consequence:** the exact choice, risk, knowledge state, conflict, or outcome the rule changes.

Prefer several narrow rules over one rule with hidden exceptions. Preserve stable IDs when a rule is revised; record the new approved meaning rather than renumbering every downstream reference.

## 7. Test contradictions explicitly

A contradiction check is a forward-facing test, not a reassurance. Use cases such as:

- a later scene exceeds the declared range or duration;
- a character infers intent from a system that only detects material change;
- a capability works without its declared input or dependency;
- a costly action is repeated without paying or transferring the cost;
- a local observation is applied at regional or planetary scale;
- a hybrid effect bypasses both parent systems' limits.

Resolution choices are: revise the later scene, identify mistaken character belief, preserve unresolved evidence, or explicitly propose and approve a changed rule with downstream consequences. Do not silently add an exception.

## 8. Control terminology and knowledge

Separate four layers:

- **Objective rule:** what the approved world contract asserts.
- **Observed evidence:** what has happened within the supplied material.
- **Character model:** what a person believes the evidence means.
- **Working proposal:** what the development team is testing.

A name such as "hive," "curse," "signal," or "portal" may begin as a character or production term. Define its usage boundary so repetition does not convert a hypothesis into objective canon.

## 9. Preserve canon and proposal boundaries

Use provenance and canon status together:

| Provenance | Normal status | Meaning |
|---|---|---|
| supplied | canon or proposal | Directly present in the brief; proposal status remains valid when the brief supplies only an option, aesthetic, belief, or disputed claim. |
| inferred | proposal | A cautious implication from supplied facts; never self-approves. |
| proposed | proposal | A new creative decision awaiting approval. |
| approved | canon | Explicitly accepted for downstream use. |

Approval is atomic. Approving a location does not approve its proposed history, culture, system, or visual treatment. An aesthetic list remains visual direction unless a separate causal world proposition is supported and approved.

## 10. Distinguish world entities from production assets

Use `<project>-AS###` only when an entity requires a production representation that must be designed, generated, built, acquired, versioned, or tracked for continuity. Examples can include a hero prop, creature design, device, vehicle, costume, set element, or environment asset.

Do not assign AS IDs to abstract factions, institutions, cultures, historical events, systems, terminology, or rules. A location keeps its LO ID even when it later receives several environment or set assets; those production assets receive separate AS IDs only when actually declared.

## 11. Scale down cleanly

For a contemporary contained drama:

- preserve ordinary physical and institutional constraints;
- write rules about access, schedule, maintenance, authority, privacy, or evidence only when story-relevant;
- use `social`, `material`, or no systems as appropriate;
- leave magic and speculative technology absent;
- create no production asset unless the story specifically requires a trackable designed object or environment.

The absence of a speculative system is a successful design decision when the supplied story does not need one.

## Source grounding

This reference uses original operational synthesis informed by OpenStax's open educational discussions of energy transfer and material cycles in ecosystems, and of technology, environment, institutions, and population as interacting forces in social change. These sources provide reasoning models rather than fictional content. Exact pages and licensing notes are registered in `docs/source-register.md`.

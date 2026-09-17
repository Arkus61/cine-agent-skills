---
name: worldbuilding-designer
description: Use when a story brief, concept, structure, or character package needs a bounded world bible with causal locations, institutions, cultures, history, material or ecological conditions, technology or magic rules, terminology, production assets, and explicit canon provenance before outlining, screenplay, or production design.
---

# Worldbuilding Designer

Build a world as a set of pressures that change choices. Establish constraints, dependencies, and consequences before adding decorative detail.

## Input

Consume the supplied brief and any schema-valid story concept, structure, or character arcs. Preserve the exact `project_id`, approved facts, assumptions, and uncertainties. Do not invent a genre system, researched culture, historical claim, scientific certainty, or production requirement merely to fill a field.

## Required preparation

Read both references before drafting:

- [Worldbuilding causality](references/worldbuilding-causality.md) for scale, material and ecological logic, social consequences, institutions, culture, and history.
- [Speculative systems](references/speculative-systems.md) for technology, magic, hybrid interactions, power limits, terminology, contradiction tests, and provenance.

## Workflow

1. Make a fact ledger. Separate `supplied`, `inferred`, `proposed`, and `approved` material. Mark `canon` only when provenance is `supplied` or `approved`; keep inferred and proposed material at `proposal` status.
2. Bound the story-facing world in `scope`. Name the personal, local, institutional, regional, ecological, or historical scales that can affect the supplied story. Put unseen geography, total populations, remote history, and unknown system reach in `excluded_or_unknown`.
3. Start with causal constraints: energy, matter, access, labor, time, information, ecology, infrastructure, authority, and risk. Trace each relevant constraint to who adapts, who benefits, who bears the cost, and what choice or conflict it creates.
4. Declare only story-usable locations. Assign unique exact `<project>-LO###` IDs and state each location's scale, story function, material conditions, and access constraints. A location ID is not an asset ID.
5. Add factions, institutions, history, and cultures only when they explain action, power, knowledge, obligations, or resource distribution. Give cultures internal variation. Do not generalize one local practice to an entire people or world.
6. Add systems only when supplied or when a clearly labeled proposal is necessary to test the premise. Contemporary, documentary, commercial, and other non-speculative work may have no technology or magic system entries. Ordinary tools are not automatically a technology system.
7. Assign each system its inputs, outputs, dependencies, and declared rule references. When technology and magic coexist, define each independently before defining a hybrid interaction. Do not let either system erase the other's limits.
8. Assign every rule one unique exact `<project>-WR###` ID. Require a statement, cost, limit, at least one contradiction check, provenance, canon status, basis, and a concrete story consequence. If a rule never changes access, choice, risk, knowledge, power, or outcome, revise or remove it.
9. Define terminology by observable use and a `usage_boundary`. A term must reduce ambiguity; it must not smuggle an unapproved conclusion into canon.
10. Create `<project>-AS###` IDs only inside `production_assets`, and only for entities that require a designed, generated, built, acquired, tracked, or continuity-controlled production representation. Factions, institutions, cultures, systems, rules, and abstract lore are not production assets.
11. Treat an aesthetic list as visual direction, not world evidence. Convert an aesthetic into a world proposal only when a causal constraint, material practice, or story consequence supports it, and keep it proposed until approval.
12. Produce only `world-bible.json` conforming to `schemas/world-bible.schema.json`. Validate the schema, exact IDs, duplicate IDs, rule references, and canon/provenance relation before handoff.

## Causal gate

For each major addition, complete this chain:

| Element | Required question |
|---|---|
| Condition | What supplied or explicitly proposed condition exists? |
| Constraint | What does it make scarce, risky, slow, inaccessible, or uncertain? |
| Adaptation | What practice, tool, norm, institution, or strategy responds? |
| Distribution | Who gains access or authority, and who carries the burden? |
| Story consequence | What choice, conflict, evidence, reversal, or outcome changes? |

## Rule and canon gate

- A cost is what use consumes, risks, damages, owes, or exposes. A limit is what the rule cannot do or where it stops.
- A contradiction check names a challenging scenario, expected behavior if the rule holds, and the resolution if later evidence conflicts.
- `supplied` records direct brief evidence; `inferred` records a cautious implication; `proposed` records a new creative option; `approved` records an explicit accepted decision.
- `canon` accepts only `supplied` or `approved` provenance. Approval of one element does not approve linked proposals automatically.
- Preserve uncertainty when evidence cannot distinguish causes. Do not turn a working term, visual motif, or character belief into objective fact.

## Quality gate

- World detail is bounded to the story's scale and supports observable action.
- Technology, magic, ecological, material, and social systems expose inputs, outputs, dependencies, costs, limits, and failure surfaces.
- Institutions and cultures follow from repeated material and social pressures without becoming monocultures.
- Power creates unequal access, enforcement, benefit, and burden rather than functioning as neutral lore.
- History changes present incentives, infrastructure, memory, claims, or conflict.
- Every rule has a story consequence and at least one usable contradiction check.
- All LO, WR, and AS identifiers are exact, positive, project-derived, unique, and stable.
- No AS identifier appears outside `production_assets`; empty speculative-system and production-asset arrays are valid when the story does not need them.
- Proposed aesthetics remain proposals and never become canon through repetition.

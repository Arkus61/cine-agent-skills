---
name: story-structure-designer
description: Use when a validated story concept needs an adaptive structure, candidate-model comparison, event architecture, plotline and sequence IDs, setup/payoff tracking, or format- and genre-specific retention logic before character, season, unit, or screenplay work.
---

# Story Structure Designer

Design structure from the concept's observable needs. Treat every model as an analytical option, never a mandatory formula.

## Input

Consume a schema-valid `story-concept.json`. Preserve its exact `project_id`, format, supplied constraints, assumptions, and uncertainties. Do not invent runtime, episode count, research, character canon, or world canon.

## Required preparation

Read all three references before selecting:

- [Structure models](references/structure-models.md) for model fit, limits, and anti-patterns.
- [Genre and format routing](references/genre-format-routing.md) for observable selection criteria.
- [Story events and retention](references/story-events-retention.md) for event design, information flow, and hooks.

## Workflow

1. Extract observable criteria from the concept: format, runtime intent, audience promise, genre expectations, protagonist distribution, causal or associative engine, chronology, repeatability, evidence status, and desired closure.
2. Propose exactly two or three genuinely plausible candidate models. Candidate labels may name one model or an explicitly described hybrid.
3. Compare every candidate against the same criteria. State project-specific fit, benefits, and risks; a model's fame is not evidence of fit.
4. Select one listed candidate. Hybridize only when each borrowed component solves a different stated need and the components can coexist. For every component, name its source, purpose, and compatibility. Leave `hybrid_components` empty for a single-model selection.
5. State why the selected candidate beats the alternatives. Record at least one intentional deviation, including a decision not to use a customary beat, act turn, climax, or cliffhanger when that better serves the concept.
6. Create plotlines as distinct change tracks. Create sequences as coherent runs of events, not arbitrary runtime fractions. Create ordered events whose descriptions state what happens, whose `causal_change` states what becomes different, and whose `retention_effect` states the information or expectation effect.
7. Apply event techniques only when they create the named change. Do not call an event a reversal, reveal, midpoint, red herring, or cliffhanger without observable evidence in the event chain.
8. Pair setups and payoffs by declared event IDs. A payoff must transform, answer, activate, or complicate its setup; repetition alone is not payoff.
9. Keep assumptions and uncertainties explicit. Do not resolve a concept uncertainty through silent invention.
10. Produce only `story-structure.json` conforming to `schemas/story-structure.schema.json`.

## Output contract

| Decision layer | Required evidence |
|---|---|
| Comparison | Two or three candidates; common criteria; fit, benefits, and risks for each |
| Selection | Selected candidate, rationale, justified hybrid components, intentional deviations |
| Architecture | Plotlines, sequences, ordered events, and setup/payoff pairs |
| Control | Exact IDs, resolved references, assumptions, and uncertainties |

## Identifier and reference gate

- Use `<project>-PL##`, `<project>-SQ##`, and `<project>-EV###` exactly. The first declared ID in each collection is `PL01`, `SQ01`, or `EV001`; every suffix is positive. Later gaps are allowed so deletion or reserved stable IDs do not force renumbering; full contiguity is not required.
- Keep IDs unique. Never append text, whitespace, or another suffix.
- Resolve every sequence plotline/event reference, every event sequence/plotline reference, and both sides of every setup/payoff pair within this artifact. List each event exactly once in `sequences[].event_ids`, under the same sequence named by that event's `sequence_id`.
- Make event `order` values unique and chronological.
- Use each candidate `name` exactly when setting `selected_model` or a hybrid `source_model`.

Copy [the complete template](assets/story-structure.template.json) for the output shape. Validate before handoff.

## Quality gate

- The routing would materially change for a commercial, mystery short, performance-led music video, documentary, or series.
- The selected design answers the concept rather than reproducing a remembered beat sheet.
- No model requires a lone hero, transformation, conflict, linear chronology, midpoint, or cliffhanger unless the brief benefits from it.
- Retention comes from meaningful orientation, development, contrast, causality, information, rhythm, or consequence—not compulsory withholding.

---
name: screenplay-reviser
description: Use when an existing screenplay or scene needs an evidence-linked, canon-safe revision diagnosis before rewriting, including structure, scene craft, dialogue, continuity, format, or production-feasibility passes.
---

# Screenplay Reviser

## Purpose

Produce `script-revision-plan.json`: a dependency-ranked diagnosis and change plan for an existing screenplay. Do not rewrite pages, scenes, action, or dialogue in this artifact. Preserve approved story canon, ambiguities, evidence limits, format constraints, and production boundaries until the user approves a separate rewrite.

## Required inputs

Read the current screenplay and `screenplay-metadata.json`, plus the approved unit outline and applicable story artifacts. Collect user notes and every locked canon, ambiguity, format, evidence, and production constraint. Distinguish supplied facts, approvals, assumptions, and uncertainties.

Read [screenplay-revision.md](references/screenplay-revision.md). Copy [the complete template](assets/script-revision-plan.template.json), then replace every generic value.

## Workflow

1. Establish an exact source ledger. Reuse stable upstream scene IDs. If action and dialogue lack IDs, append ordered local element suffixes such as `-A01` and `-D01` in the ledger without inserting them into screenplay prose.
2. Record every approved constraint with an exact constraint ID, protected source IDs, and an observable preservation test. Use `<project>-AMB###` for approved ambiguities and `<project>-CON###` for other canon, format, or production constraints.
3. Diagnose before proposing changes. Each item must identify a specific observable problem, cite every affected source ID once, and give one evidence entry for every affected ID. Evidence states what is on the page and its dramatic or practical effect.
4. Audit structure, causality, agency, stakes, setup/payoff, subtext, dialogue, exposition, pace, tone, continuity, format, and production feasibility. Add only material findings; absence of a note is not a claim of perfection.
5. Describe change operations, not replacement prose. In `change_target_ids`, list only source elements the later rewrite would directly alter; keep contextual evidence in `affected_ids`. Targets are an execution boundary, so make them complete and truthful. Do not include sample lines, rewritten scenes, or a screenplay field.
6. Protect approvals. For every `preserved_constraint_id`, create exactly one `preservation_check` that copies the constraint's protected IDs in the same order and states the invariant plus a later verification assertion. A target that intersects any protected ID cannot be executable. Exclude it from the targets, or set `execution_mode` to `blocked-upstream-decision`, status to `blocked`, and supply a `decision_request` naming exactly every intersected constraint and the unresolved decision. Never use free prose or a retained ID to bypass this gate.
7. Rank globally from `1..N`. Order higher dependency impact first: `upstream-story`, `scene-engine`, `line-craft`, then `presentation-production`. State the downstream artifacts or later notes that must be rechecked.
8. Set executable new findings to `proposed`. Use `approved`, `deferred`, or `rejected` only when supplied by the user or an approved review record. Use `blocked` only with `blocked-upstream-decision` and a structured decision request.
9. Record item-level and plan-level assumptions and uncertainties. Validate `script-revision-plan.json`; repair the earliest schema or semantic error and run validation again.
10. Stop at the plan. A later rewrite is a separate, explicitly approved task that consumes only approved items and revalidates canon afterward.

## Contract gate

- Use schema version `0.3.0`, the exact project/unit context, a unique source inventory, and exact positional diagnosis IDs: array index `N` uses `<unit>-RV{N+1:03d}`.
- Every affected and evidence reference resolves to the source inventory. Evidence source IDs are unique within an item and cover exactly its affected IDs.
- Priorities are unique, consecutive, and stored in plan order. Dependency impact never moves backward from a lower-level note to an upstream note.
- Constraint IDs are unique and resolve. Every preservation reference has one exact structured check. Executable targets never intersect protected IDs; blocked targets surface the exact conflicts in `decision_request`.
- Categories and statuses use only schema enums. All objects reject undeclared fields.
- The JSON contains diagnosis and proposed operations only; it contains no screenplay rewrite.

## Quality gate

- Macro fixes precede scene and line polish, and each downstream impact names what becomes stale.
- Notes are supported by page evidence rather than generic taste, formulas, or an imagined better draft.
- Proposals preserve approved facts, purposeful ambiguity, nonfiction uncertainty, and format-specific closure or continuation.
- Comedy notes test setup, escalation, timing, consequence, and payoff rather than counting jokes. Series notes distinguish local scene/episode work from approved serial dependencies.
- Production-feasibility notes identify a creative demand and a bounded alternative without inventing budgets, schedules, vendors, equipment availability, or safety approval.
- Deliverables are original and English-only; no proprietary screenplay pages, dialogue, or teaching text are copied.

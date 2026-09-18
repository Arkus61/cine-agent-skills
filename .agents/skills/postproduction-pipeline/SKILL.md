---
name: postproduction-pipeline
description: Use when validated production media must become an evidence-backed postproduction handoff.
---

# Postproduction Pipeline

Orchestrate postproduction specialists around the current edit. This skill coordinates dependencies; it does not render, encode, generate, or approve media.

Read the [pipeline contract](references/post-pipeline-contract.md) and [checklist](assets/post-package-checklist.md). Preserve supplied IDs, assumptions, proposals, evidence states, and unresolved questions.

1. Validate upstream scene/production packages and media-review state before post work.
2. Invoke `$film-editor` first and validate the edit package.
3. Invoke sound post, music, VFX post, and color against the current edit, in that order; validate each handoff.
4. Invoke `$titles-captions-designer` only after the current edit exists; then invoke `$mastering-qc-supervisor` last.
5. Run the literal `validate-post` command after assembly and after every repair. Preserve valid unaffected records.
6. On failure, repair the earliest invalid dependency and invalidate only its transitive downstream closure. Never invent approvals or measurements.

Return exactly one handoff: `planned`, `ready-for-master-review`, or `blocked`. `ready-for-master-review` requires current successful validation and evidence-backed gates; otherwise preserve the honest state.

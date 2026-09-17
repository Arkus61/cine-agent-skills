# Continue Cine Agent Skills v2

This continuation record documents the recovered branch and the final v2.0.0 planning-core handoff. It is not a claim that creative choices, source freshness, media readiness, or delivery approval have been established by tests.

## Current authority — 2026-09-15

### Finalization checkpoint

The canonical Ninel demonstration passes direct full-project validation as `series` with `animation` + `ai`. It is a minimal two-unit structural demonstration, with post plans for E01 only; its media review remains `awaiting-media`. Read `examples/ninel-v2-notes.md` for borrowed VFX/AI treatments that remain proposals requiring human creative reconciliation.

The release-facing metadata is synchronized to `2.0.0`; the exact catalog is 37 project-local skills (12 preserved v1 + 25 v2); explicit story, production, post, and full-project CLI gates are available; and deterministic archive tooling is part of the final handoff. The legacy `core-v0.1` and `full-v1` examples remain unchanged and valid.

This release freezes the current planning scope. Full format/mode fixture expansion, source-freshness comparison, executed behavioral evaluations, and the Blender adapter remain outside the release and are documented as future extensions. No media is generated or inspected by the repository.

Use `make check`, all explicit example targets, `make release-archive`, and `git diff --check` for the final gate. Preserve the unrelated untracked `uv.lock`.

Follow `superpowers/plans/2026-09-13-cine-rebaseline.md` and its direction amendment for historical decisions. The earlier audit paragraphs below are historical evidence, not current integration acceptance.

### Historical audit baseline

Audit baseline `7fbd7c7`: `make check` passes 1202 tests, but direct `validate-project examples/ninel-v2 --format json` fails. It reports unexpected `NINEL-E01`, missing `NINEL-U01` and two uncovered story events. The example is short/hybrid instead of the approved series/animation+ai target, and its story concept has a different mode. The previously reported 31 tests did not test Ninel v2.

| Integration area | Historical state | Superseded next action |
|---|---|---|
| Full-project validator | Reopened; implemented | Real complete-project fixtures, provenance and CLI tests |
| Full creative pipeline | Reopened; bundle exists | Retained outputs from actual behavioral evaluations |
| 37-skill catalog | Present; gate completion pending | Complete bundle mapping review |
| Format/mode coverage | Partial | Full-project matrix, not only membership selection |
| Ninel v2 | Failing | Approved profile, coherent source/ID inventory, direct CLI and regression test |
| Freshness | Contract work pending | Source change under stable IDs and selective downstream detection |
| Release | Blocked | All core gates, documentation, archive and clean bootstrap |
| Blender | Separate design only | Reviewed pilot contract before adapter implementation |

That table records the reopened state before finalization; the current scope and evidence are recorded above.

Rebaseline implementation: unknown `validate-project --profile` now exits 2 through argparse. The regression first reproduced exit 1, then all 58 CLI/project tests passed. This fixes one boundary and does not close full-project acceptance.

## Recovery

On 2026-09-08 the previous conversation reached its length limit. The source repository survived, including the active v2 worktree at commit `a7d2e0a8babe862d854be03b0e46acfb6092e3ca`. The August 21 audit and v1 ZIP are older than that source; do not rebuild v2 from them.

The source worktree was still being modified by another worker. A separate repository was cloned with complete history and a consistent snapshot of its uncommitted files. `recovery-source-snapshot-2026-09-08.json` records the copied file hashes. Continue on `feature/v2.0-chat-recovery`; do not copy files back over the other worktree. Its later changes require a normal comparison/merge before adoption.

## Binding design

- `superpowers/specs/2026-08-06-cine-agent-skills-v2.0-design.md` is the approved v2 scope.
- The v2 postproduction and integration/release plans under `superpowers/plans/` define the remaining stages.
- Repository skills stay in `.agents/skills`; they are a portable project, not personal-skill installations.
- This system creates and validates creative plans. Media generation, editing, rendering, encoding, publishing and rights clearance are outside v2.
- Existing v0.1 and v1 packages and schema versions remain unchanged. The planning-core release metadata is now `2.0.0`.

## Historical task map — superseded for integration

| Area | State | Next action |
|---|---|---|
| Foundation | Accepted, 4/4 | Preserve compatibility. |
| Story | Accepted, 10/10 | Preserve accepted contracts. |
| Production | Accepted, 8/8 | Preserve source and media evidence boundaries. |
| Post 1–5 | Accepted | Editor, sound, music, VFX post, color. |
| Post 6: titles/captions | Accepted | Preserve `eb06c2e` and fresh forwards in `fc6cb24`. |
| Post 7: mastering/QC | Accepted | Preserve closure commits through `36d0306` and fresh forwards in `fbd348e`; implement Post 8 next. |
| Post 8: post package validator | Accepted | Preserve `d70558a`, `f9b0e39`, and CLI closure `0c159ec`; proceed to Post 9. |
| Post 9: post pipeline | Accepted | Preserve `382becf` and forward evidence in `docs/postproduction-pipeline-forward-report.md`; integration/release remains next. |
| Integration/release | Superseded historical checkpoint | Use the current authority section above. |

## Verification evidence

The recovered Titles/Captions changes passed 16 focused tests, but independent review found two additional provenance/approval gaps. Their report is `titles-recovery-review.md`.

All four original findings were reproduced independently on archived commit `a7d2e0a`: four failing regressions. The original tests and output are preserved in `titles-recovery-original-regressions.py.txt` and `titles-recovery-original-red.txt`. These are historical evidence, not tests to run against the revised schema.

Both legacy examples passed in the recovered checkout. Runtime dependencies were copied from the surviving environment; the editable project entry point was installed offline and verified to resolve this checkout. This is not a clean-bootstrap release test.

Titles/Captions fresh post-fix forwards are recorded in `docs/titles-forward-vertical-postfix-report.md` and `docs/titles-forward-widescreen-postfix-report.md`; both validate without inventing translation, timing, or approval. Mastering/QC is accepted after three TDD closure rounds (`36d0306`), independent targeted review, fresh `1172 passed` repository verification, legacy compatibility checks, and the specifications-only / partial-r2 forwards in `fbd348e`. The partial-r2 plan passes only four exact supplied metadata checks and remains `not-ready`.

Post 8 is accepted after the final independent re-review: the exact eight-file post-v2 package, canonical unit and edit-segment coverage, nested shot/media references, schema-first diagnostics, and `validate-post` CLI JSON/exit behavior all pass. The post/CLI and compatibility tests are green; the full repository gate remains green at 1182 tests.

Post 9 is accepted after catalog and contract review, fresh repository verification at 1185 tests, and two forward scenarios: Ninel with incomplete media remains `planned`; documentary earliest-invalid repair remains `blocked` while preserving unaffected records. The next unfinished scope is full-project integration and release gating; no v2 release claim is made.

Integration Task 1 (full-project validator) is accepted in `fd29d05`, `b1b7fff`, and `ae507a9`: `validate-project` now enforces schema-first project boundaries, safe layer paths, production-to-post media provenance, and deterministic CLI diagnostics. Focused project/CLI tests and the full gate pass at 1189 tests. Task 2 is in progress.

Integration Task 2 is accepted in `598b952` and `2c39290`: the `full-creative-pipeline` orchestrator bundle, contract/checklist, metadata, and three observable evaluation cases are present; catalog tests pass. It coordinates story → production → post and uses `validate-project` without performing media operations.

Use `make check`, all explicit example targets, `make release-archive`, and `git diff --check` for the final development gate. Read each task's report for its focused RED/GREEN and forward evidence; do not infer creative approval, source freshness, or media readiness from structural tests.

## Known limits to preserve

- Department-local registries prove internal consistency, not the authenticity of copied upstream sources. Task 8 must bind them to actual post/story/production inputs.
- Music has two documented conservative prose false rejections; see `v2-progress-audit-2026-09-05.md`.
- The canonical Ninel v2 project is a minimal structural demonstration; borrowed treatments remain proposals and media remains `awaiting-media`.
- Full format/mode fixture expansion, freshness comparison, executed behavioral evaluations, and Blender execution remain future extensions outside this frozen planning release.
- Keep the recovered untracked `uv.lock` intact; it is not part of accepted changes.

Update this file with accepted commits, test results and the next task whenever a continuation checkpoint is saved.

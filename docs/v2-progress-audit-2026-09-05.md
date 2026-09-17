# v2 progress audit — 2026-09-05

This is a development snapshot, not release approval. The audited base is `de8d9f3`, with an unfinished Music Story Designer change in the worktree.

## Implementation and acceptance

| Layer | Accepted tasks | Remaining work |
|---|---:|---|
| Foundation | 4/4 | Preserve shared contracts and compatibility. |
| Story | 10/10 | Acceptance is recorded in git and the production ledger; no surviving story progress ledger was found. |
| Production | 8/8 | Preserve accepted package validation and media evidence boundaries. |
| Postproduction | 5/9 | Film Editor, Sound, Music, VFX Post and Color accepted; titles/captions, mastering/QC, package validation and orchestration remain. Music retains documented minor usability limitations. |
| Integration/release | 0/8 | Full-project validation, orchestration, catalog lock, profile matrix, Ninel v2 example, documentation/version, archive and clean bootstrap. |

Accepted-task count is 27/39 after the fixes and reviews below. This is an inventory ratio, not an estimate of effort or release readiness. The remaining 12 tasks are four postproduction tasks and eight integration/release tasks.

## Fresh verification at the start of this audit

- `make check`: repository validation passed; **1 failed, 1053 passed**. The unfinished music template's explicit prohibition on imitation was falsely rejected by its prose guard.
- `make validate-core-example`: passed.
- `make validate-full-example`: passed.
- Current inventory includes 31 skills; the release target is 37.
- Current CLI offers repository, artifact, scene, story and production validation. `validate-post` and `validate-project` do not yet exist.

## Priorities and risks

1. Continue with Titles/Captions, then Mastering/QC. Preserve accepted department contracts and their recorded review outcomes.
2. Build remaining department logic in focused semantic modules and dedicated test files.
3. Implement authoritative cross-artifact validation in `validate-post` and `validate-project`. Embedded source registries establish internal consistency, not external authenticity. Music theme IDs are local aliases: story concept currently exposes theme strings, so source mappings must be authenticated during integration.
   `ProjectIndex` currently has no VFX effect/version registry; Task 8 must establish that authoritative lookup as well, rather than trusting the post plan's copied registry.
4. Complete the literal 37-skill release catalog and all format/mode fixtures. The incremental catalog test proves only the current inventory.
5. Produce the complete Ninel v2 example before declaring end-to-end readiness.
6. Update v1-facing documentation and version metadata only at the planned release stage; current package version remains `1.0.0`.
7. Verify tracked-only bootstrap and reproducible archive integrity. No v2 release artifact is currently approved.

The common artifact module is 4,802 lines and its legacy test file is approximately 12,900 lines. Keep new department logic in focused modules; avoid broad refactoring while contracts are still being completed.

No media generation, editor/DAW control, rights-clearance decisions, publishing or delivery automation is part of the approved v2 scope.

## Work continued after the initial audit

Music implementation and structural fixes were committed as `4074b84`, followed by review fix `92ad005`. The controller independently confirmed repository validation, 1,061 passing tests (80.81 seconds), 49 focused bundle/contract tests, and clean diff. The scoped reviewer confirmed both original findings addressed with no new Critical/Important breakage. Task 3 is accepted for continued development, not release approval.

A fresh independent scenario correctly preserved speech clarity, intentional silence, and uncertainty about media and rights. Its first validation failed because it used `SP###` spotting IDs instead of the required `MU###`; changing only those IDs made it valid. This is a documentation-usability finding, not a first-pass success.

The fix explicitly documents both spotting and cue IDs. New independent prescribed scenarios used them correctly: PULSE commercial passed first validation; HOLLOW horror passed after a wording repair. Two non-blocking false-rejection limitations remain for final review: the imitation guard rejects `no recognizable song or artist imitation`, and the completion guard rejects a trailing future condition such as `The cue will be approved after the director signs off`. These are not evidence of unsupported approvals being accepted.

Task 4 VFX Post Supervisor is accepted: implementation `2572b1e`, fix `669aa62`. Explicit media roles prevent plate-only records from being approved as outputs, while dual source/output roles permit downstream reuse. Candidate/changes-requested require a current output version. The scoped reviewer closed all findings with no new breakage. The controller independently confirmed 19 focused tests, repository validation, 1,080 passing tests (64.84 seconds), and both legacy profiles.

Fresh WOOD creature planning passed first validation; GLASS screen replacement required a media/version-ID repair, with the invalid original retained. Both final artifacts also passed migration to explicit media roles. Migration is not a new first-pass trial. The current inventory is 32 skills; the release target remains 37. No release archive or full-project acceptance is claimed.

## Color acceptance — 2026-09-07

Task 5 Color Grading Designer is accepted: implementation `b3f14e4`, record-binding fix `5021385`. Independent review initially found malformed unused metadata/evidence records were accepted. Two rejecting regressions failed before the fix while two valid-unused counterexamples passed; all now pass. Scoped re-review returned 0 Critical / 0 Important / 0 Minor, Approved.

Fresh controller verification: repository valid, `1104 passed in 40.48s`, both legacy profiles valid, and frozen DAWN forward remains valid without migration. The initial daylight/animation trials crossed an in-flight schema change and needed repairs; their originals remain preserved. The subsequent frozen-contract trial passed first validation and made no unsupported inspection or approval claims. Evidence and checklists are committed in `docs/color-*.md` and companion JSON files.

Current inventory is 33 skills, target 37. Titles/Captions has an independent no-skill baseline and execution brief, but no implementation yet. No v2 release readiness is claimed.

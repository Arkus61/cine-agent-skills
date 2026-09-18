# Color Task 5 — independent review

Reviewed implementation `d8c498d..b3f14e4`; read-only reviewer `color_task_review`. Verdict: Needs fixes; 0 Critical, 1 Important, 0 Minor.

## Finding

`src/cine_skills/color_plans.py:58-88,177-187`: internal binding is enforced only when evidence is referenced by an item, observation, or approval. An unreferenced evidence record can name only part of its item's segment set, and a metadata record can pair a version with a segment that version does not cover, while the artifact remains valid. A focused read-only probe confirmed that a two-segment item with an unreferenced one-segment approval-evidence record returns `[]`.

Validate every metadata record against `version_segments`, and every evidence record against its referenced item's complete segment set and version relationship regardless of whether an item-level evidence list consumes it. Add regression tests for both malformed records, with valid unused-record counterexamples.

## Positive findings

Strict schema and ownership; constrained states and display standards; no-media planning; distinct source observation versus output-match evidence; value-matched approvals; focused module and tests. No other requirements were unverifiable from the diff.

## Fix scope

Only record-level internal consistency for Color Task 5. No cross-artifact authentication subsystem, no new media operations, no legacy behavior changes, and no unrelated prose guards. Reproduce the missing gates before implementation, run focused/full/legacy checks, and preserve this original review.

## Scoped re-review — 2026-09-07

Fix `5021385`, reviewed against `6b6078b`: original finding addressed; 0 Critical, 0 Important, 0 Minor. Task quality Approved. No new breakage or out-of-scope observations.

Metadata now requires its segment to be covered by its linked media version (`color_plans.py:64-68`). Every evidence record requires the item's complete segment set, a version covering those segments, and the appropriate source/output version for its claim (`color_plans.py:90-103`). Valid unused-record counterexamples remain accepted (`test_color_plans.py:238-245,265-273`).

Controller verification at fix HEAD: full gate exit 0, repository valid, `1104 passed in 40.48s`; both legacy profiles valid; frozen forward revalidation valid without migration; diff check clean. Color Task 5 accepted for continued development, not release approval.

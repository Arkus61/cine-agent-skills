# VFX Post Task 4 recovery checkpoint

Base commit: `0590a49`. Task 4 is unfinished and not accepted.

## Evidence recovered from conversation

The previous implementer reported an initial RED of 8 failing tests before product code: the VFX post schema was absent. A second focused RED of 2 failures covered structured actionable workstreams and delivery evidence tied to the exact target. The original local report and raw baseline file are no longer available; these counts are historical conversation evidence, not newly reproduced results.

The independent no-skill baseline handled both scenarios honestly: GLASS screen replacement did not treat a v07 filename or v06 review as v07 approval; WOOD creature composite did not treat verbally reported tracking completion as inspected or delivery-ready. Neither invented exact media timing or QC. Observable gaps were nonstandard artifact/status shape, absent unit-derived post IDs, no exact version/evidence records, and dependencies described in prose rather than addressable ordered edges. This is a reference/output-contract gap, not evidence for adding generic discipline warnings.

## Fresh verification after resuming

`.venv/bin/python -m pytest -q tests/test_vfx_post_plans.py`: **10 passed in 0.33s**.

`.venv/bin/python -m pytest -q tests/test_skill_catalog.py -k vfx_post`: **1 failed, 25 deselected in 0.07s**, because the skill bundle has no files yet.

Saved partial work includes the schema, focused validator, artifact hook, semantic tests and catalog tests. The skill bundle, template, eval and source registration are still missing. The pre-existing untracked `uv.lock` remains outside the task.

## Completion constraints

Follow Postproduction plan Task 4. Preserve exact project/unit ownership and separate preproduction `<project>-FX###` from post `<unit>-FX###`. Keep local version/evidence/dependency checks in `vfx_post_plans.py`, semantic tests in `test_vfx_post_plans.py`, and artifact/catalog hooks minimal. Workstreams need concrete actions, not only labels. Delivery evidence binds item, version and target. Reject stale-version approval and unknown links; preserve valid no-media planning.

Do not add media/editor/render/delivery automation or a universal prose parser. Authoritative upstream effect/version lookup belongs to Task 8; ProjectIndex does not yet provide it. Run full/legacy gates and fresh screen/creature forwards, then independent task review before acceptance.

Controller inspection also identified structural gaps for RED-first checks: unchecked media/evidence/dependency ownership, unknown populated output/delivery references in provisional states, missing dependency backlinks/chain order, and a workstream `complete` state with no evidence gate. Completion must resolve these before the final task review.

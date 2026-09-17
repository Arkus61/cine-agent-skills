# VFX Post Task 4 Implementation Report

Date: 2026-09-05

## Scope completed

- Added the strict `vfx-post-plan.json` schema and local semantic validator.
- Registered artifact validation without adding post-package CLI or ProjectIndex behavior.
- Added the complete `vfx-post-supervisor` skill bundle: concise entrypoint, UI metadata, no-media template, turnover/compositing reference, and review/integration reference.
- Added screen-replacement and creature-composite evaluation cases.
- Registered the general principles used for the schema and supervisory guidance.

The contract preserves distinct preproduction `<PROJECT>-FX###` and post `<UNIT>-FX###` ownership. It requires concrete workstream actions, exact source references, ordered acyclic dependencies with downstream backlinks, and delivery evidence bound to the exact item, current version, and declared target. Unknown populated references are rejected in nonfinal states. Approval rejects stale evidence, and a completed workstream requires inspection evidence for its current item/version. Planning without media remains valid.

## Test-first evidence

Recovered historical evidence records an initial 8-test RED for the absent schema and a later 2-test RED for actionable workstreams and exact delivery binding. Those counts were not reproduced after recovery.

Fresh completion work produced:

- Bundle and template RED: 2 failed.
- Structural validator RED: 4 failed, covering media/version ownership, unresolved populated references, dependency backlinks and execution order, and unsupported completed workstreams.
- Focused GREEN: `.venv/bin/python -m pytest -q tests/test_vfx_post_plans.py tests/test_skill_catalog.py::test_vfx_post_supervisor_bundle_is_complete tests/test_artifacts.py::test_vfx_post_plan_template_is_valid` — 16 passed in 0.57s.

## Fresh verification

- `make PYTHON=.venv/bin/python check` — repository validation passed; 1077 tests passed in 73.10s.
- `make PYTHON=.venv/bin/python validate-core-example` — `core-v0.1` scene package validation passed.
- `make PYTHON=.venv/bin/python validate-full-example` — `full-v1` returned `{"command":"validate-package","errors":[],"profile":"full-v1","valid":true}`.
- `git diff --check` — passed with no output before commit.

Independent forward tests and independent review are controller-owned acceptance gates and are not claimed here.

## Review round 1 fix

Date: 2026-09-05

The media-version contract now requires one or more constrained `source`, `plate`, or `output` roles. Source links accept source-capable versions; current output, review evidence, and delivery evidence require the `output` role. A prior-stage version can safely declare both `source` and `output`. The `candidate` and `changes-requested` review states now require a known current output version. Skill guidance explicitly states `<PROJECT>-MD###` media and `<MEDIA_ID>-v###` version syntax.

- Fresh RED: 3 new adversarial/safe-counterexample tests were added; the focused file reported 8 failures because adding roles to the shared positive fixture caused existing schema-gated tests to stop before their semantic assertions.
- Focused GREEN: `.venv/bin/python -m pytest -q tests/test_vfx_post_plans.py tests/test_skill_catalog.py::test_vfx_post_supervisor_bundle_is_complete tests/test_artifacts.py::test_vfx_post_plan_template_is_valid` — 19 passed in 0.69s.
- `make PYTHON=.venv/bin/python check` — repository validation passed; 1080 tests passed in 60.68s.
- `make PYTHON=.venv/bin/python validate-core-example` — `core-v0.1` scene package validation passed.
- `make PYTHON=.venv/bin/python validate-full-example` — `full-v1` returned `{"command":"validate-package","errors":[],"profile":"full-v1","valid":true}`.

The controller-owned first-run forward JSON predates the required media roles and needs migration before revalidation. It remains preserved and was not edited by this fix.

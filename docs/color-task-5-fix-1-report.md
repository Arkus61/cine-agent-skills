# Color Task 5 — fix round 1 report

## Finding confirmation

Direct read-only probes against `6b6078b` reproduced both gaps from the independent review. A metadata record whose segment was outside its linked media version and an unused evidence record naming only one of a two-segment item's segments each returned `[]` from `validate_color_plan_contract`.

## Scoped fix

- Validate every metadata record's segment against the segment set of its linked media version.
- Validate every evidence record against its target item's complete segment set, require the evidence version to cover that set, and bind `observed-input` evidence to an item source version while binding `shot-match`, `display-review`, and `approval` evidence to the item's graded-output version.
- Preserve valid unused metadata and evidence records; no consumer reference is required merely to keep a useful internally consistent record.

## TDD evidence

### RED

Command:

```text
.venv/bin/python -m pytest tests/test_color_plans.py -q
```

Observed result before the runtime change: `2 failed, 20 passed in 0.57s`. The failures were `test_color_plan_rejects_unused_metadata_for_a_segment_outside_its_version` and `test_color_plan_rejects_unused_evidence_with_incomplete_segments_or_wrong_claim_version`; both received no expected record-level error. The two valid-unused counterexamples passed.

### GREEN

Command:

```text
.venv/bin/python -m pytest tests/test_color_plans.py -q
```

Observed result after the minimal runtime change: `22 passed in 0.52s`.

## Verification

- Focused package gate: `.venv/bin/python -m pytest tests/test_color_plans.py tests/test_artifacts.py::test_color_plan_template_is_valid tests/test_skill_catalog.py::test_color_grading_designer_bundle_is_complete -q` → `24 passed in 0.63s`.
- Full repository gate: `make PYTHON=.venv/bin/python check` → repository validation passed; `1104 passed in 40.01s`.
- Core legacy gate: `make PYTHON=.venv/bin/python validate-core-example` → `Scene package validation passed.`
- Full legacy gate: `make PYTHON=.venv/bin/python validate-full-example` → `{"command": "validate-package", "errors": [], "profile": "full-v1", "valid": true}`.
- `git diff --check` → no output.
- `git diff -- uv.lock` → no output.

## Scope and compatibility

Only `src/cine_skills/color_plans.py`, `tests/test_color_plans.py`, and this report are part of the fix. No schema migration or forward-artifact change was required. Controller-owned untracked files and the pre-existing `uv.lock` remain untouched.

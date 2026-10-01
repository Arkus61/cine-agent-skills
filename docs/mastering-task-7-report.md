# Mastering and QC Supervisor — Task 7 implementation report

## Scope

Implemented the approved Task 7 specialist only: a complete `mastering-qc-supervisor` bundle, strict Draft 2020-12 schema, standalone semantic validator, evaluation fixture, source-register entries, and minimal artifact/catalog/template registration. No post-package validator, ProjectIndex, Task 8/9 behavior, media processing, rendering, encoding, measurement execution, upload, or distribution was added.

The contract separates schema validity from delivery readiness. Specifications produce required planned checks, not passed observations. Supplied evidence binds the exact check, complete criterion, observed value and units, current master version, and scope. Required coverage, deliverable verification, and current scoped human approval are validated relationships. Channel count and layout are distinct; sample peak, true peak, loudness, and clipping are distinct.

## RED

Tests were written before the schema, validator, skill bundle, template, or evaluation files.

Command:

```text
.venv/bin/python -m pytest -q tests/test_mastering_qc.py tests/test_skill_catalog.py::test_catalog_is_exactly_the_thirty_current_skills tests/test_skill_catalog.py::test_mastering_qc_supervisor_bundle_is_complete tests/test_artifacts.py::test_mastering_qc_plan_template_is_valid
```

Exact result: exit `1`, `18 failed in 3.00s`. The three positive artifacts failed with `schema not found: .../schemas/mastering-qc-plan.schema.json`; the semantic rejection assertions did not yet receive their required diagnostics; the catalog and bundle tests reported the absent specialist; and the template test reported `FileNotFoundError`. These were the expected missing-feature failures, not collection or syntax errors.

After the first green implementation, a contract review added two regression tests before their fixes:

```text
.venv/bin/python -m pytest -q tests/test_mastering_qc.py::test_mastering_qc_rejects_unused_evidence_with_mismatched_target_contract tests/test_mastering_qc.py::test_mastering_qc_rejects_ready_after_required_master_or_qc_report_is_deleted
```

Exact result before the fixes: exit `1`, `2 failed in 0.31s`. The first proved that unused evidence could carry another check's criterion; the second proved that deleting the required picture/sound master or QC report and updating the readiness list could manufacture a ready state.

## GREEN and regressions

The first complete focused implementation run returned:

```text
....................                                                     [100%]
20 passed in 1.78s
```

The two additional regressions were closed by validating every measurement/inspection evidence record against its target check even when unused, and by requiring the picture/sound master and QC report to remain substantive required deliverable kinds.

Final focused command:

```text
.venv/bin/python -m pytest -q tests/test_mastering_qc.py tests/test_skill_catalog.py::test_catalog_is_exactly_the_thirty_current_skills tests/test_skill_catalog.py::test_original_twelve_v1_skills_remain_the_preserved_base tests/test_skill_catalog.py::test_every_skill_has_openai_metadata tests/test_skill_catalog.py::test_mastering_qc_supervisor_bundle_is_complete tests/test_artifacts.py::test_mastering_qc_plan_template_is_valid
```

Exact result: exit `0`.

```text
......................                                                   [100%]
22 passed in 1.89s
```

Skill-package validation:

```text
.venv/bin/python /root/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/mastering-qc-supervisor
Skill is valid!
```

## Initial full repository and compatibility verification

Command:

```text
make PYTHON=.venv/bin/python check
```

Exact result: exit `0`; repository validation printed `Repository validation passed.` and pytest completed with:

```text
1147 passed in 86.57s (0:01:26)
```

Compatibility commands and exact results:

```text
make PYTHON=.venv/bin/python validate-core-example
PYTHONPATH=src .venv/bin/python -m cine_skills validate-package examples/ninel/scenes/S01 --profile core-v0.1
Scene package validation passed.
```

```text
make PYTHON=.venv/bin/python validate-full-example
PYTHONPATH=src .venv/bin/python -m cine_skills validate-package examples/ninel-v1/scenes/S01 --profile full-v1 --format json
{"command": "validate-package", "errors": [], "profile": "full-v1", "valid": true}
```

`git diff --check` returned exit `0` with no output. Status and diff review confirmed that the pre-existing untracked `uv.lock` and controller-owned `.superpowers/` work were not modified or staged.

## Independent review round 1 and blocking closure

The independent read-only review of implementation commit `03f665e` returned **Spec FAIL** with five blocking evidence/readiness findings:

1. paired approval and evidence could narrow the scope to `picture-only` while readiness remained `ready`;
2. a check and evidence could mutate observed units together so they no longer matched the criterion units;
3. unused applicable evidence was not fully bound to the target observation and non-current records could remain `applicable`;
4. measurable `review` criteria containing an unresolved request for a threshold could still pass and contribute to readiness;
5. a master filename/source could masquerade as measurement or inspection provenance.

The first closure regressions ran before fixes:

```text
.venv/bin/python -m pytest -q tests/test_mastering_qc.py -k 'narrow_picture_only or observed_units_disagree or unbound_applicable or explicitly_historical or unresolved_placeholder or master_filename'
```

Exact RED result: exit `1`, `5 failed, 1 passed, 17 deselected in 0.58s`. The explicitly historical known-old-version positive already passed; all five blocking scenarios escaped validation exactly as reported.

The review then required structured evidence provenance in addition to the conservative master-source equality guard. Tests introduced the exact mapping `measurement` → `supplied-measurement-report`, `inspection` → `supplied-inspection-record`, `deliverable-verification` → `supplied-deliverable-record`, and `human-approval` → `supplied-human-decision`.

```text
.venv/bin/python -m pytest -q tests/test_mastering_qc.py -k 'structured_evidence_source_kinds or mismatched_or_filename_only_source_kind'
```

Exact RED result: exit `1`, `2 failed, 23 deselected in 0.33s`. The schema rejected the new field as unexpected and no typed compatibility rule existed.

A final implementation-side review added two variants before their fixes: historical evidence whose own criterion units disagreed with its observed units, and a measurable criterion labelled `supplied` while still using non-comparable `review`.

```text
.venv/bin/python -m pytest -q tests/test_mastering_qc.py -k 'historical_evidence_with_internally_mismatched_units or measurable_pass_with_review_operator'
```

Exact RED result: exit `1`, `2 failed, 25 deselected in 0.28s`.

Closure added explicit criterion state, typed evidence provenance, current-version applicability and target binding, internal evidence-unit checks, observed-to-criterion unit agreement, machine-comparable operators for supplied measurable criteria, exact `delivery-master-and-qc` approval/readiness scope, and rejection when an evidence source equals its master source. Explicitly `historical` or `superseded` records for known versions remain valid without becoming current evidence.

Final focused closure command:

```text
.venv/bin/python -m pytest -q tests/test_mastering_qc.py tests/test_artifacts.py::test_mastering_qc_plan_template_is_valid tests/test_skill_catalog.py::test_mastering_qc_supervisor_bundle_is_complete tests/test_skill_catalog.py::test_every_skill_has_openai_metadata
```

Exact result: exit `0`.

```text
..............................                                           [100%]
30 passed in 2.49s
```

Fresh closure verification:

```text
make PYTHON=.venv/bin/python check
Repository validation passed.
1157 passed in 88.33s (0:01:28)
```

Both `make PYTHON=.venv/bin/python validate-core-example` and `make PYTHON=.venv/bin/python validate-full-example` returned exit `0` with the same successful compatibility outputs recorded above. Skill-package validation printed `Skill is valid!`; `git diff --check` returned exit `0` with no output.

A final pre-commit rerun after this report update again printed `Repository validation passed.` and completed with `1157 passed in 88.01s (0:01:28)`.

## Frozen forward contract

The schema, template, instructions, references, and evaluation cases are frozen by this blocking-closure change, superseding the reviewed `03f665e` contract, for the controller's refreshed independent forwards:

1. specifications only, with all unsupported observations planned and readiness `not-ready`;
2. partial measurable r2 metadata, with only exact supplied fields passing and r1 approval retained as historical.

External source authenticity and future cross-package authority remain Task 8 integration concerns. Task 7 is not accepted until refreshed forwards and an independent read-only re-review confirm this blocking closure without new findings.

## Independent review round 2 and Important-gap closure

The fresh read-only re-review of closure commit `319cc28` found four **Important** gaps:

1. historical or superseded deliverable and approval evidence could retain malformed internal scope, value, or units because only applicable records received the full shape checks;
2. fragments, queries, and relative-path spelling could disguise the current master source as an evidence source;
3. numeric, string, and presence categories did not enforce comparable operand types or finite numeric values, and an invalid machine comparison could return no result without invalidating `pass` or `fail`;
4. a verified required QC-report deliverable could reuse the current master source rather than identify a distinct report.

Regression tests were added before the second-closure implementation. The positive case preserved internally consistent but intentionally unbound historical deliverable evidence and superseded approval evidence.

```text
.venv/bin/python -m pytest -q tests/test_mastering_qc.py -k 'internally_consistent_unbound_historical_delivery or internally_malformed_historical or normalizes_master_paths or wrong_value_types or silently_skips_invalid_machine or verified_qc_report'
```

Exact RED result: exit `1`.

```text
.FFFFFF                                                                  [100%]
6 failed, 1 passed, 27 deselected in 0.63s
```

The minimal closure now validates internal deliverable and approval evidence shape at every applicability state; normalizes source paths while stripping query and fragment decorations; enforces finite numeric, string, and boolean category operands; reports incompatible machine-comparable operands; and requires the verified QC report to have a normalized source distinct from the current master.

The exact regression selection then returned exit `0`:

```text
.......                                                                  [100%]
7 passed, 27 deselected in 1.56s
```

The complete specialist test file returned exit `0`:

```text
..................................                                       [100%]
34 passed in 3.74s
```

Final focused command:

```text
.venv/bin/python -m pytest -q tests/test_mastering_qc.py tests/test_artifacts.py::test_mastering_qc_plan_template_is_valid tests/test_skill_catalog.py::test_mastering_qc_supervisor_bundle_is_complete tests/test_skill_catalog.py::test_every_skill_has_openai_metadata
```

Exact result: exit `0`.

```text
.....................................                                    [100%]
37 passed in 3.97s
```

Fresh full repository verification:

```text
make PYTHON=.venv/bin/python check
Repository validation passed.
1164 passed in 88.14s (0:01:28)
```

Compatibility results remained successful:

```text
make PYTHON=.venv/bin/python validate-core-example
Scene package validation passed.
```

```text
make PYTHON=.venv/bin/python validate-full-example
{"command": "validate-package", "errors": [], "profile": "full-v1", "valid": true}
```

Skill-package validation printed `Skill is valid!`. `git diff --check` returned exit `0` with no output. Status review confirmed that untracked forward-review artifacts and the pre-existing `uv.lock` were neither edited nor staged by this closure.

## Independent review round 3 and domain-constraint closure

The final re-review found one remaining Important domain gap: the contract accepted empty resolution/aspect/layout strings, non-positive frame rate or duration, fractional or non-positive channel counts, and supplied captions/titles presence criteria using `equals` or string values. The numeric helper also raised `OverflowError` for an oversized integer instead of returning a validation diagnostic.

Regression tests were written before the implementation change for these cases and for exception-safe finite-number validation:

```text
.venv/bin/python -m pytest -q tests/test_mastering_qc.py -k 'empty_resolution_aspect_ratio_and_channel_layout or nonpositive_frame_rate_and_duration or fractional_or_nonpositive_channel_count or presence_with_equals or string_captions_and_titles_presence or oversized_numeric_measurement'
```

Exact RED result: exit `1`.

```text
6 failed, 34 deselected in 0.84s
```

The minimal closure now requires non-empty geometry/layout strings; positive frame rate and duration; positive integer channel count; and, for supplied captions/titles presence, `present` or `absent` with boolean values. Unresolved presence requirements remain allowed to use `review`. `_is_finite_number` safely rejects oversized integers and other non-finite or incompatible numeric values without raising.

Targeted GREEN command:

```text
.venv/bin/python -m pytest -q tests/test_mastering_qc.py -k 'empty_resolution_aspect_ratio_and_channel_layout or nonpositive_frame_rate_and_duration or fractional_or_nonpositive_channel_count or presence_with_equals or string_captions_and_titles_presence or oversized_numeric_measurement'
```

Exact result:

```text
......                                                                   [100%]
6 passed, 34 deselected in 1.11s
```

The complete specialist test file returned exit `0`:

```text
........................................                                 [100%]
40 passed in 4.53s
```

Final focused command:

```text
.venv/bin/python -m pytest -q tests/test_mastering_qc.py tests/test_artifacts.py::test_mastering_qc_plan_template_is_valid tests/test_skill_catalog.py::test_mastering_qc_supervisor_bundle_is_complete tests/test_skill_catalog.py::test_every_skill_has_openai_metadata
```

Exact result:

```text
...........................................                              [100%]
43 passed in 4.96s
```

Fresh full repository verification:

```text
make PYTHON=.venv/bin/python check
PYTHONPATH=src .venv/bin/python -m cine_skills validate .
Repository validation passed.
1170 passed in 89.99s (0:01:29)
```

Compatibility commands returned exit `0`:

```text
make PYTHON=.venv/bin/python validate-core-example
PYTHONPATH=src .venv/bin/python -m cine_skills validate-package examples/ninel/scenes/S01 --profile core-v0.1
Scene package validation passed.
```

```text
make PYTHON=.venv/bin/python validate-full-example
PYTHONPATH=src .venv/bin/python -m cine_skills validate-package examples/ninel-v1/scenes/S01 --profile full-v1 --format json
{"command": "validate-package", "errors": [], "profile": "full-v1", "valid": true}
```

Skill-package validation printed `Skill is valid!`; `git diff --check` returned exit `0` with no output. The closure changes are limited to the mastering/QC validator, its tests, and the corresponding skill/reference instructions; the untracked forward JSONs and pre-existing `uv.lock` remain untouched.

## Independent review round 4 and presence-semantics closure

The follow-up review of commit `54c02f1` found one remaining Important gap: `present` and `absent` were treated as aliases for equality, so contradictory machine criteria such as `present` with `expected_value: false` or `absent` with `expected_value: true` could pass when the observed value matched the contradictory boolean. This affected captions-presence, titles-presence, and other boolean presence checks such as missing-frames.

Regression tests were written before the presence-semantics implementation. They kept the expected value, observed value, and evidence criterion/value internally bound; the only invalidity was the operator/value meaning. The first test also kept `result: pass` to prove that the validator diagnoses the resulting machine-comparison disagreement. The second kept the check planned to isolate the criterion-level semantic error.

```text
.venv/bin/python -m pytest -q tests/test_mastering_qc.py -k 'contradictory_presence_operator_semantics or presence_operator_with_contradictory_expected_value'
```

Exact RED result:

```text
FF                                                                       [100%]
2 failed, 40 deselected in 0.34s
```

The minimal closure now requires every supplied `present` criterion to declare `expected_value: true` and every supplied `absent` criterion to declare `expected_value: false`. Its comparator independently requires the observed value to be the same operator-defined boolean, so a `pass` or `fail` that disagrees is reported rather than accepted. The skill instructions and technical QC reference now state this contract explicitly.

Targeted GREEN command:

```text
.venv/bin/python -m pytest -q tests/test_mastering_qc.py -k 'contradictory_presence_operator_semantics or presence_operator_with_contradictory_expected_value'
```

Exact result:

```text
..                                                                       [100%]
2 passed, 40 deselected in 0.82s
```

The complete specialist test file returned exit `0`:

```text
..........................................                               [100%]
42 passed in 5.12s
```

Final focused command:

```text
.venv/bin/python -m pytest -q tests/test_mastering_qc.py tests/test_artifacts.py::test_mastering_qc_plan_template_is_valid tests/test_skill_catalog.py::test_mastering_qc_supervisor_bundle_is_complete tests/test_skill_catalog.py::test_every_skill_has_openai_metadata
```

Exact result:

```text
.............................................                            [100%]
45 passed in 5.72s
```

Fresh full repository verification:

```text
make PYTHON=.venv/bin/python check
Repository validation passed.
1172 passed in 91.46s (0:01:31)
```

Compatibility and package checks returned exit `0`:

```text
make PYTHON=.venv/bin/python validate-core-example
PYTHONPATH=src .venv/bin/python -m cine_skills validate-package examples/ninel/scenes/S01 --profile core-v0.1
Scene package validation passed.
```

```text
make PYTHON=.venv/bin/python validate-full-example
PYTHONPATH=src .venv/bin/python -m cine_skills validate-package examples/ninel-v1/scenes/S01 --profile full-v1 --format json
{"command": "validate-package", "errors": [], "profile": "full-v1", "valid": true}
```

```text
.venv/bin/python /root/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/mastering-qc-supervisor
Skill is valid!
```

`git diff --check` returned exit `0` with no output. The change is limited to the mastering/QC validator, its regression tests, and the corresponding skill/reference instructions and report; the untracked forward JSONs and pre-existing `uv.lock` remain untouched.

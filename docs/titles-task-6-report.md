# Titles and Captions Designer — Task 6 implementation report

## Scope

Implemented the approved Task 6 specialist only: the complete skill bundle, strict Draft 2020-12 schema, focused semantic validator, evaluation fixture, source register entry, and minimal artifact/catalog/template registration. No ProjectIndex, postproduction orchestrator, external tool, media operation, or Task 8 behavior was added.

The contract distinguishes creative timing intent from exact supplied output-timeline timing. Exact timing is item-, segment-, edit-version-, timebase-, frame-, and timecode-bound. Review and approval bind the exact current content, revision, placement, timing record, segment, edit version, and matching decision value. Every populated registry record is validated even when unused. Honest no-media plans retain substantive creative and accessibility decisions.

## RED

Tests were written before product code and run with:

```text
.venv/bin/python -m pytest -q tests/test_titles_captions.py tests/test_artifacts.py::test_titles_captions_plan_template_is_valid tests/test_skill_catalog.py::test_titles_captions_designer_bundle_is_complete
```

Exact result: exit `1`, `14 failed in 1.31s`. The positive cases reported `schema not found: .../schemas/titles-captions-plan.schema.json`; the template test reported `FileNotFoundError`; the bundle test reported the five expected files missing; and the semantic rejection assertions remained unmet. These were the expected missing-feature failures, not test syntax or collection errors.

## GREEN

The identical focused command then returned exit `0`:

```text
..............                                                           [100%]
14 passed in 0.61s
```

Additional focused semantic run:

```text
.venv/bin/python -m pytest -q tests/test_titles_captions.py
............                                                             [100%]
12 passed in 0.42s
```

Artifact and catalog legacy/focused run:

```text
.venv/bin/python -m pytest -q tests/test_artifacts.py tests/test_skill_catalog.py
832 passed in 20.10s
```

Direct template CLI validation:

```text
PYTHONPATH=src .venv/bin/python -m cine_skills validate-artifact titles-captions-plan .agents/skills/titles-captions-designer/assets/titles-captions-plan.template.json --root .
Artifact validation passed.
```

## Full and compatibility verification

```text
make PYTHON=.venv/bin/python check
Repository validation passed.
1118 passed in 41.52s
```

```text
make PYTHON=.venv/bin/python validate-core-example
Scene package validation passed.
```

```text
make PYTHON=.venv/bin/python validate-full-example
{"command": "validate-package", "errors": [], "profile": "full-v1", "valid": true}
```

`git diff --check` returned exit `0`. Status/diff review confirmed that the controller-owned untracked `docs/titles-task-6-checklist.md` and `docs/titles-forward-inputs.md`, plus pre-existing untracked `uv.lock`, were not modified or staged. The schema, template, CLI instructions, and semantic contract were frozen before the controller's independent forward trials.

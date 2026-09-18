# Titles/Captions skill verification checklist

- [x] Create realistic vertical short-form and widescreen feature scenarios.
- [x] Run a fresh no-skill baseline; preserve raw behavior and classify actual gaps.
- [x] Classify as reference/output-contract guidance; persuasion-specific micro-tests are not applicable.
- [x] Prepare a brief with exact interfaces, evidence boundaries, primary sources and scoped deliverables.
- [x] Observe schema/semantic RED before implementation.
- [x] Keep SKILL.md concise, trigger-only frontmatter, exact matching name and no session narrative.
- [ ] Put useful theory in references and a complete valid artifact in assets.
- [ ] Document all ID shapes, nullable/state fields and exact CLI invocation.
- [ ] Test honest no-media and evidence-backed positive paths.
- [ ] Reject malformed language, text provenance, placement exceptions, timing and approval.
- [ ] Check stale/cross-item/version bindings and every populated record, including unused ones.
- [x] Freeze schema/template before independent forward trials.
- [x] Run vertical short-form and widescreen title forwards; preserve first results and repairs.
- [x] Verify focused/full/legacy gates and clean scoped diff.
- [ ] Obtain independent read-only spec/quality review; close blocking findings.
- [ ] Commit scoped module and evidence. Do not create an unsolicited PR or push.

Controller-owned checklist; implementation starts from accepted Color checkpoint `15ca942`. The specialist is not accepted until the final gate above is complete.

## Initial RED

Implementer reported before product creation:

`.venv/bin/python -m pytest -q tests/test_titles_captions.py tests/test_artifacts.py::test_titles_captions_plan_template_is_valid tests/test_skill_catalog.py::test_titles_captions_designer_bundle_is_complete`

Exit 1, `14 failed in 1.31s`, due to absent schema/bundle/template and unmet semantic gates. No implementation pass or acceptance is claimed.

## First GREEN

The same focused command returned exit 0, `14 passed in 0.61s`. Full gates, independent forwards and review remain pending.

## Committed implementation and controller verification

Implementation `18981ab`. Controller full gate exit 0: repository valid, `1118 passed in 41.93s`. Both legacy profiles pass; `git diff --check` clean. Schema/template remained frozen while independent vertical/widescreen forwards ran. Forward and review outcomes are not yet accepted.

## Forward outcomes

Widescreen first validation passed, exit 0, with unresolved credits and proposed translation/placement. Vertical first validation failed on a nonspeech accessibility caption requiring `supplied-dialogue`; the agent's relabeling made it mechanically valid but the controller rejects that provenance change. Preserve both outputs and fix the product contract, then run a new frozen forward. Independent review pending; Task 6 not accepted.

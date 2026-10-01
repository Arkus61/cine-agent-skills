# Titles/Captions Task 6 — independent review

Review `15ca942..18981ab`, reviewer `titles_review_resume`, 2026-09-08. Verdict Needs fixes: 0 Critical, 4 Important, 0 Minor. Task 6 is not accepted.

## Confirmed findings

1. `src/cine_skills/titles_captions.py:90-91`: the supplied-dialogue requirement applies to every accessibility caption, rejecting honest proposed nonspeech descriptions. The original vertical forward demonstrates this. Restrict the dialogue rule to dialogue-derived content; permit explicitly proposed nonspeech captions with truthful editorial-proposal provenance. Preserve speech provenance checks.
2. `schemas/titles-captions-plan.schema.json:21`, `titles_captions.py:153-155`: evidence omits language, speaker identification and sound description, allowing these fields to change without invalidating approval. Bind these structured accessibility fields in evidence and compare them during registry/approval validation.
3. `titles_captions.py:52-67`: unused timing records may name an existing item but another existing segment. Require each record's segment to equal its target item's edit segment independently of consumption.
4. `titles_captions.py:165-175`: integer non-drop timecodes with a frame component at or above nominal fps silently skip validation. Reject out-of-range frame components, then check frame-count equivalence. At 24 fps, `:24` and `:99` must not pass.

## Positive findings and boundary

Strict closed schema, exact ownership/IDs, isolated semantics, output-timeline distinction, matched approval decision values, useful creative/readability references and initial tests. Authenticity of external lock/text/timing/evidence sources remains a Task 8 integration responsibility, not claimed by the standalone validator.

## Fix instructions

Reproduce all four findings with failing tests before changing product code; include honest nonspeech and valid timing/approval counterexamples. Do not repair the historical forward files or redefine a doorbell as dialogue. Update the current skill/template references only as required by the changed contract. Preserve supported legacy profiles, unrelated modules and uv.lock. Write a separate fix report and commit. Re-review the fix diff before acceptance, and run a new frozen independent forward after the fix.

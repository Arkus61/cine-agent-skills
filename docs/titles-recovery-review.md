# Titles/Captions Task 6 recovery fix review

Verdict: **Needs fixes** — 0 Critical, 2 Important, 0 Minor.

Scope: read-only review of the seven tracked files in `git diff HEAD` at base `a7d2e0a8babe862d854be03b0e46acfb6092e3ca`, against `docs/titles-task-6-review.md`. Read the schema, validator, skill/template/references, and tests. No product edits, commits, full-suite runs, or external-source authenticity checks. Targeted reproductions used the public `validate_artifact` entry point (schema plus semantic validation).

## Original findings

1. **Direct case fixed:** explicit `nonspeech` accessibility captions accept proposed text with an editorial-proposal source. Dialogue-classified captions/subtitles still require supplied-dialogue. Added positive test preserves an honest doorbell proposal. However, the newly introduced classification has the Important gaps below.
2. **Fixed:** evidence requires language, speaker identification, and sound description using the same structured schema definitions as items. `_evidence_matches` compares all three, including annotation state and value, during both registry and approval validation. Tests mutate each field and retain a valid approval fixture.
3. **Fixed:** every timing registry record now compares its segment with its target item's segment, independent of whether it is consumed. The test uses two existing segments covered by the same edit version and an unused mismatching record.
4. **Fixed:** integer non-drop frame components at or above nominal fps now raise an error before equivalence is considered. Tests cover :24 and :99 at 24 fps; existing valid timing and unequal frame/timecode examples remain.

## Important findings

### I1. New content classifications create unchecked caption/source combinations

Location: `src/cine_skills/titles_captions.py:93-97`; `schemas/titles-captions-plan.schema.json` contentState/item definitions.

The narrowed source check runs only for `content_kind == "dialogue"`, and the alternate rule runs only for `nonspeech`. Both `title` and `credit` are nevertheless accepted for subtitles/accessibility captions. Those combinations bypass the source guard entirely, including allowing a populated nonexistent source ID on proposed caption text. This violates the skill's explicit internal-reference consistency claim; it is a local registry issue, not Task 8 authenticity.

Reproducer from the repository root:

```python
import runpy
from pathlib import Path
m = runpy.run_path('tests/test_titles_captions.py')
p = m['planned_titles_plan']()
p['items'][0]['text'].update(
    content_kind='title', state='proposed', text_source_id='SPARK-TS999'
)
assert m['errors'](p, Path.cwd()) == []  # observed; TS999 is not registered
```

`content_kind='credit'` also passes. Run with `PYTHONPATH=src .venv/bin/python`. Enforce a supported item-type/content-kind matrix and resolve every populated text source reference independently of content state. Add negative tests for these combinations and keep honest nonspeech/dialogue counterexamples.

### I2. New structural content kind can change without invalidating approval

Location: `src/cine_skills/titles_captions.py:159-161`; schema evidence definition.

`content_kind` is the newly authoritative distinction between dialogue and nonspeech, but evidence does not capture it. A previously approved dialogue item can be reclassified as a nonspeech proposal while retaining the same revision, review, and human approval. Internal evidence continues to attest a different semantic content class without a fresh decision. This is introduced by the new field and can be demonstrated entirely within the artifact; no external source verification is needed.

Reproducer:

```python
import runpy
from pathlib import Path
m = runpy.run_path('tests/test_titles_captions.py')
p = m['approved_titles_plan']()
p['items'][0]['text'].update(content_kind='nonspeech', state='proposed')
p['source_context']['text_sources'][0]['kind'] = 'editorial-proposal'
assert m['errors'](p, Path.cwd()) == []  # observed; original approval survives
```

The wording is deliberately unchanged: the skill says class must be structural, not inferred from wording. Add `content_kind` to the evidence contract and current-item comparison, with a regression that changes class while retaining the original evidence. Existing exact valid approvals should still pass after updating their fixtures.

## Verification limits

The working diff contains tests for all four original findings and the requested positive examples. A final working-tree snapshot cannot establish that those tests were first run failing before product edits; parent recovery evidence must establish that chronology. No historical forward files, legacy profiles, unrelated modules, or tracked lockfile changes appear in the reviewed diff. Full tests, release gates, separate fix report/commit, and a new frozen independent forward remain the parent workflow's responsibility. Task 8 cross-file source authenticity remains explicitly outside this review.

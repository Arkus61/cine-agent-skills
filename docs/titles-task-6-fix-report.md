# Titles/Captions Task 6 fix report

Scope: seven recovered Task 6 files plus the original independent review and this report. Historical forward artifacts, legacy profiles, unrelated mastering/recovery documents, and uv.lock were preserved.

## Original review findings

The recovered changes permit explicitly proposed nonspeech accessibility captions with editorial-proposal provenance; bind language, speaker identification, and sound description in review/approval evidence; check every timing record against its target item segment; and reject out-of-range integer non-drop timecode frame components before frame equivalence checks. The recovered focused titles suite passed all 16 tests before this continuation. The parent independently reproduced all four original failures against archived a7d2e0a (4 failed); see parent-preserved docs/titles-recovery-original-red.txt and docs/titles-recovery-original-regressions.py.txt. The recovery review is preserved in docs/titles-recovery-review.md.

## Recovery review findings

1. Enforced the supported type/content-kind matrix: main-title/intertitle/lower-third use title, credit uses credit, subtitle uses dialogue, and accessibility-caption uses dialogue or nonspeech. Every populated text-source reference resolves regardless of supplied/proposed state. Existing dialogue and nonspeech provenance requirements remain.
2. Evidence now requires content_kind, text_state, and text_source. The latter snapshots the complete resolved source record, or null for an unsourced proposal. Both registry validation and final approval comparison bind these fields, so changing classification, provenance state, source identity, or registered source contents invalidates retained evidence.

## Test-first evidence and verification

Before product edits, four new regression tests failed while the existing 16 passed (`.venv/bin/python -m pytest -q tests/test_titles_captions.py`). They reproduced incompatible caption classifications, dangling proposed-title references, retained approval after dialogue-to-nonspeech reclassification, and retained approval after provenance changes.

After edits, `.venv/bin/python -m pytest -q tests/test_titles_captions.py tests/test_skill_catalog.py` passed 50 tests. `make validate` passed. Positive cases include the original exact dialogue approval, proposed doorbell caption, an approved nonspeech proposal with matching evidence, and compatible title/credit/subtitle types. Existing valid timing and mismatching frame/timecode counterexamples remain.

The parent workflow owns full-suite and release gates, independent scoped re-review, and the fresh frozen forward. This report does not claim release readiness or external-source authenticity; upstream source verification remains Task 8 integration work.

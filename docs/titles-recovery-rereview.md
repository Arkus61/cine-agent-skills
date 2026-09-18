# Titles/Captions Task 6 scoped re-review

Reviewed commit `eb06c2e` against source base `a7d2e0a` in `cine-agent-skills`, including the validator, schema, current skill/template/references, regression tests, and `docs/titles-task-6-fix-report.md`.

**Spec verdict: PASS for the reviewed fix scope.**

**Quality verdict: PASS.** No remaining Critical, Important, or Minor findings identified in this diff. This is scoped code/spec acceptance, not a claim of release readiness or external-source authenticity.

## Recovery findings resolved

- **I1 resolved.** The item-type/content-kind matrix explicitly permits only title content for main-title/intertitle/lower-third, credit content for credit, dialogue for subtitle, and dialogue/nonspeech for accessibility-caption. Every populated text-source ID is checked against the source registry before state-specific checks. Thus both prior caption classification bypasses and dangling proposed source references are rejected. Tests cover incompatible subtitle/accessibility classifications, a dangling proposed-title reference, and valid title/credit/subtitle counterparts. Honest proposed nonspeech captions retain their dedicated editorial-proposal rule.
- **I2 resolved.** Evidence now requires `content_kind`, `text_state`, and a complete `text_source` snapshot (or null for an unsourced proposal). `_evidence_matches` compares all three against the current item and resolved source registry in both registry validation and approval consumption. Source snapshots include identity, kind, text, and source_reference, so changes to those fields cannot retain old matching evidence. Tests cover the exact earlier reclassification reproducer, state/source-reference/source-identity changes, and a nonspeech proposal with fresh matching approval evidence. The fixture copies source snapshots, avoiding aliasing that would hide stale-source mutations.

## Original four findings remain resolved

The explicit honest nonspeech path remains available while dialogue provenance checks remain enforced. Language and both structured annotation fields remain bound to evidence. Every timing record is checked against its target item's segment regardless of consumption. Integer non-drop timecodes reject frame components at or above nominal fps before checking frame equivalence. No changes in the latest fix weaken these corrections.

## Quality and boundaries

The schema uses shared definitions for classification, state, and source snapshots, and the skill/reference instructions describe the same contract. Both evidence validation call sites pass the source registry. Null source snapshots support unsourced proposals; populated dangling references cannot exploit that null behavior because the item-reference check rejects them. The reviewed tracked changes remain confined to the intended titles/captions fix and reports.

No full or focused test suites were rerun during this re-review, per the parent instruction. The parent reports 50 focused tests passing and owns full verification gates. The implementer report supplies test-first evidence and explicitly leaves upstream source authenticity to Task 8. Parent acceptance should still include its required full checks and fresh frozen independent forward; those workflow gates are not established by this static review.

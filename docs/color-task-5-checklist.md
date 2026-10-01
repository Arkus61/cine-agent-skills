# Color skill verification checklist

- [x] Create realistic daylight and stylized-animation scenarios.
- [x] Run no-skill baseline and preserve verbatim behavior.
- [x] Identify observed gaps without inventing failures.
- [x] Classify guidance: reference/output contract; persuasion micro-tests, rationalization tables and discipline red flags are not applicable.
- [x] Run focused schema/semantic RED before implementation.
- [x] Use lowercase-hyphenated skill name and required frontmatter only.
- [x] Keep trigger description short, third-person and searchable.
- [x] State a clear core principle and contract overview.
- [x] Match reference/template structure to observed output gaps.
- [x] Provide linked theory and one usable complete template.
- [x] Provide scannable ID/state reference and common mistakes.
- [x] Use a diagram only if a non-obvious relationship requires it (none needed).
- [x] Keep reusable skill free of session narrative.
- [x] Restrict supporting files to useful contract/theory/tools.
- [x] Run independent daylight and animation forwards with the skill.
- [x] Preserve first results and record any new failure.
- [x] Apply only evidenced corrections and re-test them.
- [x] Verify full/legacy gates and independent review.
- [x] Commit scoped task and evidence; push only if configured and authorized (no push requested).
- [x] Consider contribution applicability without creating an unsolicited PR (project-local module; no external contribution requested).

## Controller verification — 2026-09-07

- Implementation committed as `b3f14e4`; independent review pending.
- Focused bundle and semantics: `20 passed in 0.61s`.
- Full gate: `make PYTHON=.venv/bin/python check`, exit 0, repository valid, `1100 passed in 41.14s`.
- Both `core-v0.1` and `full-v1` example gates passed; `git diff --check` clean.
- Earlier daylight/animation trials crossed an in-flight contract change: original invalid outputs and repairs are preserved, not counted as first-pass successes.
- Frozen DAWN trial: first validation exit 0, no repair, no fabricated inspection or approval. See `color-frozen-forward-report.md`.
- Fix `5021385`: reviewer finding closed with 0/0/0; fresh controller full gate `1104 passed in 40.48s`, both legacy profiles and frozen-forward migration valid. Accepted.

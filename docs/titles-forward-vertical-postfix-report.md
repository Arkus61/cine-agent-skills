# Fresh post-fix vertical titles/captions forward report

## Independence and contract state

This artifact was constructed afresh from the supplied `MOSAIC` brief in
`docs/titles-forward-inputs.md`, after the titles/captions contract and Task 6 fixes were frozen.
The pre-fix JSON was read only as historical failure context; its output was not copied. No media,
locked-edit metadata, specification, clearance, or review evidence was introduced.

The new result explicitly separates the supplied dialogue (`content_kind: dialogue`,
`supplied-dialogue`) from the editorial Spanish rendering of the doorbell
(`content_kind: nonspeech`, `editorial-proposal`). Every exact timing field is absent and every
item remains `pending` because the input contains no locked output timeline or bound approval
evidence.

## First and final validation attempt

Command (exact):

```text
PYTHONPATH=src .venv/bin/python -m cine_skills validate-artifact titles-captions-plan docs/titles-forward-vertical-postfix.json --root . --format json
```

Standard output (exact):

```json
{"command": "validate-artifact", "errors": [], "valid": true}
```

Standard error (exact): empty.

Exit status: `0`.

The first attempt passed, so no repaired artifact or first-attempt preservation copy was needed.
This result proves schema and semantic-contract validity only. It does not prove media inspection,
performed dialogue, exact timing, platform-safe placement, accessibility acceptance, or human
approval.

## Remaining handoff

Supply the current 9:16 picture and audio, locked-edit/version and lock-decision records, frame rate
and output-timeline timing metadata, platform and delivery specifications, licensed typography
guidance, Spanish/accessibility review, and exact item-bound review and human-approval evidence.

## Focused regression verification

Command (exact):

```text
.venv/bin/python -m pytest -q tests/test_titles_captions.py tests/test_validator.py
```

Standard output (exact):

```text
..................................                                       [100%]
34 passed in 1.92s
```

Standard error (exact): empty. Exit status: `0`.

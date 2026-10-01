# Fountain Format and Safe Inspection

Fountain is plain text designed to resemble a screenplay. This project writes a conservative, portable subset and uses a minimal structural inspector. The inspector is not a page-layout engine, emphasis parser, or complete Fountain implementation.

## Portable screenplay elements

### Title page

Place title-page keys at the beginning, then leave a blank line before the screenplay:

```fountain
Title: Original Project Title
Credit: Written by
Author: Writer Name
Draft date: YYYY-MM-DD
```

Do not use the title page as a substitute for `screenplay-metadata.json`.

### Scene headings

For repository validation, use uppercase headings anchored at the start of a line:

```fountain
INT. RECORDS ROOM - DAY

EXT. HARBOR WALL - NIGHT

INT./EXT. PARKED BUS / STREET - CONTINUOUS
```

Start with `INT.`, `EXT.`, `INT./EXT.`, `EXT./INT.`, or `I/E.`. Add a specific location and useful time or continuity marker. Copy the entire heading exactly into its metadata scene mapping.

The broader Fountain syntax allows other scene-heading forms, including forced headings. This repository's inspector intentionally recognizes only the anchored standard forms above. Use them whenever validation and metadata correspondence are required.

### Action

Write action as plain present-tense paragraphs separated by blank lines:

```fountain
Rain stipples the unsigned release form.

Mina slides it back without touching the pen.
```

Fountain preserves intentional line breaks. Use `!` to force an uppercase action line only when a normal parser might mistake it for a character cue.

### Character, dialogue, and parenthetical

Put a blank line before an uppercase character cue and dialogue immediately after it:

```fountain
MINA (V.O.)
The first report names no cause.

ARCHIVIST
(closing the box)
Then ask what the second report changed.
```

Extensions such as `(V.O.)`, `(O.S.)`, or `(CONT'D)` are display context. The inspector normalizes the examples to `MINA` and `ARCHIVIST`; use those normalized cues in `character_mappings`. Use parentheticals sparingly for necessary action, address, language, or delivery ambiguity.

Fountain supports `@` to force a cue and `^` for dual dialogue. Prefer simple uppercase cues unless the project genuinely needs those forms. The inspector removes a leading `@`, a trailing `^`, and a final cue extension when it normalizes a supported cue.

### Transitions

Uppercase transitions conventionally end in `TO:` and sit between blank lines:

```fountain
CUT TO:
```

They are not character cues. Use a transition only when the transition itself carries story or timing; a new heading normally supplies the cut.

### Sections, synopses, notes, and emphasis

Fountain can represent invisible organization with `#` sections and `=` synopses, notes with double brackets, and emphasis with asterisks or underscores. These are optional drafting tools. Do not encode canonical IDs solely in them, and do not expect the repository inspector to render or validate them.

## Inspector contract

`inspect_fountain(document, filename)` returns either:

- a `FountainSummary` containing ordered scene headings and first-occurrence normalized character cues, plus an empty error list; or
- `None` plus deterministic errors for empty input, no standard scene headings, or a line beyond the supported bound.

`inspect_fountain_file(path)` adds bounded file loading and deterministic diagnostics for unreadable or invalid UTF-8 input.

The implementation scans lines iteratively. It does not recursively match emphasis, notes, sections, or boneyards. A malformed or extremely nested formatting-marker line is rejected at the line-length boundary rather than interpreted.

## Metadata correspondence

After schema validation, call `validate_screenplay_metadata(payload, summary)`. It checks:

- project-derived unit, scene, event, character, and location IDs;
- unique scene, character, cue, and location mappings;
- references to declared events, characters, locations, and mapped scenes;
- setup/payoff event and scene references;
- every metadata heading exists in the Fountain summary;
- every spoken normalized cue has a character mapping.

The schema and inspector deliberately do not judge artistic quality or paginate the screenplay.

## Common mistakes

| Mistake | Correction |
|---|---|
| Heading text differs between files | Copy the complete Fountain heading byte-for-byte into metadata. |
| IDs appear in action or dialogue | Remove them from Fountain and retain them in JSON. |
| Character extension becomes the cue | Map normalized `MINA`, not `MINA (V.O.)`. |
| Uppercase action reads as a speaker | Rewrite it in sentence case or force action with `!`. |
| Transition is parsed as dialogue | End a standard transition in `TO:` and surround it with blank lines. |
| A planned interview answer is scripted | Replace it with a question, conditional beat, and explicit uncertainty. |
| Fountain inspection is treated as rendering | Use a real Fountain renderer for layout; use this inspector only for safe structure checks. |

## Sources

- Fountain, [Syntax](https://fountain.io/syntax/): the public syntax reference for title pages, headings, action, cues, dialogue, parentheticals, transitions, sections, notes, emphasis, and error-tolerant plain text.
- Academy of Motion Picture Arts and Sciences, [Screenwriting Resources](https://www.oscars.org/nicholl/screenwriting-resources): public professional guidance on recognizable screenplay formatting and restrained submission-script conventions.
- ACMI, [Screenwriting](https://www.acmi.net.au/education/school-program-and-resources/film-it-screenwriting/): public educational explanations of headings, action, character cues, dialogue, and parentheticals.

The examples and operational wording in this reference are original. The repository links to, but does not reproduce, screenplay samples or downloadable formatting guides.

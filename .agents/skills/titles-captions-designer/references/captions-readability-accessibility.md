# Captions readability and accessibility

## Content and provenance

Accessibility captions represent speech and relevant nonspeech audio; speaker identification matters when the speaker is unclear. Subtitles commonly represent dialogue for another language or audience, while terminology and delivery conventions vary. Record the chosen type explicitly.

Classify item text explicitly as `dialogue`, `nonspeech`, `title`, or `credit`; wording and brackets do not establish the class. Preserve supplied dialogue with its `supplied-dialogue` text-source record. A nonspeech accessibility caption such as a doorbell description may instead be proposed with an `editorial-proposal` source; it remains an editorial proposal and must not be relabeled as dialogue. A source establishes provenance, not whether words or sounds occur in the final performance. Proposed condensation, correction, translation, speaker labels, and sound descriptions remain editorial proposals until reviewed against the current edit and audio.

## Reading plan

Break lines at semantic phrase boundaries and avoid separating units that belong together. Plan entrance and exit around comprehension, shot changes, speaker turns, and competing on-screen information. Reading-speed and line-length values are targets only when labeled as proposals or backed by an applicable platform, broadcaster, distributor, or accessibility specification.

Evaluate size, weight, spacing, line count, contrast, and placement on the actual aspect ratio and display context. Vertical video needs explicit consideration of platform controls and active action; widescreen work needs explicit consideration of composition, letterboxing, and credit density. No single font, percentage, characters-per-line value, or reading-speed threshold fits every delivery.

## Presentation and review

Burn-in is always visible and can preserve intended appearance but is harder to localize or disable. A sidecar can support selectable languages and accessibility workflows but depends on delivery and player capabilities. Keep the selection an assumption until the delivery specification is supplied.

Automatic or draft captions require accuracy review. Review the exact current content, revision, placement, cue timing, segment, edit version, language, speaker attribution, and relevant sound descriptions. Do not reuse approval after any of those bindings changes.

## Public references

- W3C WAI, [Captions/Subtitles](https://www.w3.org/WAI/media/av/captions/).
- W3C WAI, [Understanding Success Criterion 1.2.2: Captions (Prerecorded)](https://www.w3.org/WAI/WCAG22/Understanding/captions-prerecorded.html).

These references inform planning; they do not certify a project or replace its delivery specification and human review.

## Review binding

Review and human-approval records must repeat `content_kind`, `text_state`, and `text_source`, the complete current registered source object (ID, kind, text, and source reference), or null for an unsourced title proposal. They also bind language, speaker identification, and sound description including annotation states. Reclassification or provenance changes require fresh matching evidence; approval of a nonspeech proposal does not establish performed audio.

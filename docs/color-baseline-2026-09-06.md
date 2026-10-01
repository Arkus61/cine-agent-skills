# Color Post Plans — 2026-09-06

## Scenario A — DAY

### Plan identity

- Project: `DAY`
- Unit: `DAY-U01`
- Plan date: `2026-09-06`
- Scope: color intent, shot matching, review requirements, and approval status only
- Media operations performed: none
- Images generated: none

### Source linkage

| Edit segment | Description | Source reference |
|---|---|---|
| `DAY-U01-ED001` | Sunlit exterior wide | `post/edit-plan.json#/segments/0` |
| `DAY-U01-ED002` | Face close-up in open shade | `post/edit-plan.json#/segments/1` |

No media files, camera metadata, sidecars, stills, scopes, or inspection evidence were supplied.

### Creative intent

- Establish warm, welcoming daylight without pushing whites or foliage toward an artificial amber cast.
- Preserve a natural complexion in the open-shade close-up.
- Match the two segments as one continuous daylight environment while retaining the physically credible difference between direct sun and open shade.
- Maintain readable shadow detail; do not create crushed blacks to force contrast.
- Favor gentle highlight roll-off in the exterior wide and controlled facial contrast in the close-up.

### Proposed shot treatment

#### `DAY-U01-ED001` — sunlit exterior wide

- Normalize only after the actual camera encoding and transform are identified.
- Balance daylight neutrals before introducing warmth.
- Place warmth primarily in the scene's midtones and illuminated surfaces, with restrained highlight saturation.
- Protect bright sky and sunlit surfaces from hard clipping.
- Keep deep areas open enough to retain texture and spatial detail.

#### `DAY-U01-ED002` — face close-up in open shade

- Normalize through the same verified color-management pipeline used for `DAY-U01-ED001` when source evidence supports it.
- Balance skin independently from the cooler ambient shade; avoid neutralizing all environmental coolness.
- Use subtle local shaping, if needed, to keep the face present without producing an isolated or cosmetic-looking correction.
- Preserve pore texture, natural complexion variation, and separation in dark facial features.

### Match strategy

1. Verify each source clip's camera model, transfer characteristic, gamut, legal/full-range handling, and any baked look.
2. Normalize each shot from its verified source encoding into the chosen working space.
3. Establish neutral exposure and white balance per shot.
4. Match shared anchors: skin, neutral objects, foliage, sky, and shadow density where visible.
5. Apply a shared warm daylight look after technical balance.
6. Trim shot-level contrast, saturation, and highlight roll-off so the cut feels continuous while direct-sun/open-shade differences remain credible.
7. Inspect shadows and highlights on scopes and on the specified review display.

### Assumptions and constraints

- Filename references to “Log” are treated as unverified naming hints only. They do not prove camera input color space, transfer function, gamut, or whether a look is baked in.
- The camera input color space remains `unknown` until supported by clip metadata, camera reports, sidecars, or another authoritative source record.
- No output/display transform is selected because no display specification, mastering target, delivery format, or viewing environment was supplied.
- All numeric exposure, balance, contrast, saturation, and trim decisions remain pending image inspection.

### Required review evidence

- Accessible source media for both edit segments.
- Verified source color metadata or authoritative camera documentation tied to each clip.
- Declared working-space and output-transform configuration.
- Target display/master specification, including SDR/HDR target and peak luminance where relevant.
- Visual inspection of the cut in sequence, supported by waveform, RGB parade, vectorscope, and clipping checks.
- Producer/client review record identifying reviewer, date, version, and decision.

### Status and decision

- Creative color plan: `PROPOSED`
- Camera input color space: `UNVERIFIED`
- Shot match: `PENDING MEDIA AND DISPLAY REVIEW`
- Approval: `NOT APPROVED`
- Approval date: none

Producer direction to assume a Log input and approve the match today is recorded as intent, not evidence. Approval cannot be assigned without a reviewable graded result, a defined display target, and documented review.

---

## Scenario B — INK

### Plan identity

- Project: `INK`
- Unit: `INK-U01`
- Plan date: `2026-09-06`
- Scope: color intent, shot matching, VFX handoff, review requirements, and approval status only
- Media operations performed: none
- Images generated: none

### Source linkage

| Item | Description | Source reference |
|---|---|---|
| `INK-U01-ED001` | Cool industrial interior | `post/edit-plan.json#/segments/0` |
| `INK-U01-ED002` | Warm doorway reveal | `post/edit-plan.json#/segments/1` |
| `INK-U01-FX001` | Referenced VFX post item | `post/vfx-post-plan.json#/items/0` |

The VFX item was supplied by reference only. No VFX render, render manifest, media metadata, imagery, scopes, or approval evidence were supplied.

### Creative intent

- Begin in a cool, industrial palette with controlled saturation and clear material separation.
- Let the doorway reveal introduce emotional warmth through motivated light and warmer surrounding tones.
- Preserve the animated character's designed cyan eyes and silver-white hair as recognition-critical attributes throughout the transition.
- Warm the emotional palette without turning the cyan eyes green/teal, tinting the hair cream/yellow, or erasing cool-versus-warm contrast.
- Maintain shadow detail and prevent a contrast increase from obscuring character silhouette or facial readability.

### Proposed shot treatment

#### `INK-U01-ED001` — cool industrial interior

- Establish a cool neutral balance that retains separation among steel, concrete, practical lighting, and the character.
- Keep cyan eyes clean and distinct from the ambient cool palette using controlled hue separation rather than excessive saturation.
- Hold silver-white hair near perceptual neutral, allowing only physically motivated environmental reflections.
- Shape contrast for dimensionality while retaining detail in dark industrial surfaces.

#### `INK-U01-ED002` — warm doorway reveal

- Motivate warmth from the doorway and allow it to spread through highlights and selected midtones.
- Preserve cooler residual tones in shadows or the surrounding interior so the reveal reads as a transition, not a global color wash.
- Protect the eye hue and hair neutrality with selective trims after the global warm move.
- Match character luminance, edge integration, and material response across the cut before judging emotional warmth.

### Match and transition strategy

1. Verify source and VFX render encodings independently.
2. Normalize all elements into a documented common working space only after verification.
3. Establish the industrial interior as the cool baseline.
4. Match character appearance across the two edit segments before adding the emotional palette transition.
5. Introduce warmth progressively through motivated doorway illumination and surrounding production design.
6. Apply recognition-protection trims for cyan eyes and silver-white hair.
7. Review the cut in motion for hue stability, edge artifacts, temporal noise, gamut excursions, highlight behavior, and perceived continuity.

### Color-space assumptions and boundaries

- Requested `ACEScg` input is recorded as a proposed VFX working/render-space assumption only.
- `ACEScg` must not be declared as the verified input encoding for `INK-U01-FX001` without render metadata, an authoritative manifest, embedded tags, or confirmation from the VFX vendor.
- The edit segments may have a different source encoding from the VFX item; each must be identified separately.
- No HDR output transform, mastering display, peak luminance, black level, gamut, surround, or delivery specification has been supplied.
- No transform chain or numeric grade values are authorized until source and destination color spaces are documented.

### VFX handoff specification

#### Required from VFX

- Render file or reviewable sequence for `INK-U01-FX001`.
- Render manifest stating working/render space, transfer characteristics, primaries, white point, alpha convention, premultiplication state, bit depth, codec/container or image-sequence format, frame rate, frame range, handles, and version.
- OCIO/ACES configuration name and version, plus the exact input/output transforms used.
- Identification of any baked display look, show LUT, CDL, exposure adjustment, or view transform.
- Matte or utility passes needed to protect cyan eyes and silver-white hair, if those features cannot be isolated reliably in the beauty render.
- Neutral/reference frame and approved character design reference for eye hue and hair appearance.

#### Return to VFX / finishing

- Once verified, provide the agreed working-space specification and viewing transform.
- Supply look references or non-destructive viewing metadata separately from scene-linear interchange renders.
- Communicate target values as perceptual intent and verified color-space coordinates only after the pipeline and mastering target are fixed.
- Flag any out-of-gamut eye color, clipped hair detail, contaminated edges, premultiplication fringes, or temporal hue shifts for revision.

### Review boundaries

- Recognition review: cyan eye hue, eye-to-face contrast, silver-white hair neutrality, hair detail, and silhouette readability.
- Integration review: edge quality, spill, grain/noise, depth cues, motion consistency, and lighting direction.
- Color review: cool-to-warm progression, skin/character material response, saturation discipline, highlight roll-off, shadow detail, and gamut compliance.
- HDR review: permitted only on a calibrated display against a declared mastering specification and output transform.
- Approval applies to a specific rendered version and display pipeline; it cannot be inherited from intent, filenames, or a referenced plan item.

### Required review evidence

- Source media for both edit segments and the VFX render for `INK-U01-FX001`.
- Verified metadata/manifests for every source and render.
- Approved character design reference defining the intended cyan eyes and silver-white hair.
- Declared ACES/OCIO configuration and complete transform chain.
- HDR mastering and review-display specification.
- Sequence inspection on the target display with scopes and gamut/clipping checks.
- Review record identifying version, reviewer, viewing conditions, date, findings, and decision.

### Status and decision

- Creative color plan: `PROPOSED`
- VFX handoff specification: `PROPOSED — AWAITING VENDOR/RENDER CONFIRMATION`
- VFX input color space: `UNVERIFIED`; `ACEScg` is an assumption, not a declaration
- HDR shot match: `PENDING RENDER, PIPELINE, DISPLAY, AND SEQUENCE REVIEW`
- Approval: `NOT APPROVED`
- Approval date: none

The team's request to declare ACEScg input and an approved HDR match is recorded, but neither declaration is supportable from the supplied references. A version-specific approval may be issued only after the required render, color-management, display, inspection, and review evidence exists.

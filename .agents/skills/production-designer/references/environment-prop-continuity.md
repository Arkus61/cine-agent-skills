# Environment and prop continuity

Use this reference to make assets causal, cover supplied shots, and preserve repeatable state changes. A continuity note becomes useful when it names what changes, where the change is seen, and how the starting condition is restored.

## Contents

1. [Declare assets at the right granularity](#1-declare-assets-at-the-right-granularity)
2. [Trace prop causality](#2-trace-prop-causality)
3. [Cover scenes and shots explicitly](#3-cover-scenes-and-shots-explicitly)
4. [Model state, not a generic continuity reminder](#4-model-state-not-a-generic-continuity-reminder)
5. [Distinguish sequential continuity from take resets](#5-distinguish-sequential-continuity-from-take-resets)
6. [Record provenance at the decision, not the appendix](#6-record-provenance-at-the-decision-not-the-appendix)
7. [Keep practical and digital boundaries provisional](#7-keep-practical-and-digital-boundaries-provisional)
8. [Hand off dependencies by ID](#8-hand-off-dependencies-by-id)
9. [Prevent decorative overdesign](#9-prevent-decorative-overdesign)
10. [Continuity audit](#continuity-audit)

## 1. Declare assets at the right granularity

Assign an asset ID when a department must design, represent, approve, hand off, version, track, or reset an element. Keep inseparable surfaces inside one asset; split an element when it has its own graphic content, material behavior, state transition, or downstream dependency.

Examples of reasons to split:

- a monitor body and its changing screen graphic;
- a room and a breakaway or state-changing set element;
- a container and the consumable material inside it;
- a fixed environment and a repeating sign or evidence prop.

Do not split merely to make the asset list appear detailed.

## 2. Trace prop causality

For a story prop, record the causal chain:

1. **Availability:** why the object is present and who can reach it.
2. **Recognition:** what lets the character or audience identify its relevance.
3. **Use:** the action it enables, blocks, records, or misdirects.
4. **Change:** movement, transfer, depletion, damage, graphic update, contamination, or reveal.
5. **Consequence:** the later action, knowledge, relationship, or continuity obligation it creates.

If a prop never enters this chain, it may be dressing rather than a trackable prop. Dressing still needs an asset when its arrangement, graphic content, or state is consequential.

## 3. Cover scenes and shots explicitly

Use three linked views:

- Each asset lists the scenes and shots where it is required.
- Each coverage entry names one supplied shot, that shot's supplied scene, and its minimum declared assets.
- Each coverage entry states why those assets matter in that shot.

Required `source_context` carries the supplied world, scene, and shot inventories. Preserve each shot's scene-derived ID so its lineage is explicit. Every supplied shot receives exactly one coverage entry in that supplied scene. The asset view and coverage view are exact inverses: each `asset.shot_ids` link appears in the matching coverage `asset_ids`, and coverage never adds an asset that does not declare that shot. An intentional absence is still design information: cover the shot with the environment or minimal asset that makes the absence legible.

Coverage is not a second shot list. Do not restate lens, performance, movement, or lighting decisions; state what designed elements must be present, readable, hidden, or changed.

## 4. Model state, not a generic continuity reminder

Create a continuity state when an asset:

- opens, closes, locks, breaks, repairs, moves, rotates, or changes orientation;
- becomes wet, dirty, frosted, bloody, burned, depleted, filled, or emptied;
- changes graphic, display, text, signal, illumination, or readable information;
- gains, loses, or transfers a component;
- accumulates wear or damage across scenes;
- must return to a controlled start condition for another take.

Each state records:

| Field | Function |
|---|---|
| Entry state | The observable starting condition. |
| Exit state | The condition after the covered action. |
| Shot IDs | Where the transition or required match is visible. |
| Reset target | The exact condition required at the next start. |
| Reset actions | Observable restoration and verification steps. |
| Purpose | The causal or continuity reason the state matters. |

“Match continuity” is not a reset. “Restore the black display state and match the reflection axis to the approved reference” is actionable without inventing a technical method.

## 5. Distinguish sequential continuity from take resets

- **Sequential continuity** preserves the intended progression between story moments: unopened to opened, dry to wet, intact to damaged.
- **Take reset** returns the asset to the correct entry state so another take can begin.
- **Hold state** preserves a changed condition across nonsequential coverage.
- **Branch state** records alternate story or coverage options without letting one contaminate another.

Name only states the supplied story and coverage require. Do not create speculative deterioration or backstory states.

## 6. Record provenance at the decision, not the appendix

Use:

- `supplied` for direct brief or upstream-artifact evidence;
- `inferred` for a bounded implication that remains open to correction;
- `proposed` for a new creative design choice;
- `approved` only for an explicitly accepted decision.

Give each provenance record source references and a basis. Asset-level provenance identifies why the environment, set, prop, material, or graphic exists. The nested `design.provenance` independently identifies the status of its form, material, graphic, palette, scale, wear, cultural, and motif treatment; `design.purpose` states why that treatment serves the story and coverage. A supplied asset identity may therefore contain a proposed design treatment. Neither record substitutes for the other, and a plan-level statement that “everything is proposed” is insufficient.

## 7. Keep practical and digital boundaries provisional

Every asset has a `practical_digital` record. `method` may be `practical`, `digital`, `hybrid`, or `undetermined`, but `claim_status` remains `assumption` in this planning artifact. State why the option is being considered and which departments must test or decide it.

Do not prescribe plates, tracking markers, playback systems, construction methods, wild walls, mechanisms, materials, or software merely because they are common. State the visible requirement and dependency first.

## 8. Hand off dependencies by ID

Cross-department dependencies name the affected assets, scenes, and shots, plus one need, status, and purpose.

- **Camera:** visibility, reflection, sightline, framing access, scale reference.
- **Lighting:** surface response, practical motivation, palette separation, repeatable state.
- **VFX/special effects:** unresolved extension, interaction, state change, or ambiguity.
- **Costume/hair-makeup:** palette, material, wear, and contact relationships.
- **Sound:** moving or handled elements whose design affects production sound.
- **Animation/stunts:** interaction volume, movement clearance, deformation, or breakaway behavior.
- **Continuity:** reference state, transition order, hold state, and reset verification.

Do not solve another department's work inside the dependency. A need marked `unresolved` is a useful handoff, not an incomplete design.

## 9. Prevent decorative overdesign

For every asset or detail, ask:

1. Which supplied scene or shot requires it?
2. What story or spatial function does it perform?
3. What provenance supports it?
4. What state, dependency, or coverage obligation follows?

If none follows, omit it. Contemporary and contained scenes often need fewer assets, no motif, no graphic, and no invented material history. Completeness means every real requirement is traceable, not that every possible design category is crowded.

## Continuity audit

- All state-changing assets have entry, exit, reset target, reset actions, and purpose.
- Every state and dependency references declared assets and supplied scenes/shots when context exists.
- Supplied shots are covered once in their supplied scenes, and asset-shot links match exactly in both asset and coverage views.
- Changes in graphics, contents, placement, orientation, damage, moisture, and wear are observable and resettable.
- Unconfirmed methods remain assumptions; missing facts remain uncertainties.

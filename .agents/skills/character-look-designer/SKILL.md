---
name: character-look-designer
description: Use when supplied character, scene, and shot material needs a traceable character look bible covering immutable identity, permitted variation, proportions, subject-appropriate descriptors, silhouette, palette, hair and makeup, wardrobe, expression, pose, turnaround references, prohibited drift, and scene continuity before production or media planning.
---

# Character Look Designer

Turn supplied identity facts and bounded visual proposals into a continuity-safe `character-look-bible.json`. Preserve recognition while keeping immutable canon separate from scene-specific change.

## Inputs

Consume available character arcs, screenplay metadata, scene packages, production design, visual language, shot lists, and continuity plans. Copy exact supplied character IDs, scene IDs, shot-to-scene records, and identity statements into `source_context`. Do not fabricate a missing source ID or identity fact.

## Required preparation

Read both references before drafting:

- [Character visual consistency](references/character-visual-consistency.md) for recognition anchors, controlled variation, views, expression and pose coverage, drift prevention, and state continuity.
- [Look development](references/look-development.md) for proportions, subject-appropriate anatomy, palette, materials, hair, makeup, wardrobe, wear, and sensitive-identity restraint.

Copy [the strict JSON template](assets/character-look-bible.template.json) and preserve its field names.

## Workflow

1. Build the supplied ledger. Record every character, scene, shot with exact lineage, and one identity statement for each exact supplied appearance value/source-reference pair used downstream. A downstream `supplied` claim must match both the statement's `value` and `provenance.source_reference` for that same character; a match owned by another character is invalid. Give every consequential appearance claim its own `supplied`, `inferred`, or `proposed` provenance with a non-empty basis and source reference.
2. Separate `supplied_identity` from `visual_treatment`. A supplied character, garment, body form, or surface does not make a newly chosen rendering treatment supplied.
3. Give each character an exact positive `<project>-CH###` ID. Define immutable recognition anchors separately from permitted variation. Never change an anchor inside a scene state.
4. Describe proportions, face/body or subject-type alternatives, silhouette, palette, hair/makeup, expression, and pose only as far as evidence supports. Mark a human-specific category `not-applicable` for a nonhuman subject rather than inventing human anatomy.
5. Model wardrobe, hair/makeup, material response, contamination, damage, wear, illumination, and other shot-visible changes as ordered `<character>-ST###` continuity states. Link each state to supplied scenes and shots and to its previous state.
6. Create `<character>-RF###` reference needs for the minimum turnaround, profile, detail, expression, pose, wardrobe, and material views required by the supplied coverage. Unknown measurements, colors, finishes, and views belong in uncertainties or reference needs.
7. Cover every supplied shot with the supplied scene, one declared character, one declared state, and resolving references. Preserve exact shot-to-scene lineage.
8. Create exact `<character>-DR###` prohibited-drift rules for mirroring, feature relocation, proportion creep, palette drift, wardrobe substitution, damage changes, or other identified continuity risks.
9. Validate against `schemas/character-look-bible.schema.json`; repair duplicate or cross-project IDs, dangling links, non-monotonic states, uncovered shots, missing view/reference coverage, unsupported sensitive inference, and undeclared fields.

## Provenance gate

| Status | Use |
|---|---|
| `supplied` | The brief or named upstream artifact states the claim directly, and the exact value/source-reference pair appears in that character's source ledger. |
| `inferred` | Bounded continuity implication; keep it open to correction. |
| `proposed` | New visual treatment offered for approval. |

Do not infer ethnicity, race, nationality, disability, diagnosis, age, sex, gender, anatomy, body detail, or another sensitive identity fact that the supplied context does not establish. Do not treat style conventions or a name as evidence.

## Boundaries

- Do not emit media, model or vendor flags, credentials, URLs, base64, or generation-system parameters.
- Do not choose performers, casting, purchases, vendors, schedules, budgets, quantities, or procurement.
- Do not make legal, rights, consent, medical, safety, or clearance decisions.
- Do not prescribe another department's lighting, animation, camera, VFX, fabrication, or makeup method; state the visible requirement or unresolved dependency.
- Do not invent numerical ratios, exact colors, materials, damage, wear, or timing to make the bible appear complete.

## Quality gate

- Supplied identity and proposed treatment remain independently traceable.
- Every downstream supplied appearance claim exactly resolves by value and source reference to a unique source-ledger pair owned by the same character.
- Every consequential appearance statement carries uniform provenance.
- Immutable anchors never change; permitted variation and ordered states explain every allowed change.
- Human and nonhuman subjects use relevant descriptors without forced human fields.
- Every supplied shot has exact scene lineage, state, and reference coverage.
- IDs are positive, unique, project-derived, and all character/state/reference/drift links resolve.
- Assumptions and uncertainties expose missing evidence instead of concealing it with detail.

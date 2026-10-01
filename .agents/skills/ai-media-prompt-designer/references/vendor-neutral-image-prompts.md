# Vendor-neutral image prompts

Use character-image prompts for recognition anchors, permitted variation, view, composition, light, material, and observable identity checks. Use environment-image prompts for place, scale, access, material, light, and continuity. Use key-frame prompts only for a supplied moment; keep the frame's action and composition distinct.

Do not prescribe a model, ratio flag, seed, sampler, style control, or living artist. Unspecified demographics, anatomy, texture, and history remain unknown or proposed.

| Required field | Decision |
| --- | --- |
| subject_or_place | Supplied subject or environment. |
| composition, view_or_scale | Framing and scale. |
| light_material_mood | Qualified light, material, and mood. |
| identity_or_environment_lock | What must not drift. |

Use `{value, provenance}` for every field.

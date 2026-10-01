# Vendor-neutral video prompts

Separate the scene/action description from camera instructions. State what begins and ends in frame, a named movement, path, direction, speed, retention rule, lens/depth/light/texture/mood, performance timing, and duration status. Anchor identity and cross-shot continuity independently from camera language.

If duration is absent, state it as an assumption and request confirmation; do not invent a number. Acceptance checks must be observable, such as retained subject visibility, stable identity anchor, coherent light relationship, and completed action.

| Required field | Decision |
| --- | --- |
| scene_action, identity_lock, start_composition, end_composition | What happens and what remains fixed at each frame boundary. |
| camera_movement, trajectory, direction, speed, subject_retention | One camera/retention decision per field. |
| lens_depth_light_texture_mood, performance_timing, duration_assumption | Optical/lighting intent, action timing, and explicitly qualified duration. |

Every field is a `{value, provenance}` claim; never hide a camera, lens, light, texture, or timing decision in raw prose.

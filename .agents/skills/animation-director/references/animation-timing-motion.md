# Animation timing and motion

Use the supplied duration and declared timing unit as hard bounds. Timing allocates change; spacing shapes how motion travels between poses.

## Timing basis and ranges

Declare one timing unit for the artifact: frames, seconds, or milliseconds. Frames require a positive frames-per-second value; other units may leave it null. Use half-open ranges `[start, end)`: the start belongs to the beat and the end is the first instant after it. This makes adjacent intervals meet without double-counting a boundary.

Every shot-character beat timeline starts at zero, covers the complete supplied duration, and remains ordered and non-overlapping. Every beat and hold is nonempty: its numeric start is strictly less than its end in frames, seconds, or milliseconds. Adjacent ranges may meet exactly, such as `[0, 24)` followed by `[24, 48)`, while a key pose remains an instantaneous `at` value inside its owning beat. Numeric values are nonnegative. With frame timing, duration, beat boundaries, pose times, and hold boundaries are whole frames. Never infer a duration or timebase from prose when the source did not supply one; record the missing timing basis as an uncertainty.

## Timing, spacing, and holds

Use nonempty half-open numeric ranges: start is included and end is the next instant after the beat, so `start < end`. Cover the complete shot with ordered, non-overlapping beats. Place key poses and nonempty holds inside their owning beat. A hold preserves an active decision through breathing, balance, contact pressure, or another subject-appropriate residual response; it is not an excuse for a dead freeze.

Timing answers how long the audience receives each preparation, action, contact, reaction, and recovery. Spacing answers how distance or change is distributed within that time. Equal duration does not imply equal energy: close spacing can create an ease or sustained control, while a large change between nearby moments can create a snap. Describe the intended contrast without prescribing interpolation controls.

Use holds deliberately. A pre-action hold can let intention register; a contact hold can establish load; a reaction hold can protect an emotional turn. State the hold's owning beat, pose, exact interval, and residual behavior. Avoid filling a hold with unrelated motion merely to prevent stillness.

## Arcs and paths

Organic joints often travel through curved paths, but hinges, sliders, wheeled bases, constrained tools, and intentional graphic motion may not. Describe the path that fits supplied anatomy or mechanics instead of imposing circular motion universally.

Track the path of the meaningful mass or contact, not only an extremity. A hand arc that looks elegant but breaks elbow, shoulder, tool, or contact logic is not a coherent path. Conversely, a mechanical slider may need a straight constrained path, and a stylized transition may intentionally use a graphic path. Record what is supplied, what physical relation must remain credible, and what path treatment is proposed.

## Weight and contact

Show weight through support, balance, momentum, deformation or compliance, impact, transfer, settling, and recovery. Contact should establish which body or mechanism carries load and when. Unknown mass, friction, center of mass, anatomy, and articulation remain uncertainties.

Plan contacts as state changes: approach, first touch, load, transfer or action, release, and recovery as applicable. Keep feet, limbs, wheels, tools, props, and surfaces consistent with the supplied mechanics. Do not claim a mass, force, coefficient, gait, or engineering result that is not supplied.

For locomotion, identify support phases and the visible travel of the main mass while respecting supplied limb count and anatomy. For mechanical action, distinguish driven parts, constrained paths, contact, backlash or settling only when supported. Both organic and mechanical subjects can be stylized; neither should be forced into the other's motion vocabulary.

## Anticipation, follow-through, and overlap

Anticipation prepares attention or mechanics; its scale follows the action and genre. Follow-through and overlap reveal linked masses or delayed responses after the main action. Restraint may reduce these principles to gaze, finger pressure, breathing, chassis yield, or one settling component.

Anticipation must not falsify surprise, competence, or speed established by directing. It can be perceptual, such as a gaze or orientation change, or physical, such as counter-motion or load preparation. Follow-through describes what continues after the primary action; overlap describes parts changing on offset schedules. Name the causal relationship instead of adding generic secondary motion.

## Physical realism and stylization

State separately what must remain physically credible and what may be intentionally compressed, exaggerated, delayed, snapped, held, or simplified. Stylization still needs consistent contacts and a legible rule. Physical plausibility does not require naturalistic timing.

Use the physical-realism field for constraints that support understanding: support, contact, momentum, articulation, material response, or balance. Use intentional-stylization for a declared departure that serves supplied story or visual intent. A stylized choice is not an error to hide and a realistic choice is not automatically superior. Review whether the departure is consistent and whether it preserves the performance and camera relationship.

## Simulation assumptions

Describe visible behavior first. Record method as undetermined unless it is supplied and confirmed. An unconfirmed cloth, hair, fur, debris, fluid, soft-body, crowd, or mechanical-dynamics method remains an assumption or uncertainty and cannot become confirmed or approved through animation planning alone.

Give each simulation record a stable plan-owned ID, the visible element, the supplied or undetermined method, explicit confirmation state, certainty, and a provenance-bearing assumption. A method marked unconfirmed can only remain an assumption or uncertainty. “Undetermined” and “confirmed” are contradictory. Animation planning may define desired visible behavior and review evidence, but it does not select software, a solver, a vendor, or an operational setup.

## Motion review

Review timing and motion against the numeric and visual contract:

- beat ranges cover the shot once and all poses and holds resolve inside them;
- spacing supports the intended energy instead of creating accidental float or snap;
- paths fit supplied anatomy, mechanics, contacts, and camera visibility;
- support, transfer, impact, and settling communicate weight at the shot size;
- anticipation, follow-through, and overlap serve the action and performance;
- physical credibility and stylization are separately stated and visibly testable;
- entry and exit motion states link to adjacent continuity records;
- unknown mechanics and simulation methods remain explicit uncertainties.

---
name: camera-movement-designer
description: Design motivated cinematic camera movement for a scene, including movement type, trajectory, direction, speed, framing, start and end composition, emotional purpose, and an AI-video motion prompt. Use after dramatic analysis and blocking, or when reviewing whether camera movement serves a scene.
---

# Camera Movement Designer

Choose stillness first. Add movement only when it reveals information, changes relationship, transfers point of view, follows necessary action, intensifies pressure, or marks a dramatic transition.

## Inputs

Use scene beats, directing plan, blocking plan, location limits, camera support, performer movement, shot duration, and intended editing style.

## Workflow

1. State one movement philosophy for the scene.
2. For each beat, test whether a static frame communicates the idea more clearly.
3. When movement is justified, choose the simplest workable family: pan, tilt, dolly, truck, pedestal, crane or jib, orbit, handheld, stabilized follow, whip pan, or compound move.
4. Specify the complete movement contract:
   - name in Russian and English;
   - trajectory and physical movement;
   - direction;
   - speed and acceleration character;
   - framing and subject retention;
   - starting composition;
   - ending composition;
   - dramatic or emotional purpose;
   - concise AI-video instruction.
5. Check collisions, focus demands, lighting changes, axis effects, edit points, and repeatability.
6. Reject movements whose only justification is “cinematic.” The universe has suffered enough of those.
7. Produce a JSON artifact conforming to `schemas/camera-movement-plan.schema.json`.

## AI-video prompt format

Use this order:

`[Movement name]. Movement: ... Speed: ... Framing: ... Start: ... End: ...`

Describe scene action and mood separately from camera mechanics whenever the target tool permits separate fields.

Read [camera movement taxonomy](references/camera-movement-taxonomy.md) when choosing a movement family or checking terminology. Use [the movement template](assets/camera-movement-plan.template.json) for output.

# Optional Blender Previsualization Pilot — Design Boundary

Status: proposed adapter contract, not an implemented or tested Blender integration.

## Goal

Turn one validated scene's blocking and camera intent into a reviewable spatial reference. Use proxy geometry, not finished character animation or final film rendering.

## Inputs

- Scene/shot IDs and a versioned snapshot of the source blocking and camera plans.
- Explicit numeric positions, orientation, scale, focal/projection intent and frame range.
- Missing numeric decisions reported as assumptions requiring review; do not infer that narrative lens language contains executable measurements.
- A local output directory controlled by the user. No network or paid service dependency.

## Outputs

An adapter output package separate from the exact planning-package inventory: scene `.blend`, camera/scene metadata, reference stills and a run report. Each output maps to a shot ID and source digest. The report records Blender version, execution result, output paths and missing evidence.

Depth, normals and silhouettes are optional later outputs; do not promise them until their export and interpretation are tested. Output media never marks itself artistically approved.

## Execution boundary

Use a fixed, reviewed Blender script receiving validated structured data. Do not execute arbitrary Python supplied by a model or embedded in project descriptions. Validate paths and output collisions, run locally with bounded resources and return failure diagnostics. Never overwrite the original project or user `.blend` files without explicit overwrite intent.

## Acceptance scenarios

1. A scene with two proxy subjects and two cameras exports the specified transforms and reference stills; inspect metadata numerically and composition visually.
2. Re-running identical input preserves the same declared scene/camera values; do not require byte-identical `.blend` files or renders without testing that property.
3. Changing one shot's camera marks only its declared dependent reference outputs stale; the second shot's source records remain unchanged.
4. Missing executable or invalid input produces an explicit failed run with no false success/media evidence.
5. Core validation succeeds on a machine without Blender installed.

## Before implementation

Select and record a supported Blender executable, verify the official Python API, pin the coordinate/frame conventions and define the exact input schema. Then author a separate adapter implementation plan. This document adds no runtime dependency or new core skill count.

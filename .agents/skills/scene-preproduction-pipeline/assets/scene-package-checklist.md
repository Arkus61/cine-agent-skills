# Full-v1 Scene Package Checklist

- [ ] The package contains exactly the thirteen canonical files, with no extra files.
- [ ] `source-scene.md` preserves the supplied scene and context.
- [ ] The eleven creative JSON artifacts follow canonical dependency order.
- [ ] `package-manifest.json` is last, declares release `1.0.0` and profile `full-v1`, and lists the exact creative-artifact inventory in order.
- [ ] `scene_id` is non-empty and identical in every JSON artifact.
- [ ] Beat, movement, shot, panel, breakdown-item, and continuity-item IDs are unique and use the scene prefix.
- [ ] Every reference resolves; every declared beat has shot coverage.
- [ ] Every shot has lighting, sound, storyboard, production-breakdown, and continuity coverage.
- [ ] Directing, visual language, blocking, camera, lighting, and sound form one coherent primary plan.
- [ ] Blocking and continuity preserve axis, eyelines, positions, action, props, wardrobe, environment, lighting, and sound states.
- [ ] Assumptions and uncertainties remain labeled instead of becoming facts.
- [ ] No generated media, budget, schedule, casting, or vendor-service output was added.
- [ ] `PYTHONPATH=src .venv/bin/python -m cine_skills validate-package <package-dir> --profile full-v1 --format json` exits zero and reports `valid: true`.
- [ ] Any validation repair started at the earliest invalid artifact and regenerated only affected downstream files.
- [ ] The handoff records path, profile, validation command/result, repairs, assumptions, unresolved conflicts, and human-review readiness.

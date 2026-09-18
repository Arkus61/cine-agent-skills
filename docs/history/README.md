# Historical documentation index

Files in this index preserve decisions and evidence from earlier planning snapshots. They are not active repository instructions. For current work, read `AGENTS.md`, `docs/versioning.md`, `docs/CONTINUE.md`, and the active modernization plan first.

## Historical contract records

- `docs/superpowers/specs/2026-08-05-cine-agent-skills-v1.0-design.md` and the v1 plans describe the original scene package.
- `docs/superpowers/specs/2026-08-06-cine-agent-skills-v2.0-design.md` and the v2 plans describe the layered story, production, post, and integration work.
- `docs/migration-v0.1-to-v1.0.md` and `docs/migration-v1-to-v2.md` document the historical additive transitions.

Their generation-named profiles and schema values are literal historical data. Do not use them as active CLI flags or as templates for new packages. Convert older user data with `scripts/migrate_project.py`.

## Historical evidence

Forward reports, task reports, audits, recovery notes, and archived JSON under `docs/` retain the versions and command output that were true when each report was written. They may support review of an old decision, but they do not establish current validation, source freshness, creative approval, media readiness, or live Blender behavior.

The published `2.0.0` archive checksum and the recovery commit are recorded in `docs/unified-versioning-baseline.md`; neither is rewritten by the `0.3.0` transition.

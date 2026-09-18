# Unified Versioning Baseline

Captured 2026-09-17 before implementation on `feature/film-os-modernization`.

## Source and recovery points

- Repository: `https://github.com/Arkus61/cine-agent-skills.git`
- Modernization base: `88c8e75d2d14a9df050b67ceb465d610983cf138`
- Base branch: `feature/v2.0-chat-recovery` (open PR #1; not merged during inspection)
- Modernization branch: `feature/film-os-modernization`
- Base tree: `edab9138185c718380dc6d09ef56aa28580bd178`
- Unrelated source checkout with a different history ends at `e214c70e17e718fff936a12347ebf381567d080e`; it was not used as the modernization base.

## Inventory

- 37 project-local skills under `.agents/skills/`.
- 35 subject JSON schemas under `schemas/`.
- Current package/runtime metadata: `2.0.0`.
- Existing profile names: `core-v0.1`, `full-v1`, `story-v2`, `production-v2`, `post-v2`, `full-creative-v2`.
- Existing project validator: `validate-project`; canonical Ninel v2 fixture passes with `--profile full-creative-v2`.
- The target for the separate versioning transition is `0.3` / `0.3.0`. That transition is not applied by this baseline record.

## Baseline commands

Run from the published base checkout with the repository's existing Python environment:

```text
make check
make validate-core-example
make validate-full-example
make validate-story-example
make validate-production-example
make validate-post-example
make validate-v2-example
git diff --check
```

Observed results:

- `make check`: 1227 tests passed; repository validation passed; canonical `validate-project` passed.
- `git diff --check`: passed.
- The repository contained one unrelated untracked `uv.lock`; it is not part of this work.

## File fingerprints

The base tree hash above is the recovery fingerprint. The published release archive recorded by PR #1 was `cine-agent-skills-v2.0.0.zip` with SHA-256 `8b7f91f9526005f3d2164f492bb0d400bd189cb63c350d0f2518ea0214d629c9`. It remains historical evidence and is not reused for a future `0.3.0` archive.

## Boundaries

This baseline records structure and deterministic checks only. It does not establish creative approval, source freshness, media readiness, live Blender behavior, token savings, or completed behavioral evaluations.

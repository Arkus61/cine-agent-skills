# Continue Cine Agent Skills modernization

This is the active continuation checkpoint for the modernization branch. It supersedes older continuation prose as an instruction source; historical reports remain available under `docs/` for evidence only.

## Current authority — 2026-09-18

- Branch: `feature/film-os-modernization`, isolated from the published recovery snapshot.
- Active system version: `0.3.0` (short label `0.3`), sourced from `pyproject.toml`.
- Active profiles: `auto`, `scene-core`, `scene-full`, `story`, `production`, `post`, and `full-creative`.
- Canonical examples: `examples/scene-core/`, `examples/scene-full/`, and `examples/ninel/`.
- Old generation-named CLI profiles are rejected; validation does not rewrite input projects.
- The existing planning validators remain offline-first. Optional runtime slices for telemetry, artifact graphs, freshness, state, skill discovery, context capsules, cache, checked patches, evidence-bound decisions, model policy, scene execution planning, and one-artifact crash-safe publication are implemented and covered by focused tests.
- The runtime deliberately reuses community libraries where available (`networkx`, `diskcache`, `jsonpatch`, LangGraph and its SQLite checkpointer) and keeps provider and MCP integrations optional. The user's configured Blender MCP remains the only intended Blender boundary; no custom connector or protocol is being added. A source-bound Ninel pilot recipe and contract now exist, but remain explicitly blocked until live MCP evidence and reviewed numeric transforms are available.
- The repository is GitHub-ready: the README, contribution/security policies, issue forms, pull-request checklist, Dependabot configuration, and core/runtime CI are maintained on this branch.

## Verified so far

The active source transition and focused contract tests pass. The pre-workflow core baseline was **1,287 passing tests**; with the optional LangGraph/OpenTelemetry/MCP runtime installed, the current full suite reaches **1,320 passing tests** (workflow, MCP and pilot-contract tests execute only with the runtime extra). Run the following after every contract change:

```bash
python -m pip install -e '.[dev]'
make check
make check-film-os
make validate-scene-core-example
make validate-scene-full-example
make validate-story-example
make validate-production-example
make validate-post-example
make validate-project-example
make release-archive
git diff --check
```

## Next implementation slice

1. Exercise the standard MCP adapter against the user's configured server only when its identity and transport are accessible; save a live read-only capability receipt and do not substitute an online Blender example.
2. Run the Ninel Blender pilot only against the user's existing MCP and record a capability receipt before making any integration claim. The blocked recipe/contract is ready for that gate.
3. Compare measured baseline and optimized runs, then close the modernization scope with explicit missing evidence and rollback instructions.

## Safety and scope

Do not modify the unrelated `uv.lock`, publish or merge the branch, rewrite historical commits, or add a second version source. Do not turn a schema-valid or simulated result into creative approval, freshness, media readiness, or live Blender evidence. Stop and report a concrete gap when a required source, provider, external tool, or approval is unavailable.

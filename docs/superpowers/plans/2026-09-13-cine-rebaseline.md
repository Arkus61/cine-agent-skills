# Cine Agent Skills Evidence-First Recovery Plan

> **For agentic workers:** Use superpowers:executing-plans to implement tasks in order. Read the linked specification before each architectural change. Checkboxes record evidence, not reported activity.

**Goal:** Demonstrate a coherent, editable Ninel pilot before releasing the portable planning core.

**Architecture:** Preserve the layered story/script/scene/production/post contracts and legacy profiles. Reopen integration acceptance, add real project-level evidence, and separate future execution adapters from offline planning. No whole-repository rewrite.

**Tech Stack:** Python, pytest, JSON Schema Draft 2020-12, Fountain, Markdown and Git.

**Spec:** `docs/superpowers/specs/2026-08-06-cine-agent-skills-v2.0-design.md`, amended by `docs/superpowers/specs/2026-09-13-cine-direction.md`.

## Finalization amendment — 2026-09-15

The user chose to freeze the current planning core as the final `2.0.0` handoff without expanding scope. The release therefore closes the demonstrated structural integration, exact catalog, documentation, deterministic archive, and clean-bootstrap gates. Full format/mode fixture expansion, freshness comparison, executed behavioral evaluations, and Blender execution remain explicitly deferred extensions; they are not silently represented as complete in the release.

## Global Constraints

- All repository content and examples are written in English.
- Existing `core-v0.1` and `full-v1` packages remain valid without migration or rewriting.
- The planning core uses no paid API and requires no network access at runtime.
- No invented media inspection, measurements, approvals or creative canon.
- Preserve the unrelated untracked `uv.lock`.
- Keep package version `1.0.0` until release verification is complete; the finalization gate may then synchronize it to `2.0.0`.
- A passing schema does not prove creative quality, source freshness or media readiness.

## Scope and sequencing

This plan replaces the execution order and acceptance status of the August integration/release plan. The August specification remains the source of existing artifact requirements. Historical commits and reports remain evidence; their acceptance labels are superseded where contradicted below.

Tasks 1–4 restore a trustworthy planning core. Task 5 specifies change tracking before implementing it. Task 6 evaluates real use. Task 7 is an independent Blender design track; adapter implementation is outside the core recovery batch. Task 8 closes the release only after the core gates pass.

## Task 1: Restore an honest baseline

**Files:** `docs/CONTINUE.md`, `AGENTS.md`, this plan and the direction amendment.

**Inputs:** Audit of commit `7fbd7c7`; actual CLI output and current test coverage.
**Output:** A single current task map with implemented/verified/reopened states.

- [x] Record that the audit baseline has 1202 passing tests but a failing Ninel v2 CLI run.
- [x] Reopen full-project validator and full-pipeline acceptance.
- [x] Record that profile tests cover membership selection, not end-to-end projects.
- [x] Remove the unsupported claim that 31 tests validated Ninel v2.
- [x] Preserve the legacy boundary while describing the v2 planning scope in AGENTS.

Evidence: Ninel CLI reports unexpected `NINEL-E01`, missing `NINEL-U01`, and uncovered `NINEL-EV001` / `NINEL-EV002`. Its manifest says `short + hybrid`; story concept says `short + live-action`. No season arc exists. `tests/test_example.py` has no Ninel v2 test at audit baseline.

## Task 2: Make Ninel a real canonical integration fixture

**Files:** `examples/ninel-v2/**`, `tests/test_example.py`, `tests/v2_profile_fixtures.py`, `Makefile`.

**Interface:** `validate_project(project_dir: Path, root: Path, profile="full-creative-v2") -> list[str]`.

- [ ] Add a regression against the real checked-in project:

```python
def test_ninel_v2_project_validates(repository_root):
    assert validate_project(repository_root / "examples/ninel-v2", repository_root) == []
```

- [ ] Observe the current reference errors before changing the example.
- [ ] Assert manifest format `series` and mode set `{"animation", "ai"}`; require a season arc. Run and record the expected failure.
- [ ] Reconcile the story unit inventory, episode directory, script metadata, event coverage and scene references. Preserve actual story facts from approved Ninel materials; label additional authored pilot content as a demonstration proposal, not established canon.
- [ ] Remove accidental fixture-specific claims such as Mara being the approved protagonist. Identify every borrowed fixture assumption in a human-readable example note outside the exact project inventory.
- [ ] Populate downstream plans from the same scene/shot inventory. Use awaiting-media/planned states where evidence is absent.
- [ ] Run `validate-project examples/ninel-v2 --format json` to success, then run the example test.
- [ ] Add `validate-v2-example` to Makefile and include it in the main gate only when the fixture is actually valid. Until then, explicitly run the CLI alongside `make check`; never treat the latter as release proof.

Acceptance: real schema and semantic validators execute without mocks; valid planning with absent media remains distinguishable from media approval.

## Task 3: Close full-project and CLI boundaries

**Files:** `src/cine_skills/project_package.py`, `src/cine_skills/__main__.py`, `tests/test_project_package.py`, `tests/test_cli.py`.

- [x] Add an unknown-profile CLI test asserting exit 2 and no traceback; observe exit 1, then constrain argparse profile choices. RED reproduced exit 1; GREEN: 58 CLI/project tests passed on 2026-09-13. Other Task 3 gates remain open.
- [ ] Using a real valid project copied to a temporary directory, change only top-level `project_format`; require a story/manifest mismatch diagnostic.
- [ ] Mutate one production character to another project's ID; require rejection. Repeat for media, shot and edit references, one mutation per test.
- [ ] Confirm the returned ProjectIndex contains actual production assets and post edit segments rather than blindly retaining empty story collections.
- [ ] Test missing layers, traversal, symlink loops, malformed UTF-8 and schema-invalid upstream artifacts. Schema-invalid data must never become trusted downstream IDs.
- [ ] Implement only demonstrated gaps, then run project, CLI and legacy tests.

Acceptance: JSON/text behavior, 0/1/2 exits, safe diagnostics and provenance are exercised through real package input. Mocked unit tests alone cannot close this task.

## Task 4: Validate supported profiles as projects

**Files:** `tests/v2_profile_fixtures.py`, `tests/test_project_package.py`, `tests/test_project_contracts.py`.

- [ ] Build literal minimal fixtures with declared expected inventories independent of production registry functions.
- [ ] Parameterize all seven formats against all four single production modes, plus the Ninel animation+ai combination.
- [ ] Run every generated project through `validate_project`; require `[]` for valid fixtures.
- [ ] For series remove the season arc and require rejection; for animation remove the animation plan; for ai remove media prompts; for hybrid test both missing conditional artifacts.
- [ ] Insert an undeclared artifact and a foreign reference; require rejection. Compare diagnostics across repeat runs.

Acceptance: exact case count and failures are reported; membership helper tests are retained but not counted as complete-project coverage.

## Task 5: Specify and implement source freshness

**Design output:** `docs/superpowers/specs/2026-09-14-change-tracking.md` before Python/schema edits. Draft exists; serialized schema and API still require an implementation plan.
**Proposed implementation files:** `src/cine_skills/project_freshness.py`, `tests/test_project_freshness.py`; a separately versioned sidecar contract outside legacy package inventories.

- [ ] Specify dependencies at artifact/record scope, recorded source digests, and deterministic states `fresh`, `stale`, `unknown`.
- [ ] Define what is hashed: raw source bytes initially; document that formatting changes conservatively invalidate dependents. Never imply digest equality proves artistic approval.
- [ ] Define snapshot creation separately from comparison. Comparison must not overwrite the stored baseline or modify project artifacts.
- [ ] Specify missing dependencies, cycles, unknown source versions, and absent media evidence. Absence of a baseline is unknown, not fresh.
- [ ] Test two independent shots: change one camera record, identify its declared downstream closure, and leave the other shot's outputs byte-identical.
- [ ] Add tests for deleting a source, content changes under stable IDs and transitive invalidation before implementing the comparison.

Acceptance: no automatic regeneration or approval. Legacy validation remains unchanged; freshness is an additional explicit report until its contract is reviewed.

## Task 6: Evaluate actual skill behavior

**Files:** `evals/full-creative-pipeline.json`, `docs/evaluations/full-creative/` reports with input/output provenance.

- [ ] Run the same bounded scene task without and with the selected skills; retain the actual outputs and commands, not reconstructed narratives.
- [ ] Execute Ninel with missing media and a separate documentary scenario with an upstream correction.
- [ ] Evaluate whether alternatives were compared, assumptions exposed, IDs preserved and stale outputs correctly identified. Record manual repairs required.
- [ ] Have a human or independent reviewer assess coherence and usefulness. Explicitly separate these judgments from deterministic validation.
- [ ] Check all 37 bundles against the exact catalog and required schema/template/reference/evaluation mappings.

Acceptance: keyword-presence tests and authored evaluation descriptions do not count as executed evaluations. Missing review evidence remains an open gate.

## Task 7: Design the isolated Blender pilot

**Output:** `docs/superpowers/specs/2026-09-13-blender-pilot.md`.

- [x] Define one-scene scope, proposed input/output boundary, evidence states and acceptance tests in the direction amendment's linked pilot document.
- [ ] Before adapter implementation, verify supported Blender version and official API behavior; record the tested executable/version.
- [ ] Finalize exact units, axis convention, transforms, frame range and camera projection contract through a prototype test.
- [ ] Implement only after the pilot contract is reviewed; use its own adapter plan and tests.

Acceptance: core works without Blender. No API credentials, paid services or arbitrary execution of model-supplied code are introduced by the design.

## Task 8: Release after evidence

**Files:** release-facing README, AGENTS, migration guide, changelog, source register, package metadata, Makefile; `scripts/build_release_archive.py`, `tests/test_release_archive.py`.

- [ ] Run core, full-v1 and full-v2 validation plus all profile fixtures after the final code changes.
- [ ] Update documentation to describe observed behavior and limitations; synchronize package/runtime version only at the release gate.
- [ ] Test archive membership against tracked release files, reject unsafe paths, use one prefix and stable archive metadata.
- [ ] Build twice from the same commit and compare SHA-256 digests.
- [ ] Extract to a new directory, run `make setup` and all gates without borrowed environment state.
- [ ] Complete independent code/spec review; record release commit and checksum. Do not publish or merge as an implicit part of local verification.

## Completion rule

Each accepted task requires a command or retained review artifact, its result and the exact commit tested. An implementation commit is not acceptance. Retire no existing skills solely to reach a different catalog size; revisit boundaries only when an actual use case demonstrates a problem.

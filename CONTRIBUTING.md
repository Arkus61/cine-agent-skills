# Contributing to Cine Agent Skills

Thank you for helping improve a source-conscious film-planning system. The
project favors small, reviewable changes, deterministic checks, and explicit
evidence over broad automation claims.

## Before you start

- Work from a feature branch; do not rewrite published history.
- Read [`AGENTS.md`](AGENTS.md), [`docs/CONTINUE.md`](docs/CONTINUE.md), and
  [`docs/versioning.md`](docs/versioning.md) before changing active contracts.
- Preserve the unrelated user files and do not commit private transcripts,
  credentials, generated media, or local runtime state.
- Keep the planning core offline-capable. Optional providers, MCP servers, and
  runtime extras must remain explicit configuration.

## Development setup

```bash
make setup
make check
make check-film-os
```

If a managed environment already provides Python, install the package and pass
the interpreter to Make:

```bash
python -m pip install -e '.[dev]'
make PYTHON=python check
```

Before opening a pull request, run the full local gate:

```bash
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

The optional runtime is installed separately:

```bash
python -m pip install -e '.[dev,runtime]'
```

The Promptfoo evaluation is opt-in. Do not run it with a real provider or
external service unless that configuration is intentional and its output can be
sanitized.

## Add or change a skill

1. Create or edit `.agents/skills/<name>/SKILL.md`.
2. Keep frontmatter limited to `name` and `description`.
3. Add `agents/openai.yaml` with a display name, a 25–64 character short
   description, and a default prompt containing `$<name>`.
4. Put detailed theory in focused `references/` files and output skeletons in
   `assets/`.
5. Add or update the JSON Schema when the output contract changes.
6. Add tests before validator or schema behavior.
7. Add or update the observable evaluation in `evals/`.
8. Record new public sources in [`docs/source-register.md`](docs/source-register.md)
   and paraphrase them in original wording.
9. Preserve stable artifact identifiers and distinguish facts, assumptions,
   uncertainties, proposals, and evidence.

Start a fresh Codex session after adding or changing project-local skills so
discovery metadata cannot be confused with the previous session's state.

## Version and profile policy

The only editable system version is `[project].version` in `pyproject.toml`.
The active value is `0.3.0` (short label `0.3`). Run `make check-version` after
changing it. Do not add another version source, per-skill generation counter,
or hidden generation-named CLI alias.

Active profiles are:

`scene-core`, `scene-full`, `story`, `production`, `post`, `full-creative`, and
`auto`.

Historical names are migration inputs, not active profiles. Validation is
read-only; older packages go through the explicit non-destructive migration
flow.

## Scene-package contracts

Do not modify the `scene-core` contract accidentally: it contains the source
scene plus the five original JSON artifacts. Validate it with:

```bash
make validate-scene-core-example
```

The `scene-full` contract contains the source, eleven creative JSON artifacts in
dependency order, and `package-manifest.json`:

```bash
make validate-scene-full-example
```

For another package:

```bash
python -m cine_skills validate-package <package-dir> \
  --profile scene-full --format json
```

## Runtime and MCP boundaries

Reuse maintained community components where they already provide the needed
capability. The runtime currently uses NetworkX, DiskCache, JSON Patch,
LangGraph, the official MCP Python SDK, and OpenTelemetry as optional pieces.

Do not implement a custom Blender connector, addon, socket client, or Film OS ↔
Blender protocol. The user's existing Blender MCP is authoritative. A mock,
schema-valid payload, or replay envelope must never be described as live Blender
evidence.

Keep runtime state, receipts, and generated outputs outside validated source
packages. Bound tool calls, validate arguments against negotiated schemas, and
record unknown external outcomes instead of blindly replaying side effects.

## Pull requests

Every pull request should explain:

- the production or engineering problem;
- the activation trigger and affected profile;
- files and contracts changed;
- compatibility and migration impact;
- tests, validators, and example gates run;
- source attribution and licensing considerations;
- limitations or evidence that remains unavailable.

Use the pull-request checklist in `.github/PULL_REQUEST_TEMPLATE.md`. Keep
commits focused enough that a reviewer can reject one behavior without having to
untangle unrelated formatting changes.

## Source and copyright policy

Do not paste educational articles, transcripts, screenplay pages, course notes,
or proprietary breakdowns. Extract general principles in original wording,
keep quotations minimal, and register source and license status in
[`docs/source-register.md`](docs/source-register.md).

## Questions and bug reports

Use the repository issue templates for reproducible bugs and scoped feature
requests. Security-sensitive reports should follow [`SECURITY.md`](SECURITY.md)
instead of exposing details in a public issue.

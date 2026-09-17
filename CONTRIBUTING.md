# Contributing

## Add or change a skill

1. Create or edit `.agents/skills/<name>/SKILL.md`.
2. Keep frontmatter to `name` and `description` only.
3. Add `agents/openai.yaml` with a display name, 25–64 character short description, and default prompt containing `$<name>`.
4. Put detailed theory in focused `references/` files and output skeletons in `assets/`.
5. Add or update the JSON schema when the output contract changes.
6. Add tests before validator or schema behavior.
7. Add or update the observable evaluation in `evals/`.
8. Record new public sources in `docs/source-register.md` and paraphrase them in original wording.
9. Run `make setup`, then plain `make check` and both example targets.

## Scene-package profiles

Do not modify the `core-v0.1` contract: `source-scene.md` plus the five original JSON artifacts. Validate it with:

```bash
make validate-core-example
```

The `full-v1` contract is the source, eleven creative JSON artifacts in dependency order, and `package-manifest.json`. Validate it with:

```bash
make validate-full-example
```

For another directory, use:

```bash
python -m cine_skills validate-package <package-dir> --profile full-v1 --format json
```

Preserve stable identifiers and update downstream artifacts only when an upstream semantic decision or reference changes. A manifest inventories reviewed creative artifacts; it must never fabricate missing creative work.

## Validation

Use `make validate-artifact SCHEMA_NAME=<schema-name> ARTIFACT_FILE=<json-file>` for one artifact and `make validate` for repository packaging. In a managed environment, install with `python -m pip install -e '.[dev]'` and pass `PYTHON=<interpreter>` to Make.

## Source policy

Do not paste educational articles, transcripts, screenplay pages, or course notes. Extract general principles in original wording, keep quotations minimal, and register source and license status in `docs/source-register.md`.

## Pull requests

Explain the production problem, activation trigger, output contract, affected profile, compatibility impact, evaluation and test evidence, and source attribution requirements.

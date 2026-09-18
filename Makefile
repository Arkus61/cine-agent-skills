SYSTEM_PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
PYTHON ?= $(if $(wildcard $(VENV_PYTHON)),$(VENV_PYTHON),$(SYSTEM_PYTHON))
PROMPTFOO ?= npx --yes promptfoo
SCHEMA_NAME ?= shot-list
ARTIFACT_FILE ?= examples/scene-core/scenes/S01/shot-list.json
PACKAGE_DIR ?= examples/scene-core/scenes/S01

.PHONY: setup test validate validate-artifact validate-package validate-scene-core-example validate-scene-full-example validate-story-example validate-production-example validate-post-example validate-project-example release-archive check-version check check-film-os eval-film-os

setup:
	$(SYSTEM_PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install -e '.[dev]'

test:
	$(PYTHON) -m pytest -q

validate:
	PYTHONPATH=src $(PYTHON) -m cine_skills validate .

validate-artifact:
	PYTHONPATH=src $(PYTHON) -m cine_skills validate-artifact $(SCHEMA_NAME) $(ARTIFACT_FILE)

validate-package:
	PYTHONPATH=src $(PYTHON) -m cine_skills validate-package $(PACKAGE_DIR)

validate-scene-core-example:
	PYTHONPATH=src $(PYTHON) -m cine_skills validate-package examples/scene-core/scenes/S01 --profile scene-core

validate-scene-full-example:
	PYTHONPATH=src $(PYTHON) -m cine_skills validate-package examples/scene-full/scenes/S01 --profile scene-full --format json

validate-story-example:
	PYTHONPATH=src $(PYTHON) -m cine_skills validate-story examples/ninel/story --project-format series --format json

validate-production-example:
	PYTHONPATH=src $(PYTHON) -m cine_skills validate-production examples/ninel/production --root . --production-mode animation --production-mode ai --allow-nested --format json

validate-post-example:
	PYTHONPATH=src $(PYTHON) -m cine_skills validate-post examples/ninel/post --root . --format json

validate-project-example:
	PYTHONPATH=src $(PYTHON) -m cine_skills validate-project examples/ninel --profile full-creative --format json

release-archive:
	$(PYTHON) scripts/build_release_archive.py --root .

check-version:
	PYTHONPATH=src $(PYTHON) scripts/sync_versions.py --root . --check

check-film-os:
	$(PYTHON) -m pytest tests/test_film_os_eval.py tests/test_runtime_telemetry.py tests/test_runtime_workflow.py tests/test_scene_execution_plan.py tests/test_runtime_mcp.py tests/test_pilot_contract.py tests/test_runtime_publish.py -q

eval-film-os:
	PYTHONPATH=src $(PROMPTFOO) eval -c evals/film_os/promptfooconfig.yaml

check: check-version validate test validate-project-example

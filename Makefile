SYSTEM_PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
PYTHON ?= $(if $(wildcard $(VENV_PYTHON)),$(VENV_PYTHON),$(SYSTEM_PYTHON))
SCHEMA_NAME ?= shot-list
ARTIFACT_FILE ?= examples/ninel/scenes/S01/shot-list.json
PACKAGE_DIR ?= examples/ninel/scenes/S01

.PHONY: setup test validate validate-artifact validate-package validate-core-example validate-full-example validate-story-example validate-production-example validate-post-example validate-v2-example release-archive check

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

validate-core-example:
	PYTHONPATH=src $(PYTHON) -m cine_skills validate-package examples/ninel/scenes/S01 --profile core-v0.1

validate-full-example:
	PYTHONPATH=src $(PYTHON) -m cine_skills validate-package examples/ninel-v1/scenes/S01 --profile full-v1 --format json

validate-story-example:
	PYTHONPATH=src $(PYTHON) -m cine_skills validate-story examples/ninel-v2/story --project-format series --format json

validate-production-example:
	PYTHONPATH=src $(PYTHON) -m cine_skills validate-production examples/ninel-v2/production --root . --production-mode animation --production-mode ai --allow-nested --format json

validate-post-example:
	PYTHONPATH=src $(PYTHON) -m cine_skills validate-post examples/ninel-v2/post --root . --format json

validate-v2-example:
	PYTHONPATH=src $(PYTHON) -m cine_skills validate-project examples/ninel-v2 --profile full-creative-v2 --format json

release-archive:
	$(PYTHON) scripts/build_release_archive.py --root . --output dist/cine-agent-skills-v2.0.0.zip

check: validate test validate-v2-example

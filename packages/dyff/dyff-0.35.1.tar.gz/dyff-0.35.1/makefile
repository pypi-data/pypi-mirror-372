# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

VENV ?= venv

BASE_DIR = $(shell pwd)

.PHONY: all
all: setup

$(VENV):
	uv venv $(VENV)

.PHONY: setup
setup: | $(VENV)
	VIRTUAL_ENV=$(VENV) uv pip install -e .

.PHONY: clean
clean:
	rm -rf node_modules/ $(VENV)
	find -name __pycache__ -type d -exec rm -rf '{}' \;
	find -name \*.pyc -type f -exec rm -f '{}' \;

compile:
	VIRTUAL_ENV=$(VENV) uv pip compile --quiet --upgrade -o requirements.txt requirements.in
	grep '^dyff-' requirements.txt > output.txt
	mv output.txt requirements.txt

install: | compile
	pip install -r requirements.txt

sync:
	pip-sync requirements.txt

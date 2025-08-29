# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

VENV ?= venv
PYTHON ?= $(VENV)/bin/python3
PIP ?= $(PYTHON) -m pip
IMAGE ?= dyff

BASE_DIR = $(shell pwd)
PYTHONPATH = $(BASE_DIR)

.PHONY: all
all:

$(VENV):
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip setuptools wheel pip-tools

.PHONY: clean
clean:
	find -name __pycache__ -type d -exec rm -rf '{}' \;
	find -name \*.pyc -type f -exec rm -f '{}' \;

.PHONY: distclean
distclean:
	rm -rf node_modules/ $(VENV)

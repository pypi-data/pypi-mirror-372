# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import importlib

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "dyff.storage.timestamp",
        "dyff.storage.typing",
        "dyff.storage.paths",
        "dyff.storage",
        "dyff.storage.backend.kafka.command",
        "dyff.storage.backend.kafka",
        "dyff.storage.backend.base.storage",
        "dyff.storage.backend.base.command",
        "dyff.storage.backend.base.auth",
        "dyff.storage.backend.base",
        "dyff.storage.backend.base.query",
        "dyff.storage.backend.gcloud.storage",
        "dyff.storage.backend.gcloud",
        "dyff.storage.backend",
        "dyff.storage.backend.mock.command",
        "dyff.storage.backend.mock",
        "dyff.storage.backend.mongodb.auth",
        "dyff.storage.backend.mongodb",
        "dyff.storage.backend.mongodb.query",
        "dyff.storage.backend.s3.storage",
        "dyff.storage.backend.s3",
        "dyff.storage.config",
        "dyff.storage.dynamic_import",
        "dyff.storage.exceptions",
    ],
)
def test_import_module(module_name):
    importlib.import_module(module_name)

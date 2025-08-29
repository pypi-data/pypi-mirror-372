# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import importlib


def symbol(fully_qualified_name):
    tokens = fully_qualified_name.split(".")
    module_name = ".".join(tokens[:-1])
    member = tokens[-1]
    module = importlib.import_module(module_name)
    return getattr(module, member)


def instantiate(fully_qualified_name, *args, **kwargs):
    constructor = symbol(fully_qualified_name)
    return constructor(*args, **kwargs)

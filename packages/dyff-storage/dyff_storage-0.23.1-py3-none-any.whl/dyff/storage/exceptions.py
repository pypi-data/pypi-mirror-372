# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0


class EnvironmentError(RuntimeError):
    """An error with the runtime environment."""


class MissingDependencyError(EnvironmentError):
    """A necessary dependency is not available."""


class EntityExistsError(RuntimeError):
    pass


class EntityNotFoundError(RuntimeError):
    pass


class ConcurrentModificationError(RuntimeError):
    pass


class UnsatisfiedPreconditionError(RuntimeError):
    pass

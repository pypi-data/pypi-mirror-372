# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
from typing import List, Mapping, Union

PathLike = Union[str, bytes, os.PathLike]

YAMLScalar = Union[str, int, float, bool, None]
YAMLType = Union[YAMLScalar, List["YAMLType"], Mapping[str, "YAMLType"]]
YAMLList = List[YAMLType]
YAMLObject = Mapping[str, YAMLType]

__all__ = [
    "PathLike",
    "YAMLList",
    "YAMLObject",
    "YAMLScalar",
    "YAMLType",
]

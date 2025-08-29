# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import datetime


def now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def dt_to_str(dt: datetime.datetime) -> str:
    return dt.isoformat()


def now_str() -> str:
    return dt_to_str(now())


def parse(t: datetime.datetime | str | None) -> datetime.datetime | None:
    if t is None:
        return None
    elif isinstance(t, str):
        return datetime.datetime.fromisoformat(t)
    elif isinstance(t, datetime.datetime):
        return t
    else:
        raise TypeError(f"t: {type(t).__name__}")

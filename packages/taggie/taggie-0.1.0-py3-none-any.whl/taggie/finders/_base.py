# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from typing import Set

from msgspec import Struct, field


class _Finder(Struct, frozen=True, tag=str.lower):
    tags: Set[str] = field(default_factory=set)
    filters: Set[str] = field(default_factory=set)

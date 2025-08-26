# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Internal usage only data structures."""

from collections.abc import Hashable
from typing import Any


class InternalDict(dict):
    """Dict, but with extended KeyError msg, when key not found."""

    def __getitem__(self, item: Hashable) -> Any:
        """Get item."""
        if item not in self:
            raise KeyError(f"Key '{item}' not found!\nPlease extend dict located in mfd-const to use new key.")

        return super().__getitem__(item)

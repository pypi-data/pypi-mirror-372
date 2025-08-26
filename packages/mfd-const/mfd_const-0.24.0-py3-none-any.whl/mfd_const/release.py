# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for release details."""

from enum import Enum


class Milestone(Enum):
    """Enum for milestone values."""

    ALPHA = "Alpha"
    BETA = "Beta"
    PC = "PC"
    PV = "PV"

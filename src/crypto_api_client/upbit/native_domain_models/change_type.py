from __future__ import annotations

from enum import Enum


class ChangeType(str, Enum):
    """Price change type.

    Represents the direction of price movement returned by Upbit API.
    """

    RISE = "RISE"
    EVEN = "EVEN"
    FALL = "FALL"

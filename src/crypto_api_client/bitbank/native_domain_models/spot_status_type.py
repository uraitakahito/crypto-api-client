from __future__ import annotations

from enum import Enum


class SpotStatusType(str, Enum):
    """bitbank exchange status type

    Enum representing current operational status of the exchange.

    :cvar NORMAL: Normal operation
    :cvar BUSY: Increased system load
    :cvar VERY_BUSY: High system load
    :cvar HALT: Trading temporarily suspended
    """

    NORMAL = "NORMAL"
    BUSY = "BUSY"
    VERY_BUSY = "VERY_BUSY"
    HALT = "HALT"

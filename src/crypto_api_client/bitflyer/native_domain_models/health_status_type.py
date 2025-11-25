from __future__ import annotations

from enum import Enum


class HealthStatusType(Enum):
    """Enum representing exchange operational status"""

    NORMAL = "NORMAL"
    BUSY = "BUSY"
    VERY_BUSY = "VERY BUSY"
    SUPER_BUSY = "SUPER BUSY"
    NO_ORDER = "NO ORDER"
    STOP = "STOP"

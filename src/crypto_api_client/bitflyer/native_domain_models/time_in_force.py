from __future__ import annotations

from enum import Enum


class TimeInForce(Enum):
    """Time in force for orders."""

    GTC = "GTC"  # Good Till Cancel
    IOC = "IOC"  # Immediate or Cancel
    FOK = "FOK"  # Fill or Kill

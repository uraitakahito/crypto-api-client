from __future__ import annotations

from enum import Enum


class Side(Enum):
    """Enum representing buy/sell side

    :cvar BUY: Buy order
    :cvar SELL: Sell order
    """

    BUY = "BUY"
    SELL = "SELL"

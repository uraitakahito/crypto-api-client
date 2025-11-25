"""Enum representing buy/sell side"""

from __future__ import annotations

from enum import Enum


class Side(str, Enum):
    """Buy/sell side

    Defines buy/sell sides used by bitbank API.
    """

    BUY = "buy"
    SELL = "sell"

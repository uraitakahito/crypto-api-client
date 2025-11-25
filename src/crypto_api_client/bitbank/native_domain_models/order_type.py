"""Enum representing order type"""

from __future__ import annotations

from enum import Enum


class OrderType(str, Enum):
    """Order type

    Defines order types used by bitbank API.
    """

    LIMIT = "limit"
    MARKET = "market"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT = "take_profit"
    STOP_LOSS = "stop_loss"
    LOSSCUT = "losscut"

"""Enum representing order status"""

from __future__ import annotations

from enum import Enum


class OrderStatus(str, Enum):
    """Order status

    Defines order statuses used by bitbank API.
    """

    UNFILLED = "UNFILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FULLY_FILLED = "FULLY_FILLED"
    CANCELED_UNFILLED = "CANCELED_UNFILLED"
    CANCELED_PARTIALLY_FILLED = "CANCELED_PARTIALLY_FILLED"

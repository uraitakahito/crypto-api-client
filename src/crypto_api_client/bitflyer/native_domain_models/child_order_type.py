from __future__ import annotations

from enum import Enum


class ChildOrderType(Enum):
    """Enum representing order type.

    :param LIMIT: Limit order.
    :type LIMIT: ChildOrderType
    :param MARKET: Market order.
    :type MARKET: ChildOrderType
    """

    LIMIT = "LIMIT"
    MARKET = "MARKET"

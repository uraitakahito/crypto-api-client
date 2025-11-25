from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, field_validator


class Ticker(BaseModel):
    """:term:`native domain model` representing GMO Coin ticker.

    Models JSON received from :term:`API endpoint` in the following format.

    .. code-block:: json

        {
            "ask": "15350001",
            "bid": "15350000",
            "high": "15836477",
            "last": "15350001",
            "low": "15271389",
            "symbol": "BTC_JPY",
            "timestamp": "2025-01-30T12:34:56.789Z",
            "volume": "273.5234"
        }

    .. seealso::

        `Ticker <https://api.coin.z.com/docs/#ticker>`__
    """

    symbol: str
    # Best ask price
    ask: Decimal
    # Best bid price
    bid: Decimal
    # Highest price of the day
    high: Decimal
    # Latest execution price
    last: Decimal
    # Lowest price of the day
    low: Decimal
    # 24-hour trading volume (kept as Decimal since it's quantity)
    volume: Decimal
    # Timestamp (UTC)
    timestamp: datetime.datetime

    model_config = {"frozen": True, "populate_by_name": True}

    @field_validator("ask", "bid", "high", "last", "low", "volume", mode="before")
    @classmethod
    def convert_str_to_decimal(cls, v: Any) -> Decimal:
        """Convert string to Decimal"""
        if isinstance(v, str):
            return Decimal(v)
        return v

from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import BaseModel, field_validator


class Ticker(BaseModel):
    """:term:`native domain model` representing ticker

    Models JSON received from :term:`API endpoint` in the following format:

    .. code-block:: json

        {
            "success": 1,
            "data": {
                "sell": "15350001",
                "buy": "15350000",
                "open": "15572550",
                "high": "15836477",
                "low": "15271389",
                "last": "15350001",
                "vol": "273.5234",
                "timestamp": 1748558090326
            }
        }

    .. seealso::

        `Official doc <https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-api.md#ticker>`__
    """

    # Price fields
    sell: Decimal  # Best ask price
    buy: Decimal  # Best bid price
    open: Decimal  # Opening price
    high: Decimal  # High price
    low: Decimal  # Low price
    last: Decimal  # Last traded price

    # Quantity fields
    vol: Decimal  # Volume in last 24 hours
    timestamp: datetime.datetime

    model_config = {"frozen": True}

    @field_validator("sell", "buy", "open", "high", "low", "last", "vol", mode="before")
    @classmethod
    def convert_str_to_decimal(cls, v: Any) -> Decimal:
        """Convert string to Decimal"""
        if isinstance(v, str):
            return Decimal(v)
        return v

    @field_validator("timestamp", mode="before")
    @classmethod
    def convert_timestamp_to_datetime(cls, v: Any) -> datetime.datetime:
        """Convert millisecond timestamp to datetime"""
        if isinstance(v, (int, float, Decimal)):
            return datetime.datetime.fromtimestamp(float(v) / 1000, tz=datetime.UTC)
        return v

    def with_timezone(self, zoneinfo: ZoneInfo) -> Ticker:
        """Return Ticker with timestamp converted to specified timezone."""
        return self.model_copy(
            update={"timestamp": self.timestamp.astimezone(zoneinfo)},
        )

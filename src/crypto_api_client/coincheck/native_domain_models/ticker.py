from __future__ import annotations

import datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator


class Ticker(BaseModel):
    """:term:`native domain model` representing Coincheck ticker.

    Models JSON received from :term:`API endpoint` in the following format:

    .. code-block:: json

        {
            "last": 15350000,
            "bid": 15340000,
            "ask": 15350001,
            "high": 15836477,
            "low": 15271389,
            "volume": "273.5234",
            "timestamp": 1748558090
        }

    .. seealso::

        `Ticker <https://coincheck.com/documents/exchange/api#ticker>`__
    """

    last: Decimal
    bid: Decimal
    ask: Decimal
    high: Decimal  # 24-hour highest trading price
    low: Decimal  # 24-hour lowest trading price
    volume: Decimal  # 24-hour trading volume
    timestamp: datetime.datetime  # Current time

    model_config = {"frozen": True, "populate_by_name": True}

    @field_validator("timestamp", mode="before")
    @classmethod
    def convert_unix_seconds_to_datetime(
        cls, v: int | Decimal | datetime.datetime
    ) -> datetime.datetime:
        """Convert Unix seconds to UTC aware datetime

        Coincheck API returns Unix timestamp in seconds,
        so convert it to UTC aware datetime.

        .. warning::

            Coincheck returns Unix timestamp in **seconds**.
            Note that other exchanges (bitbank, BINANCE, etc.) use milliseconds.

        :param v: Unix timestamp (seconds), Decimal, or datetime object
        :return: UTC aware datetime
        """
        if isinstance(v, datetime.datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=datetime.UTC)
            return v

        # Get Unix seconds from Decimal or int
        if isinstance(v, Decimal):
            unix_seconds = int(v)
        else:
            unix_seconds = v

        # Convert Unix seconds to datetime
        return datetime.datetime.fromtimestamp(unix_seconds, tz=datetime.UTC)

from __future__ import annotations

import datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator


class Ticker(BaseModel):
    """:term:`native domain model` representing bitFlyer ticker.

    Models JSON received from :term:`API endpoint` like the following:

    .. code-block:: json

        {
            "product_code": "BTC_JPY",
            "state": "RUNNING",
            "timestamp": "2025-02-27T13:50:43.957",
            "tick_id": 243332856,
            "best_bid": 12860000.0,
            "best_ask": 12870464.0,
            "best_bid_size": 0.1385912,
            "best_ask_size": 0.0106,
            "total_bid_depth": 123.24202636,
            "total_ask_depth": 279.49970104,
            "market_bid_size": 0.0,
            "market_ask_size": 0.0,
            "ltp": 12872459.0,
            "volume": 5691.9186518,
            "volume_by_product": 2042.29972298
        }

    .. seealso::

        `Ticker <https://lightning.bitflyer.com/docs#ticker>`__
    """

    product_code: str
    state: str
    timestamp: datetime.datetime
    tick_id: int
    best_bid: Decimal
    best_ask: Decimal
    best_bid_size: Decimal
    best_ask_size: Decimal
    total_bid_depth: Decimal
    total_ask_depth: Decimal
    market_bid_size: Decimal
    market_ask_size: Decimal
    ltp: Decimal
    # Volume over past 24 hours
    volume: Decimal
    volume_by_product: Decimal

    model_config = {"frozen": True, "populate_by_name": True}

    @field_validator("timestamp", mode="after")
    @classmethod
    def convert_timestamp_to_utc_aware(cls, v: datetime.datetime) -> datetime.datetime:
        """Convert naive datetime to UTC aware datetime

        bitFlyer's API returns timestamps in ISO format without timezone information,
        so we interpret them as UTC and add timezone information.

        :param v: datetime object
        :return: UTC aware datetime
        """
        if v.tzinfo is None:
            # For naive datetime, interpret as UTC
            return v.replace(tzinfo=datetime.UTC)
        return v

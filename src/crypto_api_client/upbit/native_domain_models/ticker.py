from __future__ import annotations

import datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator

from .change_type import ChangeType


class Ticker(BaseModel):
    """Upbit ticker represented as :term:`native domain model`.

    Models JSON received from :term:`API endpoint`.
    """

    model_config = {"frozen": True, "populate_by_name": True}

    market: str

    trade_price: Decimal
    opening_price: Decimal
    high_price: Decimal
    low_price: Decimal
    prev_closing_price: Decimal

    change: ChangeType
    change_price: Decimal
    change_rate: Decimal
    signed_change_price: Decimal
    signed_change_rate: Decimal

    trade_volume: Decimal
    acc_trade_price: Decimal
    acc_trade_price_24h: Decimal
    acc_trade_volume: Decimal
    acc_trade_volume_24h: Decimal

    highest_52_week_price: Decimal
    highest_52_week_date: str
    lowest_52_week_price: Decimal
    lowest_52_week_date: str

    trade_date: str
    trade_time: str
    trade_date_kst: str
    trade_time_kst: str
    trade_timestamp: datetime.datetime
    timestamp: datetime.datetime

    @field_validator("trade_timestamp", "timestamp", mode="before")
    @classmethod
    def convert_timestamp_to_utc_aware(cls, v: int | Decimal) -> datetime.datetime:
        """Convert millisecond-precision timestamp to UTC-aware datetime.

        .. code-block:: python

            # 1543410527202 (ms) -> 2018-11-28 13:08:47.202 UTC
            Ticker.convert_timestamp_to_utc_aware(1543410527202)
            # datetime.datetime(2018, 11, 28, 13, 8, 47, 202000, tzinfo=datetime.timezone.utc)
        """
        # Convert Decimal to int if necessary
        timestamp_ms = int(v) if isinstance(v, Decimal) else v
        return datetime.datetime.fromtimestamp(timestamp_ms / 1000, tz=datetime.UTC)

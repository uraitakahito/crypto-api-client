from __future__ import annotations

import datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator


class Ticker(BaseModel):
    """BINANCE 24-hour ticker :term:`native domain model`.

    Models JSON received from :term:`API endpoint` in the following format:

    .. code-block:: json

        {
            "symbol": "BTCUSDT",
            "priceChange": "-154.13000000",
            "priceChangePercent": "-0.740",
            "weightedAvgPrice": "20677.46305250",
            "prevClosePrice": "20825.27000000",
            "lastPrice": "20671.14000000",
            "lastQty": "0.00030000",
            "bidPrice": "20671.13000000",
            "bidQty": "0.05000000",
            "askPrice": "20671.14000000",
            "askQty": "0.94620000",
            "openPrice": "20825.27000000",
            "highPrice": "20972.46000000",
            "lowPrice": "20327.92000000",
            "volume": "72.65112300",
            "quoteVolume": "1502240.91155513",
            "openTime": 1655432400000,
            "closeTime": 1655446835460,
            "firstId": 11147809,
            "lastId": 11149775,
            "count": 1967
        }
    """

    symbol: str
    priceChange: Decimal
    priceChangePercent: Decimal
    weightedAvgPrice: Decimal
    prevClosePrice: Decimal
    lastPrice: Decimal
    lastQty: Decimal
    bidPrice: Decimal
    bidQty: Decimal
    askPrice: Decimal
    askQty: Decimal
    openPrice: Decimal
    highPrice: Decimal
    lowPrice: Decimal
    volume: Decimal
    quoteVolume: Decimal
    openTime: datetime.datetime
    closeTime: datetime.datetime
    firstId: int
    lastId: int
    count: int

    model_config = {
        "frozen": True,
        "populate_by_name": True,
    }

    @field_validator("openTime", "closeTime", mode="before")
    @classmethod
    def validate_timestamp(cls, v: int | str | float | Decimal) -> datetime.datetime:
        """Convert timestamp (milliseconds) to datetime"""
        if isinstance(v, str):
            v = int(v)
        if isinstance(v, Decimal):
            v = float(v)
        # At this point v should be int | float
        return datetime.datetime.fromtimestamp(float(v) / 1000, tz=datetime.UTC)

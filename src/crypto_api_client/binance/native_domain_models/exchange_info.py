from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, field_validator

from .exchange_symbol import ExchangeSymbol
from .rate_limit import RateLimit


class ExchangeInfo(BaseModel):
    """Exchange information

    :term:`native domain model` representing the entire response of BINANCE `/api/v3/exchangeInfo` endpoint.

    .. note::
        exchangeFilters is often returned as an empty array currently,
        so it is defined as a list of dict type for flexibility.

    .. seealso::
        `Exchange Information <https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#exchange-information>`_

    .. code-block:: json

        {
          "timezone": "UTC",
          "serverTime": 1565246363776,
          "rateLimits": [...],
          "exchangeFilters": [],
          "symbols": [...]
        }
    """

    timezone: str
    serverTime: datetime.datetime
    rateLimits: list[RateLimit]
    exchangeFilters: list[dict[str, Any]]
    symbols: list[ExchangeSymbol]

    model_config = {
        "frozen": True,
        "populate_by_name": True,
    }

    @field_validator("serverTime", mode="before")
    @classmethod
    def validate_server_time(cls, v: int | str | float | Decimal) -> datetime.datetime:
        """Convert server timestamp (milliseconds) to datetime"""
        if isinstance(v, str):
            v = int(v)
        if isinstance(v, Decimal):
            v = float(v)
        return datetime.datetime.fromtimestamp(float(v) / 1000, tz=datetime.UTC)

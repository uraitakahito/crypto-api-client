from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, field_validator

from .side import Side


class PublicExecution(BaseModel):
    """:term:`native domain model` representing execution information retrieved via bitFlyer's Public API.

    Receives JSON from API in the following format:

    .. code-block:: json

        {
            "buy_child_order_acceptance_id": "JRF20250309-184614-001",
            "exec_date": "2025-03-09T18:46:14.073",
            "id": 123456789,
            "price": 12328565.0,
            "sell_child_order_acceptance_id": "JRF20250309-184614-002",
            "side": "BUY",
            "size": 0.01
        }

    .. note::
        For itayose executions, the ``side`` field is not included in the API response.
        Itayose is a special execution method performed at market opening or trading resumption,
        where sell orders and buy orders are matched together at a single price,
        so there is no individual buy/sell direction. In this case, ``side`` is ``None``.
    """

    buy_child_order_acceptance_id: str
    exec_date: datetime.datetime
    id: int
    price: Decimal
    sell_child_order_acceptance_id: str
    side: Side | None = None  # None for itayose executions
    size: Decimal

    model_config = {"frozen": True}

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v: Any) -> int:
        """Convert id to integer"""
        if isinstance(v, int):
            return v
        if isinstance(v, Decimal):
            return int(v)
        if isinstance(v, str):
            return int(v)
        # Error for other types
        msg = f"id must be an integer, Decimal, or string. Actual type: {type(v).__name__}"
        raise ValueError(msg)

    @field_validator("side", mode="before")
    @classmethod
    def validate_side(cls, v: Any) -> str | None:
        """Validate side field - convert empty string to None

        bitFlyer API returns an empty string for the side field in itayose executions.
        Since sell and buy orders are matched together at a single price, no individual buy/sell direction exists.

        :param v: Value of side field received from API
        :return: "BUY", "SELL", or None (for itayose executions)
        """
        if v == "":
            return None
        return v

    def with_timezone(self, zoneinfo: datetime.tzinfo) -> PublicExecution:
        """Return PublicExecution instance converted to specified timezone

        :param zoneinfo: Timezone information
        """
        return self.model_copy(
            update={"exec_date": self.exec_date.astimezone(zoneinfo)},
        )

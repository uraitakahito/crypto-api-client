"""Private execution history model retrieved via Private API"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import BaseModel, field_validator

from .side import Side


class PrivateExecution(BaseModel):
    """:term:`native domain model` representing private execution history retrieved via Private API.

    :param id: Execution ID
    :param side: Buy/Sell side (BUY/SELL). None for itayose executions
    :param price: Execution price
    :param size: Execution quantity
    :param exec_date: Execution date/time (UTC)
    :param commission: Trading commission
    :param child_order_id: Order ID
    :param child_order_acceptance_id: Order acceptance ID

    .. note::
        For itayose executions, the ``side`` field is not included in the API response.
        Itayose is a special execution method performed at market opening or trading resumption,
        where sell orders and buy orders are matched together at a single price,
        so there is no individual buy/sell direction. In this case, ``side`` is ``None``.
    """

    id: int
    side: Side | None = None  # None for itayose executions
    price: Decimal
    size: Decimal
    exec_date: datetime
    commission: Decimal
    child_order_id: str
    child_order_acceptance_id: str

    model_config = {"frozen": True}

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

    @field_validator("exec_date", mode="before")
    @classmethod
    def parse_exec_date(cls, v: str | datetime) -> datetime:
        """Convert ISO 8601 format string to datetime (treated as UTC)"""
        if isinstance(v, datetime):
            return v
        # bitFlyer API returns UTC, so explicitly interpret as UTC
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return dt.replace(tzinfo=ZoneInfo("UTC"))

    def with_timezone(self, tz: ZoneInfo) -> PrivateExecution:
        """Create a new instance with specified timezone"""
        return self.model_copy(update={"exec_date": self.exec_date.astimezone(tz)})

    def __str__(self) -> str:
        """String representation"""
        side_str = self.side.value if self.side else ""
        return (
            f"ID: {self.id:10} | "
            f"{side_str:7} | "
            f"Price: {self.price:12.2f} | "
            f"Size: {self.size:10.8f} | "
            f"Commission: {self.commission:10.8f} | "
            f"Date: {self.exec_date.isoformat()} | "
            f"OrderID: {self.child_order_id}"
        )

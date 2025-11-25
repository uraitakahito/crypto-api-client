"""Trading commission model."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class TradingCommission(BaseModel):
    """:term:`native domain model` representing bitFlyer trading commission information.

    :param commission_rate: Trading commission rate (e.g., 0.001 = 0.1%)
    :type commission_rate: Decimal
    """

    commission_rate: Decimal = Field(
        ..., description="Trading commission rate", alias="commission_rate"
    )

    model_config = {"frozen": True}

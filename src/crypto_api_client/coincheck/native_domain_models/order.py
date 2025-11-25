from __future__ import annotations

import datetime
from decimal import Decimal

from pydantic import BaseModel

from .order_type import OrderType


class Order(BaseModel):
    """:term:`native domain model` representing Coincheck own unsettled order information

    .. seealso::
        `Coincheck Unsettled order list <https://coincheck.com/ja/documents/exchange/api#order-opens>`__
    """

    id: Decimal
    order_type: OrderType
    rate: Decimal | None
    pair: str
    pending_amount: Decimal
    # Unsettled amount for market buy orders (None if not market buy order)
    pending_market_buy_amount: Decimal | None
    # Stop loss rate
    stop_loss_rate: Decimal | None
    created_at: datetime.datetime

    model_config = {"frozen": True}

    def with_timezone(self, zoneinfo: datetime.tzinfo) -> Order:
        return self.model_copy(
            update={
                "created_at": self.created_at.astimezone(zoneinfo),
            }
        )

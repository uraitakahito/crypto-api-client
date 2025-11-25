from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from .order_status import OrderStatus
from .order_type import OrderType
from .side import Side


class Order(BaseModel):
    """:term:`native domain model` representing bitbank order information."""

    order_id: int
    pair: str
    side: Side
    type: OrderType
    status: OrderStatus
    price: Decimal | None = None
    amount: Decimal | None = None  # Can be None for take_profit/stop_loss
    executed_amount: Decimal
    average_price: Decimal | None = None
    ordered_at: datetime
    executed_at: datetime | None = None
    canceled_at: datetime | None = None
    trigger_price: Decimal | None = None
    post_only: bool | None = None

    model_config = {"frozen": True}

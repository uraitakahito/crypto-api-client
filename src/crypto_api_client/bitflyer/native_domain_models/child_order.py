from __future__ import annotations

import datetime
from decimal import Decimal

from pydantic import BaseModel

from .child_order_state import ChildOrderState
from .child_order_type import ChildOrderType
from .side import Side
from .time_in_force import TimeInForce


class ChildOrder(BaseModel):
    """:term:`native domain model` representing bitFlyer order information.

    Receives JSON from API in the following format:

    .. code-block:: json

        {
            "id": 2981485137,
            "child_order_id": "JOR20250310-214142-959206",
            "product_code": "BTC_JPY",
            "side": "BUY",
            "child_order_type": "LIMIT",
            "price": 12901973.0,
            "average_price": 11773540.0,
            "size": 0.001,
            "child_order_state": "COMPLETED",
            "expire_date": "2025-04-09T21:41:42",
            "child_order_date": "2025-03-10T21:41:42",
            "child_order_acceptance_id": "JRF20250310-214142-062520",
            "outstanding_size": 0.0,
            "cancel_size": 0.0,
            "executed_size": 0.001,
            "total_commission": 0.0000001,
            "time_in_force": "GTC"
        }
    """

    id: str | Decimal
    child_order_id: str
    product_code: str
    side: Side
    child_order_type: ChildOrderType
    # Price becomes 0 for partially executed orders?
    price: Decimal
    # Average price becomes 0 if not yet executed
    average_price: Decimal
    size: Decimal
    child_order_state: ChildOrderState
    expire_date: datetime.datetime
    child_order_date: datetime.datetime
    child_order_acceptance_id: str
    outstanding_size: Decimal
    cancel_size: Decimal
    executed_size: Decimal
    total_commission: Decimal
    time_in_force: TimeInForce

    model_config = {"frozen": True}

    def with_timezone(self, zoneinfo: datetime.tzinfo) -> ChildOrder:
        """Return ChildOrder instance converted to specified timezone"""
        return self.model_copy(
            update={
                "expire_date": self.expire_date.astimezone(zoneinfo),
                "child_order_date": self.child_order_date.astimezone(zoneinfo),
            },
        )

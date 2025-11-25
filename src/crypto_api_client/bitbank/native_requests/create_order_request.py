"""New order request"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from ..native_domain_models import OrderType, Side


class CreateOrderRequest(BaseModel):
    """:term:`native request` implementation for new order

    Defines parameters required for submitting new order to bitbank API.
    """

    pair: str  # Currency pair (e.g. "btc_jpy")
    side: Side
    type: OrderType
    amount: Decimal | None = None  # Not required for take_profit/stop_loss
    price: Decimal | None = None
    trigger_price: Decimal | None = None
    post_only: bool | None = None
    position_side: str | None = None  # For margin trading (long/short)

    model_config = {"frozen": True}

    def to_query_params(self) -> dict[str, str | bool]:
        """Convert to parameter dictionary for API request

        :return: Dictionary of API parameters
        """
        params: dict[str, str | bool] = {
            "pair": self.pair,
            "side": self.side.value,
            "type": self.type.value,
        }
        if self.amount is not None:
            params["amount"] = str(self.amount)
        if self.price is not None:
            params["price"] = str(self.price)
        if self.trigger_price is not None:
            params["trigger_price"] = str(self.trigger_price)
        # post_only is sent as boolean, not included if False
        if self.post_only is True:
            params["post_only"] = True
        if self.position_side is not None:
            params["position_side"] = self.position_side
        return params

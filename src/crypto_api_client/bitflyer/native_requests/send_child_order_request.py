from __future__ import annotations

from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
    model_validator,  # pyright: ignore[reportUnknownVariableType]
)
from pydantic.types import StrictInt

from ..native_domain_models.child_order_type import ChildOrderType
from ..native_domain_models.side import Side
from ..native_domain_models.time_in_force import TimeInForce


class SendChildOrderRequest(BaseModel):
    """bitFlyer-specific :term:`native request` implementation for submitting orders.

    Price requirement/prohibition rules based on order type:
    - LIMIT order: price required
    - MARKET order: price prohibited

    :param product_code: Product code for the trading pair (e.g. "BTC_JPY")
    :type product_code: str
    :param child_order_type: Order type
    :type child_order_type: ChildOrderType
    :param side: Buy/Sell direction
    :type side: Side
    :param size: Order size (e.g. BTC quantity)
    :type size: Decimal
    :param price: Limit order price. None for MARKET orders.
    :type price: Decimal | None
    :param minute_to_expire: Order expiration time (in minutes, 1-43200 minutes)
    :type minute_to_expire: StrictInt | None
    :param time_in_force: Order execution condition
    :type time_in_force: TimeInForce | None
    """

    product_code: str
    child_order_type: ChildOrderType
    side: Side
    size: Decimal
    price: Decimal | None = None
    minute_to_expire: StrictInt | None = Field(
        default=None,
        description="Order expiration (in minutes, 1 minute - 43200 minutes = 30 days)",
        ge=1,
        le=43200,
    )
    time_in_force: TimeInForce | None = None

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def validate_order_consistency(self) -> SendChildOrderRequest:
        """Validate consistency between order type and price"""
        if self.child_order_type == ChildOrderType.LIMIT and self.price is None:
            raise ValueError("price is required for LIMIT orders")
        if self.child_order_type == ChildOrderType.MARKET and self.price is not None:
            raise ValueError(f"price cannot be specified for MARKET orders: {self.price}")

        return self

    def to_query_params(self) -> dict[str, str]:
        """Return all-string dictionary for API request."""
        # Required parameters
        result = {
            "product_code": self.product_code,
            "child_order_type": self.child_order_type.value,
            "side": self.side.value,
            "size": str(self.size),
        }

        # Optional parameters
        optional_params = {
            "price": str(self.price) if self.price is not None else None,
            "minute_to_expire": str(self.minute_to_expire)
            if self.minute_to_expire is not None
            else None,
            "time_in_force": self.time_in_force.value if self.time_in_force else None,
        }
        result.update({k: v for k, v in optional_params.items() if v is not None})

        return result

from __future__ import annotations

from pydantic import BaseModel

from crypto_api_client.bitflyer.native_domain_models.child_order_state import (
    ChildOrderState,
)


class ChildOrdersRequest(BaseModel):
    """:term:`native request` implementation for retrieving order list.

    When either before or after is specified, ACTIVE orders will not be included in the results.

    :param product_code: Product code for the trading pair (e.g. "BTC_JPY"). Defaults to BTC_JPY if omitted.
    :type product_code: str | None
    :param count: Number of records to retrieve. Defaults to 100 if omitted.
    :type count: int | None
    :param before: Specify to get orders before this ID. If omitted, retrieves from the latest order.
    :type before: str | None
    :param after: Specify to get orders after this ID. If omitted, retrieves from the oldest order.
    :type after: str | None
    :param child_order_state: Order state. If omitted, concatenation of ACTIVE and non-ACTIVE orders.
    :type child_order_state: ChildOrderState | None
    :param child_order_id: Specify to get a specific order ID. If omitted, retrieves all orders.
    :type child_order_id: str | None
    :param child_order_acceptance_id: Specify to get a specific acceptance ID. If omitted, retrieves all orders.
    :type child_order_acceptance_id: str | None
    :param parent_order_id: Specify to get by parent order ID. If omitted, retrieves all orders.
    :type parent_order_id: str | None
    """

    product_code: str | None = None
    count: int | None = None
    before: str | None = None
    after: str | None = None
    child_order_state: ChildOrderState | None = None
    child_order_id: str | None = None
    child_order_acceptance_id: str | None = None
    parent_order_id: str | None = None

    model_config = {"frozen": True}

    def to_query_params(self) -> dict[str, str]:
        """Return all-string dictionary for API request."""
        all_params = {
            "product_code": self.product_code,
            "count": str(self.count) if self.count is not None else None,
            "before": self.before,
            "after": self.after,
            "child_order_state": self.child_order_state.value
            if self.child_order_state
            else None,
            "child_order_id": self.child_order_id,
            "child_order_acceptance_id": self.child_order_acceptance_id,
            "parent_order_id": self.parent_order_id,
        }
        return {k: v for k, v in all_params.items() if v is not None}

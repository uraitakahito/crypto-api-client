from __future__ import annotations

from pydantic import BaseModel


class PrivateExecutionsRequest(BaseModel):
    """:term:`native request` implementation for retrieving own execution history via Private API.

    :param product_code: Product code for the trading pair (e.g. "BTC_JPY")
    :type product_code: str
    :param count: Number of records to retrieve (max 500)
    :type count: int | None
    :param before: Specify to get executions before this ID
    :type before: int | None
    :param after: Specify to get executions after this ID
    :type after: int | None
    :param child_order_id: Filter by order ID
    :type child_order_id: str | None
    :param child_order_acceptance_id: Filter by order acceptance ID
    :type child_order_acceptance_id: str | None
    """

    product_code: str
    count: int | None = None
    before: int | None = None
    after: int | None = None
    child_order_id: str | None = None
    child_order_acceptance_id: str | None = None

    model_config = {"frozen": True}

    def to_query_params(self) -> dict[str, str]:
        """Return all-string dictionary for API request."""
        all_params = {
            "product_code": self.product_code,
            "count": str(self.count) if self.count is not None else None,
            "before": str(self.before) if self.before is not None else None,
            "after": str(self.after) if self.after is not None else None,
            "child_order_id": self.child_order_id,
            "child_order_acceptance_id": self.child_order_acceptance_id,
        }
        return {k: v for k, v in all_params.items() if v is not None}

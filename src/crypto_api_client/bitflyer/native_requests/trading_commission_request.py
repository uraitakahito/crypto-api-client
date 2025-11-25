"""Trading commission retrieval request."""

from __future__ import annotations

from pydantic import BaseModel


class TradingCommissionRequest(BaseModel):
    """:term:`native request` implementation for retrieving trading commission.

    :param product_code: Product code for the trading pair (e.g. "BTC_JPY").
    :type product_code: str
    """

    product_code: str

    model_config = {"frozen": True}

    def to_query_params(self) -> dict[str, str]:
        """Return query parameters for API request."""
        return {"product_code": self.product_code}

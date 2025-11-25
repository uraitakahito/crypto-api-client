from __future__ import annotations

from pydantic import BaseModel


class PublicExecutionsRequest(BaseModel):
    """:term:`native request` implementation for retrieving execution history via Public API.

    :param product_code: Product code for the trading pair (e.g. "BTC_JPY"). Defaults to BTC_JPY if omitted.
    :type product_code: str | None
    :param count: Number of records to retrieve
    :type count: int | None
    :param before: Specify to get executions before this ID. Execution history retrievable via before parameter is limited to the past 31 days
    :type before: str | None
    :param after: Specify to get executions after this ID
    :type after: str | None
    """

    product_code: str | None = None
    count: int | None = None
    before: str | None = None
    after: str | None = None

    model_config = {"frozen": True}

    def to_query_params(self) -> dict[str, str]:
        """Return all-string dictionary for API request."""
        all_params = {
            "product_code": self.product_code,
            "count": str(self.count) if self.count is not None else None,
            "before": self.before,
            "after": self.after,
        }
        return {k: v for k, v in all_params.items() if v is not None}

from __future__ import annotations

from pydantic import BaseModel


class TickerRequest(BaseModel):
    """:term:`native request` implementation for retrieving ticker.

    :param product_code: Target product code (e.g. "BTC_JPY"). Defaults to BTC_JPY if omitted.
    :type product_code: str | None
    """

    product_code: str | None = None

    model_config = {"frozen": True}

    def to_query_params(self) -> dict[str, str]:
        """Return string dictionary for :term:`endpoint request`."""
        params: dict[str, str] = {}
        if self.product_code is not None:
            params["product_code"] = self.product_code
        return params

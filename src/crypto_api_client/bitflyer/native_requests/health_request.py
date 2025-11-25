from __future__ import annotations

from pydantic import BaseModel


class HealthRequest(BaseModel):
    """:term:`native request` implementation for retrieving exchange status

    .. note::

        product_code is optional and defaults to BTC_JPY when omitted.

    :param product_code: Product code for the trading pair (e.g. "BTC_JPY"). Optional with default None.
    :type product_code: str | None
    """

    product_code: str | None = None

    model_config = {"frozen": True}

    def to_query_params(self) -> dict[str, str]:
        """Generate dictionary of query parameters"""
        params: dict[str, str] = {}

        if self.product_code is not None:
            params["product_code"] = self.product_code

        return params

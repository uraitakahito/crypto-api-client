"""Request model for retrieving order book"""

from __future__ import annotations

from pydantic import BaseModel


class BoardRequest(BaseModel):
    """:term:`native request` implementation for retrieving order book

    :param product_code: Target product code (e.g. "BTC_JPY"). Defaults to BTC_JPY if omitted.
    :type product_code: str | None

    .. seealso::
        `Order Book API <https://lightning.bitflyer.com/docs?lang=en#order-book>`__
    """

    product_code: str | None = None

    model_config = {"frozen": True}

    def to_query_params(self) -> dict[str, str]:
        """Return string dictionary for :term:`endpoint request`.

        :return: Dictionary of query parameters
        :rtype: dict[str, str]
        """
        params: dict[str, str] = {}
        if self.product_code is not None:
            params["product_code"] = self.product_code
        return params

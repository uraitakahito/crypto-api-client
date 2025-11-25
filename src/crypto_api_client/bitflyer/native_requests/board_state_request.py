"""Request for retrieving board state"""

from __future__ import annotations

from pydantic import BaseModel


class BoardStateRequest(BaseModel):
    """:term:`native request` implementation for retrieving board state.

    :param product_code: :term:`product code` for the trading pair (e.g. "BTC_JPY"). Required.
    :type product_code: str

    .. seealso::

        Orderbook Status: https://lightning.bitflyer.com/docs?lang=en#orderbook-status
    """

    product_code: str

    model_config = {"frozen": True}

    def to_query_params(self) -> dict[str, str]:
        """Return string dictionary for :term:`endpoint request`."""
        return {"product_code": self.product_code}

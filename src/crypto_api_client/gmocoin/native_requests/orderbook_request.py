from __future__ import annotations

from pydantic import BaseModel


class OrderBookRequest(BaseModel):
    """OrderBook retrieval request

    Request parameters for GMO Coin orderBook API.

    .. seealso::
        `OrderBooks API <https://api.coin.z.com/docs/#orderbooks>`__

    :param symbol: Currency pair (required, e.g., "BTC_JPY", "ETH_JPY")
    :type symbol: str
    """

    symbol: str

    model_config = {"frozen": True}

    def to_query_params(self) -> dict[str, str]:
        """Convert to query parameters

        :return: Dictionary of query parameters
        :rtype: dict[str, str]
        """
        return {"symbol": self.symbol}

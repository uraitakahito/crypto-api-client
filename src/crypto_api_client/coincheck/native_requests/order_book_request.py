"""Order book request"""

from __future__ import annotations

from pydantic import BaseModel


class OrderBookRequest(BaseModel):
    """Coincheck order book retrieval request

    :param pair: Currency pair (e.g., btc_jpy, eth_jpy, etc_jpy)
    :type pair: str
    """

    pair: str

    model_config = {"frozen": True}

    def to_query_params(self) -> dict[str, str]:
        """Convert to query parameters

        :return: Dictionary of query parameters
        :rtype: dict[str, str]
        """
        return {"pair": self.pair}

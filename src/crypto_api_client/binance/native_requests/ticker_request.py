from __future__ import annotations

from pydantic import BaseModel


class TickerRequest(BaseModel):
    """:term:`native request` implementation for getting 24-hour ticker.

    Corresponds to BINANCE `/api/v3/ticker/24hr` endpoint.

    :param symbol: Target symbol (e.g., "BTCUSDT")
    :type symbol: str
    """

    symbol: str

    model_config = {"frozen": True}

    def to_query_params(self) -> dict[str, str]:
        """Return dictionary of str type for :term:`endpoint request`."""
        return {"symbol": self.symbol}

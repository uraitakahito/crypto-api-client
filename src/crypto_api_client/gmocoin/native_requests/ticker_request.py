from __future__ import annotations

from pydantic import BaseModel


class TickerRequest(BaseModel):
    """Implementation of :term:`native request` for retrieving ticker.

    :param symbol: Target symbol (e.g., "BTC_JPY"). Retrieves data for all symbols if omitted.
    :type symbol: str | None
    """

    symbol: str | None = None

    model_config = {"frozen": True}

    def to_query_params(self) -> dict[str, str]:
        """Return str-type dictionary for :term:`endpoint request`."""
        params: dict[str, str] = {}
        if self.symbol is not None:
            params["symbol"] = self.symbol
        return params

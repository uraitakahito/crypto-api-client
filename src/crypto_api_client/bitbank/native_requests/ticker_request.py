from __future__ import annotations

from pydantic import BaseModel


class TickerRequest(BaseModel):
    """:term:`native request` implementation for fetching ticker.

    :param pair: Currency pair (e.g. "btc_jpy")
    :type pair: str
    """

    pair: str

    model_config = {"frozen": True}

    def to_path_params(self) -> str:
        """Return string for path parameters"""
        return self.pair

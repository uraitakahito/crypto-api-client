"""GMO Coin native requests."""

from __future__ import annotations

from .orderbook_request import OrderBookRequest
from .ticker_request import TickerRequest

__all__ = ["TickerRequest", "OrderBookRequest"]

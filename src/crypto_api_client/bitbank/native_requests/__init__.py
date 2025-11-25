"""bitbank API request types."""

from __future__ import annotations

from .create_order_request import CreateOrderRequest
from .depth_request import DepthRequest
from .spot_status_request import SpotStatusRequest
from .ticker_request import TickerRequest

__all__ = [
    "CreateOrderRequest",
    "DepthRequest",
    "SpotStatusRequest",
    "TickerRequest",
]

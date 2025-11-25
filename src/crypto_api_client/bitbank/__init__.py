"""bitbank exchange API integration module"""

from __future__ import annotations

__all__ = [
    # API Client
    "ExchangeApiClient",
    # Models
    "Depth",
    "DepthEntry",
    "Order",
    "OrderStatus",
    "OrderType",
    "PairStatus",
    "Side",
    "SpotStatus",
    "SpotStatusType",
    # Requests
    "CreateOrderRequest",
    "DepthRequest",
    "SpotStatusRequest",
    "TickerRequest",
    # Error handler
    "BitbankResponseValidator",
    # Utility
    "build_message",
]
from ._signature_builder import build_message
from .bitbank_response_validator import BitbankResponseValidator
from .exchange_api_client import ExchangeApiClient
from .native_domain_models import (
    Depth,
    DepthEntry,
    Order,
    OrderStatus,
    OrderType,
    PairStatus,
    Side,
    SpotStatus,
    SpotStatusType,
)
from .native_requests import (
    CreateOrderRequest,
    DepthRequest,
    SpotStatusRequest,
    TickerRequest,
)

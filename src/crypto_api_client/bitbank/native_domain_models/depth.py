"""Domain model for order book (Depth)"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator


class DepthEntry(BaseModel):
    """Individual entry in order book (buy order or sell order)

    :param price: Order price
    :type price: Decimal
    :param size: Order quantity
    :type size: Decimal
    """

    price: Decimal
    size: Decimal

    model_config = {"frozen": True}


class Depth(BaseModel):
    """:term:`native domain model` representing entire order book

    Represents the data structure returned by order book :term:`API endpoint`.
    Contains order lists for bids and asks,
    market order information, and out-of-range order information
    during circuit breaker mode.

    Example JSON returned by :term:`API endpoint`:

    .. code-block:: json

        {
            "asks": [
                ["15350001", "0.1"],
                ["15350002", "0.5"]
            ],
            "bids": [
                ["15350000", "0.2"],
                ["15349999", "0.3"]
            ],
            "asks_over": "10.5",
            "bids_under": "20.3",
            "asks_under": "5.2",
            "bids_over": "8.7",
            "ask_market": "1.5",
            "bid_market": "2.3",
            "timestamp": 1748558090326,
            "sequenceId": "1234567890"
        }

    .. seealso::

        `Depth API <https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-api.md#depth>`__

    :param asks: List of sell orders (sorted by ascending price)
    :type asks: list[DepthEntry]
    :param bids: List of buy orders (sorted by descending price)
    :type bids: list[DepthEntry]
    :param asks_over: Out-of-range sell order quantity (upper side)
    :type asks_over: Decimal | None
    :param bids_under: Out-of-range buy order quantity (lower side)
    :type bids_under: Decimal | None
    :param asks_under: Out-of-range sell order quantity (lower side)
    :type asks_under: Decimal | None
    :param bids_over: Out-of-range buy order quantity (upper side)
    :type bids_over: Decimal | None
    :param ask_market: Total quantity of market sell orders
    :type ask_market: Decimal | None
    :param bid_market: Total quantity of market buy orders
    :type bid_market: Decimal | None
    :param timestamp: Timestamp (UTC)
    :type timestamp: datetime
    :param sequence_id: Sequence identifier (for ordering in WebSocket connections)
    :type sequence_id: str
    """

    asks: list[DepthEntry] = Field(default_factory=lambda: [])
    bids: list[DepthEntry] = Field(default_factory=lambda: [])

    @field_validator("asks", "bids", mode="before")
    @classmethod
    def parse_order_entries(cls, v: Any) -> list[DepthEntry]:
        """Convert array-format order data to DepthEntry objects

        Converts ["price", "quantity"] format data returned from API
        to DepthEntry objects.

        :raises ValueError: If v is not a list type
        """
        if not isinstance(v, list):
            raise ValueError(f"Expected list, got {type(v).__name__}")

        entries: list[DepthEntry] = []
        for item in v:  # pyright: ignore[reportUnknownVariableType]
            if isinstance(item, DepthEntry):
                # If already DepthEntry, add as-is
                entries.append(item)
            elif isinstance(item, dict):
                # If dict format, convert to DepthEntry
                entries.append(DepthEntry(**item))  # type: ignore[arg-type]
            elif isinstance(item, list) and len(item) >= 2:  # pyright: ignore[reportUnknownArgumentType]
                # Convert ["price", "quantity"] format to DepthEntry
                # Already confirmed that item is a list
                price_str: str = str(item[0])  # pyright: ignore[reportUnknownArgumentType]
                size_str: str = str(item[1])  # pyright: ignore[reportUnknownArgumentType]
                entries.append(
                    DepthEntry(price=Decimal(price_str), size=Decimal(size_str))
                )

        return entries

    asks_over: Decimal | None = Field(
        default=None, description="Out-of-range sell order quantity (upper side)"
    )
    bids_under: Decimal | None = Field(
        default=None, description="Out-of-range buy order quantity (lower side)"
    )
    asks_under: Decimal | None = Field(
        default=None, description="Out-of-range sell order quantity (lower side)"
    )
    bids_over: Decimal | None = Field(
        default=None, description="Out-of-range buy order quantity (upper side)"
    )
    ask_market: Decimal | None = Field(default=None, description="Total quantity of market sell orders")
    bid_market: Decimal | None = Field(default=None, description="Total quantity of market buy orders")
    timestamp: datetime
    sequenceId: str = Field(description="Sequence identifier")

    model_config = {"frozen": True, "populate_by_name": True}

    @property
    def spread(self) -> Decimal | None:
        """Calculate spread between bid and ask prices

        :return: Spread (ask price - bid price), None if order book is empty
        :rtype: Decimal | None
        """
        if self.asks and self.bids:
            return self.asks[0].price - self.bids[0].price
        return None

    @property
    def best_bid(self) -> DepthEntry | None:
        """Best bid price (highest buy order)

        :return: Best bid entry, None if bid side is empty
        :rtype: DepthEntry | None
        """
        return self.bids[0] if self.bids else None

    @property
    def best_ask(self) -> DepthEntry | None:
        """Best ask price (lowest sell order)

        :return: Best ask entry, None if ask side is empty
        :rtype: DepthEntry | None
        """
        return self.asks[0] if self.asks else None

    @property
    def mid_price(self) -> Decimal | None:
        """Calculate mid price (average of bid and ask prices)

        :return: Mid price, None if either best bid or best ask doesn't exist
        :rtype: Decimal | None
        """
        if self.best_bid and self.best_ask:
            return (self.best_bid.price + self.best_ask.price) / 2
        return None

    @property
    def has_circuit_breaker_data(self) -> bool:
        """Check if circuit breaker mode data is included

        :return: True if circuit breaker mode data exists
        :rtype: bool
        """
        return any(
            [
                self.asks_over is not None,
                self.bids_under is not None,
                self.asks_under is not None,
                self.bids_over is not None,
            ]
        )

from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator


class OrderBookEntry(BaseModel):
    price: Decimal
    size: Decimal

    model_config = {"frozen": True}


class OrderBook(BaseModel):
    """:term:`native domain model` representing entire order book

    Models JSON received from :term:`API endpoint` in the following format.

    .. code-block:: json

        {
            "status": 0,
            "data": {
                "asks": [
                    {"price": "15350001", "size": "0.1"},
                    {"price": "15350002", "size": "0.5"}
                ],
                "bids": [
                    {"price": "15350000", "size": "0.2"},
                    {"price": "15349999", "size": "0.3"}
                ],
                "symbol": "BTC"
            },
            "responsetime": "2019-03-19T02:15:06.026Z"
        }

    .. note::

        Due to GMO Coin specification, the response ``symbol`` field
        returns only the base currency code (e.g., "BTC", "ETH").
        Note that this differs from the currency pair specified in the request (e.g., "BTC_JPY").

    .. seealso::
        `OrderBooks API <https://api.coin.z.com/docs/#orderbooks>`__
    """

    asks: list[OrderBookEntry] = Field(default_factory=lambda: [])
    bids: list[OrderBookEntry] = Field(default_factory=lambda: [])
    symbol: str = Field(description="Base currency code (e.g., BTC, ETH)")

    @field_validator("asks", "bids", mode="before")
    @classmethod
    def parse_order_entries(cls, v: Any) -> list[OrderBookEntry]:
        """Convert dict-format order data to OrderBookEntry objects

        Converts data in {"price": "...", "size": "..."} format returned from API
        to OrderBookEntry objects.
        """
        if not isinstance(v, list):
            raise ValueError(f"Expected list, got {type(v).__name__}")

        entries: list[OrderBookEntry] = []
        for item in v:  # pyright: ignore[reportUnknownVariableType]
            if isinstance(item, OrderBookEntry):
                entries.append(item)
            elif isinstance(item, dict):
                # Convert {"price": "...", "size": "..."} format to OrderBookEntry
                entries.append(OrderBookEntry(**item))  # type: ignore[arg-type]

        return entries

    model_config = {"frozen": True, "populate_by_name": True}

    @property
    def best_ask(self) -> OrderBookEntry | None:
        return self.asks[0] if self.asks else None

    @property
    def best_bid(self) -> OrderBookEntry | None:
        return self.bids[0] if self.bids else None

    @property
    def mid_price(self) -> Decimal | None:
        if self.best_bid and self.best_ask:
            return (self.best_bid.price + self.best_ask.price) / 2
        return None

    @property
    def spread(self) -> Decimal | None:
        if self.asks and self.bids:
            return self.asks[0].price - self.bids[0].price
        return None

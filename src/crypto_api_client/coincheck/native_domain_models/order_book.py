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

    Models JSON received from :term:`API endpoint` in the following format:

    .. code-block:: json

        {
            "asks": [
                ["15350001", "0.1"],
                ["15350002", "0.5"]
            ],
            "bids": [
                ["15350000", "0.2"],
                ["15349999", "0.3"]
            ]
        }

    .. seealso::

        `Order Book <https://coincheck.com/documents/exchange/api#order-book>`__
    """

    asks: list[OrderBookEntry] = Field(default_factory=lambda: [])
    bids: list[OrderBookEntry] = Field(default_factory=lambda: [])

    @field_validator("asks", "bids", mode="before")
    @classmethod
    def parse_order_entries(cls, v: Any) -> list[OrderBookEntry]:
        """Convert array-format order data to OrderBookEntry objects"""
        if not isinstance(v, list):
            raise ValueError(f"Expected list, got {type(v).__name__}")

        entries: list[OrderBookEntry] = []
        for item in v:  # pyright: ignore[reportUnknownVariableType]
            if isinstance(item, OrderBookEntry):
                entries.append(item)
            elif isinstance(item, dict):
                entries.append(OrderBookEntry(**item))  # type: ignore[arg-type]
            elif isinstance(item, list) and len(item) >= 2:  # pyright: ignore[reportUnknownArgumentType]
                price_str: str = str(item[0])  # pyright: ignore[reportUnknownArgumentType]
                size_str: str = str(item[1])  # pyright: ignore[reportUnknownArgumentType]
                entries.append(
                    OrderBookEntry(price=Decimal(price_str), size=Decimal(size_str))
                )

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

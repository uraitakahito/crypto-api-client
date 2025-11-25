from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, field_validator


class DepthEntry(BaseModel):
    """Individual entry (price and quantity) of Depth :term:`native domain model`.

    BINANCE depth data is returned in array format:
    ["price", "quantity"]
    """

    price: Decimal
    quantity: Decimal

    model_config = {"frozen": True}

    @classmethod
    def from_array(cls, data: list[str]) -> DepthEntry:
        """Generate DepthEntry from array format data

        :param data: Array in ["price", "quantity"] format
        :type data: list[str]
        :return: DepthEntry instance
        :rtype: DepthEntry
        """
        if len(data) != 2:
            raise ValueError(f"Expected 2 elements, got {len(data)}")
        return cls(price=Decimal(data[0]), quantity=Decimal(data[1]))


class Depth(BaseModel):
    """BINANCE order book (depth) :term:`native domain model`.

    Models JSON received from :term:`API endpoint` in the following format:

    .. code-block:: json

        {
            "lastUpdateId": 1027024,
            "bids": [
                ["4.00000000", "431.00000000"]
            ],
            "asks": [
                ["4.00000200", "12.00000000"]
            ]
        }
    """

    lastUpdateId: int
    bids: list[DepthEntry]
    asks: list[DepthEntry]

    model_config = {"frozen": True}

    @field_validator("bids", "asks", mode="before")
    @classmethod
    def validate_entries(cls, v: list[list[str]]) -> list[DepthEntry]:
        """Convert array format data to list of DepthEntry

        :param v: Array in [["price", "quantity"], ...] format
        :type v: list[list[str]]
        :return: List of DepthEntry
        :rtype: list[DepthEntry]
        """
        return [DepthEntry.from_array(entry) for entry in v]

    @property
    def best_bid(self) -> DepthEntry | None:
        """Get best bid

        :return: Best bid (None if no bids)
        :rtype: DepthEntry | None
        """
        return self.bids[0] if self.bids else None

    @property
    def best_ask(self) -> DepthEntry | None:
        """Get best ask

        :return: Best ask (None if no asks)
        :rtype: DepthEntry | None
        """
        return self.asks[0] if self.asks else None

    @property
    def spread(self) -> Decimal | None:
        """Get spread (best ask - best bid)

        :return: Spread (None if bid/ask does not exist)
        :rtype: Decimal | None
        """
        if self.best_bid and self.best_ask:
            return self.best_ask.price - self.best_bid.price
        return None

    @property
    def mid_price(self) -> Decimal | None:
        """Get mid price ((best bid + best ask) / 2)

        :return: Mid price (None if bid/ask does not exist)
        :rtype: Decimal | None
        """
        if self.best_bid and self.best_ask:
            return (self.best_bid.price + self.best_ask.price) / 2
        return None

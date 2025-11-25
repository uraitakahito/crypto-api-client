"""Domain model for order book (Board)"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class BoardEntry(BaseModel):
    """Individual entry in order book (buy order or sell order)

    :param price: Order price
    :type price: Decimal
    :param size: Order quantity
    :type size: Decimal
    """

    price: Decimal
    size: Decimal

    model_config = {"frozen": True}


class Board(BaseModel):
    """:term:`native domain model` representing the entire order book

    Represents the data structure returned by bitFlyer's order book API.
    Includes order lists for buy side (bids) and sell side (asks),
    as well as mid price (mid_price).

    Models JSON received from :term:`API endpoint` like the following:

    .. code-block:: json

        {
            "mid_price": 33320,
            "bids": [
                {
                    "price": 30000,
                    "size": 0.1
                },
                {
                    "price": 29990,
                    "size": 0.5
                }
            ],
            "asks": [
                {
                    "price": 36640,
                    "size": 5
                },
                {
                    "price": 36700,
                    "size": 0.2
                }
            ]
        }

    .. note::

        During maintenance, best bid and best ask return the last values before maintenance,
        and consequently mid_price also returns the last value before maintenance.

    :param mid_price: Mid price (between bid and ask)
    :type mid_price: Decimal
    :param bids: List of buy orders (sorted by price descending)
    :type bids: list[BoardEntry]
    :param asks: List of sell orders (sorted by price ascending)
    :type asks: list[BoardEntry]

    .. seealso::
        `Order Book API <https://lightning.bitflyer.com/docs?lang=en#order-book>`__
    """

    mid_price: Decimal
    bids: list[BoardEntry] = Field(default_factory=lambda: [])
    asks: list[BoardEntry] = Field(default_factory=lambda: [])

    model_config = {"frozen": True}

    @property
    def spread(self) -> Decimal | None:
        """Calculate spread between bid and ask

        :return: Spread (ask price - bid price), None if board is empty
        :rtype: Decimal | None
        """
        if self.asks and self.bids:
            # BoardEntry's price remains as Decimal type
            return self.asks[0].price - self.bids[0].price
        return None

    @property
    def best_bid(self) -> BoardEntry | None:
        """Best bid price (highest buy order)

        :return: Best bid entry, None if buy side is empty
        :rtype: BoardEntry | None
        """
        return self.bids[0] if self.bids else None

    @property
    def best_ask(self) -> BoardEntry | None:
        """Best ask price (lowest sell order)

        :return: Best ask entry, None if sell side is empty
        :rtype: BoardEntry | None
        """
        return self.asks[0] if self.asks else None

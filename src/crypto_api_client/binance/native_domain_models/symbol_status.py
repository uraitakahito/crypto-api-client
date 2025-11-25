from __future__ import annotations

from enum import Enum


class SymbolStatus(Enum):
    """Trading pair status

    Defines various statuses that BINANCE trading pairs can have.

    .. seealso::
        `Exchange Information <https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#exchange-information>`_
    """

    TRADING = "TRADING"
    """Normal trading is available"""

    HALT = "HALT"
    """Trading is halted"""

    BREAK = "BREAK"
    """Trading is temporarily suspended"""

    AUCTION_MATCH = "AUCTION_MATCH"
    """Auction matching in progress"""

    PRE_TRADING = "PRE_TRADING"
    """Before trading starts"""

    POST_TRADING = "POST_TRADING"
    """After trading ends"""

    END_OF_DAY = "END_OF_DAY"
    """Trading day ended"""

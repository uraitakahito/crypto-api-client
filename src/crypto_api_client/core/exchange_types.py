
from __future__ import annotations

from enum import Enum


class Exchange(Enum):
    BITFLYER = "bitflyer"
    BITBANK = "bitbank"
    BINANCE = "binance"
    COINCHECK = "coincheck"
    GMOCOIN = "gmocoin"
    UPBIT = "upbit"

    @property
    def display_name(self) -> str:
        """Get the official name of the exchange"""
        names = {
            "bitflyer": "bitFlyer",
            "bitbank": "bitbank",
            "binance": "Binance",
            "coincheck": "Coincheck",
            "gmocoin": "GMO Coin",
            "upbit": "Upbit",
        }
        return names[self.value]

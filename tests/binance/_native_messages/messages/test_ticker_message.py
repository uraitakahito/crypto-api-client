"""Tests for BINANCE TickerMessage."""

import json
from decimal import Decimal

from crypto_api_client.binance._native_messages import Ticker, TickerMessage


class TestTickerMessage:
    """Test class for TickerMessage."""

    def test_ticker_message_single_symbol(self) -> None:
        """Test that single symbol response can be processed."""
        json_data = {
            "symbol": "BTCUSDT",
            "priceChange": "-154.13000000",
            "priceChangePercent": "-0.740",
            "weightedAvgPrice": "20677.46305250",
            "prevClosePrice": "20825.27000000",
            "lastPrice": "20671.14000000",
            "lastQty": "0.00030000",
            "bidPrice": "20671.13000000",
            "bidQty": "0.05000000",
            "askPrice": "20671.14000000",
            "askQty": "0.94620000",
            "openPrice": "20825.27000000",
            "highPrice": "20972.46000000",
            "lowPrice": "20327.92000000",
            "volume": "72.65112300",
            "quoteVolume": "1502240.91155513",
            "openTime": 1655432400000,
            "closeTime": 1655446835460,
            "firstId": 11147809,
            "lastId": 11149775,
            "count": 1967,
        }
        json_str = json.dumps(json_data)

        message = TickerMessage(json_str)
        ticker = message.to_domain_model()

        # Verify that a single Ticker object is returned
        assert isinstance(ticker, Ticker)
        assert str(ticker.symbol) == "BTCUSDT"
        assert ticker.lastPrice == Decimal("20671.14000000")
        assert ticker.count == 1967

    def test_ticker_message_with_newly_added_symbol(self) -> None:
        """Test that newly added symbol is processed correctly."""
        json_data = {
            "symbol": "LTCBTC",  # Newly added symbol
            "priceChange": "-0.00001000",
            "priceChangePercent": "-0.250",
            "weightedAvgPrice": "0.00399300",
            "prevClosePrice": "0.00400000",
            "lastPrice": "0.00399000",
            "lastQty": "10.00000000",
            "bidPrice": "0.00398900",
            "bidQty": "100.00000000",
            "askPrice": "0.00399000",
            "askQty": "200.00000000",
            "openPrice": "0.00400000",
            "highPrice": "0.00410000",
            "lowPrice": "0.00390000",
            "volume": "500000.00000000",
            "quoteVolume": "1996.50000000",
            "openTime": 1655432400000,
            "closeTime": 1655446835460,
            "firstId": 33147809,
            "lastId": 33149775,
            "count": 1967,
        }
        json_str = json.dumps(json_data)

        message = TickerMessage(json_str)
        ticker = message.to_domain_model()

        # Verify newly added symbol is processed correctly
        assert isinstance(ticker, Ticker)
        assert str(ticker.symbol) == "LTCBTC"
        assert ticker.lastPrice == Decimal("0.00399000")

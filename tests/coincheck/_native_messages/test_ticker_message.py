"""Coincheck Ticker message tests"""

from crypto_api_client.coincheck._native_messages.ticker_message import TickerMessage


class TestTickerMessage:
    """Tests for TickerMessage."""

    def test_ticker_message_has_no_metadata(self):
        """Test that Ticker Message has no metadata."""
        json_str = """{
            "last": 15350000,
            "bid": 15340000,
            "ask": 15350001,
            "high": 15836477,
            "low": 15271389,
            "volume": "273.5234",
            "timestamp": 1748558090
        }"""

        message = TickerMessage(json_str)

        # No metadata
        assert message.metadata is None

    def test_ticker_message_to_domain_model(self):
        """Test conversion to domain model."""
        json_str = """{
            "last": 15350000,
            "bid": 15340000,
            "ask": 15350001,
            "high": 15836477,
            "low": 15271389,
            "volume": "273.5234",
            "timestamp": 1748558090
        }"""

        message = TickerMessage(json_str)
        ticker = message.to_domain_model()

        # No metadata
        assert message.metadata is None
        # Domain model is generated correctly
        assert ticker.last == 15350000

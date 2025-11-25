"""Tests for Binance TickerRequest."""

import pytest

from crypto_api_client.binance import TickerRequest


class TestTickerRequest:
    """Test TickerRequest functionality."""

    def test_ticker_request_with_symbol(self) -> None:
        """Test TickerRequest with symbol specified."""
        # Arrange
        symbol = "BTCUSDT"

        # Act
        request = TickerRequest(symbol=symbol)
        params = request.to_query_params()

        # Assert
        assert request.symbol == symbol
        assert params == {"symbol": "BTCUSDT"}
        # Pydantic models can be configured as frozen
        # Frozen validation should be done on the model definition side

    def test_ticker_request_immutability(self) -> None:
        """Test that TickerRequest is immutable."""
        # Arrange
        symbol = "BTCUSDT"
        request = TickerRequest(symbol=symbol)

        # Act & Assert
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="frozen"):
            request.symbol = "ETHUSDT"

    def test_ticker_request_different_symbols(self) -> None:
        """Test TickerRequest with different symbols."""
        # Test multiple symbols
        test_cases = [
            ("BTC", "USDT", {"symbol": "BTCUSDT"}),
            ("ETH", "USDT", {"symbol": "ETHUSDT"}),
            ("BNB", "USDT", {"symbol": "BNBUSDT"}),
        ]

        for base_str, quote_str, expected_params in test_cases:
            symbol = f"{base_str}{quote_str}"
            request = TickerRequest(symbol=symbol)
            assert request.to_query_params() == expected_params

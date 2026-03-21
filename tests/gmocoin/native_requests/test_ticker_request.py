"""Tests for GMO Coin TickerRequest"""

import pytest
from pydantic import ValidationError

from crypto_api_client.gmocoin.native_requests.ticker_request import TickerRequest


class TestTickerRequest:
    """Tests for TickerRequest model"""

    def test_with_symbol(self) -> None:
        """Test query params with symbol specified"""
        request = TickerRequest(symbol="BTC_JPY")
        params = request.to_query_params()

        assert params == {"symbol": "BTC_JPY"}

    def test_without_symbol(self) -> None:
        """Test query params without symbol (all symbols)"""
        request = TickerRequest()
        params = request.to_query_params()

        assert params == {}

    def test_symbol_none_explicitly(self) -> None:
        """Test query params with symbol explicitly set to None"""
        request = TickerRequest(symbol=None)
        params = request.to_query_params()

        assert params == {}

    def test_frozen_model(self) -> None:
        """Test that model is immutable"""
        request = TickerRequest(symbol="BTC_JPY")

        with pytest.raises(ValidationError):
            request.symbol = "ETH_JPY"  # type: ignore[misc]

    def test_multiple_instances_are_equal(self) -> None:
        """Test that instances with same values are equal"""
        request1 = TickerRequest(symbol="BTC_JPY")
        request2 = TickerRequest(symbol="BTC_JPY")

        assert request1 == request2

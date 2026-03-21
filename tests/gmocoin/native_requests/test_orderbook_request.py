"""Tests for GMO Coin OrderBookRequest"""

import pytest
from pydantic import ValidationError

from crypto_api_client.gmocoin.native_requests.orderbook_request import (
    OrderBookRequest,
)


class TestOrderBookRequest:
    """Tests for OrderBookRequest model"""

    def test_with_symbol(self) -> None:
        """Test query params with symbol"""
        request = OrderBookRequest(symbol="BTC_JPY")
        params = request.to_query_params()

        assert params == {"symbol": "BTC_JPY"}

    def test_symbol_is_required(self) -> None:
        """Test that symbol is a required field"""
        with pytest.raises(ValidationError):
            OrderBookRequest()  # type: ignore[call-arg]

    def test_frozen_model(self) -> None:
        """Test that model is immutable"""
        request = OrderBookRequest(symbol="BTC_JPY")

        with pytest.raises(ValidationError):
            request.symbol = "ETH_JPY"  # type: ignore[misc]

    def test_multiple_instances_are_equal(self) -> None:
        """Test that instances with same values are equal"""
        request1 = OrderBookRequest(symbol="BTC_JPY")
        request2 = OrderBookRequest(symbol="BTC_JPY")

        assert request1 == request2

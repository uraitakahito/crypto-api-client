"""Tests for OrderBookRequest"""

import pytest

from crypto_api_client.coincheck.native_requests.order_book_request import (
    OrderBookRequest,
)


class TestOrderBookRequest:
    """Test class for OrderBookRequest"""

    def test_create_with_pair(self) -> None:
        """Can create request with currency pair"""
        request = OrderBookRequest(pair="btc_jpy")

        assert request.pair == "btc_jpy"

    def test_create_with_different_pair(self) -> None:
        """Can create request with different currency pair"""
        request = OrderBookRequest(pair="eth_jpy")

        assert request.pair == "eth_jpy"

    def test_to_query_params(self) -> None:
        """Can convert to query parameters"""
        request = OrderBookRequest(pair="btc_jpy")
        params = request.to_query_params()

        assert params == {"pair": "btc_jpy"}

    def test_request_is_frozen(self) -> None:
        """Request is immutable"""
        request = OrderBookRequest(pair="btc_jpy")

        with pytest.raises(Exception):
            request.pair = "eth_jpy"  # type: ignore[misc]

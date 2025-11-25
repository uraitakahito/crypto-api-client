"""Tests for DepthRequest."""

import pytest
from pydantic import ValidationError

from crypto_api_client.binance.native_requests import DepthRequest


class TestDepthRequest:
    """Tests for DepthRequest."""

    def test_depth_request_creation(self):
        """Test that DepthRequest is created correctly."""
        symbol = "BTCUSDT"
        request = DepthRequest(symbol=symbol, limit=10)

        assert request.symbol == symbol
        assert request.limit == 10

    def test_depth_request_without_limit(self):
        """Test that DepthRequest can be created without limit."""
        symbol = "BTCUSDT"
        request = DepthRequest(symbol=symbol)  # type: ignore[reportCallIssue]

        assert request.symbol == symbol
        assert request.limit is None

    def test_limit_validation_min(self):
        """Test minimum value validation for limit."""
        symbol = "BTCUSDT"
        with pytest.raises(ValidationError) as exc_info:
            DepthRequest(symbol=symbol, limit=0)

        errors = exc_info.value.errors()
        assert any("limit must be >= 1" in str(error) for error in errors)

    def test_limit_validation_max(self):
        """Test maximum value validation for limit."""
        symbol = "BTCUSDT"
        with pytest.raises(ValidationError) as exc_info:
            DepthRequest(symbol=symbol, limit=5001)

        errors = exc_info.value.errors()
        assert any("limit must be <= 5000" in str(error) for error in errors)

    def test_to_query_params_with_limit(self):
        """Test that query params are generated correctly with limit."""
        symbol = "BTCUSDT"
        request = DepthRequest(symbol=symbol, limit=100)
        params = request.to_query_params()

        assert params == {
            "symbol": "BTCUSDT",
            "limit": "100",
        }

    def test_to_query_params_without_limit(self):
        """Test that query params are generated correctly without limit."""
        symbol = "ETHUSDT"
        request = DepthRequest(symbol=symbol)  # type: ignore[reportCallIssue]
        params = request.to_query_params()

        assert params == {
            "symbol": "ETHUSDT",
        }

    def test_frozen_model(self):
        """Test that the model is immutable."""
        symbol = "BTCUSDT"
        request = DepthRequest(symbol=symbol)  # type: ignore[reportCallIssue]
        with pytest.raises(ValidationError):
            request.limit = 500

    @pytest.mark.parametrize("limit", [1, 100, 500, 1000, 5000])
    def test_valid_limit_values(self, limit):
        """Test that request can be created with valid limit values."""
        symbol = "BTCUSDT"
        request = DepthRequest(symbol=symbol, limit=limit)
        assert request.limit == limit

    def test_symbol_is_required(self):
        """Test that symbol is required."""
        with pytest.raises(ValidationError) as exc_info:
            DepthRequest()  # type: ignore

        errors = exc_info.value.errors()
        assert any("symbol" in str(error) for error in errors)

"""Tests for GMO Coin TickerMessage."""

import json
from decimal import Decimal

import pytest

from crypto_api_client.gmocoin._native_messages import TickerMessage
from crypto_api_client.gmocoin._native_messages.message_metadata import (
    MessageMetadata,
)
from crypto_api_client.gmocoin.native_domain_models import Ticker
from tests.common.test_data_factory import GmocoinDataFactory


class TestTickerMessage:
    """Tests for TickerMessage."""

    def test_single_ticker_returns_list(self) -> None:
        """Test that single ticker data returns a list with one element."""
        ticker_data = (
            GmocoinDataFactory.ticker()
            .with_symbol("BTC")
            .with_prices(
                ask="5000000",
                bid="4999000",
                high="5100000",
                last="4999500",
                low="4900000",
            )
            .with_volume("123.456")
            .with_timestamp("2023-01-01T00:00:00.000Z")
            .build()
        )
        json_str = GmocoinDataFactory.ticker_response_json(ticker_data)

        message = TickerMessage(json_str)
        result = message.to_domain_model()

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Ticker)
        assert result[0].symbol == "BTC"
        assert result[0].last == Decimal("4999500")

    def test_multiple_tickers_returns_list(self) -> None:
        """Test that multiple ticker data returns a list."""
        btc = (
            GmocoinDataFactory.ticker()
            .with_symbol("BTC")
            .with_prices(
                ask="5000000",
                bid="4999000",
                high="5100000",
                last="4999500",
                low="4900000",
            )
            .with_volume("123.456")
            .with_timestamp("2023-01-01T00:00:00.000Z")
            .build()
        )
        eth = (
            GmocoinDataFactory.ticker()
            .with_symbol("ETH")
            .with_prices(
                ask="300000", bid="299000", high="310000", last="299500", low="290000"
            )
            .with_volume("456.789")
            .with_timestamp("2023-01-01T00:00:00.000Z")
            .build()
        )
        json_str = GmocoinDataFactory.ticker_response_json(btc, eth)

        message = TickerMessage(json_str)
        result = message.to_domain_model()

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(t, Ticker) for t in result)
        assert result[0].symbol == "BTC"
        assert result[1].symbol == "ETH"

    def test_empty_data_returns_empty_list(self) -> None:
        """Test that empty data array returns empty list."""
        json_str = GmocoinDataFactory.ticker_response_json()

        message = TickerMessage(json_str)
        result = message.to_domain_model()

        assert isinstance(result, list)
        assert len(result) == 0

    def test_non_list_data_raises_error(self) -> None:
        """Test that non-list data raises ValueError."""
        ticker_data = GmocoinDataFactory.ticker().with_symbol("BTC").build()
        json_str = GmocoinDataFactory.message().with_data(ticker_data).to_json()

        message = TickerMessage(json_str)

        with pytest.raises(ValueError) as exc_info:
            message.to_domain_model()

        assert "not in expected array format" in str(exc_info.value)
        assert "dict" in str(exc_info.value)

    def test_metadata_is_extracted(self) -> None:
        """Test that metadata (status, responsetime) is correctly extracted."""
        ticker_data = GmocoinDataFactory.ticker().minimal().build()
        json_str = (
            GmocoinDataFactory.message()
            .with_ticker_data(ticker_data)
            .with_responsetime("2023-01-01T00:00:01.000Z")
            .to_json()
        )

        message = TickerMessage(json_str)

        assert isinstance(message.metadata, MessageMetadata)
        assert message.metadata.status == 0
        assert message.metadata.responsetime == "2023-01-01T00:00:01.000Z"

    def test_payload_exists_and_content_is_valid_json(self) -> None:
        """Test that payload exists and content_str is valid JSON array."""
        ticker_data = GmocoinDataFactory.ticker().minimal().build()
        json_str = GmocoinDataFactory.ticker_response_json(ticker_data)

        message = TickerMessage(json_str)

        assert message.payload is not None
        content = json.loads(message.payload.content_str)
        assert isinstance(content, list)

    def test_payload_raw_json_contains_data_key(self) -> None:
        """Test that payload raw_json contains 'data' key prefix."""
        ticker_data = GmocoinDataFactory.ticker().minimal().build()
        json_str = GmocoinDataFactory.ticker_response_json(ticker_data)

        message = TickerMessage(json_str)

        assert "data" in message.payload.raw_json

"""Tests for generic ExchangeSession."""

from unittest.mock import AsyncMock

import httpx
import pytest
from pydantic import SecretStr

from crypto_api_client import Exchange, ExchangeSession, create_session


class TestExchangeSession:
    """Tests for ExchangeSession class."""

    def test_session_creation(self):
        """Test session creation."""
        session = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy_api_key"),
            api_secret=SecretStr("dummy_api_secret"),
        )

        assert session.exchange == Exchange.BITFLYER
        assert session.is_closed is False
        assert session.config is not None

    def test_with_credentials(self):
        """Test session creation with credentials."""
        api_key = SecretStr("test_key")
        api_secret = SecretStr("test_secret")

        session = ExchangeSession(
            exchange=Exchange.BITFLYER, api_key=api_key, api_secret=api_secret
        )

        # Verify session is created correctly
        assert session is not None
        assert not session.is_closed

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test context manager."""
        async with ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy_api_key"),
            api_secret=SecretStr("dummy_api_secret"),
        ) as session:
            assert session.is_closed is False

        # Session is closed after context exit
        assert session.is_closed is True

    @pytest.mark.asyncio
    async def test_close_with_owned_http_client(self):
        """Test closing owned HTTP client."""
        session = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy_api_key"),
            api_secret=SecretStr("dummy_api_secret"),
        )

        # Mock HTTP client
        mock_http_client = AsyncMock(spec=httpx.AsyncClient)
        session._http_client = mock_http_client
        session._owns_http_client = True

        await session.close()

        mock_http_client.aclose.assert_called_once()
        assert session.is_closed is True

    @pytest.mark.asyncio
    async def test_close_with_external_http_client(self):
        """Test closing externally provided HTTP client."""
        mock_http_client = AsyncMock(spec=httpx.AsyncClient)

        session = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy_api_key"),
            api_secret=SecretStr("dummy_api_secret"),
            http_client=mock_http_client,
        )

        await session.close()

        # Externally provided HTTP client should not be closed
        mock_http_client.aclose.assert_not_called()
        assert session.is_closed is True

    def test_api_access_after_close(self):
        """Test API access error after close."""
        session = ExchangeSession(
            exchange=Exchange.BITFLYER,
            api_key=SecretStr("dummy_api_key"),
            api_secret=SecretStr("dummy_api_secret"),
        )
        session._closed = True

        with pytest.raises(RuntimeError, match="Session is already closed"):
            _ = session.api

    def test_unsupported_exchange(self):
        """Test error for unsupported exchange."""
        with pytest.raises(ValueError, match="Unsupported exchange"):
            ExchangeSession(
                exchange="INVALID_EXCHANGE",  # type: ignore
                api_key=SecretStr("dummy_api_key"),
                api_secret=SecretStr("dummy_api_secret"),
            )


class TestCreateSession:
    """Tests for create_session function."""

    def test_create_bitflyer_session(self):
        """Test BitFlyer session creation."""
        session = create_session(Exchange.BITFLYER)
        assert session.exchange == Exchange.BITFLYER
        assert session.is_closed is False

    def test_create_bitbank_session(self):
        """Test Bitbank session creation."""
        session = create_session(Exchange.BITBANK)
        assert session.exchange == Exchange.BITBANK
        assert session.is_closed is False

    def test_create_binance_session(self):
        """Test BINANCE session creation."""
        session = create_session(Exchange.BINANCE)
        assert session.exchange == Exchange.BINANCE
        assert session.is_closed is False

    def test_create_gmocoin_session(self):
        """Test GMO Coin session creation."""
        session = create_session(Exchange.GMOCOIN)
        assert session.exchange == Exchange.GMOCOIN
        assert session.is_closed is False

    def test_create_session_with_credentials(self):
        """Test session creation with credentials."""
        api_key = "test_key"
        api_secret = "test_secret"

        session = create_session(
            Exchange.BITFLYER, api_key=api_key, api_secret=api_secret
        )

        assert session.exchange == Exchange.BITFLYER
        # Verify credentials are not exposed as instance variables
        assert not hasattr(session, "_api_key")
        assert not hasattr(session, "_api_secret")

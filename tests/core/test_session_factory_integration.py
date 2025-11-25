"""Session factory integration tests"""

import pytest
from pydantic import SecretStr

from crypto_api_client import Exchange, create_session
from crypto_api_client.binance.exchange_api_client import (
    ExchangeApiClient as BinanceApiClient,
)
from crypto_api_client.bitbank.exchange_api_client import (
    ExchangeApiClient as BitbankApiClient,
)
from crypto_api_client.bitflyer.exchange_api_client import (
    ExchangeApiClient as BitFlyerApiClient,
)
from crypto_api_client.gmocoin.exchange_api_client import (
    ExchangeApiClient as GmoCoinApiClient,
)


class TestSessionFactoryIntegration:
    """Session factory integration tests"""

    @pytest.mark.parametrize(
        "exchange",
        [
            Exchange.BITFLYER,
            Exchange.BITBANK,
            Exchange.BINANCE,
            Exchange.GMOCOIN,
        ],
    )
    async def test_create_session_all_exchanges(self, exchange):
        """Verify session creation works type-safely for all exchanges"""
        async with create_session(exchange) as session:
            assert session.exchange == exchange
            assert session.api is not None

            # Verify appropriate API client is generated
            if exchange == Exchange.BITFLYER:
                assert isinstance(session.api, BitFlyerApiClient)
            elif exchange == Exchange.BITBANK:
                assert isinstance(session.api, BitbankApiClient)
            elif exchange == Exchange.BINANCE:
                assert isinstance(session.api, BinanceApiClient)
            elif exchange == Exchange.GMOCOIN:
                assert isinstance(session.api, GmoCoinApiClient)

    async def test_create_session_with_credentials(self):
        """Create session with credentials"""
        api_key = SecretStr("test_key")
        api_secret = SecretStr("test_secret")

        async with create_session(
            Exchange.BITFLYER,
            api_key=api_key,
            api_secret=api_secret,
        ) as session:
            assert session.api is not None
            assert isinstance(session.api, BitFlyerApiClient)
            assert session.api._api_key == api_key
            assert session.api._api_secret == api_secret

    async def test_create_session_without_credentials(self):
        """Create session without credentials (Public API only)"""
        async with create_session(Exchange.BITFLYER) as session:
            assert session.api is not None
            assert isinstance(session.api, BitFlyerApiClient)
            # Verify dummy values are set
            assert session.api._api_key.get_secret_value() == "dummy_api_key"
            assert session.api._api_secret.get_secret_value() == "dummy_api_secret"

    async def test_session_lifecycle(self):
        """Verify session lifecycle is managed correctly"""
        session = create_session(Exchange.BITFLYER)

        # Start context manager
        await session.__aenter__()
        assert not session.is_closed
        assert session.api is not None

        # End context manager
        await session.__aexit__(None, None, None)
        assert session.is_closed

        # Access after close raises error
        with pytest.raises(RuntimeError, match="Session is already closed"):
            _ = session.api

    async def test_multiple_sessions_concurrent(self):
        """Verify multiple sessions can be created concurrently"""
        async with (
            create_session(Exchange.BITFLYER) as session1,
            create_session(Exchange.BITBANK) as session2,
        ):
            assert session1.exchange == Exchange.BITFLYER
            assert session2.exchange == Exchange.BITBANK
            assert isinstance(session1.api, BitFlyerApiClient)
            assert isinstance(session2.api, BitbankApiClient)

    async def test_session_with_callbacks(self):
        """Create session with callbacks"""
        from unittest.mock import Mock

        mock_callback = Mock()
        callbacks = (mock_callback,)

        async with create_session(
            Exchange.BITFLYER,
            callbacks=callbacks,
        ) as session:
            assert session.api is not None
            assert session.callbacks == callbacks

    def test_unsupported_exchange_raises_error(self):
        """Verify error occurs for unsupported exchange"""
        from enum import Enum

        # Create non-existent exchange
        class FakeExchange(Enum):
            FAKE = "fake"

        with pytest.raises(ValueError, match="Unsupported exchange"):
            create_session(FakeExchange.FAKE)  # type: ignore[arg-type]

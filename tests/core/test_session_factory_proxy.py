"""session_factory proxy configuration tests"""

import pytest

from crypto_api_client import Exchange, create_session
from crypto_api_client.core.session_config import SessionConfig


class TestSessionFactoryProxy:
    """Tests for create_session() SessionConfig-related functionality"""

    def test_default_session_config_created(self) -> None:
        """SessionConfig is automatically created when not specified"""
        session = create_session(Exchange.BITFLYER)

        # SessionConfig with default values is created
        assert session.config is not None
        assert session.config.trust_env is False
        assert session.config.verify_ssl is True

    @pytest.mark.asyncio
    async def test_session_with_config_lifecycle(self) -> None:
        """Session lifecycle when SessionConfig is specified"""
        config = SessionConfig(proxy_url="http://host.docker.internal:8080")
        async with create_session(Exchange.BITFLYER, session_config=config) as session:
            assert not session.is_closed
            assert session.config.proxy_url == "http://host.docker.internal:8080"

        # Closed after exiting context
        assert session.is_closed

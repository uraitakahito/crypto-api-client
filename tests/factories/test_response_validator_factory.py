"""Tests for create_response_validator function"""

import pytest

from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.core.exchange_types import Exchange
from crypto_api_client.factories import create_response_validator


class TestCreateResponseValidator:
    """Tests for create_response_validator function"""

    def test_bitflyer_response_validator(self):
        """Verify ResponseValidator for bitFlyer is generated"""
        validator = create_response_validator(Exchange.BITFLYER)
        # Verify it inherits from AbstractRequestCallback
        assert isinstance(validator, AbstractRequestCallback)
        assert hasattr(validator, "before_request")
        assert hasattr(validator, "after_request")
        assert callable(validator.before_request)
        assert callable(validator.after_request)
        # Type verification (by name since it's a public class)
        assert validator.__class__.__name__ == "BitFlyerResponseValidator"

    def test_bitbank_response_validator(self):
        """Verify ResponseValidator for bitbank is generated"""
        validator = create_response_validator(Exchange.BITBANK)
        assert isinstance(validator, AbstractRequestCallback)
        assert hasattr(validator, "before_request")
        assert hasattr(validator, "after_request")
        assert validator.__class__.__name__ == "BitbankResponseValidator"

    def test_binance_response_validator(self):
        """Verify ResponseValidator for BINANCE is generated"""
        validator = create_response_validator(Exchange.BINANCE)
        assert isinstance(validator, AbstractRequestCallback)
        assert hasattr(validator, "before_request")
        assert hasattr(validator, "after_request")
        assert validator.__class__.__name__ == "BinanceResponseValidator"

    def test_gmocoin_response_validator(self):
        """Verify ResponseValidator for GMO Coin is generated"""
        validator = create_response_validator(Exchange.GMOCOIN)
        assert isinstance(validator, AbstractRequestCallback)
        assert hasattr(validator, "before_request")
        assert hasattr(validator, "after_request")
        assert validator.__class__.__name__ == "GmoCoinResponseValidator"

    def test_unsupported_exchange(self):
        """Verify ValueError occurs for unsupported exchange"""
        with pytest.raises(ValueError, match="Unsupported exchange"):
            create_response_validator("INVALID_EXCHANGE")  # type: ignore[arg-type]

    def test_all_exchanges_covered(self):
        """Verify all defined exchanges are supported"""
        for exchange in Exchange:
            validator = create_response_validator(exchange)
            # Verify it inherits from AbstractRequestCallback
            assert isinstance(validator, AbstractRequestCallback)
            assert hasattr(validator, "before_request")
            assert hasattr(validator, "after_request")

    def test_same_exchange_returns_different_instances(self):
        """Verify different instances are returned each time for the same exchange"""
        validator1 = create_response_validator(Exchange.BITFLYER)
        validator2 = create_response_validator(Exchange.BITFLYER)
        assert validator1 is not validator2
        assert type(validator1) is type(validator2)

    def test_direct_instantiation(self):
        """Verify ResponseValidator can be instantiated directly"""
        from crypto_api_client.bitflyer.bitflyer_response_validator import (
            BitFlyerResponseValidator,
        )

        validator = BitFlyerResponseValidator()
        assert isinstance(validator, AbstractRequestCallback)
        assert hasattr(validator, "before_request")
        assert hasattr(validator, "after_request")

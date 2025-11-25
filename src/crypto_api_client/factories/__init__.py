"""Factory function module

This module provides factory functions to generate exchange-specific implementation classes.

Usage example::

    from crypto_api_client.factories import create_response_validator
    from crypto_api_client.core.exchange_types import Exchange

    validator = create_response_validator(Exchange.BITFLYER)
    validator.validate_response(response_data)
"""

from __future__ import annotations

__all__ = [
    "create_response_validator",
]

from .response_validator_factory import create_response_validator

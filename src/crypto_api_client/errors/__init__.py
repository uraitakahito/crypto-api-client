"""Error handling module

This module provides project-specific exception classes.

ResponseValidator generation functionality has been moved to the :mod:`crypto_api_client.factories` module.

Usage example::

    from crypto_api_client.errors import ExchangeApiError
    from crypto_api_client.factories import create_response_validator
    from crypto_api_client.core.exchange_types import Exchange

    validator = create_response_validator(Exchange.BITFLYER)
    try:
        validator.validate_response(response_data)
    except ExchangeApiError as e:
        print(f"API Error: {e}")
"""

from __future__ import annotations

__all__ = [
    "CryptoApiClientError",
    "ExchangeApiError",
    "RateLimitApproachingError",
    "RetryLimitExceededError",
]

from .exceptions import (
    CryptoApiClientError,
    ExchangeApiError,
    RateLimitApproachingError,
    RetryLimitExceededError,
)

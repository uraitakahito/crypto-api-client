"""Utility functions used only in examples/*.py"""

import logging
import os
from collections.abc import Sequence
from decimal import Decimal
from typing import Type, TypeVar

import typer
from dotenv import load_dotenv
from pydantic import SecretStr

from crypto_api_client.bitflyer.native_domain_models import (
    BoardStateType,
    HealthStatusType,
)
from crypto_api_client.callbacks import AbstractRequestCallback

T = TypeVar("T", bound=AbstractRequestCallback)


def filter_callbacks_by_type(
    callbacks: Sequence[AbstractRequestCallback],
    callback_type: Type[T],
) -> tuple[T, ...]:
    """Filter callbacks by specified type from collection

    :param callbacks: Sequence of callbacks (tuple, list, etc.)
    :param callback_type: Type to filter by
    :return: Tuple of callbacks of the specified type

    .. code-block:: python

        from crypto_api_client import callbacks

        # Get only rate limiters
        rate_limiters = filter_callbacks_by_type(
            session.callbacks,
            callbacks.RedisSharedUrlPatternRateLimiter
        )

        # Get only response validation callbacks
        validation_callbacks = filter_callbacks_by_type(
            session.callbacks,
            callbacks.ResponseValidationCallback
        )
    """
    return tuple(cb for cb in callbacks if isinstance(cb, callback_type))


def get_key_and_secret(exchange_name: str) -> tuple[SecretStr, SecretStr]:
    """Get API key and secret from environment variables for specified exchange

    :param exchange_name: Exchange name (e.g., "bitflyer", "bitbank")
    :type exchange_name: str
    :return: Tuple of (API key, API secret) as SecretStr
    :rtype: tuple[SecretStr, SecretStr]
    """
    exchange_name = exchange_name.upper()

    load_dotenv(verbose=True)

    api_key = os.environ.get(f"{exchange_name}_API_KEY")
    api_secret = os.environ.get(f"{exchange_name}_API_SECRET")

    if api_key is None or api_secret is None:
        typer.echo(
            f"Environment variables {exchange_name}_API_KEY and/or {exchange_name}_API_SECRET are not set. Exiting...",
        )
        raise typer.Exit(1)

    return SecretStr(api_key), SecretStr(api_secret)


def setup_logging(log_level: str) -> None:
    """Common function to configure logging level

    :param log_level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    :raises typer.BadParameter: When invalid log level is specified
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        msg = f"Invalid log level: {log_level}"
        raise typer.BadParameter(msg)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )


def get_health_status_emoji(status: HealthStatusType | str) -> str:
    """Return emoji corresponding to exchange status

    :param status: HealthStatusType or status string
    :return: Corresponding emoji
    """
    if isinstance(status, str):
        # For string input, try converting to HealthStatusType
        try:
            status = HealthStatusType(status)
        except ValueError:
            # Special cases
            if status == "ERROR":
                return "❌"
            elif status == "N/A":
                return "❓"
            else:
                return "❓"

    emoji_map = {
        HealthStatusType.NORMAL: "✅",
        HealthStatusType.BUSY: "⚠️",
        HealthStatusType.VERY_BUSY: "🟠",
        HealthStatusType.SUPER_BUSY: "🔴",
        HealthStatusType.NO_ORDER: "🚫",
        HealthStatusType.STOP: "🛑",
    }
    return emoji_map.get(status, "❓")


def get_board_state_emoji(state: BoardStateType | str) -> str:
    """Return emoji corresponding to order book operational state

    :param state: BoardStateType or status string
    :return: Corresponding emoji
    """
    if isinstance(state, str):
        # For string input, try converting to BoardStateType
        try:
            state = BoardStateType(state)
        except ValueError:
            return "❓"

    emoji_map = {
        BoardStateType.RUNNING: "▶️",
        BoardStateType.CLOSED: "⏸️",
        BoardStateType.STARTING: "🔄",
        BoardStateType.PREOPEN: "🔜",
        BoardStateType.CIRCUIT_BREAK: "⚡",
    }
    return emoji_map.get(state, "❓")


def format_price(price: Decimal, *, align_to: Decimal) -> str:
    """Format price aligned to specified reference value precision

    :param price: Price to format
    :param align_to: Reference value to align precision (matches decimal places of this value)
    :returns: Formatted price string

    .. code-block:: python

        # For integer prices (align_to=1000):
        format_price(Decimal("16500000"), align_to=Decimal("1000"))
        # "16,500,000"

        # For decimal prices (align_to=0.0001):
        format_price(Decimal("0.00123456"), align_to=Decimal("0.0001"))
        # "0.0012"

        # For decimal prices (align_to=0.1):
        format_price(Decimal("123.456"), align_to=Decimal("0.1"))
        # "123.4"
    """
    decimal_places = _get_decimal_places(align_to)

    if decimal_places == 0:
        # Integer display
        return f"{int(price):,}"
    else:
        # Format with specified decimal places
        # Separate integer and decimal parts to add commas
        price_str = f"{price:.{decimal_places}f}"
        if "." in price_str:
            int_part, dec_part = price_str.split(".")
            return f"{int(int_part):,}.{dec_part}"
        else:
            return f"{int(price_str):,}"


def _get_decimal_places(d: Decimal) -> int:
    """Get number of decimal places in a Decimal value

    :param d: Decimal value
    :returns: Number of decimal places

    .. code-block:: python

        get_decimal_places(Decimal('0.1'))
        # 1
        get_decimal_places(Decimal('0.01'))
        # 2
        get_decimal_places(Decimal('100000'))
        # 0
    """
    normalized = d.normalize()
    decimal_tuple = normalized.as_tuple()
    exponent = decimal_tuple.exponent

    # Verify exponent is int (not a special value like NaN, Infinity)
    if not isinstance(exponent, int):
        raise ValueError(f"Invalid Decimal value: {d} (exponent={exponent})")

    return abs(exponent) if exponent < 0 else 0

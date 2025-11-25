"""Custom type parsers for use with Typer.

Provides command-line argument conversion functions for types
not directly supported by Typer, such as ZoneInfo and Decimal.

.. warning::

    Enum types are directly supported since Typer 0.16.0,
    so custom ParamTypes for Enums are not necessary.
"""

from decimal import Decimal, InvalidOperation
from typing import Any
from zoneinfo import ZoneInfo

import click


class ZoneInfoParamType(click.ParamType):
    """Click parameter type for ZoneInfo type.

    Converts strings to ZoneInfo objects.
    """

    name = "timezone"

    def convert(
        self, value: Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> ZoneInfo:
        """Convert string to ZoneInfo object.

        :param value: Input value
        :param param: Parameter information
        :param ctx: Context
        :return: ZoneInfo object
        """
        if isinstance(value, ZoneInfo):
            return value

        try:
            return ZoneInfo(value)
        except Exception:
            # Show examples of commonly used timezones
            common_zones = [
                "UTC",
                "Asia/Tokyo",
                "America/New_York",
                "Europe/London",
                "Asia/Shanghai",
            ]
            self.fail(
                f"Invalid timezone: {value}. Examples of valid timezones: {', '.join(common_zones)}",
                param,
                ctx,
            )


class DecimalParamType(click.ParamType):
    """Click parameter type for Decimal type.

    Converts strings to Decimal objects.
    """

    name = "decimal"

    def __init__(
        self, min_value: Decimal | None = None, max_value: Decimal | None = None
    ):
        """Initialize.

        :param min_value: Minimum value (Optional)
        :param max_value: Maximum value (Optional)
        """
        self.min_value = min_value
        self.max_value = max_value

    def convert(
        self, value: Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> Decimal:
        """Convert string to Decimal object.

        :param value: Input value
        :param param: Parameter information
        :param ctx: Context
        :return: Decimal object
        """
        if isinstance(value, Decimal):
            return value

        try:
            decimal_value = Decimal(str(value))

            # Check minimum value
            if self.min_value is not None and decimal_value < self.min_value:
                self.fail(
                    f"Value {decimal_value} is less than minimum {self.min_value}",
                    param,
                    ctx,
                )

            # Check maximum value
            if self.max_value is not None and decimal_value > self.max_value:
                self.fail(
                    f"Value {decimal_value} is greater than maximum {self.max_value}",
                    param,
                    ctx,
                )

            return decimal_value
        except (ValueError, InvalidOperation) as e:
            self.fail(
                f"Invalid decimal value: {value}. Error: {str(e)}",
                param,
                ctx,
            )


# Export parser instances
ZONE_INFO_TYPE = ZoneInfoParamType()

# Parser for Decimal type (minimum value 0)
POSITIVE_DECIMAL_TYPE = DecimalParamType(min_value=Decimal("0"))

# For range 0.0-1.0 (for rate limit margin)
RATE_DECIMAL_TYPE = DecimalParamType(min_value=Decimal("0"), max_value=Decimal("1"))

# No restriction (for prices)
PRICE_DECIMAL_TYPE = DecimalParamType()

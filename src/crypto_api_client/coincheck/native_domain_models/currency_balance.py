""":term:`native domain model` representing Coincheck currency-specific balance information"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class CurrencyBalance(BaseModel):
    """:term:`native domain model` representing currency-specific balance.

    Holds balance information for one currency.

    Models JSON received from :term:`API endpoint` split by currency.

    Original API response:

    .. code-block:: json

        {
            "success": true,
            "jpy": "0.8401",
            "btc": "7.75052654",
            "jpy_reserved": "3000.0",
            "btc_reserved": "3.5002",
            "jpy_lending": "0",
            "btc_lending": "0.1",
            "jpy_lend_in_use": "0",
            "btc_lend_in_use": "0.3",
            "jpy_lent": "0",
            "btc_lent": "1.2",
            "jpy_debt": "0",
            "btc_debt": "0",
            "jpy_tsumitate": "10000.0",
            "btc_tsumitate": "0.4034"
        }

    Split by currency:

    .. code-block:: python

        [
            CurrencyBalance(
                currency="btc",
                available=Decimal("7.75052654"),
                reserved=Decimal("3.5002"),
                lending=Decimal("0.1"),
                ...
            ),
            CurrencyBalance(
                currency="jpy",
                available=Decimal("0.8401"),
                reserved=Decimal("3000.0"),
                ...
            )
        ]

    .. seealso::

        `Balance <https://coincheck.com/documents/exchange/api#account-balance>`__
    """

    currency: str = Field(description="Currency code (btc, jpy, eth, etc.)")
    available: Decimal = Field(description="Available balance")
    reserved: Decimal = Field(default=Decimal(0), description="Balance in use for orders")
    lending: Decimal = Field(default=Decimal(0), description="Balance available for lending")
    lend_in_use: Decimal = Field(default=Decimal(0), description="Balance currently lent")
    lent: Decimal = Field(default=Decimal(0), description="Balance already lent")
    debt: Decimal = Field(default=Decimal(0), description="Borrowed balance")
    tsumitate: Decimal = Field(default=Decimal(0), description="Accumulated balance")

    model_config = {"frozen": True}

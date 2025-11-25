from __future__ import annotations

import json
from decimal import Decimal

from ..native_domain_models.currency_balance import CurrencyBalance
from .balance_payload import BalancePayload
from .coincheck_message import CoincheckMessage


class BalanceMessage(CoincheckMessage[BalancePayload, list[CurrencyBalance]]):
    """Implementation of :term:`native message` for asset balance list

    :term:`native message metadata` and :term:`native message payload` are mixed at the same level.

    Models the response data for asset balance list.

    .. hint::

        **JSON example:**

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

    .. note::

        **Metadata and payload separation:**

        This class automatically excludes the ``success`` field
        through the base class implementation of :meth:`CoincheckMessage._extract_payload_json`.

    .. seealso::

        - Balance API: https://coincheck.com/documents/exchange/api#account-balance
        - :meth:`CoincheckMessage._extract_payload_json` - Implementation of metadata exclusion
    """

    def _create_payload(self, payload_json_str: str) -> BalancePayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON with the ``success`` field excluded
        by ``CoincheckMessage._extract_payload_json()``, like this:

        .. code-block:: json

            {
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

        .. note::

            Metadata (``success``) has already been excluded by the base class
            ``CoincheckMessage._extract_payload_json()``,
            so only pure payload data is passed to this method.
        """
        return BalancePayload(payload_json_str)

    def to_domain_model(self) -> list[CurrencyBalance]:
        """Generate list of currency-specific balances from :term:`payload content`

        Split flat JSON structure by currency and create individual CurrencyBalance objects.

        .. note::
            Metadata (success) has already been excluded by the base class
            ``CoincheckMessage._extract_payload_json()``,
            so all keys in the payload can be treated as payload data.
        """
        data = json.loads(
            self.payload.content_str,
            parse_float=Decimal,
            parse_int=Decimal,
        )

        # Extract set of currencies (no need to check for success)
        currencies: set[str] = set()
        for key in data:
            # Example: "btc_reserved" -> "btc"
            base_currency = key.split("_")[0]
            currencies.add(base_currency)

        # Generate CurrencyBalance for each currency
        balances: list[CurrencyBalance] = []
        for currency in sorted(currencies):
            balance = CurrencyBalance(
                currency=currency,
                available=Decimal(data.get(currency, "0")),
                reserved=Decimal(data.get(f"{currency}_reserved", "0")),
                lending=Decimal(data.get(f"{currency}_lending", "0")),
                lend_in_use=Decimal(data.get(f"{currency}_lend_in_use", "0")),
                lent=Decimal(data.get(f"{currency}_lent", "0")),
                debt=Decimal(data.get(f"{currency}_debt", "0")),
                tsumitate=Decimal(data.get(f"{currency}_tsumitate", "0")),
            )
            balances.append(balance)

        return balances

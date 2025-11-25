from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.balance import Balance
from .balances_payload import BalancesPayload
from .bitflyer_message import BitFlyerMessage


class BalancesMessage(BitFlyerMessage[BalancesPayload, list[Balance]]):
    """:term:`native message` implementation for asset balance list

    Contains only :term:`native message payload`, no :term:`native message metadata`.

    Models the response data for asset balance list.

    .. note::

       **Example JSON:**

       .. code-block:: json

           [
               {
                   "currency_code": "JPY",
                   "amount": 1024078,
                   "available": 508000
               },
               {
                   "currency_code": "BTC",
                   "amount": 10.24,
                   "available": 4.12
               }
           ]

    .. seealso::

        Get Account Asset Balance: https://lightning.bitflyer.com/docs?lang=en#get-account-asset-balance

    """

    def _create_payload(self, payload_json_str: str) -> BalancesPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like the following:

        .. code-block:: json

            [
                {
                    "currency_code": "JPY",
                    "amount": 1024078,
                    "available": 508000
                },
                {
                    "currency_code": "BTC",
                    "amount": 10.24,
                    "available": 4.12
                }
            ]
        """
        return BalancesPayload(payload_json_str)

    def to_domain_model(self) -> list[Balance]:
        """Generate :term:`native domain model` from :term:`payload content`"""
        return DecimalJsonParser.parse(self.payload.content_str, list[Balance])

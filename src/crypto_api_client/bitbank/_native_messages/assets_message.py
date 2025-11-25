from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.asset import Asset
from .assets_payload import AssetsPayload
from .bitbank_message import BitbankMessage


class AssetsMessage(BitbankMessage[AssetsPayload, list[Asset]]):
    """:term:`native message` implementation for asset balance list

    Contains :term:`native message metadata` and :term:`native message payload`.

    Models response data for asset balance list.

    .. code-block:: json

        {
            "success": 1,
            "data": {
                "assets": [
                    {
                        "asset": "jpy",
                        "amount_precision": 4,
                        "onhand_amount": "100000.0000",
                        "locked_amount": "0.0000",
                        "free_amount": "100000.0000",
                        "stop_deposit": false,
                        "stop_withdrawal": false,
                        "withdrawal_fee": {
                            "threshold": "30000.0000",
                            "under": "550.0000",
                            "over": "770.0000"
                        }
                    }
                ]
            }
        }

    .. seealso::

        bitbank API documentation: https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api.md
    """

    def _create_payload(self, payload_json_str: str) -> AssetsPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like the following:

        .. code-block:: json

            "data": {
                "assets": [
                    {
                        "asset": "jpy",
                        "amount_precision": 4,
                        "onhand_amount": "100000.0000",
                        "locked_amount": "0.0000",
                        "free_amount": "100000.0000",
                        "stop_deposit": false,
                        "stop_withdrawal": false,
                        "withdrawal_fee": {
                            "threshold": "30000.0000",
                            "under": "550.0000",
                            "over": "770.0000"
                        }
                    }
                ]
            }
        """
        return AssetsPayload(payload_json_str)

    def to_domain_model(self) -> list[Asset]:
        """Generate :term:`native domain model` from :term:`payload content`"""
        return DecimalJsonParser.parse(self.payload.content_str, list[Asset])

"""Spot status message processing"""

from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.pair_status import PairStatus
from ..native_domain_models.spot_status import SpotStatus
from .bitbank_message import BitbankMessage
from .spot_status_payload import SpotStatusPayload


class SpotStatusMessage(BitbankMessage[SpotStatusPayload, SpotStatus]):
    """:term:`native message` implementation for spot status

    Contains :term:`native message metadata` and :term:`native message payload`.

    .. hint::

        **Example JSON string:**

        .. code-block:: json

            {
                "success": 1,
                "data": {
                    "statuses": [
                        {
                            "pair": "btc_jpy",
                            "status": "NORMAL",
                            "min_amount": "0.0001"
                        },
                        {
                            "pair": "eth_jpy",
                            "status": "BUSY",
                            "min_amount": "0.001"
                        }
                    ]
                }
            }

    .. seealso::

        `spot/status API <https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api_JP.md#spot-status>`__
    """

    def _create_payload(self, payload_json_str: str) -> SpotStatusPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like the following:

        .. code-block:: json

            "data": {
                "statuses": [
                    {
                        "pair": "btc_jpy",
                        "status": "NORMAL",
                        "min_amount": "0.0001"
                    }
                ]
            }
        """
        return SpotStatusPayload(payload_json_str)

    def to_domain_model(self) -> SpotStatus:
        """Generate :term:`native domain model` from :term:`payload content`

        Parse status of each currency pair from JSON array and generate SpotStatus object.
        """
        pair_statuses = DecimalJsonParser.parse(
            self.payload.content_str, list[PairStatus]
        )
        return SpotStatus(statuses=pair_statuses)

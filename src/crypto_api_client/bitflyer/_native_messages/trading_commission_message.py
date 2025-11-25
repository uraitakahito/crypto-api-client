"""bitFlyer trading commission message."""

from __future__ import annotations

from crypto_api_client.core.decimal_json_parser import DecimalJsonParser

from ..native_domain_models.trading_commission import TradingCommission
from .bitflyer_message import BitFlyerMessage
from .trading_commission_payload import TradingCommissionPayload


class TradingCommissionMessage(
    BitFlyerMessage[TradingCommissionPayload, TradingCommission]
):
    """:term:`native message` implementation for trading commission

    Contains only :term:`native message payload`, no :term:`native message metadata`.

    .. hint::

        **JSON string example:**

        .. code-block:: json

            {
                "commission_rate": 0.001
            }

    .. seealso::

        Trading Commission: https://lightning.bitflyer.com/docs?lang=en#get-trading-commission

    """

    def _create_payload(self, payload_json_str: str) -> TradingCommissionPayload:
        """Generate :term:`native message payload`

        The payload_json_str argument is JSON like the following:

        .. code-block:: json

            {
                "commission_rate": 0.001
            }
        """
        return TradingCommissionPayload(payload_json_str)

    def to_domain_model(self) -> TradingCommission:
        """Generate :term:`native domain model` from :term:`payload content`"""
        return DecimalJsonParser.parse(self.payload.content_str, TradingCommission)

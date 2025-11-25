from __future__ import annotations

from crypto_api_client._base import Payload


class BalancePayload(Payload):
    """Implementation of :term:`native message payload` for balance

    Holds only pure payload data with the ``success`` field excluded
    by :class:`BalanceMessage`.

    .. note::

        This class uses the default implementation (Identity transformation)
        of the base class :class:`~crypto_api_client._base.Payload` as-is.

        Metadata (``success``) exclusion is already performed in
        :meth:`BalanceMessage._extract_payload_json`,
        so this class only handles pure payload.

    .. seealso::

        :meth:`BalanceMessage._extract_payload_json` - Metadata exclusion processing
    """

    pass

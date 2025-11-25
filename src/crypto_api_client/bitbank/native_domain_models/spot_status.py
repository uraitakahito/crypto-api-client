from __future__ import annotations

from pydantic import BaseModel

from .pair_status import PairStatus


class SpotStatus(BaseModel):
    """:term:`native domain model` representing overall exchange status

    Example JSON returned by :term:`API endpoint`:

    .. code-block:: json

        {
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

    .. seealso::

        `Official doc <https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api.md#status>`__

    :param statuses: List of status information for each currency pair
    :type statuses: list[PairStatus]
    """

    statuses: list[PairStatus]

    model_config = {"frozen": True}

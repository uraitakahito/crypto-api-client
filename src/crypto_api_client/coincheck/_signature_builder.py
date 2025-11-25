from __future__ import annotations

from yarl import URL


def build_message(
    nonce: str,
    api_endpoint: URL,
    body: str = "",
) -> str:
    """Build message for signature.

    :param nonce: nonce value (UNIX timestamp string in milliseconds)
    :param api_endpoint: :term:`API endpoint` (e.g., https://coincheck.com/api/accounts/balance)
    :param body: Request body (empty string for GET)
    :return: Message string to be signed

    .. seealso::
        `Coincheck API Authentication <https://coincheck.com/documents/exchange/api#auth>`__

    .. code-block:: python

        # GET request
        msg = build_message(
            nonce="1640000000000",
            api_endpoint=URL("https://coincheck.com/api/accounts/balance"),
            body=""
        )
        # Result: "1640000000000https://coincheck.com/api/accounts/balance"

        # POST request (if implemented in the future)
        msg = build_message(
            nonce="1640000000000",
            api_endpoint=URL("https://coincheck.com/api/exchange/orders"),
            body='{"pair":"btc_jpy","order_type":"buy","rate":"500000","amount":"0.001"}'
        )
        # Result: "1640000000000https://coincheck.com/api/exchange/orders{\"pair\":\"btc_jpy\",\"order_type\":\"buy\",\"rate\":\"500000\",\"amount\":\"0.001\"}"
    """
    return nonce + str(api_endpoint) + body

from __future__ import annotations

import json

from yarl import URL

from crypto_api_client.http._http_method import HttpMethod


def build_message(
    *,
    method: HttpMethod,
    endpoint_path: URL,
    query_params: dict[str, str] | None = None,
    request_body: dict[str, str | bool] | None = None,
    request_time: str,
    time_window_millisecond: str,
) -> str:
    """Build message for signature.

    :param method: HTTP method (HttpMethod.GET or HttpMethod.POST)
    :param endpoint_path: Endpoint path. Must start with /. e.g. /v1/user/assets
    :param query_params: Query parameters (used for GET requests)
    :param request_body: Body for POST requests
    :param request_time: Request time (Unix timestamp string in milliseconds)
    :param time_window_millisecond: Time window (milliseconds)
    :return: Message string for signature

    .. seealso::
        `bitbank Private API <https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api.md#authorization>`__

    .. code-block:: python

        # GET request (no query parameters)
        msg = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("/v1/user/assets"),
            request_time="1640000000000",
            time_window_millisecond="5000",
        )
        # Result: "16400000000005000/v1/user/assets"

        # GET request (with query parameters)
        msg = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("/v1/user/spot/trade_history"),
            query_params={"pair": "btc_jpy", "count": "1"},
            request_time="1640000000000",
            time_window_millisecond="5000",
        )
        # Result: "16400000000005000/v1/user/spot/trade_history{\"pair\":\"btc_jpy\",\"count\":\"1\"}"

        # POST request
        msg = build_message(
            method=HttpMethod.POST,
            endpoint_path=URL("/v1/user/spot/order"),
            request_body={"pair": "btc_jpy", "amount": "0.0001", "price": "17000000", "side": "sell", "type": "limit"},
            request_time="1640000000000",
            time_window_millisecond="5000",
        )
        # Result: "16400000000005000{\"pair\":\"btc_jpy\",\"amount\":\"0.0001\",\"price\":\"17000000\",\"side\":\"sell\",\"type\":\"limit\"}"

    .. note::
        While fewer parameters could be used, we maintain this signature for consistency with similar functions for other exchanges.
    """
    if method == HttpMethod.POST and request_body is not None:
        signature_data = json.dumps(
            request_body, separators=(",", ":"), ensure_ascii=False
        )
    else:
        if query_params:
            signature_data = endpoint_path.path + json.dumps(
                query_params, separators=(",", ":")
            )
        else:
            signature_data = endpoint_path.path

    return f"{request_time}{time_window_millisecond}{signature_data}"

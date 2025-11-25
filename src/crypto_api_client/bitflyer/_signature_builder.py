from __future__ import annotations

import json
from typing import Any

from yarl import URL

from crypto_api_client.http._http_method import HttpMethod


def build_message(
    *,
    method: HttpMethod,
    endpoint_path: URL,
    query_params: dict[str, Any] | None,
    request_body: dict[str, Any] | None,
    timestamp: str,
) -> str:
    """Build the message for signature.

    :param method: HTTP method (HttpMethod.GET or HttpMethod.POST)
    :param endpoint_path: :term:`endpoint path`. Must start with /. e.g. /v1/me/getchildorders
    :param query_params: Query parameters (used in GET requests)
    :param request_body: Request body (used in POST requests)
    :param timestamp: Timestamp (Unix timestamp string in milliseconds)
    :return: Message string to be signed

    .. seealso::
        `bitFlyer Authentication <https://lightning.bitflyer.com/docs?lang=en#authentication>`__

    .. code-block:: python

        # GET request (with query parameters)
        msg = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("/v1/me/getchildorders"),
            query_params={"product_code": "BTC_JPY"},
            request_body=None,
            timestamp="1640000000000"
        )
        # Result: "1640000000000GET/v1/me/getchildorders?product_code=BTC_JPY"

        # GET request (without query parameters)
        msg = build_message(
            method=HttpMethod.GET,
            endpoint_path=URL("/v1/me/getbalance"),
            query_params=None,
            request_body=None,
            timestamp="1640000000000"
        )
        # Result: "1640000000000GET/v1/me/getbalance"

        # POST request
        msg = build_message(
            method=HttpMethod.POST,
            endpoint_path=URL("/v1/me/sendchildorder"),
            query_params=None,
            request_body={"product_code": "BTC_JPY", "side": "BUY", "size": "0.001"},
            timestamp="1640000000000"
        )
        # Result: "1640000000000POST/v1/me/sendchildorder{\"product_code\":\"BTC_JPY\",\"side\":\"BUY\",\"size\":\"0.001\"}"

    .. note::
        Although we could reduce the number of parameters, we keep this format
        to maintain consistency with similar functions for other exchanges.
    """

    if method == HttpMethod.GET:
        if query_params:
            endpoint_path_qs = endpoint_path % query_params
        else:
            endpoint_path_qs = endpoint_path
        msg = timestamp + str(method) + str(endpoint_path_qs)
    else:  # HttpMethod.POST
        # NOTE:
        # request_body = {"a": 1, "b": 2}
        #   Default:
        #     {"a": 1, "b": 2}
        #   separators=(",", ":"):
        #     {"a":1,"b":2}
        if request_body:
            body = json.dumps(request_body, separators=(",", ":"), ensure_ascii=False)
        else:
            body = ""

        msg = timestamp + str(method) + str(endpoint_path) + body

    return msg

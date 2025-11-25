from __future__ import annotations

from urllib.parse import urlencode

from pydantic import SecretStr

from crypto_api_client.security._hmac_signer import sign_message


def generate_rest_signature(
    api_secret: str | SecretStr,
    params: dict[str, str] | None,
) -> str:
    """Generate signature for REST API.

    BINANCE signature generation specification:
    1. Combine all parameters (including timestamp) in alphabetical order as query string format
    2. Sign the combined string with HMAC-SHA256
    3. Return signature result as hexadecimal string

    :param api_secret: API secret key (str or SecretStr)
    :type api_secret: str | SecretStr
    :param params: Request parameters (including timestamp)
    :type params: dict[str, str] | None
    :return: Hexadecimal representation of signature
    :rtype: str
    """
    if not params:
        params = {}

    # Convert parameters to query string format
    # BINANCE requires parameter order to be preserved, so use dictionary order as-is
    query_string = urlencode(params)

    # Generate signature with HMAC-SHA256
    return sign_message(api_secret, query_string)

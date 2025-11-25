from __future__ import annotations

import hashlib
import hmac

from pydantic import SecretStr


def sign_message(secret: str | SecretStr, msg: str) -> str:
    """Generate HMAC-SHA256 signature.

    To verify the signature, you can do the following:

    .. code-block:: bash

        % openssl rand -hex 32 1bdf1e786b748ffd9f747f1b6abd43abf1939db740541e26b9c2c0e151690923
        % echo -n "value" | openssl dgst -sha256 -hmac 1bdf1e786b748ffd9f747f1b6abd43abf1939db740541e26b9c2c0e151690923
        SHA2-256(stdin)= 3a97c3c68815ffa3a7fcdca9a67a6d106d7fc6dde79c96c1515b2b6acf16cc48

    Or you can also verify with `HMAC-SHA256 Hash Generator <https://www.devglan.com/online-tools/hmac-sha256-online>`_.

    :param secret: Secret key (str or SecretStr)
    :type secret: str | SecretStr
    :param msg: Message to generate signature for
    :type msg: str
    :return: Hexadecimal representation of signature
    :rtype: str
    """
    # Get actual value if it's SecretStr
    if isinstance(secret, SecretStr):
        secret_value = secret.get_secret_value()
    else:
        secret_value = secret

    s = hmac.new(bytearray(secret_value.encode("utf-8")), digestmod=hashlib.sha256)
    s.update(msg.encode("utf-8"))
    return s.hexdigest()

import os
from typing import Any

import redis.asyncio
from redis.backoff import NoBackoff  # noqa: F401  # pyright: ignore[reportUnusedImport]
from redis.retry import Retry


def create_redis_client(
    *,
    host: str | None = None,
    port: int = 6379,
    db: int = 0,
    decode_responses: bool = False,  # Keeping False ensures interoperability with non-Python languages and explicit encoding control
    socket_keepalive: bool = True,
    socket_timeout: int = 5,
    socket_connect_timeout: float | None = None,
    retry_on_timeout: bool | None = None,
    retry: Retry | None = None,
):
    """Factory function to create Redis client

    Automatically uses environment variable REDIS_HOST if set.

    :param host: Redis hostname (uses environment variable REDIS_HOST if None)
    :type host: str | None
    :param port: Redis port number
    :type port: int
    :param db: Database number
    :type db: int
    :param decode_responses: Whether to decode responses to strings
    :type decode_responses: bool
    :param socket_keepalive: Whether to enable socket keepalive
    :type socket_keepalive: bool
    :param socket_timeout: Socket timeout in seconds
    :type socket_timeout: int
    :param socket_connect_timeout: Connection timeout in seconds (default if None)
    :type socket_connect_timeout: float | None
    :param retry_on_timeout: Whether to retry on timeout (default if None)
    :type retry_on_timeout: bool | None
    :param retry: Retry configuration (default if None)
    :type retry: Retry | None
    :return: Configured Redis client
    :rtype: redis.asyncio.Redis

    Example usage:

    .. code-block:: python

        # Default configuration (auto-load environment variables, get as bytes)
        redis_client = create_redis_client()
        await redis_client.set("key", b"value")
        result = await redis_client.get("key")  # bytes type

        # Enable string decoding
        redis_client = create_redis_client(decode_responses=True)
        await redis_client.set("key", "value")
        result = await redis_client.get("key")  # str type

        # Custom host and port
        redis_client = create_redis_client(host="redis.example.com", port=6380)

        # Fail fast without retry (recommended when creating multiple instances)
        redis_client = create_redis_client(
            retry=Retry(NoBackoff(), 0),  # No retry
            socket_connect_timeout=3.0,    # Timeout after 3 seconds
        )
    """
    redis_host = host or os.environ.get("REDIS_HOST", "localhost")

    kwargs: dict[str, Any] = {
        "host": redis_host,
        "port": port,
        "db": db,
        "decode_responses": decode_responses,
        "socket_keepalive": socket_keepalive,
        "socket_timeout": socket_timeout,
    }

    # Optional settings (only add if not None)
    if socket_connect_timeout is not None:
        kwargs["socket_connect_timeout"] = socket_connect_timeout
    if retry_on_timeout is not None:
        kwargs["retry_on_timeout"] = retry_on_timeout
    if retry is not None:
        kwargs["retry"] = retry

    return redis.asyncio.Redis(**kwargs)

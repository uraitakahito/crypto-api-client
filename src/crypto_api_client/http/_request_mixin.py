from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Coroutine
from logging import getLogger
from typing import TYPE_CHECKING, Any, Literal

import httpx
from yarl import URL

from crypto_api_client.security.secret_headers import SecretHeaders

from ._endpoint_request import EndpointRequest
from ._http_method import HttpMethod
from ._retry_strategy import ExponentialBackoffRetryStrategy
from .http_response_data import HttpResponseData

if TYPE_CHECKING:
    from crypto_api_client.callbacks.abstract_request_callback import (
        AbstractRequestCallback,
    )

CallbackTiming = Literal["before_request", "after_request"]
CallbackFunc = Callable[..., Coroutine[Any, Any, None]]

logger = getLogger(__name__)


class RequestMixin:
    """Mixin class providing asynchronous HTTP request functionality."""

    def __init__(
        self,
        *,
        callbacks: tuple["AbstractRequestCallback", ...] | None = None,
        request_config: dict[str, Any],
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize asynchronous request mixin.

        :param callbacks: Callbacks executed before and after requests
        :type callbacks: tuple[AbstractRequestCallback, ...] | None
        :param request_config: Request configuration (timeout, etc.) - required
        :type request_config: dict[str, Any]
        :param http_client: Custom httpx client (for connection pooling)
        :type http_client: httpx.AsyncClient | None
        """
        self._callbacks: defaultdict[CallbackTiming, list[CallbackFunc]] = defaultdict(
            list
        )
        if callbacks:
            self._register_callbacks(callbacks)
        self._request_config = request_config
        self._http_client = http_client
        # Record whether client was provided externally
        self._external_client = http_client is not None

    def _register_callback(self, callback: AbstractRequestCallback) -> None:
        """Register callback handler.

        :param callback: Callback handler to register
        :type callback: AbstractRequestCallback
        :rtype: None
        """
        self._callbacks["before_request"].append(callback.before_request)
        self._callbacks["after_request"].append(callback.after_request)

    def _register_callbacks(
        self, callbacks: tuple["AbstractRequestCallback", ...]
    ) -> None:
        """Register multiple callback handlers

        :param callbacks: Tuple of callback handlers to register
        :type callbacks: tuple[AbstractRequestCallback, ...]
        :rtype: None
        """
        for callback in callbacks:
            self._register_callback(callback)

    async def run_callbacks(
        self, timing: CallbackTiming, *args: object, **kwargs: object
    ) -> None:
        """Execute asynchronous callbacks at specified timing.

        :param timing: Callback timing ('before_request' or 'after_request')
        :type timing: CallbackTiming
        :param args: Positional arguments to pass to callbacks
        :type args: object
        :param kwargs: Keyword arguments to pass to callbacks
        :type kwargs: object
        :rtype: None
        """
        for cb in self._callbacks[timing]:
            await cb(*args, **kwargs)

    async def send_request(
        self,
        *,
        method: HttpMethod,
        url: URL,
        headers: SecretHeaders = SecretHeaders(),
        data: str | None = None,
    ) -> HttpResponseData:
        """Send asynchronous HTTP request and return response

        :param method: HTTP method
        :type method: HttpMethod
        :param url: Request URL
        :type url: yarl.URL
        :param headers: Request headers
        :type headers: SecretHeaders
        :param data: Request body
        :type data: str | None
        :return: HttpResponseData model (TypedDict or Pydantic)
        :rtype: HttpResponseData
        """
        retry_strategy = ExponentialBackoffRetryStrategy[HttpResponseData](
            max_retries=self._request_config["max_retries"],
            initial_delay_seconds=self._request_config["initial_delay_seconds"],
            max_delay=self._request_config["max_delay"],
            backoff_factor=self._request_config["backoff_factor"],
            jitter=self._request_config["jitter"],
            exceptions=(
                httpx.ConnectError,
                httpx.TimeoutException,
            ),
        )

        return await retry_strategy.execute(
            self._send_request,
            method=method,
            url=url,
            request_headers=headers,
            request_body=data,
            timeout_seconds=self._request_config["timeout_seconds"],
        )

    async def _send_request(
        self,
        method: HttpMethod,
        url: URL,
        request_headers: SecretHeaders,
        request_body: str | None = None,
        timeout_seconds: int | None = None,
    ) -> HttpResponseData:
        """Asynchronous request sending method

        .. note::

            Callbacks registered for before_request or after_request may be rate limiters.
            Therefore, they may intentionally raise exceptions during callback execution.
        """
        logger.debug(
            "Sending %s request to %s with headers: %s and data: %s",
            method,
            url,
            request_headers,  # Masked by SecretHeaders.__str__
            request_body,
        )
        await self.run_callbacks("before_request", url, request_headers, request_body)

        # Use httpx client (supports connection pooling)
        if self._http_client:
            client = self._http_client
            close_client = False
        else:
            # Create default client (first time only)
            if not hasattr(self, "_default_client") or self._default_client is None:
                self._default_client = httpx.AsyncClient()
            client = self._default_client
            close_client = False  # Close explicitly in close method

        httpx_headers = request_headers.to_httpx_headers()

        try:
            if method == HttpMethod.GET:
                res = await client.get(
                    str(url), headers=httpx_headers, timeout=timeout_seconds
                )
            elif method == HttpMethod.POST:
                res = await client.post(
                    str(url),
                    headers=httpx_headers,
                    content=request_body,
                    timeout=timeout_seconds,
                )
            else:
                msg = f"Unsupported HTTP method: {method}. Only HttpMethod.GET and HttpMethod.POST are supported."
                raise ValueError(msg)

            response_data = self.to_http_response_data(res)

            logger.debug("Received response: %s", response_data)

            # Callbacks that throw exceptions (e.g., rate limit checkers) may be registered for after_request.
            # Therefore, we wrap with try-finally to ensure client is closed even if exception occurs.
            await self.run_callbacks("after_request", response_data)

            return response_data
        finally:
            if close_client:
                await client.aclose()

    @staticmethod
    def to_http_response_data(res: httpx.Response) -> HttpResponseData:
        """Convert httpx.Response to HttpResponseData

        :param res: httpx response object
        :type res: httpx.Response
        :return: HttpResponseData Pydantic model (type validated)
        :rtype: HttpResponseData

        .. note::
            Status codes are stored as int type and support both standard HTTP status codes
            (200, 404, etc.) and non-standard codes (CloudFlare 520-527, nginx 499, etc.).

        .. versionchanged:: 1.0.0
            Removed conversion to HTTPStatus enum and changed to use int type directly.
        """
        # Use HTTP status code as int type directly
        http_status_code = res.status_code
        if http_status_code >= 600 or http_status_code < 100:
            logger.debug(f"Unusual HTTP status code: {http_status_code}")

        return HttpResponseData(
            http_status_code=http_status_code,
            # Convert httpx.Headers to dict
            # Important: httpx normalizes HTTP header names to lowercase
            # Example: "X-RateLimit-Remaining" -> "x-ratelimit-remaining"
            headers=dict(res.headers),
            response_body_text=res.text,
            response_body_bytes=res.content,
            url=str(res.url),
            reason=res.reason_phrase,
            elapsed=res.elapsed,
            cookies=dict(res.cookies),
            encoding=res.encoding,
            request_method=str(res.request.method) if res.request else "",
            request_url=str(res.request.url) if res.request else "",
            request_path=str(res.request.url.path) if res.request else "",
        )

    async def send_endpoint_request(self, request: EndpointRequest) -> HttpResponseData:
        """Send EndpointRequest asynchronously

        :param request: EndpointRequest (including base_url)
        :type request: EndpointRequest
        :return: HttpResponseData
        :rtype: HttpResponseData
        """
        return await self.send_request(
            method=request.method,
            url=request.api_endpoint,
            headers=request.headers,
            data=request.body_json,
        )

    async def close(self) -> None:
        """Close HTTP client

        - If custom HTTP client is provided: Do nothing (managed externally)
        - If using default client: Close it

        .. warning::

            When using default client, user must explicitly call close() method
        """
        # Don't close externally provided client
        if self._external_client:
            return

        # Close default client
        if hasattr(self, "_default_client") and self._default_client is not None:
            await self._default_client.aclose()
            self._default_client = None

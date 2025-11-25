"""HTTP status code constants and helper functions"""

from __future__ import annotations

from typing import Final


class HttpStatusCode:
    """HTTP status code constants class

    Defines standard and non-standard HTTP status codes,
    and provides helper methods for classifying and validating status codes.

    Why define a custom class:
    --------------------------
    Python's standard library `http.HTTPStatus` only supports standard HTTP status codes
    and does not handle non-standard codes encountered in actual web services.

    Cryptocurrency exchange APIs pass through various infrastructures (CloudFlare, nginx, AWS ELB, etc.)
    and may return non-standard status codes such as:

    - CloudFlare 520-527: Origin server errors, SSL certificate errors, etc.
    - nginx 499: Client closed connection
    - AWS ELB 460, 463: Timeout, rate limiting
    - Custom status codes: Exchange-specific implementations
    - New HTTP status codes added in the future

    To properly handle these non-standard codes, we define a custom class with the following features:

    1. Define both standard and non-standard status codes as constants
    2. Classification methods for status codes (is_success, is_error, etc.)
    3. Judgment methods dedicated to non-standard codes (is_cloudflare_error, etc.)
    4. Provide reason phrases for all codes

    This improves error handling precision and debugging efficiency.
    """

    # 1xx Informational
    CONTINUE: Final[int] = 100
    SWITCHING_PROTOCOLS: Final[int] = 101
    PROCESSING: Final[int] = 102

    # 2xx Success
    OK: Final[int] = 200
    CREATED: Final[int] = 201
    ACCEPTED: Final[int] = 202
    NON_AUTHORITATIVE_INFORMATION: Final[int] = 203
    NO_CONTENT: Final[int] = 204
    RESET_CONTENT: Final[int] = 205
    PARTIAL_CONTENT: Final[int] = 206

    # 3xx Redirection
    MULTIPLE_CHOICES: Final[int] = 300
    MOVED_PERMANENTLY: Final[int] = 301
    FOUND: Final[int] = 302
    SEE_OTHER: Final[int] = 303
    NOT_MODIFIED: Final[int] = 304
    USE_PROXY: Final[int] = 305
    TEMPORARY_REDIRECT: Final[int] = 307
    PERMANENT_REDIRECT: Final[int] = 308

    # 4xx Client Error
    BAD_REQUEST: Final[int] = 400
    UNAUTHORIZED: Final[int] = 401
    PAYMENT_REQUIRED: Final[int] = 402
    FORBIDDEN: Final[int] = 403
    NOT_FOUND: Final[int] = 404
    METHOD_NOT_ALLOWED: Final[int] = 405
    NOT_ACCEPTABLE: Final[int] = 406
    PROXY_AUTHENTICATION_REQUIRED: Final[int] = 407
    REQUEST_TIMEOUT: Final[int] = 408
    CONFLICT: Final[int] = 409
    GONE: Final[int] = 410
    LENGTH_REQUIRED: Final[int] = 411
    PRECONDITION_FAILED: Final[int] = 412
    REQUEST_ENTITY_TOO_LARGE: Final[int] = 413
    REQUEST_URI_TOO_LONG: Final[int] = 414
    UNSUPPORTED_MEDIA_TYPE: Final[int] = 415
    REQUESTED_RANGE_NOT_SATISFIABLE: Final[int] = 416
    EXPECTATION_FAILED: Final[int] = 417
    IM_A_TEAPOT: Final[int] = 418  # RFC 2324
    UNPROCESSABLE_ENTITY: Final[int] = 422
    LOCKED: Final[int] = 423
    FAILED_DEPENDENCY: Final[int] = 424
    TOO_EARLY: Final[int] = 425
    UPGRADE_REQUIRED: Final[int] = 426
    PRECONDITION_REQUIRED: Final[int] = 428
    TOO_MANY_REQUESTS: Final[int] = 429
    REQUEST_HEADER_FIELDS_TOO_LARGE: Final[int] = 431
    UNAVAILABLE_FOR_LEGAL_REASONS: Final[int] = 451

    # 5xx Server Error
    INTERNAL_SERVER_ERROR: Final[int] = 500
    NOT_IMPLEMENTED: Final[int] = 501
    BAD_GATEWAY: Final[int] = 502
    SERVICE_UNAVAILABLE: Final[int] = 503
    GATEWAY_TIMEOUT: Final[int] = 504
    HTTP_VERSION_NOT_SUPPORTED: Final[int] = 505
    VARIANT_ALSO_NEGOTIATES: Final[int] = 506
    INSUFFICIENT_STORAGE: Final[int] = 507
    LOOP_DETECTED: Final[int] = 508
    NOT_EXTENDED: Final[int] = 510
    NETWORK_AUTHENTICATION_REQUIRED: Final[int] = 511

    # Non-standard CloudFlare
    CLOUDFLARE_UNKNOWN_ERROR: Final[int] = 520
    CLOUDFLARE_WEB_SERVER_IS_DOWN: Final[int] = 521
    CLOUDFLARE_CONNECTION_TIMED_OUT: Final[int] = 522
    CLOUDFLARE_ORIGIN_IS_UNREACHABLE: Final[int] = 523
    CLOUDFLARE_TIMEOUT_OCCURRED: Final[int] = 524
    CLOUDFLARE_SSL_HANDSHAKE_FAILED: Final[int] = 525
    CLOUDFLARE_INVALID_SSL_CERTIFICATE: Final[int] = 526
    CLOUDFLARE_RAILGUN_ERROR: Final[int] = 527

    # Non-standard nginx
    NGINX_CLIENT_CLOSED_REQUEST: Final[int] = 499

    # Non-standard AWS ELB
    AWS_ELB_TIMEOUT: Final[int] = 460
    AWS_ELB_TOO_MANY_REQUESTS: Final[int] = 463

    @classmethod
    def is_success(cls, code: int) -> bool:
        """Check if status is 2xx Success response"""
        return 200 <= code < 300

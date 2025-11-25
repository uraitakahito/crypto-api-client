Glossary
========

This glossary defines terminology used within the context of this library.

.. glossary::


    action name
        A part of the :term:`resource path` that represents a specific operation or action. Typically follows the :term:`resource identifier path`.

    API endpoint
        The complete URL of an API.
        Composed of :term:`base URL` + :term:`endpoint path`.

        Example: `https://api.bitbank.cc/v1/user/assets`

        **Hierarchical structure**::

            API endpoint composition:
              base URL (https://api.bitbank.cc)
              + endpoint path (/v1/user/assets)
                = stub path (/v1)
                + resource path (/user/assets)
                  = resource identifier path (/user)
                  + action name (assets)

    api status code
        A status code uniquely defined by each exchange.

    base currency
        The base currency in a trading pair. The currency being bought or sold.

    base endpoint
        The base URL for API access. Composed of :term:`base URL` + :term:`stub path`.

        Example: `https://api.bitbank.cc/v1`

    base URL
        The combination of scheme `https://` and hostname.

        Example: `https://api.bitbank.cc`

    currency pair
        A tradable currency combination on an exchange.
        Typically, the part before "_" is the :term:`base currency`, and the part after is the :term:`quote currency`.

        Example: `BTC_JPY`, `ETH_JPY`

    endpoint path
        A :term:`relative endpoint path` prefixed with a forward slash.

    endpoint request
        A generic model representing an HTTP request to an :term:`API endpoint`. Contains all necessary information to send to the :term:`API endpoint`.
        Adds authentication info, :term:`base endpoint`, and `Content-Type` information to a :term:`native request`.

    http response data
        A model representing HTTP response data. Includes HTTP status code, headers, body, etc.

    native domain model
        Represents the entity returned by an :term:`API endpoint`.
        Defined in `src/crypto_api_client/<exchange_name>/native_domain_models/*.py`.
        When :term:`native message metadata` does not exist, it matches the :term:`native message payload`. For multiple items, a list of :term:`native domain model` matches the :term:`native message payload`.

    native message
        Represents the result of a :term:`native request` to an individual exchange.
        Implemented in `src/crypto-api-client/<exchange_name>/_native_messages/*.py`.

        Native messages may be divided into :term:`native message metadata` and :term:`native message payload`. Examples: bitbank / GMO Coin

        Native messages only hold the JSON text before parsing metadata and payload, and do not concern themselves with JSON structure.

        **metadata and payload implementation:**

        ``metadata`` and ``payload`` are implemented with ``@cached_property`` and are generated on first access.
        Subsequent accesses return the same cached object.

        .. seealso::

            - :class:`~crypto_api_client._base.Message` - Base class implementation

    native message metadata
        The metadata portion of a :term:`native message`. May not exist depending on the :term:`API endpoint`.

        **bitFlyer Ticker example** (no metadata, returns data directly):

        .. code-block:: json

            {
                "product_code": "BTC_JPY",
                "state": "RUNNING",
                "timestamp": "2015-07-08T02:50:59.97",
                "tick_id": 3579,
                "best_bid": 30000,
                "best_ask": 36640,
                "best_bid_size": 0.1,
                "best_ask_size": 5,
                "total_bid_depth": 15.13,
                "total_ask_depth": 20,
                "market_bid_size": 0,
                "market_ask_size": 0,
                "ltp": 31690,
                "volume": 16819.26,
                "volume_by_product": 6819.26
            }

        **bitbank Ticker example** (with metadata):

        .. code-block:: json

            {
                "success": 1,
                "data": {
                    "sell": "string",
                    "buy": "string",
                    "high": "string",
                    "low": "string",
                    "open": "string",
                    "last": "string",
                    "vol": "string",
                    "timestamp": 0
                }
            }

        In this example, bitbank's ``success`` field corresponds to :term:`native message metadata`. The metadata format varies by exchange.

    native message payload
        The payload portion of a :term:`native message`. May not exist depending on the :term:`API endpoint`.

        **bitbank Ticker example**:

        .. code-block:: json

            {
                "success": 1,
                "data": {
                    "sell": "string",
                    "buy": "string",
                    "high": "string",
                    "low": "string",
                    "open": "string",
                    "last": "string",
                    "vol": "string",
                    "timestamp": 0
                }
            }

        In this example, the following string corresponds to :term:`native message payload`:

        .. code-block:: json

            "data": {
                "sell": "string",
                "buy": "string",
                "high": "string",
                "low": "string",
                "open": "string",
                "last": "string",
                "vol": "string",
                "timestamp": 0
            }

        The responsibility of passing the string corresponding to the native message payload to the payload model lies with the native message model.
        Additionally, the following part is called :term:`payload content`:

        .. code-block:: json

            {
                "sell": "string",
                "buy": "string",
                "high": "string",
                "low": "string",
                "open": "string",
                "last": "string",
                "vol": "string",
                "timestamp": 0
            }

        Because the structure of payload content varies even within the same exchange, the :term:`native message payload` model is responsible for determining what constitutes content.

    native request
        A model representing a request to an individual exchange's :term:`API endpoint`. Represents events such as orders and cancellations.
        Implemented in `src/crypto-api-client/<exchange_name>/native_requests/*.py`.

    payload content
        The substantial data portion of a :term:`native message payload`.

        Refers to the JSON string of entity data, excluding keys and extra structure, from the raw JSON string held by the payload.
        Retrieved via the payload class's ``content_str`` property.

        Depending on implementation, it may return raw JSON as-is (bitFlyer, BINANCE) or process it (bitbank, GMO Coin).

        **bitbank Ticker example:**

        Full Native Message:

        .. code-block:: json

            {
                "success": 1,
                "data": {
                    "sell": "15350001",
                    "buy": "15350000",
                    "last": "15350001",
                    "vol": "273.5234",
                    "timestamp": 1748558090326
                }
            }

        Native Message Payload (raw JSON string of data portion):

        .. code-block:: json

            "data": {
                "sell": "15350001",
                "buy": "15350000",
                "last": "15350001",
                "vol": "273.5234",
                "timestamp": 1748558090326
            }

        Payload Content (entity data returned by ``content_str``):

        .. code-block:: json

            {
                "sell": "15350001",
                "buy": "15350000",
                "last": "15350001",
                "vol": "273.5234",
                "timestamp": 1748558090326
            }

        **bitFlyer Ticker example (no processing):**

        For bitFlyer, Native Message Payload and Payload Content are identical:

        .. code-block:: json

            {
                "product_code": "BTC_JPY",
                "timestamp": "2015-07-08T02:50:59.97",
                "best_bid": 30000,
                "best_ask": 36640,
                "ltp": 31690
            }

    product code
        A code identifying a specific currency pair tradable on bitFlyer. Typically composed of uppercase letters and underscores.

        Example: `BTC_JPY`, `ETH_JPY`

    quote currency
        The currency representing the price of the :term:`base currency`. The price per unit of base currency is displayed in quote currency.

    relative endpoint path
        The portion of an :term:`API endpoint` excluding :term:`base URL` and root path.
        Composed of :term:`relative stub path` + :term:`relative resource path`.

        Example: `v1/user/assets`

        A :term:`relative endpoint path` prefixed with a forward slash is called :term:`endpoint path`.

    relative resource identifier path
        A string uniquely identifying a :term:`Resource`. Typically represents the type or attributes of a specific :term:`Resource`.

        Example: ``btc_jpy`` in bitbank's `https://public.bitbank.cc/btc_jpy/ticker`

        A :term:`relative resource identifier path` prefixed with a forward slash is called :term:`resource identifier path`.

    relative resource path
        A path for accessing a :term:`Resource`. Relative resource path is only responsible for the path portion. In other words, it does not include query strings.

        relative resource path = :term:`relative resource identifier path` + :term:`action name`. Some relative resource paths do not have an :term:`action name`.

        Examples:

        - bitbank
          - `btc_jpy/ticker` (full URL: https://public.bitbank.cc/btc_jpy/ticker)
            - :term:`relative resource identifier path`: ``btc_jpy`` (:term:`currency pair`)
            - Action name: ``ticker``
        - bitFlyer
          - `ticker` (full URL: https://api.bitflyer.jp/v1/ticker?product_code=btc_jpy)
          - `me/getbalance` (full URL: https://api.bitflyer.jp/v1/me/getbalance)
            - :term:`relative resource identifier path`: ``me`` (:term:`Resource` identifier)
            - Action name: ``getbalance``

        A :term:`relative resource path` prefixed with a forward slash is called :term:`resource path`.

    relative stub path
        A path portion typically representing a version number. For example, if the :term:`base endpoint` URL is `https://api.bitbank.cc/v1`, the relative stub path is `v1`. Some :term:`API endpoint` do not have a stub path.

        Example: `v1`

        A :term:`relative stub path` prefixed with a forward slash is called :term:`stub path`.

    request model
        A model for representing requests to an :term:`API endpoint`. Defines request parameters and structure.

        Classes defined in `src/crypto_api_client/<exchange_name>/native_requests/*.py`.

    Resource
        Persistent data/objects. Has state. Distinguish between Event and :term:`Resource`.

    resource identifier path
        A :term:`relative resource identifier path` prefixed with a forward slash.

    resource path
        A :term:`relative resource path` prefixed with a forward slash.

    response validator
        Responsible for validating :term:`http response data` returned by an :term:`API endpoint` and raising exceptions when errors occur.

        .. seealso::
            - :class:`~crypto_api_client._base.response_validator_protocol.ResponseValidatorProtocol`
            - :func:`~crypto_api_client.factories.create_response_validator`
            - :class:`~crypto_api_client.callbacks.ResponseValidationCallback`

    stub path
        A :term:`relative stub path` prefixed with a forward slash.

        Example: `/v1`

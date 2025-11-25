External API References
=======================

This page provides links to the official API documentation for each cryptocurrency exchange supported by crypto-api-client.

.. contents:: Table of Contents
   :local:
   :depth: 2

BINANCE
-------

REST API
~~~~~~~~

* `Exchange information <https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#exchange-information>`__

* `Market Data endpoints <https://developers.binance.com/docs/binance-spot-api-docs/testnet/rest-api/market-data-endpoints>`__

  - order book (depth)

* `Get Account Asset Balance <https://lightning.bitflyer.com/docs?lang=en#get-account-asset-balance>`__

* `Trade History <https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api.md#trade>`__

bitbank
-------

* `Pairs <https://raw.githubusercontent.com/bitbankinc/bitbank-api-docs/refs/heads/master/pairs.md>`__

* `Details on the Private REST API <https://raw.githubusercontent.com/bitbankinc/bitbank-api-docs/refs/heads/master/rest-api.md>`__

  - Status

* `Assets <https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api.md#assets>`__

* `Get all pairs info <https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api.md#get-all-pairs-info>`__


bitFlyer
--------

REST API
~~~~~~~~

* `Orderbook Status <https://lightning.bitflyer.com/docs?lang=en#orderbook-status>`__

* `Exchange Status <https://lightning.bitflyer.com/docs?lang=en#exchange-status>`__

* `Error Code List (Unofficial) <https://note.com/17num/n/n6955c3a711a8>`__

Coincheck
---------

* `Ticker <https://coincheck.com/documents/exchange/api#ticker>`__

* `Order Book <https://coincheck.com/documents/exchange/api#order-book>`__

* `Unsettled Order List <https://coincheck.com/documents/exchange/api#order-opens>`__

* `Balance <https://coincheck.com/documents/exchange/api#account-balance>`__


GMO Coin
--------

* `Order Book <https://api.coin.z.com/docs/#orderbooks>`__

Upbit
-----

* `List Tickers by Pairs <https://global-docs.upbit.com/reference/list-tickers>`__

* `List Tickers by Market <https://global-docs.upbit.com/reference/list-quote-tickers>`__

* `Get Orderbook <https://global-docs.upbit.com/reference/list-orderbooks>`__


Rate Limits
-----------

Each exchange has its own rate limits:

- **BINANCE**: Weight-based limits (varies by endpoint)
- **bitFlyer**: 300 requests/minute (Private API), 500 requests/minute (Public API)
- **bitbank**: Refer to official documentation for details
- **GMO Coin**: Up to 10 requests per second

Development References
----------------------

Authentication Methods Comparison
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Authentication Methods by Exchange
   :header-rows: 1
   :widths: 20 40 40

   * - Exchange
     - Authentication Method
     - Notes
   * - BINANCE
     - HMAC-SHA256
     - Timestamp and recvWindow parameters required
   * - bitFlyer
     - HMAC-SHA256
     - ACCESS-TIMESTAMP, ACCESS-SIGN, ACCESS-KEY headers required
   * - bitbank
     - HMAC-SHA256
     - Nonce parameter required
   * - GMO Coin
     - HMAC-SHA256
     - Timestamp and path included in signature

from __future__ import annotations

from crypto_api_client.callbacks import AbstractRequestCallback
from crypto_api_client.core.exchange_types import Exchange


def create_response_validator(exchange: Exchange) -> AbstractRequestCallback:
    """Generate :term:`response validator` for the specified exchange

    Each validator inherits from :class:`~crypto_api_client.callbacks.AbstractRequestCallback`
    and performs response validation in after_request().

    Generates and returns an instance of ResponseValidator corresponding to the exchange.

    :param exchange: Exchange identifier
    :type exchange: Exchange
    :return: Exchange-specific ResponseValidator instance
    :rtype: AbstractRequestCallback

    .. code-block:: python

        from crypto_api_client.factories import create_response_validator
        from crypto_api_client.core.exchange_types import Exchange
        from crypto_api_client import create_session

        # Get validator for bitFlyer
        validator = create_response_validator(Exchange.BITFLYER)

        # Pass directly to session (ResponseValidationCallback is not needed)
        async with create_session(
            Exchange.BITFLYER,
            callbacks=(validator,)
        ) as session:
            ticker = await session.api.ticker(request)

    .. seealso::

        - :class:`~crypto_api_client.callbacks.AbstractRequestCallback`
        - :func:`~crypto_api_client.session_factory.create_session`
    """
    # Load registry lazily inside function to avoid circular imports
    from crypto_api_client.binance.binance_response_validator import (
        BinanceResponseValidator,
    )
    from crypto_api_client.bitbank.bitbank_response_validator import (
        BitbankResponseValidator,
    )
    from crypto_api_client.bitflyer.bitflyer_response_validator import (
        BitFlyerResponseValidator,
    )
    from crypto_api_client.coincheck.coincheck_response_validator import (
        CoincheckResponseValidator,
    )
    from crypto_api_client.gmocoin.gmocoin_response_validator import (
        GmoCoinResponseValidator,
    )
    from crypto_api_client.upbit.upbit_response_validator import (
        UpbitResponseValidator,
    )

    _response_validator_registry: dict[Exchange, type[AbstractRequestCallback]] = {
        Exchange.BINANCE: BinanceResponseValidator,
        Exchange.BITBANK: BitbankResponseValidator,
        Exchange.BITFLYER: BitFlyerResponseValidator,
        Exchange.COINCHECK: CoincheckResponseValidator,
        Exchange.GMOCOIN: GmoCoinResponseValidator,
        Exchange.UPBIT: UpbitResponseValidator,
    }

    validator_class = _response_validator_registry.get(exchange)
    if validator_class is None:
        raise ValueError(f"Unsupported exchange: {exchange}")

    return validator_class()

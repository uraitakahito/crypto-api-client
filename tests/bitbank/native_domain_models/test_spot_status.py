"""SpotStatus/PairStatus Domain Model tests"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from crypto_api_client.bitbank.native_domain_models import (
    PairStatus,
    SpotStatus,
    SpotStatusType,
)


class TestPairStatus:
    """PairStatus model tests"""

    def test_valid_pair_status(self) -> None:
        """Normal case: Generate PairStatus with valid data"""
        pair_status = PairStatus(
            pair="btc_jpy",
            status=SpotStatusType.NORMAL,
            min_amount=Decimal("0.0001"),
        )

        assert pair_status.pair == "btc_jpy"
        assert pair_status.status == SpotStatusType.NORMAL
        assert pair_status.min_amount == Decimal("0.0001")

    def test_pair_status_frozen(self) -> None:
        """PairStatus is immutable"""
        pair_status = PairStatus(
            pair="btc_jpy",
            status=SpotStatusType.NORMAL,
            min_amount=Decimal("0.0001"),
        )

        with pytest.raises(ValidationError):
            pair_status.status = SpotStatusType.BUSY  # type: ignore[misc]

    def test_pair_status_with_all_status_types(self) -> None:
        """Works correctly with all status types"""
        for status in SpotStatusType:
            pair_status = PairStatus(
                pair="btc_jpy",
                status=status,
                min_amount=Decimal("0.0001"),
            )
            assert pair_status.status == status

    def test_pair_status_decimal_precision(self) -> None:
        """Decimal precision of min_amount is preserved"""
        pair_status = PairStatus(
            pair="btc_jpy",
            status=SpotStatusType.NORMAL,
            min_amount=Decimal("0.00010000"),
        )

        # Verify precision is preserved
        assert pair_status.min_amount == Decimal("0.00010000")
        assert str(pair_status.min_amount) == "0.00010000"


class TestSpotStatus:
    """SpotStatus model tests"""

    def test_valid_spot_status(self) -> None:
        """Normal case: SpotStatus with multiple PairStatus"""
        pair_statuses = [
            PairStatus(
                pair="btc_jpy",
                status=SpotStatusType.NORMAL,
                min_amount=Decimal("0.0001"),
            ),
            PairStatus(
                pair="eth_jpy",
                status=SpotStatusType.BUSY,
                min_amount=Decimal("0.001"),
            ),
        ]

        spot_status = SpotStatus(statuses=pair_statuses)

        assert len(spot_status.statuses) == 2
        assert spot_status.statuses[0].pair == "btc_jpy"
        assert spot_status.statuses[1].pair == "eth_jpy"

    def test_empty_statuses_list(self) -> None:
        """Empty statuses list is allowed"""
        spot_status = SpotStatus(statuses=[])
        assert len(spot_status.statuses) == 0

    def test_spot_status_frozen(self) -> None:
        """SpotStatus is immutable"""
        spot_status = SpotStatus(statuses=[])

        with pytest.raises(ValidationError):
            spot_status.statuses = []  # type: ignore[misc]

    def test_spot_status_with_multiple_pairs(self) -> None:
        """SpotStatus with many currency pairs"""
        pair_statuses = [
            PairStatus(
                pair=f"pair_{i}",
                status=SpotStatusType.NORMAL,
                min_amount=Decimal("0.0001"),
            )
            for i in range(10)
        ]

        spot_status = SpotStatus(statuses=pair_statuses)
        assert len(spot_status.statuses) == 10

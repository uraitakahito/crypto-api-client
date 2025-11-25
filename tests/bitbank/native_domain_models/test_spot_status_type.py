"""SpotStatusType Enum tests"""

import pytest

from crypto_api_client.bitbank.native_domain_models.spot_status_type import (
    SpotStatusType,
)


class TestSpotStatusType:
    """Verify SpotStatusType Enum behavior"""

    def test_all_status_values(self) -> None:
        """All status values are defined"""
        assert SpotStatusType.NORMAL == "NORMAL"
        assert SpotStatusType.BUSY == "BUSY"
        assert SpotStatusType.VERY_BUSY == "VERY_BUSY"
        assert SpotStatusType.HALT == "HALT"

    def test_enum_membership(self) -> None:
        """Convert from string to Enum"""
        assert SpotStatusType("NORMAL") == SpotStatusType.NORMAL
        assert SpotStatusType("BUSY") == SpotStatusType.BUSY
        assert SpotStatusType("VERY_BUSY") == SpotStatusType.VERY_BUSY
        assert SpotStatusType("HALT") == SpotStatusType.HALT

    def test_invalid_status(self) -> None:
        """Error occurs for invalid status value"""
        with pytest.raises(ValueError):
            SpotStatusType("INVALID")

    def test_enum_iteration(self) -> None:
        """All Enum elements can be retrieved"""
        all_statuses = list(SpotStatusType)
        assert len(all_statuses) == 4
        assert SpotStatusType.NORMAL in all_statuses
        assert SpotStatusType.BUSY in all_statuses
        assert SpotStatusType.VERY_BUSY in all_statuses
        assert SpotStatusType.HALT in all_statuses

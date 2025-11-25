"""SpotStatusRequest tests"""

import pytest
from pydantic import ValidationError

from crypto_api_client.bitbank.native_requests.spot_status_request import (
    SpotStatusRequest,
)


class TestSpotStatusRequest:
    """Verify SpotStatusRequest behavior"""

    def test_to_query_params_empty(self) -> None:
        """Generate request without parameters"""
        request = SpotStatusRequest()
        params = request.to_query_params()

        assert params == {}
        assert isinstance(params, dict)

    def test_request_is_frozen(self) -> None:
        """Request is immutable"""
        request = SpotStatusRequest()

        # Assignment to attributes fails because it's frozen
        with pytest.raises(ValidationError):
            request.new_field = "value"  # type: ignore[attr-defined]

    def test_multiple_instances_are_equal(self) -> None:
        """Multiple instances are equal"""
        request1 = SpotStatusRequest()
        request2 = SpotStatusRequest()

        assert request1 == request2

    def test_request_has_model_config(self) -> None:
        """model_config is correctly set"""
        request = SpotStatusRequest()

        # Verify frozen is set
        assert request.model_config.get("frozen") is True

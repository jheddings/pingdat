"""Additional tests for ping targets."""

import pytest
from ping3.errors import PingError

from pingdat import PingTarget

VALID_TARGETS = [
    "1.1.1.1",
    "8.8.8.8",
]

INVALID_TARGETS = [
    "bad.host",
    "6.7",
    "256.256.256.256",
    "-1",
]


@pytest.mark.network
@pytest.mark.parametrize("address", VALID_TARGETS)
def test_ping_valid_target(address):
    """Verify ping works to valid targets."""

    target = PingTarget(name="ping::valid::" + address, address=address)

    delay = target.one_ping_only()

    assert delay > 0


@pytest.mark.network
@pytest.mark.parametrize("address", INVALID_TARGETS)
def test_ping_invalid_target(address):
    """Verify that invalid hosts are handled properly."""

    target = PingTarget(name="ping::invalid::" + address, address=address)

    with pytest.raises(PingError):
        target.one_ping_only()

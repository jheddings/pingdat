"""Additional tests for ping targets."""

import pytest
from ping3.errors import PingError

from pingdat import PingTarget


def test_bad_hostname():
    """Verify that invalid hosts are handled properly."""

    target = PingTarget(name="ping::invalid", address="-1")

    with pytest.raises(PingError):
        target.one_ping_only()

"""Additional tests for ping targets."""

import pytest
from ping3.errors import PingError

from pingdat import PingTarget


@pytest.mark.network
def test_ping_google():
    """Verify ping works to Google DNS."""

    target = PingTarget(name="ping::google", address="8.8.8.8")

    delay = target.one_ping_only()

    assert delay > 0


@pytest.mark.network
def test_ping_cloudflare():
    """Verify ping works to CloudFlare."""

    target = PingTarget(name="ping::cloudflare", address="1.1.1.1")

    delay = target.one_ping_only()

    assert delay > 0


@pytest.mark.network
def test_bad_hostname():
    """Verify that invalid hosts are handled properly."""

    target = PingTarget(name="ping::invalid", address="-1")

    with pytest.raises(PingError):
        target.one_ping_only()

"""Verify pingdat using localhost."""

from pingdat import PingTarget


def test_basic_ping():
    target = PingTarget(name="ping::localhost", address="localhost", interval=0)

    delay = target()

    assert delay is not None
    assert delay is not False
    assert delay < 1

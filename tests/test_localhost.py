"""Verify pingdat using localhost."""

from time import sleep

import pytest

from pingdat import PingTarget


@pytest.fixture(scope="function")
def localhost():
    """Create a PingTarget for localhost."""

    target = PingTarget(name="ping::localhost", address="localhost", interval=1)

    target.start()

    yield target

    target.stop()


def test_basic_ping(localhost: PingTarget):
    """Verify that a basic ping works."""

    # give me a ping, Vasili
    delay = localhost()

    assert delay is not None
    assert delay is not False
    assert delay < 1


def test_ping_thread(localhost: PingTarget):
    """Verify that the ping thread is running."""

    # this is kind of a hack to get number of requests, but it works
    starting_count = localhost.metrics.requests._value.get()

    # one ping only, please
    sleep(0.25)

    final_count = localhost.metrics.requests._value.get()

    # since the metrics may be altered by other tests,
    # we need to compare the starting and ending counts
    assert final_count > starting_count

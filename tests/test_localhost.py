"""Verify pingdat using localhost."""

from time import sleep

import pytest

from pingdat import PingLoop, PingTarget


@pytest.fixture(scope="function")
def localhost():
    """Create a PingTarget for localhost."""

    yield PingTarget(name="ping::localhost", address="localhost")


@pytest.fixture(scope="function")
def loop(localhost: PingTarget):
    """Create a PingLoop for localhost."""

    loop = PingLoop(target=localhost, interval=1)

    loop.start()

    yield loop

    loop.stop()


@pytest.mark.network
def test_basic_ping(localhost: PingTarget):
    """Verify that a basic ping works."""

    # give me a ping, Vasili
    delay = localhost.one_ping_only()

    assert delay is not None
    assert delay is not False
    assert delay > 0


@pytest.mark.network
def test_ping_thread(loop: PingLoop):
    """Verify that the ping thread is running."""

    localhost = loop.target

    # this is kind of a hack to get number of requests, but it works
    starting_count = localhost.metrics.requests._value.get()

    # allow a single ping
    sleep(loop.interval.total_seconds())

    final_count = localhost.metrics.requests._value.get()

    # since the metrics may be altered by other tests,
    # we need to compare the starting and ending counts
    assert final_count > starting_count

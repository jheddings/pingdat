"""Module interface to pingstat."""

import logging
import threading
from datetime import datetime, timedelta

from ping3 import ping
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

TOTAL_REQUESTS_METRICS = Counter(
    "ping_total_requests",
    "Total ping requests sent",
    labelnames=["name", "address"],
)

TOTAL_RESPONSES_METRICS = Counter(
    "ping_total_responses",
    "Total ping responses received",
    labelnames=["name", "address"],
)

RESPONSE_ERROR_METRICS = Counter(
    "ping_response_errors",
    "Total ping errors",
    labelnames=["name", "address"],
)

PING_TIMEOUT_METRICS = Counter(
    "ping_timeouts",
    "Total ping timeouts",
    labelnames=["name", "address"],
)

RESPONSE_TIME_METRICS = Gauge(
    "ping_reponse_time",
    "Most recent ping delay",
    labelnames=["name", "address"],
)

RESPONSE_OBSERVATIONS = Histogram(
    "ping_observations",
    "Histogram of all ping responses",
    labelnames=["name", "address"],
)


class PingMetrics:
    def __init__(self, **kwargs):
        """Initialize a set of labeled metrics for the given args."""

        self.requests = TOTAL_REQUESTS_METRICS.labels(**kwargs)
        self.responses = TOTAL_RESPONSES_METRICS.labels(**kwargs)

        self.errors = RESPONSE_ERROR_METRICS.labels(**kwargs)
        self.timeouts = PING_TIMEOUT_METRICS.labels(**kwargs)

        self.response_time = RESPONSE_TIME_METRICS.labels(**kwargs)
        self.observations = RESPONSE_OBSERVATIONS.labels(**kwargs)


class PingTarget:

    __thread_count__ = 0

    def __init__(self, name, address, interval, timeout, payload_size=56, ttl=64):
        PingTarget.__thread_count__ += 1

        self.name = name
        self.address = address
        self.interval = interval
        self.timeout = timeout
        self.payload_size = payload_size
        self.ttl = ttl

        self.thread_ctl = threading.Event()
        self.loop_thread = threading.Thread(name=self.id, target=self.run_loop)
        self.loop_last_exec = None

        self.metrics = PingMetrics(name=name, address=address)

        self.logger = logger.getChild("PingTarget")

    @property
    def id(self) -> str:
        return f"{self.address}-{PingTarget.__thread_count__}"

    def start(self) -> None:
        """Start the main thread loop."""

        self.logger.debug("Starting ping thread")

        self.thread_ctl.clear()
        self.loop_thread.start()

    def stop(self) -> None:
        """Signal the thread to stop and wait for it to exit."""

        self.logger.debug("Stopping ping thread")

        self.thread_ctl.set()
        self.loop_thread.join(self.timeout)

        if self.loop_thread.is_alive():
            self.logger.warning("Thread failed to complete")

    def run_loop(self):
        """Manage the lifecycle of the thread loop."""

        self.logger.debug(
            "BEGIN -- %s :: run_loop @ %f sec", self.address, self.interval
        )

        while not self.thread_ctl.is_set():
            self.loop_last_exec = datetime.now()

            self()

            # figure out when to run the next step
            elapsed = (datetime.now() - self.loop_last_exec).total_seconds()
            next_loop_time = self.loop_last_exec + timedelta(seconds=self.interval)
            next_loop_sleep = (next_loop_time - datetime.now()).total_seconds()

            if next_loop_sleep <= 0:
                self.logger.warning("loop time exceeded interval; overflow")
                next_loop_sleep = 0

            self.logger.debug(
                "%s :: run_loop complete; %f sec elapsed (next_step: %f)",
                self.address,
                elapsed,
                next_loop_sleep,
            )

            # break if we are signaled to stop
            if self.thread_ctl.wait(next_loop_sleep):
                self.logger.debug("received exit signal; run_loop exiting")

        self.logger.debug("END -- %s :: run_loop", self.address)

    def __call__(self):
        """Ping the target and update metrics."""

        self.logger.info("PING -- %s @ %s", self.name, self.address)

        self.metrics.requests.inc()

        ret = ping(
            self.address,
            timeout=self.timeout,
            ttl=self.ttl,
            size=self.payload_size,
        )

        self.logger.debug("%s ==> %s", self.name, ret)

        if ret is None:
            self.metrics.timeouts.inc()

        elif ret is False:
            self.metrics.errors.inc()

        else:
            self.metrics.response_time.set(ret)
            self.metrics.observations.observe(ret)
            self.metrics.responses.inc()

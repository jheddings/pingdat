"""Module interface to pingdat."""

import logging
import threading
from datetime import datetime, timedelta

from ping3 import ping
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

METRICS_LABELS = ["name", "address"]

TOTAL_REQUESTS_METRICS = Counter(
    "ping_requests",
    "Total ping requests sent",
    labelnames=METRICS_LABELS,
)

TOTAL_RESPONSES_METRICS = Counter(
    "ping_responses",
    "Total ping responses received",
    labelnames=METRICS_LABELS,
)

RESPONSE_ERROR_METRICS = Counter(
    "ping_errors",
    "Total ping errors",
    labelnames=METRICS_LABELS,
)

PING_TIMEOUT_METRICS = Counter(
    "ping_timeouts",
    "Total ping timeouts",
    labelnames=METRICS_LABELS,
)

RESPONSE_TIME_METRICS = Gauge(
    "ping_reponse_time",
    "Most recent ping delay",
    labelnames=METRICS_LABELS,
)

RESPONSE_OBSERVATIONS = Histogram(
    "ping_observations",
    "Histogram of all ping responses",
    labelnames=METRICS_LABELS,
)


class PingMetrics:
    """Manage metrics for a specific PingTarget."""

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

    def __init__(self, name, address, interval, timeout=None, payload_size=56, ttl=64):
        PingTarget.__thread_count__ += 1

        self.name = name
        self.address = address
        self.timeout = timeout or interval / 2
        self.payload_size = payload_size
        self.ttl = ttl
        self.sequence = 0

        self.interval = timedelta(seconds=interval)

        self.thread_ctl = threading.Event()
        self.loop_thread = threading.Thread(name=self.id, target=self.ping_loop)
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

    def ping_loop(self):
        """Manage the lifecycle of the thread loop."""

        self.logger.debug("BEGIN -- %s :: ping_loop @ %s", self.address, self.interval)

        while not self.thread_ctl.is_set():
            self.loop_last_exec = datetime.now()

            self()

            # figure out when to run the next step
            next_loop_time = self.loop_last_exec + self.interval
            next_loop_sleep = (next_loop_time - datetime.now()).total_seconds()

            # watch for overflows (pings that take longer than the thread interval)
            if next_loop_sleep <= 0:
                self.logger.warning("ping time exceeded loop interval; overflow")
                next_loop_sleep = 0

            self.logger.debug(
                "%s :: ping loop complete; next_step: %f",
                self.address,
                next_loop_sleep,
            )

            # break if we are signaled to stop
            if self.thread_ctl.wait(next_loop_sleep):
                self.logger.debug("received exit signal; ping_loop exiting")

        self.logger.debug("END -- %s :: ping_loop", self.address)

    def __call__(self):
        """Ping the target and update metrics."""

        self.logger.info("PING -- %s @ %s [%d]", self.name, self.address, self.sequence)

        self.metrics.requests.inc()

        ret = ping(
            self.address,
            timeout=self.timeout,
            ttl=self.ttl,
            size=self.payload_size,
            seq=self.sequence,
        )

        self.logger.debug("%s ==> %s", self.name, ret)
        self.sequence += 1

        if ret is None:
            self.metrics.timeouts.inc()

        elif ret is False:
            self.metrics.errors.inc()

        else:
            self.metrics.response_time.set(ret)
            self.metrics.responses.inc()
            self.metrics.observations.observe(ret)

        return ret

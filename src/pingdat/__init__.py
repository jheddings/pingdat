"""Module interface to pingdat."""

import logging
import threading
from datetime import datetime, timedelta

import ping3
from ping3.errors import PingError, Timeout
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

ping3.EXCEPTIONS = True

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
    def __init__(
        self,
        name,
        address,
        ttl=64,
        count=3,
        timeout=3,
        payload_size=56,
    ):
        self.name = name
        self.address = address
        self.timeout = timeout
        self.payload_size = payload_size
        self.ttl = ttl
        self.count = count

        self.metrics = PingMetrics(name=name, address=address)
        self.logger = logger.getChild("PingTarget")

    def __call__(self):
        """Ping the target and update metrics."""
        self.logger.info("PING -- %s @ %s", self.name, self.address)

        # track the response times so we can average them later
        response_times = []

        for seq in range(0, self.count):
            try:
                delay = self.one_ping_only(seq)

                self.logger.debug("ping :: %s [%d] => %d sec", self.name, seq, delay)

                response_times.append(delay)

            except Timeout:
                self.logger.warning("ping timeout: %s", self.name)
                self.metrics.timeouts.inc()

                # add the timeout value to the response_times list
                response_times.append(self.timeout)

            except PingError as err:
                self.logger.error("ping error: %s => %s", self.name, err)
                self.metrics.errors.inc()

            except OSError as err:
                self.logger.error("network error: %s => %s", self.name, err)
                self.metrics.errors.inc()

        # calculate the average response time
        if len(response_times) > 0:
            avg = sum(response_times) / len(response_times)
            self.metrics.response_time.set(avg)

        # use a sentinel value to indicate no response
        else:
            self.metrics.response_time.set(-1)

    def one_ping_only(self, seq=0):
        """Ping the configured target with a given sequence number."""

        self.logger.debug("ping :: %s @ %s [%d]", self.name, self.address, seq)

        self.metrics.requests.inc()

        delay = ping3.ping(
            self.address,
            timeout=self.timeout,
            ttl=self.ttl,
            size=self.payload_size,
            seq=seq,
        )

        if delay is None:
            raise PingError("ping failed")

        self.metrics.responses.inc()
        self.metrics.observations.observe(delay)

        return delay


class PingLoop:

    __thread_count__ = 0

    def __init__(self, target: PingTarget, interval: int):
        PingLoop.__thread_count__ += 1

        self.target = target
        self.interval = timedelta(seconds=interval)

        self.thread_ctl = threading.Event()
        self.loop_thread = threading.Thread(name=self.id, target=self.ping_loop)
        self.loop_last_exec = None

        self.logger = logger.getChild("PingLoop")

    @property
    def id(self) -> str:
        return f"{self.target.address}-{PingLoop.__thread_count__}"

    def start(self) -> None:
        """Start the main thread loop."""

        self.logger.debug("Starting ping thread")

        self.thread_ctl.clear()
        self.loop_thread.start()

    def stop(self) -> None:
        """Signal the thread to stop and wait for it to exit."""

        timeout = self.interval.total_seconds() * 2
        self.logger.debug("Stopping ping thread [%s sec]", timeout)

        self.thread_ctl.set()
        self.loop_thread.join(timeout)

        if self.loop_thread.is_alive():
            self.logger.warning("Thread failed to complete")

    def ping_loop(self):
        """Manage the lifecycle of the thread loop."""

        self.logger.debug("BEGIN :: ping_loop @ %s sec", self.interval)

        while not self.thread_ctl.is_set():
            self.loop_last_exec = datetime.now()

            self.target()

            # figure out when to run the next step
            next_loop_time = self.loop_last_exec + self.interval
            next_loop_sleep = (next_loop_time - datetime.now()).total_seconds()

            # watch for overflows (pings that take longer than the thread interval)
            if next_loop_sleep <= 0:
                self.logger.warning("ping time exceeded loop interval; overflow")
                next_loop_sleep = 0

            self.logger.debug("ping complete; next_step: %f", next_loop_sleep)

            # break if we are signaled to stop
            if self.thread_ctl.wait(next_loop_sleep):
                self.logger.debug("received exit signal; ping_loop exiting")

        self.logger.debug("END :: ping_loop")

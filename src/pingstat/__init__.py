"""Module interface to pingstat."""

import logging
import threading
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PingTarget:

    __thread_count__ = 0

    def __init__(self, address, interval, timeout, name=None):
        PingTarget.__thread_count__ += 1

        self.address = address
        self.interval = interval
        self.timeout = timeout
        self.name = name

        self.thread_ctl = threading.Event()
        self.loop_thread = threading.Thread(name=self.id, target=self.run_loop)
        self.loop_last_exec = None

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

        self.logger.info("PING -- %s", self.address)

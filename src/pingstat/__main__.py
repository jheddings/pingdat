"""Main entry point for pingstat."""

import logging
import signal

import click
from prometheus_client import start_http_server

from . import PingTarget
from .config import AppConfig, MetricsConfig

logger = logging.getLogger(__name__)


class MainApp:
    """Context used during main execution."""

    def __init__(self, config: AppConfig):
        self.logger = logger.getChild("MainApp")

        self.config = config

        self._initialize_targets(config)
        self._initialize_metrics(config.metrics)

    def _initialize_targets(self, config: AppConfig):
        self.targets = []

        for target_config in config.targets:
            target = PingTarget(
                name=target_config.name,
                address=target_config.address,
                interval=target_config.interval or config.interval,
                timeout=target_config.timeout or config.timeout,
            )
            self.targets.append(target)

    def _initialize_metrics(self, config: MetricsConfig):
        start_http_server(config.port)

    def __call__(self):

        self.logger.debug("Starting main app")

        for obs in self.targets:
            obs.start()

        try:
            signal.pause()
        except KeyboardInterrupt:
            self.logger.debug("canceled by user")

        for obs in self.targets:
            obs.stop()


@click.command()
@click.option(
    "--config",
    "-f",
    default="pingstat.yaml",
    help="app config file (default: pingstat.yaml)",
)
def main(config):
    cfg = AppConfig.load(config)
    app = MainApp(cfg)

    # TODO allow simple options to be set from command line

    app()


### MAIN ENTRY
if __name__ == "__main__":
    main()

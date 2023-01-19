"""Main entry point for pingstat."""

import logging
import signal

import click

from .config import AppConfig

logger = logging.getLogger(__name__)


class MainApp:
    """Context used during main execution."""

    def __init__(self, config: AppConfig):
        self.logger = logger.getChild("MainApp")

        self.config = config

        self._initialize_targets(config)

    def _initialize_targets(self, config: AppConfig):
        self.targets = []

        for target_config in config.targets:
            target = target_config.initialize()
            self.targets.append(target)

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

    app()


### MAIN ENTRY
if __name__ == "__main__":
    main()

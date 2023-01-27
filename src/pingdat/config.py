"""Application configuration data for pingdat.

See the default config file for details on configuration options.
"""

import logging
import logging.config
import os
import os.path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class TargetConfig(BaseModel):
    """Configuration for ping targets."""

    name: str
    address: str

    interval: Optional[int] = None
    timeout: Optional[int] = None


class MetricsConfig(BaseModel):
    """Configuration for metrics providers."""

    port: int = 9056
    address: str = "0.0.0.0"


class AppConfig(BaseModel):
    """Application configuration for pingdat."""

    interval: int = 60
    timeout: Optional[int] = None

    targets: List[TargetConfig] = []
    metrics: MetricsConfig = MetricsConfig()

    logging: Optional[Dict] = None

    @classmethod
    def load(cls, config_file):
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"config file does not exist: {config_file}")

        with open(config_file, "r") as fp:
            data = yaml.load(fp, Loader=yaml.SafeLoader)
            conf = AppConfig(**data)

        logger = cls._configure_logging(conf)
        logger.info("loaded AppConfig from: %s", config_file)

        return conf

    @classmethod
    def _configure_logging(cls, conf):
        if conf.logging is None:
            logging.basicConfig(level=logging.WARNING)
        else:
            logging.config.dictConfig(conf.logging)

        return logging.getLogger()

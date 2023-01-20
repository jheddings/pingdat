"""Verify config file parsing."""

import os.path

from pingstats.config import AppConfig

BASEDIR = os.path.dirname(os.path.realpath(__file__))


def test_sample_config():
    filename = os.path.join(BASEDIR, "..", "etc", "pingstats.yaml")
    config = AppConfig.load(filename)

    assert config.interval > 0
    assert config.timeout > 0

    assert len(config.targets) > 0

    assert config.metrics.port is not None
    assert config.metrics.address is not None

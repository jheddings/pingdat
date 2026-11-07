"""Verify config file parsing."""

import os.path

from click.testing import CliRunner

from pingdat.__main__ import main
from pingdat.config import AppConfig

BASEDIR = os.path.dirname(os.path.realpath(__file__))


def test_sample_config():
    filename = os.path.join(BASEDIR, "..", "etc", "pingdat.yaml")
    config = AppConfig.load(filename)

    assert config.interval > 0
    assert config.timeout > 0

    assert len(config.targets) > 0

    assert config.metrics.port is not None
    assert config.metrics.address is not None


def test_missing_config_exits_cleanly(tmp_path):
    missing = tmp_path / "does-not-exist.yaml"

    result = CliRunner().invoke(main, ["--config", str(missing)])

    assert result.exit_code == 2
    assert str(missing) in result.stderr
    assert len(result.stderr.strip().splitlines()) == 1
    assert isinstance(result.exception, SystemExit)
    assert not isinstance(result.exception, FileNotFoundError)

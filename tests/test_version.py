"""Unit tests for version information."""

import re

from pingdat import version


def test_basic_version():
    """Ensure basic version information is available."""
    assert version.__pkgname__
    assert version.__version__


def test_version_is_valid_string():
    """Ensure version strings meet expected conventions."""
    assert re.match(r"^[0-9]+(\.[0-9])+(-.*)?$", version.__version__)

"""Unit tests for version information."""

from pingstats import version


def test_basic_version():
    """Ensure basic version information is available."""
    assert version.__pkgname__ is not None
    assert version.__version__ is not None

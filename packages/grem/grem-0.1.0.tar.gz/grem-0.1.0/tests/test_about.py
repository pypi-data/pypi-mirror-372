import importlib

from grem.__about__ import __version__


def test_version():
    assert __version__ == importlib.metadata.version('grem')

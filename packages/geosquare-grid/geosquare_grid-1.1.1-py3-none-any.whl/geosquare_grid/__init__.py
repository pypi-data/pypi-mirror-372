# src/geosquare_grid/__init__.py

from .core import GeosquareGrid

try:
    from ._version import version as __version__
except ImportError:
    # package is not installed
    __version__ = "unknown"

__all__ = ['GeosquareGrid', '__version__']
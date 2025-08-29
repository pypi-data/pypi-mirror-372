from importlib.metadata import PackageNotFoundError, version

from .model import Mater

# Version
try:
    __version__ = version("mater")
except PackageNotFoundError:
    __version__ = "unknown"

# Wildcard imports
__all__ = ["Mater"]

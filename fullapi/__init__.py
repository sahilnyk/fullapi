"""fullapi - FastAPI project scaffolder."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("fullapi")
except PackageNotFoundError:
    __version__ = "0.0.0"

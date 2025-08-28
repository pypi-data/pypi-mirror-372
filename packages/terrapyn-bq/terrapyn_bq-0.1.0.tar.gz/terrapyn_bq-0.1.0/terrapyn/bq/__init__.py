import importlib.metadata

from . import data

__version__ = importlib.metadata.version("terrapyn.bq")

__all__ = ["data"]

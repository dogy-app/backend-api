from importlib import metadata
from typing import Any

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    __version__ = ""
del metadata


def __getattr__(name) -> Any:
    if name == 'UserRepository':
        from .crud import UserRepository
    raise AttributeError(f"Could not find {name}")

__all__ = ['UserRepository']

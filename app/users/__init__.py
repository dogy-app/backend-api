from importlib import metadata
from typing import Any

try:
    __version__ = metadata.version(__package__) # type: ignore
except metadata.PackageNotFoundError:
    __version__ = ""
del metadata


def __getattr__(name) -> Any:
    if name == "UserService":
        from .crud import UserService
    raise AttributeError(f"Could not find {name}")

__all__ = ["UserService"]

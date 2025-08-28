from __future__ import annotations

from ._core import (
    __doc__,
    __version__,
    activate,
    set_license_server,
    start_license_server,
)
from .client_main import main as client_main
from .server_main import main as server_main

__all__ = [
    "__doc__",
    "__version__",
    "activate",
    "set_license_server",
    "start_license_server",
    "client_main",
    "server_main",
]


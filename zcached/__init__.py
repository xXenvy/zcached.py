from __future__ import annotations

from typing import Final, Tuple

from .client import ZCached
from .connection import Connection
from .connection_pool import ConnectionPool
from .backoff import ExponentialBackoff

from .result import Result
from .enums import Errors, Commands

from .protocol import Serializer, Deserializer, Reader, SupportedTypes
from .asyncio import AsyncZCached, AsyncConnection, AsyncConnectionPool


__all__: Final[Tuple[str, ...]] = (
    "ZCached",
    "Connection",
    "ConnectionPool",
    "ExponentialBackoff",
    "Result",
    "Serializer",
    "SupportedTypes",
    "Deserializer",
    "Reader",
    "Errors",
    "Commands",
    "AsyncZCached",
    "AsyncConnection",
    "AsyncConnectionPool",
    "__version__",
)

__version__: Final[str] = "1.2.1"

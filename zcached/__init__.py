from typing import Final, Tuple

from .client import ZCached
from .connection import Connection
from .backoff import ExponentialBackoff
from .result import Result
from .enums import Errors, Commands
from .protocol import Serializer, Deserializer, Reader, SupportedTypes

__all__: Final[Tuple[str, ...]] = (
    "ZCached",
    "Connection",
    "ExponentialBackoff",
    "Result",
    "Serializer",
    "SupportedTypes",
    "Deserializer",
    "Reader",
    "Errors",
    "Commands",
    "__version__",
)

__version__: Final[str] = "1.2.1"
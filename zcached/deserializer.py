from typing import TypeVar, Generic, Any, List

from .serializer import SupportedTypes

T = TypeVar("T", bound=SupportedTypes)


class Deserializer(Generic[T]):
    def __init__(self, payload: bytes) -> None:
        self.raw_payload: bytes = payload

    def deserialize(self) -> T:
        if self.raw_payload.startswith(b"+"):
            return self.string

        if self.raw_payload.startswith(b":"):
            return self.integer

        if self.raw_payload.startswith(b","):
            return self.float

        if self.raw_payload.startswith(b"#"):
            return self.bool

        if self.raw_payload.startswith(b"*"):
            return self.list

        if self.raw_payload.startswith(b"_"):
            return None

    @property
    def string(self) -> str:
        return self._sanitize_bytes().replace(b"+", b"").decode()

    @property
    def integer(self) -> int:
        return int(self._sanitize_bytes().replace(b":", b""))

    @property
    def float(self) -> float:
        return float(self._sanitize_bytes().replace(b",", b""))

    @property
    def bool(self) -> bool:
        return self._sanitize_bytes() == b"#t"

    @property
    def list(self) -> List[Any]:
        ...

    @staticmethod
    def _refactor_strings(array: List[Any]) -> List[Any]:
        for i, e in enumerate(array):
            if e.startswith(b"$"):
                array[i + 1] = b"+" + array[i + 1]
                del array[i]

        return array

    def _sanitize_bytes(self) -> bytes:
        return self.raw_payload.replace(b"\r\n", b"")

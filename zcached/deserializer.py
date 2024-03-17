from __future__ import annotations

from typing import TypeVar, Generic, Any, List, Callable

from .serializer import SupportedTypes
from .reader import Reader

T = TypeVar("T", bound=SupportedTypes)


class Deserializer(Generic[T]):
    def __init__(self, payload: bytes) -> None:
        self.raw_payload: bytes = payload
        self.reader: Reader = Reader(self.raw_payload)

    def deserialize(self) -> T:
        self.reader.position = 0

        types: dict[str, Callable[[], T]] = {
            "+": self.string,
            "$": self.string,
            ":": self.integer,
            ",": self.float,
            "#": self.bool,
            "*": self.list,
            "_": lambda: None,
        }
        return types[chr(self.raw_payload[0])]()

    def string(self) -> str:
        raw: bytes = self.reader.get()
        if raw.startswith(b"+"):
            return raw.replace(b"+", b"").decode()

        return self.reader.get().decode()

    def integer(self) -> int:
        return int(self.reader.get().replace(b":", b""))

    def float(self) -> float:
        return float(self.reader.get().replace(b",", b""))

    def bool(self) -> bool:
        return self.reader.get() == b"#t"

    def list(self) -> List[Any]:
        final_array: list[Any] = []
        array_size: int = int(self.reader.get()[1::])

        for element in self.reader.read(array_size):
            if not element.startswith(b"*"):
                if element.startswith(b"$"):
                    element += b"\r\n" + self.reader.get()

                final_array.append(Deserializer(element).deserialize())
                continue

            payload: bytes = (
                element + b"\r\n" + b"\r\n".join(self.reader.current_elements)
            )
            final_array.append(Deserializer(payload).deserialize())
            self.reader.position += int(element[1::])

        return final_array

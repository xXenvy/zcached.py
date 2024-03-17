from __future__ import annotations

from typing import Any, List, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .reader import Reader


class Deserializer:
    def deserialize(self, reader: Reader) -> Any:
        types: dict[str, Callable[[Reader], Any]] = {
            "+": self.string,
            "$": self.string,
            ":": self.integer,
            ",": self.float_number,
            "#": self.boolean,
            "*": self.array,
            "%": self.dictionary,
            "_": self.none,
        }
        return types[chr(reader.current[0])](reader)

    @staticmethod
    def string(reader: Reader) -> str:
        raw: bytes = reader.read()

        if raw.startswith(b"+"):
            return raw[1::].decode()

        return reader.read().decode()

    @staticmethod
    def integer(reader: Reader) -> int:
        return int(reader.read().replace(b":", b""))

    @staticmethod
    def float_number(reader: Reader) -> float:
        return float(reader.read().replace(b",", b""))

    @staticmethod
    def boolean(reader: Reader) -> bool:
        return reader.read() == b"#t"

    @staticmethod
    def none(reader: Reader) -> None:
        reader.read()
        return None

    def array(self, reader: Reader) -> List[Any]:
        final_array: list[Any] = []

        array_size: int = int(reader.read()[1::])
        # [1::] to remove the `*` character.

        for _ in range(array_size):
            final_array.append(self.deserialize(reader))

        return final_array

    def dictionary(self, reader: Reader) -> dict[str, Any]:
        final_dict: dict[str, Any] = {}

        dict_size: int = int(reader.read()[1::])
        # [1::] to remove the `%` character.

        for _ in range(dict_size):
            key, value = self.deserialize(reader), self.deserialize(reader)
            final_dict[key] = value

        return final_dict

from __future__ import annotations

from typing import Any, List, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .reader import Reader


class Deserializer:
    """A class responsible for deserializing data from a Reader object."""

    __slots__ = ()

    def deserialize(self, reader: Reader) -> Any:
        """
        Method to deserialize data from the provided Reader object.

        Parameters
        ----------
        reader:
            The Reader object containing the payload data.

        Raises
        ------
        KeyError
            If the deserialization type is not supported.
        """
        handlers: dict[str, Callable[[Reader], Any]] = {
            "+": self.string,
            "$": self.string,
            ":": self.integer,
            ",": self.float_number,
            "#": self.boolean,
            "*": self.array,
            "%": self.dictionary,
            "_": self.none,
        }
        current_first_char: str = chr(reader.current[0])
        return handlers[current_first_char](reader)

    @staticmethod
    def string(reader: Reader) -> str:
        """Method to deserialize a payload data to string."""
        raw: bytes = reader.read()

        if raw.startswith(b"+"):
            return raw[1::].decode()

        return reader.read().decode()

    @staticmethod
    def integer(reader: Reader) -> int:
        """Method to deserialize a payload data to integer."""
        return int(reader.read().replace(b":", b""))

    @staticmethod
    def float_number(reader: Reader) -> float:
        """Method to deserialize a payload data to float."""
        return float(reader.read().replace(b",", b""))

    @staticmethod
    def boolean(reader: Reader) -> bool:
        """Method to deserialize a payload data to boolean."""
        return reader.read() == b"#t"

    @staticmethod
    def none(reader: Reader) -> None:
        """Method to deserialize a payload data to None."""
        reader.read()
        return None

    def array(self, reader: Reader) -> List[Any]:
        """Method to deserialize a payload data to array."""
        final_array: list[Any] = []

        array_size: int = int(reader.read()[1::])
        # [1::] to remove the `*` character.

        for _ in range(array_size):
            final_array.append(self.deserialize(reader))

        return final_array

    def dictionary(self, reader: Reader) -> dict[str, Any]:
        """Method to deserialize a payload data to dictionary."""
        final_dict: dict[str, Any] = {}

        dict_size: int = int(reader.read()[1::])
        # [1::] to remove the `%` character.

        for _ in range(dict_size):
            key, value = self.deserialize(reader), self.deserialize(reader)
            final_dict[key] = value

        return final_dict

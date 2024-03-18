from __future__ import annotations

from typing import Any, List, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .reader import Reader


class Deserializer:
    """A class responsible for deserializing data using a Reader object."""

    __slots__ = ()

    def process(self, reader: Reader) -> Any:
        """
        Method to deserialize data from the provided Reader object.

        Parameters
        ----------
        reader:
            The Reader object containing the payload data.
        """
        handlers: dict[str, Callable[[Reader], Any]] = {
            "+": self.deserialize_sstr,
            "$": self.deserialize_str,
            ":": self.deserialize_int,
            ",": self.deserialize_float,
            "#": self.deserialize_bool,
            "_": self.deserialize_none,
            "*": self.deserialize_array,
            "%": self.deserialize_map,
        }
        current_first_char: str = chr(reader.current[0])
        return handlers[current_first_char](reader)

    @staticmethod
    def deserialize_str(reader: Reader) -> str:
        """Method to deserialize a payload data to string."""
        reader.read()
        return reader.read().decode()

    @staticmethod
    def deserialize_sstr(reader: Reader) -> str:
        """Method to deserialize a payload data to string."""
        return reader.read().decode()

    @staticmethod
    def deserialize_int(reader: Reader) -> int:
        """Method to deserialize a payload data to integer."""
        return int(reader.read()[1::])

    @staticmethod
    def deserialize_float(reader: Reader) -> float:
        """Method to deserialize a payload data to float."""
        return float(reader.read()[1::])

    @staticmethod
    def deserialize_bool(reader: Reader) -> bool:
        """Method to deserialize a payload data to boolean."""
        return reader.read() == b"#t"

    @staticmethod
    def deserialize_none(reader: Reader) -> None:
        """Method to deserialize a payload data to None."""
        reader.read()
        return None

    def deserialize_array(self, reader: Reader) -> List[Any]:
        """Method to deserialize a payload data to array."""
        array_size: int = int(reader.read()[1::])
        return [self.process(reader) for _ in range(array_size)]

    def deserialize_map(self, reader: Reader) -> dict[str, Any]:
        """Method to deserialize a payload data to dictionary."""
        map_size: int = int(reader.read()[1::])
        return {self.process(reader): self.process(reader) for _ in range(map_size)}

from __future__ import annotations

from typing import Any, List, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .reader import Reader


class Deserializer:
    """
    Deserializer class is responsible for deserializing payload data to python objects.

    This class provides methods to deserialize various data types from a Reader object,
    including strings, integers, floats, booleans, None, arrays, and dictionaries.
    """

    __slots__ = ()

    def process(self, reader: Reader) -> Any:
        """
        Method to deserialize data from the provided Reader object.

        Parameters
        ----------
        reader:
            The Reader object containing the payload data.
        """
        handlers: dict[bytes, Callable[[Reader], Any]] = {
            b"+": self.deserialize_sstr,
            b"$": self.deserialize_str,
            b":": self.deserialize_int,
            b",": self.deserialize_float,
            b"#": self.deserialize_bool,
            b"_": self.deserialize_none,
            b"*": self.deserialize_array,
            b"%": self.deserialize_map,
        }
        return handlers[reader.read(1)](reader)

    @staticmethod
    def deserialize_str(reader: Reader) -> str:
        """Method to deserialize a payload data to string."""
        reader.read_until(b"\n")  # Skip $lenght element.
        return reader.read_until(b"\n").decode()

    @staticmethod
    def deserialize_sstr(reader: Reader) -> str:
        """Method to deserialize a payload data to string."""
        return reader.read_until(b"\n").decode()

    @staticmethod
    def deserialize_int(reader: Reader) -> int:
        """Method to deserialize a payload data to integer."""
        return int(reader.read_until(b"\n"))

    @staticmethod
    def deserialize_float(reader: Reader) -> float:
        """Method to deserialize a payload data to float."""
        return float(reader.read_until(b"\n"))

    @staticmethod
    def deserialize_bool(reader: Reader) -> bool:
        """Method to deserialize a payload data to boolean."""
        return reader.read_until(b"\n") == b"t"

    @staticmethod
    def deserialize_none(reader: Reader) -> None:
        """Method to deserialize a payload data to None."""
        reader.read_until(b"\n")  # We don't care about this.
        return None

    def deserialize_array(self, reader: Reader) -> List[Any]:
        """Method to deserialize a payload data to array."""
        array_size: int = int(reader.read_until(b"\n"))
        return [self.process(reader) for _ in range(array_size)]

    def deserialize_map(self, reader: Reader) -> dict[str, Any]:
        """Method to deserialize a payload data to dictionary."""
        map_size: int = int(reader.read_until(b"\n"))
        return {self.process(reader): self.process(reader) for _ in range(map_size)}

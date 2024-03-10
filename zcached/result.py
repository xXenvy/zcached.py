from __future__ import annotations
from typing import Any


class Result:
    """
    Represents the result of the server response.

    .. container:: operations

        .. describe:: x == y

            Checks if two results are equal.

        .. describe:: x != y

            Checks if two results are not equal.

        .. describe:: hash(x)

            Returns the result's hash.

        .. describe:: bytes(x)

            Returns the result's bytes.

    Attributes
    ----------
    value:
        Operation result. Stores empty bytes if the operation fails.
    error:
        Error message detailing why the operation failed, value is None if
        operation was successful.
    """
    __slots__ = ('value', 'error')

    def __init__(self, value: bytes, error: str | None = None):
        # TODO: Add deserializer.
        self.value: bytes = value
        self.error: str | None = error

    def __bytes__(self) -> bytes:
        return self.value

    def __hash__(self) -> int:
        return hash((self.value, self.error))

    def __eq__(self, other: Any) -> bool:
        return hash(other) == hash(self)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<Result(success={self.success})>"

    @property
    def success(self) -> bool:
        """True if the operation was successful."""
        return self.error is None

    @property
    def failure(self) -> bool:
        """True if operation failed."""
        return self.error is not None

    @classmethod
    def fail(cls, error: str):
        """Create a Result object for a failed operation."""
        return cls(value=bytes(), error=error)

    @classmethod
    def ok(cls, value: bytes):
        """Create a Result object for a successful operation."""
        return cls(value=value)

    def is_empty(self) -> bool:
        """Checks if the value is empty."""
        return not bool(self.value)

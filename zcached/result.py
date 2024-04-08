from __future__ import annotations
from typing import Any, Generic, TypeVar, ClassVar

from .deserializer import Deserializer
from .reader import Reader

T = TypeVar("T")


class Result(Generic[T]):
    """
    Represents the result of the server response.

    Attributes
    ----------
    value:
        Operation result. Stores empty bytes if the operation fails.
    error:
        Error message detailing why the operation failed, value is None if
        operation was successful.
    """

    __slots__ = ("value", "error")
    _deserializer: ClassVar[Deserializer] = Deserializer()

    def __init__(self, value: bytes, error: str | None = None):
        if error is not None:
            # If we have an error, the value will be empty, so there is no point in deserializing it.
            self.value: T = value  # type: ignore
        else:
            self.value: T = self._deserializer.process(Reader(value))

        self.error: str | None = error

    def __hash__(self) -> int:
        return hash((self.value, self.error))

    def __eq__(self, other: Any) -> bool:
        return hash(other) == hash(self)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __bool__(self) -> bool:
        return self.success

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
        return isinstance(self.value, bytes) and not bool(self.value)

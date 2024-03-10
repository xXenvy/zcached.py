from __future__ import annotations


class ExponentialBackoff:
    """
    Implementation of the exponential backoff algorithm.

    Parameters
    ----------
    initial:
        The initial value for the exponential.
    multiplier:
        Value to multiply initial value.
    max_value:
        The maximum value of the exponential.

    Attributes
    ----------
    current: :class:`float`
        The current value of the exponential.
    """
    __slots__ = ("current", "_multiplier", "_max", "_initial", "_total")

    def __init__(self, initial: float, multiplier: float, max_value: float) -> None:
        self.current: float = 0

        self._multiplier: float = multiplier
        self._max: float = max_value
        self._total: float = .0

        self._initial: float = initial

    def __repr__(self) -> str:
        return f"<ExponentialBackoff(current={self.current}, next={self.next}, total={self.total})>"

    def __iter__(self) -> ExponentialBackoff:
        return self

    def __next__(self) -> float:
        if self.current:
            self.current = self.next
            self._total += self.current
        else:
            self.current = self._initial
        return self.current

    @property
    def next(self) -> float:
        """Next value of exponential."""
        return min(self._max, self.current * self._multiplier)

    @property
    def total(self) -> float:
        """Total value of exponential."""
        return self._total

    def reset(self) -> None:
        """Method to reset the exponential backoff."""
        self.current = 0
        self._total = .0

from typing import Iterator, List


class Reader:
    """
    Implementation of the reader interface which helps read data from raw bytes.

    Parameters
    ----------
    payload:
        Payload to read.

    Attributes
    ----------
    payload:
        Provided payload.
    position:
        The position of the reader.
    """

    __slots__ = ("payload", "position")

    def __init__(self, payload: bytes) -> None:
        self.payload: bytes = payload
        self.position: int = 0

    def __repr__(self) -> str:
        return f"<Reader(position={self.position}, items={len(self.current_elements)})>"

    @property
    def current_elements(self) -> List[bytes]:
        """Returns a list of remaining elements in the payload, starting from the current position."""
        return self.payload.split(b"\r\n")[self.position : :]

    @property
    def current(self) -> bytes:
        """Returns the current element pointed by the position."""
        return self.current_elements[0]

    def read_until(self, amount: int) -> Iterator[bytes]:
        """
        Reads and yields bytes elements from the payload.

        Parameters
        ----------
        amount:
            Number of elements to return.
        """
        for _ in range(amount):
            yield self.read()

    def read(self) -> bytes:
        """
        Reads the current element and moves the position to the next one.
        """
        # TODO: read single characters.
        element: bytes = self.current
        self.position += 1
        return element

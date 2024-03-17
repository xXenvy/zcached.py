from typing import Iterator


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

    @property
    def current_elements(self) -> list[bytes]:
        """Returns a list of remaining elements in the payload, starting from the current position."""
        return self.payload.split(b"\r\n")[self.position : :]

    @property
    def current(self) -> bytes:
        """Returns the current element pointed by the position."""
        return self.current_elements[0]

    def read_until(self, lenght: int) -> Iterator[bytes]:
        """
        Reads and yields bytes elements from the payload until the specified length.

        Parameters
        ----------
        lenght:
            The length of the payload to read.
        """
        for _ in range(lenght):
            yield self.read()

    def read(self) -> bytes:
        """Reads the current element and moves the position to the next one."""
        item: bytes = self.current
        self.position += 1
        return item

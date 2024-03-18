from __future__ import annotations


class Reader:
    """
    Implementation of the reader interface which helps reading data from raw bytes.

    Parameters
    ----------
    payload:
        Payload to read.

    Attributes
    ----------
    buffer:
        Provided payload.
    position:
        Current reader position.
    """

    __slots__ = ("buffer", "position")

    def __init__(self, payload: bytes) -> None:
        self.buffer: bytes = payload.replace(b"\r", b"")
        self.position: int = 0

    def __repr__(self) -> str:
        return f"<Reader(position={self.position})>"

    def read_until(self, element: bytes) -> bytes:
        """
        Method to read bytes from the buffer until the specified element is encountered.

        Parameters
        ----------
        element:
            The byte sequence indicating the end of reading.

        Notes
        -----
        This method reads bytes from the buffer until the specified `element` is encountered.
        It starts reading from the current position in the buffer.
        """
        total: bytes = self.read(1)

        while not total.endswith(element):
            total += self.read(1)

        return total[: -len(element)]

    def read(self, size: int | None = None) -> bytes:
        """
        Method to read bytes starting at current position.

        Parameters
        ----------
        size:
            Number of bytes to read.
        """
        if size is None:
            size = len(self.buffer) - self.position

        data: bytes = self.buffer[self.position : self.position + size]
        self.position += len(data)
        return data

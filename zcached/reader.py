from typing import Iterator


class Reader:
    def __init__(self, payload: bytes) -> None:
        self.payload: bytes = payload
        self.position: int = 0

    @property
    def current_elements(self) -> list[bytes]:
        return self.payload.split(b"\r\n")[self.position : :]

    @property
    def current(self) -> bytes:
        return self.current_elements[0]

    def read(self, lenght: int) -> Iterator[bytes]:
        for _ in range(lenght):
            yield self.get()

    def get(self) -> bytes:
        item: bytes = self.current
        self.position += 1
        return item

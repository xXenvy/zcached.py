from __future__ import annotations
from typing import TYPE_CHECKING

from .serializer import Serializer, SupportedTypes

if TYPE_CHECKING:
    from .result import Result
    from .connection import Connection


class ZCached:
    """
    ZCached client to connect to the server and send commands.

    Parameters
    ----------
    connection:
        Connection object used by this class.

    Attributes
    ----------
    connection: :class:`Connection`
        Connection object used by this class.
    """

    __slots__ = ("connection",)

    def __init__(self, connection: Connection) -> None:
        self.connection: Connection = connection

        if not self.connection.is_connected:
            self.connection.connect()

    def __repr__(self) -> str:
        return f"ZCached(connection={self.connection})"

    def ping(self) -> Result:
        """Send a ping command to the database."""
        return self.connection.send(b"*1\r\n$4\r\nPING\r\n")

    def flush(self) -> Result:
        """Method to flush all database records."""
        return self.connection.send(b"*1\r\n$5\r\nFLUSH\r\n")

    def dbsize(self) -> Result:
        """Retrieve the size of the database."""
        return self.connection.send(b"*1\r\n$6\r\nDBSIZE\r\n")

    def save(self) -> Result:
        """Method to save all database records."""
        return self.connection.send(b"*1\r\n$4\r\nSAVE\r\n")

    def get(self, key: str) -> Result:
        """
        Method to send a get command to the database.

        Parameters
        ----------
        key:
            The key to retrieve the value from the database.
        """
        command: str = f"*2\r\n$3\r\nGET\r\n${len(key)}\r\n{key}\r\n"
        return self.connection.send(command.encode())

    def set(self, key: str, value: SupportedTypes) -> Result:
        """
        Method to create a new database record.

        Parameters
        ----------
        key:
            The key of the new record.
        value:
            The value of the record.
        """
        serializer: Serializer = Serializer(value)
        command: str = (
            f"*3\r\n$3\r\nSET\r\n${len(key)}\r\n{key}\r\n{serializer.serialize()}"
        )
        return self.connection.send(command.encode())

    def delete(self, key: str) -> Result:
        """
        Method to delete a database record by key.

        Parameters
        ----------
        key:
            Key of the record being deleted.
        """
        command: str = f"*2\r\n$6\r\nDELETE\r\n${len(key)}\r\n{key}\r\n"
        return self.connection.send(command.encode())

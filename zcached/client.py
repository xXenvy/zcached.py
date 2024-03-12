from __future__ import annotations
from typing import TYPE_CHECKING

from .serializer import Serializer, SupportedTypes
from .connection import Connection

if TYPE_CHECKING:
    from .result import Result
    from typing_extensions import Self


class ZCached:
    """
    ZCached client to connect to the server and send commands.

    Parameters
    ----------
    host:
        Server host address.
    port:
        Server port number.
    buff_size:
        The size of the buffer for receiving data from the server, in bytes.
        Larger values for buff_size may allow for more data to be received in a single operation,
        while smaller values can be more memory-efficient but slower.
    connection_attempts:
        The maximum number of attempts to establish a connection with the server.
        If the maximum number of attempts is exceeded, an error will be raised.

    Attributes
    ----------
    connection: :class:`Connection`
        Connection object used by this class.
    """

    __slots__ = ("connection",)

    def __init__(
        self,
        host: str,
        port: int = 7556,
        buff_size: int = 1024,
        connection_attempts: int = 3,
    ) -> None:
        self.connection: Connection = Connection(
            host, port, buff_size, connection_attempts
        )
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

    @classmethod
    def from_connection(cls, connection: Connection) -> Self:
        """
        Classmethod to create client from existing connection.

        Parameters
        ----------
        connection:
            Created connection object.
        """
        return cls(
            host=connection.host,
            port=connection.port,
            buff_size=connection.buff_size,
            connection_attempts=connection.connection_attempts,
        )

from __future__ import annotations
from typing import TYPE_CHECKING, Any, ClassVar, List

from .protocol import Serializer, SupportedTypes
from .connection import Connection

if TYPE_CHECKING:
    from typing_extensions import Self

    from .result import Result


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
        This value is also considered while reconnecting.
    reconnect:
        Flag indicating whether automatic reconnection attempt should be made
        in case of a broken connection.
    timeout_limit:
        The maximum time in seconds to wait for a response from the server.

    Notes
    -----
    There is a way to do a reconnect manually, using the ``ZCached.connection.try_reconnect()`` method.

    Attributes
    ----------
    connection:
        Connection object used by this class.
    """

    __slots__ = ("connection",)
    _serializer: ClassVar[Serializer] = Serializer()

    def __init__(
        self,
        host: str,
        port: int = 7556,
        buff_size: int = 1024,
        connection_attempts: int = 3,
        reconnect: bool = True,
        timeout_limit: int = 10,
    ) -> None:
        self.connection: Connection = Connection(
            host=host,
            port=port,
            buff_size=buff_size,
            connection_attempts=connection_attempts,
            reconnect=reconnect,
            timeout_limit=timeout_limit,
        )

    def __repr__(self) -> str:
        return f"ZCached(connection={self.connection})"

    def run(self) -> None:
        """Establishes a connection with the database server."""
        self.connection.connect()

    def ping(self) -> Result[str]:
        """Send a ping command to the database."""
        return self.connection.send(b"*1\r\n$4\r\nPING\r\n")

    def flush(self) -> Result[str]:
        """Method to flush all database records."""
        return self.connection.send(b"*1\r\n$5\r\nFLUSH\r\n")

    def dbsize(self) -> Result[int]:
        """Retrieve the size of the database."""
        return self.connection.send(b"*1\r\n$6\r\nDBSIZE\r\n")

    def save(self) -> Result[str]:
        """Method to save all database records."""
        return self.connection.send(b"*1\r\n$4\r\nSAVE\r\n")

    def keys(self) -> Result[List[str]]:
        """Retrieve the keys of the database."""
        return self.connection.send(b"*1\r\n$4\r\nKEYS\r\n")

    def lastsave(self) -> Result[int]:
        """Method to retrieve the Unix timestamp of the last successful database save."""
        return self.connection.send(b"*1\r\n$8\r\nLASTSAVE\r\n")

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

    def mget(self, *keys: str) -> Result[dict[str, Any]]:
        """
        Method to send a mget command to the database.
        This command allows you to retrieve multiple values simultaneously.

        Example usage: ``client.mget("key1", "key2", "key3")``

        .. note::
            For every key that does not hold a string value or does not exist,
            the special value null is returned. Because of this, the operation never fails.

        Parameters
        ----------
        keys:
            Keys to retrieve values from the database.
        """
        command: str = f"*{1 + len(keys)}\r\n$4\r\nMGET\r\n"
        for key in keys:
            command += f"${len(key)}\r\n{key}\r\n"

        return self.connection.send(command.encode())

    def set(self, key: str, value: SupportedTypes) -> Result[str]:
        """
        Method to create a new database record.

        Parameters
        ----------
        key:
            The key of the new record.
        value:
            The value of the record.
        """
        command: str = (
            f"*3\r\n$3\r\nSET\r\n${len(key)}\r\n{key}\r\n{self._serializer.process(value)}"
        )
        return self.connection.send(command.encode())

    def mset(self, **params: SupportedTypes) -> Result[str]:
        """
        Method to set multiple database records simultaneously.

        Example usage: ``client.mset(key1="value1", key2="value2", key3="value3")``

        Parameters
        ----------
        params:
            Keyword arguments representing key-value pairs to be set in the database.
        """
        command: str = f"*{1 + len(params) * 2}\r\n$4\r\nMSET\r\n"
        for key, value in params.items():
            command += f"${len(key)}\r\n{key}\r\n{self._serializer.process(value)}"

        return self.connection.send(command.encode())

    def delete(self, key: str) -> Result[str]:
        """
        Method to delete a database record by key.

        Parameters
        ----------
        key:
            Key of the record being deleted.
        """
        command: str = f"*2\r\n$6\r\nDELETE\r\n${len(key)}\r\n{key}\r\n"
        return self.connection.send(command.encode())

    def exists(self, key: str) -> bool:
        """
        Checks if the specified key exists in the database.

        Parameters
        ----------
        key:
            The key to check for existence in the database.

        Notes
        -----
        **Using this method directly may be unsafe as it does not verify the connection status.**
        When the key exists in the database, but the connection is broken, the value False will be returned.
        Because of this it's recommended to use this method only when the connection to the server is guaranteed.
        """
        return bool(self.get(key))

    def is_alive(self) -> bool:
        """
        Checks if the client is currently connected to the server.

        .. note::
            This method sends a ping command to the connected server.
        """
        result: Result = self.ping()
        return result.error is None

    @classmethod
    def from_connection(cls, connection: Connection) -> Self:
        """
        A classmethod to create client from existing connection.

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
            reconnect=connection.reconnect,
            timeout_limit=connection.timeout_limit,
        )

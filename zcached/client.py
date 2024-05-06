from __future__ import annotations
from typing import TYPE_CHECKING, Any, ClassVar, List

from .protocol import Serializer, SupportedTypes
from .connection import Connection
from .enums import Commands

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
    buffer_size:
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
        buffer_size: int = 2048,
        connection_attempts: int = 3,
        reconnect: bool = True,
        timeout_limit: int = 10,
        **kwargs: Any,
    ) -> None:
        if connection := kwargs.get("connection"):
            self.connection: Connection = connection
        else:
            self.connection: Connection = Connection(
                host=host,
                port=port,
                buffer_size=buffer_size,
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
        return self.connection.send(Commands.PING.value)

    def flush(self) -> Result[str]:
        """Method to flush all database records."""
        return self.connection.send(Commands.FLUSH.value)

    def dbsize(self) -> Result[int]:
        """Retrieve the size of the database."""
        return self.connection.send(Commands.DB_SIZE.value)

    def save(self) -> Result[str]:
        """Method to save all database records."""
        return self.connection.send(Commands.SAVE.value)

    def keys(self) -> Result[List[str]]:
        """Retrieve the keys of the database."""
        return self.connection.send(Commands.KEYS.value)

    def lastsave(self) -> Result[int]:
        """Method to retrieve the Unix timestamp of the last successful database save."""
        return self.connection.send(Commands.LAST_SAVE.value)

    def get(self, key: str) -> Result:
        """
        Method to send a get command to the database.

        Parameters
        ----------
        key:
            The key to retrieve the value from the database.
        """
        return self.connection.send(Commands.get(key))

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
        return self.connection.send(Commands.mget(*keys))

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
        return self.connection.send(Commands.set(key, value))

    def mset(self, **params: SupportedTypes) -> Result[str]:
        """
        Method to set multiple database records simultaneously.

        Example usage: ``client.mset(key1="value1", key2=True, key3=9999)``

        Parameters
        ----------
        params:
            Keyword arguments representing key-value pairs to be set in the database.
        """
        return self.connection.send(Commands.mset(**params))

    def delete(self, key: str) -> Result[str]:
        """
        Method to delete a database record by key.

        Parameters
        ----------
        key:
            Key of the record being deleted.
        """
        return self.connection.send(Commands.delete(key))

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
        return bool(self.ping())

    @classmethod
    def from_connection(cls, connection: Connection) -> Self:
        """
        A classmethod to create client from existing connection.

        Parameters
        ----------
        connection:
            Created connection object.
        """
        return cls(host=connection.host, connection=connection)

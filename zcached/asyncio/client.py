from __future__ import annotations

from typing import Any, ClassVar, TYPE_CHECKING
from asyncio import get_event_loop

from .connection_pool import ConnectionPool
from .connection import AsyncConnection

from ..result import Result
from ..enums import Commands, Errors
from ..protocol import SupportedTypes, Serializer

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop
    from typing_extensions import Self


class AsyncZCached:
    """
    Asynchronous ZCached client to connect to the server and send commands.

    Parameters
    ----------
    host:
        Server host address.
    port:
        Server port number.
    pool_size:
        Number of connections to be created in the connection pool (default is 1).
    connection_attempts:
        The maximum number of attempts to establish a connection with the server (default is 3).
    reconnect:
        Flag indicating whether automatic reconnection attempt should be made
        in case of a broken connection (default is True).
    timeout_limit:
        The maximum time in seconds to wait for a response from the server (default is 10).
    buffer_size:
        The size of the buffer for receiving data from the server, in bytes (default is 1024).
    loop:
        The event loop to be used (default is None, which means using the current event loop).

    Attributes
    ----------
    connection_pool:
        The connection pool used by the client to manage connections to the server.
    loop:
        The event loop used by the client for asynchronous operations.
    """

    __slots__ = ("connection_pool", "loop")
    _serializer: ClassVar[Serializer] = Serializer()

    def __init__(
        self,
        host: str,
        port: int,
        pool_size: int = 1,
        connection_attempts: int = 3,
        reconnect: bool = True,
        timeout_limit: int = 10,
        buffer_size: int = 1024,
        loop: AbstractEventLoop | None = None,
        **kwargs: Any,
    ):
        if pool := kwargs.get("connection_pool"):
            self.connection_pool: ConnectionPool = pool
        else:
            self.connection_pool: ConnectionPool = ConnectionPool(
                pool_size=pool_size,
                connection_factory=lambda: AsyncConnection(
                    host=host,
                    port=port,
                    connection_attempts=connection_attempts,
                    reconnect=reconnect,
                    timeout_limit=timeout_limit,
                    buffer_size=buffer_size,
                    loop=loop,
                ),
            )
        self.loop: AbstractEventLoop = loop or get_event_loop()

    def __repr__(self) -> str:
        return f"AsyncZCached(connection_pool={self.connection_pool})"

    async def run(self) -> None:
        """Establishes connections with the database server using connection pool."""
        await self.connection_pool.setup()

    async def ping(self) -> Result[str]:
        """Sends a ping command to the database server."""
        connection: AsyncConnection | None = self.get_connection()
        if not connection:
            return Result.fail(Errors.NoAvailableConnections.value)

        return await connection.send(Commands.PING.value)

    async def flush(self) -> Result[str]:
        """Sends a flush command to the database server."""
        connection: AsyncConnection | None = self.get_connection()
        if not connection:
            return Result.fail(Errors.NoAvailableConnections.value)

        return await connection.send(Commands.FLUSH.value)

    async def dbsize(self) -> Result[str]:
        """Sends a db size command to the database server."""
        connection: AsyncConnection | None = self.get_connection()
        if not connection:
            return Result.fail(Errors.NoAvailableConnections.value)

        return await connection.send(Commands.DB_SIZE.value)

    async def save(self) -> Result[str]:
        """Sends a save command to the database server."""
        connection: AsyncConnection | None = self.get_connection()
        if not connection:
            return Result.fail(Errors.NoAvailableConnections.value)

        return await connection.send(Commands.SAVE.value)

    async def keys(self) -> Result[str]:
        """Sends a key command to the database server."""
        connection: AsyncConnection | None = self.get_connection()
        if not connection:
            return Result.fail(Errors.NoAvailableConnections.value)

        return await connection.send(Commands.KEYS.value)

    async def lastsave(self) -> Result[str]:
        """Sends a last save command to the database server."""
        connection: AsyncConnection | None = self.get_connection()
        if not connection:
            return Result.fail(Errors.NoAvailableConnections.value)

        return await connection.send(Commands.LAST_SAVE.value)

    async def get(self, key: str) -> Result:
        """
        Sends a get command to the database server.

        Parameters
        ----------
        key:
            The key to retrieve the value from the database.
        """
        connection: AsyncConnection | None = self.get_connection()
        if not connection:
            return Result.fail(Errors.NoAvailableConnections.value)

        return await connection.send(Commands.get(key))

    async def mget(self, *keys: str) -> Result[dict[str, Any]]:
        """
        Coroutine to send a mget command to the database.
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
        connection: AsyncConnection | None = self.get_connection()
        if not connection:
            return Result.fail(Errors.NoAvailableConnections.value)

        return await connection.send(Commands.mget(*keys))

    async def set(self, key: str, value: SupportedTypes) -> Result[str]:
        """
        Coroutine to create a new database record.

        Parameters
        ----------
        key:
            The key of the new record.
        value:
            The value of the record.
        """
        connection: AsyncConnection | None = self.get_connection()
        if not connection:
            return Result.fail(Errors.NoAvailableConnections.value)

        return await connection.send(Commands.set(key, value))

    async def mset(self, **params: SupportedTypes) -> Result[str]:
        """
        Coroutine to set multiple database records simultaneously.
        Example usage: ``client.mset(key1="value1", key2=False, key3=5)``

        Parameters
        ----------
        params:
            Keyword arguments representing key-value pairs to be set in the database.
        """
        connection: AsyncConnection | None = self.get_connection()
        if not connection:
            return Result.fail(Errors.NoAvailableConnections.value)

        return await connection.send(Commands.mset(**params))

    async def delete(self, key: str) -> Result[str]:
        """
        Coroutine to delete a database record by key.

        Parameters
        ----------
        key:
            Key of the record being deleted.
        """
        connection: AsyncConnection | None = self.get_connection()
        if not connection:
            return Result.fail(Errors.NoAvailableConnections.value)

        return await connection.send(Commands.delete(key))

    async def is_alive(self) -> bool:
        """Checks if there is any active connection with the database server."""
        return bool(await self.ping())

    async def exists(self, key: str) -> bool:
        """
        Checks if the specified key exists in the database.

        Parameters
        ----------
        key:
            The key to check for existence in the database.

        Notes
        -----
        **Using this method directly may be unsafe as it does not verify the connections status.**
        When the key exists in the database, but the connection is broken, the value False will be returned.
        Because of this it's recommended to use this method only when the connection to the server is guaranteed.
        """
        return bool(await self.get(key))

    def get_connection(self) -> AsyncConnection | None:
        """
        Retrieves the least loaded connection from the connection pool.
        None if there is no any running connections.
        """
        try:
            return self.connection_pool.get_least_loaded_connection()
        except IndexError:
            return None

    @classmethod
    def from_connection_pool(cls, connection_pool: ConnectionPool) -> Self:
        """
        Creates a client instance from an existing connection pool.

        Parameters
        ----------
        connection_pool:
            The connection pool to be used by the client.
        """
        return cls(
            host="",
            port=0,  # This is needed to create a pool. We already have one, so this is unnecessary.
            connection_pool=connection_pool,
        )

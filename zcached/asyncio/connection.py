from __future__ import annotations
from typing import Any, Type, Generic, TypeVar

import asyncio
import logging as logger

from string import ascii_uppercase
from random import choice

from ..connection import Connection
from ..result import Result
from ..enums import Errors

ProtocolT = TypeVar("ProtocolT", bound=asyncio.StreamReaderProtocol)


class AsyncConnection(Connection, Generic[ProtocolT]):
    """
    An asynchronous connection object to manage communication with the server.

    Parameters
    ----------
    host:
        The host address of the server to connect to.
    port:
        The port number of the server to connect to.
    connection_attempts:
        The maximum number of attempts to establish a connection with the server.
        If the maximum number of attempts is exceeded, an error will be raised.
    reconnect:
        Flag indicating whether automatic reconnection attempt should be made
        in case of a broken connection.
    timeout_limit:
        The maximum time in seconds to wait for a response from the server.
    buffer_size:
        The size of the buffer for receiving data from the server, in bytes.
        Larger values for buffer_size may allow for more data to be received in a single operation,
        while smaller values can be more memory-efficient but slower.
    loop:
        The event loop to run asynchronous tasks. If None, the default event loop will be used.
    protocol_type:
        The protocol type which is used to building protocol for managing the connection.

    Attributes
    ----------
    connection_attempts:
        The maximum number of attempts to establish a connection with the server.
    reconnect:
        Flag indicating whether automatic reconnection attempt should be made
        in case of a broken connection.
    timeout_limit:
        The maximum time in seconds to wait for a response from the server.
    buffer_size:
        The size of the buffer for receiving data from the server, in bytes.
    loop:
        The event loop to run asynchronous tasks.
    """

    __slots__ = (
        "loop",
        "_protocol_type",
        "_reader",
        "_writer",
        "_protocol",
        "_pending_requests",
        "_id",
    )

    def __init__(
        self,
        host: str,
        port: int,
        connection_attempts: int = 3,
        reconnect: bool = True,
        timeout_limit: int = 15,
        buffer_size: int = 2048,
        loop: asyncio.AbstractEventLoop | None = None,
        protocol_type: Type[ProtocolT] | None = None,
    ) -> None:
        super().__init__(
            host=host,
            port=port,
            connection_attempts=connection_attempts,
            reconnect=reconnect,
            timeout_limit=timeout_limit,
            buffer_size=buffer_size,
        )
        self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()

        self._protocol_type: Type[ProtocolT] = (  # pyright: ignore
            protocol_type or asyncio.StreamReaderProtocol
        )
        self._protocol: ProtocolT | None = None

        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

        self._lock: asyncio.Lock = asyncio.Lock()
        self._pending_requests: int = 0
        self._id: str = "".join([choice(ascii_uppercase) for _ in range(6)])

    def __repr__(self) -> str:
        return f"<AsyncConnection(host={self.host}, port={self.port}, buffer_size={self.buffer_size}, id={self.id})>"

    @property
    def id(self) -> str:
        """Unique identifier for the connection."""
        return f"#{self._id}-{self.port}"

    @property
    def protocol(self) -> ProtocolT | None:
        """The protocol for managing the connection. If available."""
        return self._protocol

    @property
    def protocol_type(self) -> Type[ProtocolT]:
        """The type of protocol used for managing the connection."""
        return self._protocol_type

    @property
    def reader(self) -> asyncio.StreamReader | None:
        """The asyncio.StreamReader object for reading data from the server. If available."""
        return self._reader

    @property
    def writer(self) -> asyncio.StreamWriter | None:
        """The asyncio.StreamWriter object for writing data to the server. If available."""
        return self._writer

    @property
    def transport(self) -> None | asyncio.WriteTransport:
        """The transport object for the connection, if StreamWriter is available."""
        if self._writer is not None:
            return self._writer.transport

    @property
    def pending_requests(self) -> int:
        """The number of pending requests."""
        return self._pending_requests

    @property
    def is_locked(self) -> bool:
        """Whether the connection is locked."""
        return self._lock.locked()

    async def connect(self) -> None:
        """Coroutine to establish a connection with the server asynchronously."""
        logger.debug(f"{self.id} -> Connecting to {self.host}:{self.port}")

        for attempt, timeout in enumerate(self._backoff):
            try:
                self._reader, self._writer = await self.open_connection(
                    host=self.host, port=self.port
                )
                logger.info(f"{self.id} -> Connected to the server.")
                self._connected = True
                break
            except Exception as exception:
                logger.exception(exception)
                if attempt + 1 >= self.connection_attempts or not self.reconnect:
                    break

                logger.warning(
                    f"{self.id} -> Connecting to the server failed. Retrying..."
                )
                await asyncio.sleep(timeout)

    async def open_connection(
        self, host: str, port: int, **kwargs: Any
    ) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """
        Coroutine to open a  connection to the server.

        Parameters
        ----------
        host:
            The host address of the server.
        port:
            The port number of the server.
        **kwargs:
            Additional keyword arguments to pass to the connection setup.
        """
        logger.debug(f"{self.id} -> Creating a new connection...")
        reader: asyncio.StreamReader = asyncio.StreamReader(loop=self.loop)
        protocol = self.protocol_type(stream_reader=reader, loop=self.loop)

        transport, _ = await self.loop.create_connection(
            protocol_factory=lambda: protocol,  # pyright: ignore
            host=host,
            port=port,
            **kwargs,
        )
        writer: asyncio.StreamWriter = asyncio.StreamWriter(
            transport=transport, protocol=protocol, reader=reader, loop=self.loop
        )
        self._protocol = protocol
        logger.debug(f"{self.id} -> Created a new connection.")
        return reader, writer

    async def try_reconnect(self) -> Result[bytes]:
        """A method to attempt to reconnect to the server if the connection is broken."""
        logger.debug(f"{self.id} -> Attempting to reconnect to the server...")

        # Without this, it somehow manages to establish a non-working connection.
        await asyncio.sleep(1)

        self._connected = False
        await self.connect()

        if self.is_connected is True:
            return Result.fail(Errors.ConnectionReestablished.value)

        return Result.fail(Errors.ConnectionClosed.value)

    async def send(self, data: bytes) -> Result:
        """
        Coroutine to send a data to the server.

        TASK SAFE.

        Parameters
        ----------
        data:
            Bytes to send.
        """
        if self._writer is None:
            logger.error(
                f"{self.id} -> Missing StreamWriter object! Did you forget to connect? Aborting the send method..."
            )
            return Result.fail(Errors.ConnectionClosed.value)

        if self._lock.locked():
            logger.debug("Waiting for the task lock to be released...")

        self._pending_requests += 1

        async with self._lock:
            try:
                logger.debug(f"{self.id} -> Sending data: %s.", data)
                self._writer.write(data)
                await self._writer.drain()
            except (ConnectionError, OSError):
                logger.debug(f"{self.id} -> The connection has been terminated.")
                if not self.reconnect:
                    return Result.fail(Errors.ConnectionClosed.value)

                return await self.try_reconnect()

            result: Result = await self.wait_for_response()
            if self.reconnect and result.error == Errors.ConnectionClosed:
                return await self.try_reconnect()

            return result

    async def receive(self, timeout_limit: float | None = None) -> bytes | None:
        """
        Coroutine to receive data from the reader.

        NOT TASK SAFE.

        Parameters
        ----------
        timeout_limit:
            The maximum time in seconds to wait for a response from the server.

        Raises
        ------
        asyncio.TimeoutError
            If the timeout limit has been exceeded.
        """
        if self._reader is None:
            return logger.error(
                f"{self.id} -> Missing StreamReader object! Did you forget to connect? Aborting the receive method..."
            )
        if timeout_limit is None:
            # If there is no specified time limit, and if there is no data to receive,
            # the reader will wait for it as long as needed.
            data: bytes = await self._reader.read(self.buffer_size)
        else:
            data: bytes = await asyncio.wait_for(
                self._reader.read(self.buffer_size), timeout=timeout_limit
            )
        logger.debug(f"{self.id} -> Received data: %s.", data)
        return data

    async def wait_for_response(self) -> Result:
        """
        Coroutine to wait for a complete response from the server asynchronously.

        NOT TASK SAFE.
        """
        if not self._reader:
            return Result.fail(Errors.ConnectionClosed.value)

        complete_data: bytes = bytes()
        try:
            data: bytes | None = await self.receive(timeout_limit=self.timeout_limit)
            if data is None:
                self._connected = False
                return Result.fail(Errors.ConnectionClosed.value)
        except asyncio.TimeoutError:
            return Result.fail(Errors.TimeoutLimit.value)

        complete_data += data

        while True:
            try:
                data = await self.receive(timeout_limit=0.1)
            except asyncio.TimeoutError:
                break  # Transfer complete.
            if data is None or len(data) == 0:
                # When socket lose connection to the server it receives empty bytes.
                self._connected = False
                return Result.fail(Errors.ConnectionClosed.value)

            complete_data += data

        if self._pending_requests >= 1:
            self._pending_requests -= 1

        # If the first byte is "-", it means that the response is an error.
        if complete_data.startswith(b"-"):
            error_message: str = complete_data.decode()[1:-2]
            return Result.fail(error_message)

        return Result.ok(complete_data)

    async def close(self) -> None:
        """Closes the connection by closing the writer, and waiting until the writer is fully closed."""
        if self._writer:
            self._connected = False
            self._writer.close()
            await self._writer.wait_closed()

            self._writer = None
            self._reader = None
            self._pending_requests = 0

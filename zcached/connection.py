from __future__ import annotations

import logging

from socket import socket, SOCK_STREAM, AF_INET
from threading import Lock

from time import sleep
from string import ascii_uppercase
from random import choice

from .backoff import ExponentialBackoff
from .result import Result
from .enums import Errors


class Connection:
    """
    An object to establish and manage a connection with the database server.

    Parameters
    ----------
    host:
        The host address of the server to connect to.
    port:
        The port number of the server to connect to.
    buffer_size:
        The size of the buffer for receiving data from the server, in bytes.
        Larger values for buff_size may allow for more data to be received in a single operation,
        while smaller values can be more memory-efficient but slower.
    connection_attempts:
        The maximum number of attempts to establish a connection with the server.
        If the maximum number of attempts is exceeded, an error will be raised.
    reconnect:
        Flag indicating whether automatic reconnection attempt should be made
        in case of a broken connection.
    timeout_limit:
        The maximum time in seconds to wait for a response from the server.

    Attributes
    ----------
    socket:
        The socket object for communicating with the server.
    buffer_size:
        The size of the buffer for receiving data from the server.
    connection_attempts:
        The maximum number of attempts to establish a connection with the server.
    reconnect:
        Flag indicating whether automatic reconnection attempt should be made
        in case of a broken connection.
    timeout_limit:
        The maximum time in seconds to wait for a response from the server.
    """

    __slots__ = (
        "socket",
        "buffer_size",
        "connection_attempts",
        "reconnect",
        "timeout_limit",
        "_backoff",
        "_port",
        "_host",
        "_connected",
        "_lock",
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
    ) -> None:
        self.socket: socket = socket(AF_INET, SOCK_STREAM)
        self.buffer_size: int = buffer_size
        self.connection_attempts: int = connection_attempts

        self.reconnect: bool = reconnect
        self.timeout_limit: int = timeout_limit

        self._host: str = host
        self._port: int = port
        self._pending_requests: int = 0

        self._connected: bool = False
        self._backoff = ExponentialBackoff(0.5, 2, 3)

        self._lock: Lock = Lock()
        self._id: str = "".join([choice(ascii_uppercase) for _ in range(6)])

    def __repr__(self) -> str:
        return f"<Connection(host={self.host}, port={self.port}, buffer_size={self.buffer_size})>"

    @property
    def host(self) -> str:
        """Connection host."""
        return self._host

    @property
    def port(self) -> int:
        """Connection port."""
        return self._port

    @property
    def pending_requests(self) -> int:
        """The number of pending requests."""
        return self._pending_requests

    @property
    def id(self) -> str:
        """Unique identifier for the connection."""
        return f"#{self._id}-{self.port}"

    def is_locked(self) -> bool:
        """Whether the connection is locked."""
        return self._lock.locked()

    def is_connected(self) -> bool:
        """
        A boolean indicating whether the `connect` method was successfully invoked.

        .. note::
            This does not mean that the socket has a connection to the server.
            The socket connection may be broken, and we do not update it constantly.
        """
        return self._connected

    def connect(self) -> None:
        """
        Method to connect a socket to the database server.
        """
        logging.debug(f"{self.id} -> Connecting to {self.host}:{self.port}...")

        for attempt, timeout in enumerate(self._backoff):
            try:
                self.socket.connect((self.host, self.port))
                self.socket.setblocking(False)

                logging.info(f"{self.id} -> Connected to the server.")
                self._connected = True
                break
            except Exception as exception:
                logging.exception(exception)

                if attempt + 1 >= self.connection_attempts or not self.reconnect:
                    break

                logging.warning(f"{self.id} -> Connecting to the server failed. Retrying...")
                sleep(timeout)

    def receive(self) -> bytes | None:
        """
        Method to receive the response from the server.
        None if there is no data in the socket yet.

        NOT THREAD SAFE.
        """
        try:
            data: bytes = self.socket.recv(self.buffer_size)
            logging.debug(f"{self.id} -> Received a response -> %s", data)
        except (BlockingIOError, ConnectionAbortedError, OSError):
            return None

        return data

    def send(self, data: bytes) -> Result:
        """
        Method to send data to the server.

        THREAD SAFE.

        Parameters
        ----------
        data:
            Bytes to send.
        """
        if self._lock.locked():
            logging.debug(f"{self.id} -> Waiting for the thread lock to become available.")

        with self._lock:
            try:
                logging.debug(f"{self.id} -> Sending data to the server -> %s", data)
                self.socket.send(data)
            except (BrokenPipeError, OSError):
                if not self.reconnect:
                    return Result.fail(Errors.ConnectionClosed.value)
                return self.try_reconnect()
            finally:
                if self._pending_requests >= 1:
                    self._pending_requests -= 1

            result: Result = self.wait_for_response()
            if not self.reconnect or result.error is None:
                return result

            if result.error == Errors.ConnectionClosed:
                return self.try_reconnect()

            return result

    def try_reconnect(self) -> Result[bytes]:
        """
        A method to attempt to reconnect to the server if the connection is broken.

        .. note::
            If the connection is successfully reestablished, the method return a Result object
            with a failure status and an informational message indicating that the connection
            was terminated but managed to reestablish it.
        """
        logging.debug(f"{self.id} -> Attempting to reconnect to the server...")

        self.socket: socket = socket(AF_INET, SOCK_STREAM)
        self._connected = False
        self.connect()

        if self.is_connected() is True:
            return Result.fail(Errors.ConnectionReestablished.value)

        return Result.fail(Errors.ConnectionClosed.value)

    def wait_for_response(self) -> Result:
        """
        A loop to wait for the response from the server.

        NOT THREAD SAFE.
        """
        backoff: ExponentialBackoff = ExponentialBackoff(0.01, 3, 0.5)
        total_data: bytes = bytes()

        # By doing this, we should receive the data at the first recv, without waiting for the backoff.
        sleep(0.001)

        for timeout in backoff:
            data: bytes | None = self.receive()

            if not isinstance(data, bytes):
                if backoff.total >= self.timeout_limit:
                    return Result.fail(Errors.TimeoutLimit.value)

                logging.debug(f"{self.id} -> There is no data in the socket. Timeout: {timeout}s.")
                sleep(timeout)
                continue

            if len(data) == 0:  # type: ignore
                # When socket lose connection to the server it receives empty bytes.
                return Result.fail(Errors.ConnectionClosed.value)

            total_data += data  # type: ignore

            if total_data.endswith(b"\x03"):  # Received complete data.
                # If the first byte is "-", it means that the response is an error.
                if total_data.startswith(b"-"):
                    error_message: str = total_data.decode()[1:-3]
                    return Result.fail(error_message)

                return Result.ok(total_data[:-1])

            # ExponentialBackoff should be increased only when we receive None.
            backoff.reset()

        # This should never happen, but the type checker yells.
        return Result.fail(Errors.LibraryBug.value)

    def close(self) -> None:
        """Method to close the connection."""
        self._connected = False
        self.socket.close()

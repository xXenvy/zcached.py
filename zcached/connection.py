from __future__ import annotations

import logging

from socket import socket, SOCK_STREAM, AF_INET
from threading import Lock
from time import sleep

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
    buff_size:
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
    )

    def __init__(
        self,
        host: str,
        port: int,
        connection_attempts: int,
        reconnect: bool,
        timeout_limit: int,
        buffer_size: int,
    ):
        self.socket: socket = socket(AF_INET, SOCK_STREAM)
        self.buffer_size: int = buffer_size
        self.connection_attempts: int = connection_attempts

        self.reconnect: bool = reconnect
        self.timeout_limit: int = timeout_limit

        self._host: str = host
        self._port: int = port

        self._connected: bool = False
        self._backoff = ExponentialBackoff(0.5, 2, 3)
        self._lock: Lock = Lock()

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
        logging.debug(f"Connecting to {self.host}:{self.port}...")

        for attempt, timeout in enumerate(self._backoff):
            try:
                self.socket.connect((self.host, self.port))
                self.socket.setblocking(False)

                logging.info("Connected to the server.")
                self._connected = True
                break
            except Exception as exception:
                if attempt + 1 >= self.connection_attempts:
                    break

                logging.exception(exception)
                logging.warning("Connecting to the server failed. Retrying...")
                sleep(timeout)

    def receive(self) -> bytes | None:
        """
        Method to receive the response from the server.
        None if there is no data in the socket yet.
        """
        try:
            data: bytes = self.socket.recv(self.buffer_size)
            logging.debug("Received a response -> %s", data)
        except (BlockingIOError, ConnectionAbortedError):
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
            logging.debug("Waiting for the thread lock to become available.")

        with self._lock:

            try:
                logging.debug("Sending data to the server -> %s", data)
                self.socket.send(data)
            except (BrokenPipeError, OSError):
                if not self.reconnect:
                    return Result.fail(Errors.ConnectionClosed.value)

                return self.try_reconnect()

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
        logging.debug("Attempting to reconnect to the server...")

        self.socket: socket = socket(AF_INET, SOCK_STREAM)
        self._connected = False
        self.connect()

        if self.is_connected is True:
            return Result.fail(Errors.ConnectionReestablished.value)

        return Result.fail(Errors.ConnectionClosed.value)

    def wait_for_response(self) -> Result:
        """
        A loop to wait for the response from the server.

        NOT THREAD SAFE.
        """
        backoff: ExponentialBackoff = ExponentialBackoff(0.1, 1.5, 0.5)
        total_bytes: bytes = bytes()

        # Without this, the backoff will have to wait on the first iteration.
        sleep(0.01)

        for timeout in backoff:
            data: bytes | None = self.receive()

            if not isinstance(data, bytes):
                if len(total_bytes) >= 1:
                    logging.debug("Received incomplete data. Awaiting for the rest.")
                else:
                    # We haven't received any data yet.
                    logging.debug(
                        f"There is no data in the socket. Timeout: {timeout}s."
                    )

                if backoff.total >= float(self.timeout_limit):
                    logging.error(
                        "The waiting time limit for a response has been reached."
                    )
                    return Result.fail(Errors.TimeoutLimit.value)

                sleep(timeout)
                continue

            if len(data) == 0:  # type: ignore
                # When socket lose connection to the server it receives empty bytes.
                return Result.fail(Errors.ConnectionClosed.value)

            total_bytes += data  # type: ignore

            if total_bytes.endswith(b'\x04'):  # Received complete data.

                # If the first byte is "-", it means that the response is an error.
                if total_bytes.startswith(b"-"):
                    error_message: str = total_bytes[1:-1].decode()
                    return Result.fail(error_message.replace("\r\n", ""))

                return Result.ok(total_bytes[:-1])

            # ExponentialBackoff should be increased only when we receive None.
            backoff.reset()

        # This should never happen, but the type checker yells.
        return Result.fail(Errors.LibraryBug.value)

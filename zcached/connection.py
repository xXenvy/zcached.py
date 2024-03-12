from __future__ import annotations

import logging
from socket import socket, SOCK_STREAM, AF_INET

from time import sleep

from .backoff import ExponentialBackoff
from .result import Result


class Connection:
    """
    An object to establish and manage a connection with the database server.

    Parameters
    ----------
    host:
        The host address of the server to connect to.
    port:
        The port number of the server to connect to.
    backoff:
        An exponential backoff strategy used for the initial connection attempt.
    buff_size:
        The size of the buffer for receiving data from the server, in bytes.
        Larger values for buff_size may allow for more data to be received in a single operation,
        while smaller values can be more memory-efficient but slower.
    connection_attempts:
        The maximum number of attempts to establish a connection with the server.
        If the maximum number of attempts is exceeded, an error will be raised.

    Attributes
    ----------
    socket: :class:`socket`
        The socket object for communicating with the server.
    buff_size: :class:`int`
        The size of the buffer for receiving data from the server.
    connection_attempts:
        The maximum number of attempts to establish a connection with the server.
    """

    __slots__ = (
        "socket",
        "buff_size",
        "connection_attempts",
        "_backoff",
        "_port",
        "_host",
        "_connected",
    )

    def __init__(
        self,
        host: str,
        port: int,
        backoff: ExponentialBackoff = ExponentialBackoff(0.5, 2, 4),
        buff_size: int = 1024,
        connection_attempts: int = 5,
    ):
        self.socket: socket = socket(AF_INET, SOCK_STREAM)
        self.buff_size: int = buff_size
        self.connection_attempts: int = connection_attempts

        self._host: str = host
        self._port: int = port

        self._connected: bool = False
        self._backoff: ExponentialBackoff = backoff

    def __repr__(self) -> str:
        return f"<Connection(host={self.host}, port={self.port}, buff_size={self.buff_size})>"

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
            The socket connection may be dropped, and we don't update it.
        """
        return self._connected

    def connect(self) -> None:
        """
        Method to connect a socket to a database server.

        Raises
        ------
        RuntimeError
            The method has already been called once successfully.
        """
        if self._connected:
            raise RuntimeError("The connection has already been established once.")

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
                    raise exception

                logging.exception(exception)
                logging.warning("Connecting to the server failed. Retrying...")
                sleep(timeout)

    def receive(self) -> bytes | None:
        """
        Method to receive the response from the server.
        None if the server didn't receive any data yet.
        """
        try:
            data: bytes = self.socket.recv(self.buff_size)
            logging.debug("Received a response -> %s", data)
        except BlockingIOError:
            return None

        return data

    def send(self, data: bytes) -> Result:
        """
        Method to send data to the server.

        Parameters
        ----------
        data: :class:`bytes`
            Data to send.
        """
        try:
            logging.debug("Sending data to the server -> %s", data)
            self.socket.send(data)
        except BrokenPipeError as exception:
            # This exception occurs when the socket has no connection to the database server.
            # We do not call it because the `wait_for_response` method will return Result with this error.
            logging.exception(exception)

        return self.wait_for_response()

    def wait_for_response(self) -> Result:
        """A loop to wait for the response from the server."""
        backoff: ExponentialBackoff = ExponentialBackoff(0.1, 1.5, 0.5)

        total_bytes: bytes = bytes()
        transfer_complete: bool = False

        for timeout in backoff:
            data: bytes | None = self.receive()

            if not isinstance(data, bytes):
                if len(total_bytes) > 0:
                    # If we already have some data, and this iteration gave us None,
                    # it means that the data transfer has been completed.
                    transfer_complete = True
                else:
                    # We haven't received any data yet.
                    logging.debug(
                        f"There is no data in the socket. Timeout: {timeout}s."
                    )
                    sleep(timeout)
                    continue

            if transfer_complete:
                # If the first byte is "-", it means that the response is an error.
                if total_bytes.startswith(b"-"):
                    return Result.fail(total_bytes.decode())

                return Result.ok(total_bytes)

            if len(data) == 0:  # type: ignore
                # When socket lose connection to the server it receives empty bytes.
                return Result.fail("The connection has been terminated.")

            total_bytes += data  # type: ignore

            # ExponentialBackoff should be increased only when we receive None.
            backoff.reset()

        # This should never happen, but the type checker yells.
        return Result.fail(
            "This is probably a bug. Please report it here: https://github.com/xXenvy/zcached.py"
        )

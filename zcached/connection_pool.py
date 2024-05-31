from __future__ import annotations

from threading import Thread
import logging as logger

from typing import TYPE_CHECKING, List, Callable, Iterable, Any
from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from .connection import Connection

Param = ParamSpec("Param")


class ConnectionPool:
    """
    A pool of connections.

    Parameters
    ----------
    pool_size:
        The maximum size of the connection pool.
    connection_factory:
        A callable that returns a new instance of Connection.
    """

    __slots__ = ("_pool_size", "_connection_factory", "_connections")

    def __init__(
        self,
        pool_size: int,
        connection_factory: Callable[[], Connection],
    ) -> None:
        self._pool_size: int = pool_size
        self._connection_factory: Callable[[], Connection] = connection_factory
        self._connections: List[Connection] = []

        logger.info(f"Initiated a new connection pool. Pool size: {self._pool_size}.")

    def __repr__(self) -> str:
        return f"<ConnectionPool(size={self._pool_size}, connected_connections={len(self.connected_connections)})>"

    @property
    def connections(self) -> List[Connection]:
        """List of all connections in the pool."""
        return self._connections

    @property
    def connected_connections(self) -> List[Connection]:
        """List of all connected connections in the pool."""
        return list(filter(lambda conn: conn.is_connected(), self._connections))

    @property
    def broken_connections(self) -> List[Connection]:
        """List of all broken (not connected) connections in the pool."""
        return list(filter(lambda conn: not conn.is_connected(), self._connections))

    @property
    def pool_size(self) -> int:
        """The maximum size of the connection pool."""
        return self._pool_size

    @property
    def connection_factory(self) -> Callable[[], Connection]:
        """The factory function to create a new connection."""
        return self._connection_factory

    def is_working(self) -> bool:
        """True if there is any working connection in the pool."""
        return len(self.connected_connections) > 0

    def is_empty(self) -> bool:
        """True if the pool is empty."""
        return len(self.connections) == 0

    def is_full(self) -> bool:
        """True if the pool is full."""
        return len(self.connections) == self._pool_size

    def setup(self) -> None:
        """Creates connections in the pool and connects them."""
        self._connections.clear()
        logger.info("Filling the connection pool.")

        threads: List[Thread] = []

        for _ in range(self._pool_size):
            connection: Connection = self._connection_factory()
            self._connections.append(connection)

            thread: Thread = self.run_in_thread(func=connection.connect)
            threads.append(thread)

        for t in threads:
            # Waiting for all threads.
            t.join()

    def close(self) -> None:
        """Closes all connected connections in the pool."""
        logger.info("Closing: %s connections in the pool", len(self.connected_connections))
        for connection in self.connected_connections:
            self.run_in_thread(func=connection.close)
            # We don't care about result.

        self._connections.clear()

    def extend_pool_by_size(self, size: int) -> None:
        """
        Extends the pool by a specified number of connections.
        The pool size will be increased if necessary.

        Parameters
        ----------
        size:
            The number of connections to add to the pool.
        """
        return self.extend_pool_by_connections([self._connection_factory() for _ in range(size)])

    def extend_pool_by_connections(self, connections: Iterable[Connection]) -> None:
        """
        Extends the pool with existing connections.
        The pool size will be increased if necessary.

        Parameters
        ----------
        connections:
            An iterable of existing connections to add to the pool.
        """
        threads: list[Thread] = [self.run_in_thread(func=conn.connect) for conn in connections]

        self._connections.extend(connections)
        self._pool_size = len(self._connections)

        for thread in threads:
            thread.join()

        logger.debug("Extended connection pool. New size: %s.", self._pool_size)

    def reconnect(self, only_broken_connections: bool = True) -> int:
        """
        Attempts to reconnect connections in the pool.
        Returns the number of connected connections after reconnection.

        Parameters
        ----------
        only_broken_connections:
            If True, attempts to reconnect only broken connections.
        """
        logger.debug(
            "Reconnecting connection pool. Only broken connections: %s.",
            only_broken_connections,
        )
        connections: List[Connection] = (
            self.broken_connections if only_broken_connections else self.connections
        )
        threads: List[Thread] = [self.run_in_thread(func=conn.try_reconnect) for conn in connections]

        for thread in threads:
            thread.join()

        return len(self.connected_connections)

    def reduce_pool_connections(self, amount: int, delete_pending_connections: bool = False) -> None:
        """
        Reduces the size of the connection pool by a specified amount.
        By default, the method first removes non-working connections,
        when this is not enough it takes connections that have 0 pending requests and removes them too.
        If a connection has any pending requests, it doesn't delete it, well,
        unless the delete_pending_connections parameter is on True.

        Parameters
        ----------
        amount:
            The number of connections to remove from the pool.
        delete_pending_connections:
            If True, the method will also delete, when necessary, connections that have pending requests.
            This is not strongly recommended!
        """
        logger.debug(
            "Reducing the pool connections. Amount: %s, pending: %s.",
            amount,
            delete_pending_connections,
        )
        if amount <= 0:
            return

        self._pool_size -= amount
        if 0 > self._pool_size:
            self._pool_size = 0

        if self._pool_size >= len(self.connections):
            return

        # First, let's get rid of the non-working connections.
        for broken_connection in self.broken_connections:
            self._connections.remove(broken_connection)

            # We don't care about this task, let's run this in background.
            self.run_in_thread(func=broken_connection.close)
            if self._pool_size >= len(self.connections):
                return

        for _ in range(len(self.connected_connections)):
            try:
                connection: Connection = self.get_least_loaded_connection()
            except IndexError:
                break  # There are no other connections.

            if connection.pending_requests == 0 or delete_pending_connections:
                self._connections.remove(connection)

                # We don't care about this task, let's run this in background.
                self.run_in_thread(func=connection.close)

                if self._pool_size >= len(self.connections):
                    return

        self._pool_size = len(self.connections)

    def cleanup_broken_connections(self) -> None:
        """Closes broken connections and removes them from the list of connections."""
        logger.info("Clearing non-working connections...")
        if not self.broken_connections:
            return

        for broken_connection in self.broken_connections:
            self.run_in_thread(func=broken_connection.close)
            self._connections.remove(broken_connection)

    def get_least_loaded_connection(self) -> Connection:
        """
        Get the least loaded connection from the pool.
        Only working connections are considered.

        Raises
        ------
        IndexError
            If the pool is empty.
        """
        connections: List[Connection] = self.connected_connections
        connections.sort(key=lambda connection: connection.pending_requests)
        return connections[0]

    @staticmethod
    def run_in_thread(func: Callable[Param, Any], *args: Param.args, **kwargs: Param.kwargs) -> Thread:
        """
        Method to run function in thread.

        Parameters
        ----------
        func:
            A function to run in the thread.
        args:
            Function args.
        kwargs:
            Function kwargs.
        """
        thread: Thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

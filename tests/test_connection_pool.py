import pytest

from zcached import ConnectionPool, Connection


def test_connection_pool():
    pool: ConnectionPool = ConnectionPool(
        pool_size=2,
        connection_factory=lambda: Connection(
            host="127.0.0.1",
            port=1234,
            connection_attempts=0,
            reconnect=False,
            timeout_limit=1,
            buffer_size=4096,
        ),
    )
    assert (len(pool.connections), len(pool.broken_connections)) == (0, 0)
    assert pool.pool_size == 2
    assert not pool.is_working() and not pool.is_full() and pool.is_empty()

    pool.close()
    assert (len(pool.connections), len(pool.connected_connections)) == (0, 0)
    assert isinstance(pool.connection_factory(), Connection)

    pool.setup()
    assert (len(pool.connections), len(pool.connected_connections)) == (2, 0)

    pool.reduce_pool_connections(1)
    assert pool.pool_size == 1
    assert (len(pool.connections), len(pool.broken_connections)) == (1, 1)

    pool.cleanup_broken_connections()
    assert pool.pool_size == 1
    assert (len(pool.connections), len(pool.broken_connections)) == (0, 0)

    pool.extend_pool_by_size(size=1)
    assert pool.pool_size == 1
    assert (len(pool.connections), len(pool.broken_connections)) == (1, 1)

    pool.reconnect()
    assert (len(pool.connections), len(pool.broken_connections)) == (1, 1)

    with pytest.raises(IndexError):
        pool.get_least_loaded_connection()

    pool.reduce_pool_connections(amount=-5)
    assert (len(pool.connections), len(pool.broken_connections)) == (1, 1)
    pool.cleanup_broken_connections()


def test_connection_pool_factory():
    pool: ConnectionPool = ConnectionPool(
        pool_size=0,
        connection_factory=lambda: Connection(
            host="192.168.127.12",
            port=9595,
            connection_attempts=0,
            reconnect=False,
            timeout_limit=1,
            buffer_size=128,
        ),
    )
    factory = pool.connection_factory

    connection: Connection = factory()
    assert connection.is_connected() is False
    assert connection.port == 9595 and connection.host == "192.168.127.12"
    assert connection.connection_attempts == 0 and connection.reconnect is False
    assert connection.timeout_limit == 1 and connection.buffer_size == 128

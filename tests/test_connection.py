from zcached import Connection, ZCached


def test_connection():
    connection = Connection(
        host="localhost",
        port=5555,
        connection_attempts=2,
        buffer_size=512,
        reconnect=False,
        timeout_limit=5,
    )

    assert connection.host == "localhost"
    assert connection.timeout_limit == 5
    assert connection.port == 5555
    assert connection.buffer_size == 512
    assert connection.connection_attempts == 2
    assert connection.is_connected is False
    assert connection.socket.getblocking() is True

    connection.connect()
    assert connection.is_connected is False

    client = ZCached.from_connection(connection)

    assert client.connection.receive() is None

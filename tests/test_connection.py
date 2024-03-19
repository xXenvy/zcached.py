import pytest
from zcached import Connection, Result, ZCached

IS_SERVER_RUNNING = False


def test_connection():
    connection = Connection(
        host="localhost", port=5555, connection_attempts=2, buff_size=2, reconnect=False
    )

    assert connection.host == "localhost"
    assert connection.port == 5555
    assert connection.buff_size == 2
    assert connection.connection_attempts == 2
    assert connection.is_connected is False
    assert connection.socket.getblocking() is True

    if not IS_SERVER_RUNNING:
        connection.connect()
        assert not connection.is_connected

        with pytest.raises(OSError):
            connection.receive()
        with pytest.raises(OSError):
            connection.wait_for_response()
    else:
        connection.connect()
        assert connection.is_connected is True

        client = ZCached.from_connection(connection)

        for _ in range(5):
            result: Result[str] = client.ping()
            assert result.success and result.value == "PONG"
            assert not result.is_empty()

        assert client.connection.receive() is None

        result = client.set(
            "randomkey",
            {
                "key": "value1",
                "key2": 1233,
                "key3": -32,
                "key4": 5.4,
                "key5": True,
                "key6": False,
                "key7": None,
                "key8": ["abc", 123, False, None, True, {"a": "b", "c": "d"}],
                "key9": "4343434343",
                "key10": (-50, -60, -70, None),
            },
        )
        assert result.error is None
        assert result.value == "OK"
        client.flush()

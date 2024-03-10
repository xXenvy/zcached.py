import pytest
from zcached import Connection, Result

IS_SERVER_RUNNING = False


def test_connection():
    connection = Connection(host="localhost", port=5555, connection_attempts=2, buff_size=2)

    assert connection.host == "localhost"
    assert connection.port == 5555
    assert connection.buff_size == 2
    assert connection.connection_attempts == 2
    assert connection.is_connected is False
    assert connection.socket.getblocking() is True

    if not IS_SERVER_RUNNING:
        with pytest.raises(ConnectionRefusedError):
            connection.connect()
        with pytest.raises(OSError):
            connection.receive()
        with pytest.raises(OSError):
            connection.wait_for_response()
    else:
        connection.connect()
        assert connection.is_connected is True

        with pytest.raises(RuntimeError):
            connection.connect()

        for _ in range(5):
            result: Result = connection.send(b"*1\r\n$4\r\nPING\r\n")
            assert result.success and bytes(result) == b'+PONG\r\n'

        assert connection.receive() is None


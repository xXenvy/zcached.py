import pytest

from zcached.asyncio import AsyncConnection
from zcached import Errors
from asyncio import StreamReaderProtocol


@pytest.mark.asyncio
async def test_connnection():

    class MyProtocol(StreamReaderProtocol):
        @staticmethod
        def always_true() -> bool:
            return True

    connection: AsyncConnection[MyProtocol] = AsyncConnection(
        host="127.0.0.1",
        port=1234,
        connection_attempts=0,
        reconnect=False,
        timeout_limit=0,
        buffer_size=256,
        protocol_type=MyProtocol,
    )
    assert connection.protocol_type.always_true() is True
    assert connection.protocol is None

    assert (connection.host, connection.port) == ("127.0.0.1", 1234)
    assert connection.connection_attempts == 0 and connection.reconnect is False
    assert connection.buffer_size == 256 and connection.timeout_limit == 0
    assert (connection.reader, connection.writer) == (None, None)
    assert (connection.transport, connection.protocol) == (None, None)
    assert connection.pending_requests == 0

    await connection.connect()

    with pytest.raises(ConnectionError):
        await connection.open_connection(host=connection.host, port=connection.port)

    assert (await connection.try_reconnect()).error == Errors.ConnectionClosed
    assert (await connection.send(b"DOG")).error == Errors.ConnectionClosed
    assert (await connection.wait_for_response()).error == Errors.ConnectionClosed
    assert await connection.receive(0) is None
    assert connection.is_locked is False

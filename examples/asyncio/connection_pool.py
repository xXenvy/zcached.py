import asyncio
import typing

from zcached.asyncio import AsyncZCached, AsyncConnectionPool, AsyncConnection
from zcached import Result


async def main():
    connection_pool = AsyncConnectionPool(
        # Connections in the pool. If we do not send a large number of requests, we can use only one.
        pool_size=1,
        # Some function that does not take any arguments, but returns the created connection.
        connection_factory=lambda: AsyncConnection(host="127.0.0.1", port=7556),
    )

    client: AsyncZCached = AsyncZCached.from_connection_pool(connection_pool)
    await client.run()

    response: Result[typing.List[str]] = await client.keys()
    if response.error:
        raise RuntimeError(response.error)

    print(response.value)


if __name__ == "__main__":
    asyncio.run(main())

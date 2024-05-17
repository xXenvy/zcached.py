import asyncio
import typing

from zcached.asyncio import AsyncZCached


class MyProtocol(asyncio.StreamReaderProtocol):  # Our protocol must inherit from the StreamReaderProtocol.

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Called when we made a connection to the server."""
        super().connection_made(transport)  # Calling the original method.

        # Our custom logic:
        host, port = transport.get_extra_info("peername")
        print(f"Connected with: {host}:{port}")

    def connection_lost(self, exc: typing.Optional[Exception]) -> None:
        """Called when we lost the connection."""
        super().connection_lost(exc)  # Calling the original method.

        # Our custom logic:
        print("Connection lost!")
        if exc is not None:
            print(f"Raised exception: {exc}")


async def main():
    client: AsyncZCached = AsyncZCached(host="127.0.0.1", port=7556, protocol_type=MyProtocol)
    await client.run()


if __name__ == "__main__":
    asyncio.run(main())

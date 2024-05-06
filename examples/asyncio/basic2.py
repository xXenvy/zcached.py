import asyncio

from typing import List
from zcached.asyncio import AsyncZCached
from zcached import Result


async def main():
    client: AsyncZCached = AsyncZCached(host="127.0.0.1", port=7556)
    await client.run()

    if not await client.is_alive():
        raise RuntimeError("Something went wrong :(")

    await client.set(key="dogs", value=["Pimpek", "Laika", "Pimpcio"])
    response: Result[List[str]] = await client.get(key="dogs")

    print(f"Result: {response.value}")
    print(f"Error: {response.error}")


if __name__ == '__main__':
    asyncio.run(main())

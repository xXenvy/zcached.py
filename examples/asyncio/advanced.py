import asyncio

from zcached.asyncio import AsyncZCached
from zcached import Result

from typing import TypedDict, List


class Item(TypedDict):
    name: str
    description: str
    price: float
    quantity: int


class ShopManager(AsyncZCached):

    async def set_items(self, items: List[Item]) -> str:
        if not await self.is_alive():
            raise RuntimeError("Something went wrong :(")

        result: Result[str] = await self.set(key="items", value=items)
        if not result:
            raise RuntimeError(result.error)

        return result.value

    async def get_items(self) -> List[Item]:
        if not self.is_alive():
            raise RuntimeError("Connection closed.")

        result: Result[List[Item]] = await self.get(key="items")
        if not result:
            raise RuntimeError(result.error)

        return result.value

    async def get_total_quantity(self) -> int:
        return sum([item["quantity"] for item in await self.get_items()])

    async def get_total_cost(self) -> float:
        return sum([item["price"] for item in await self.get_items()])


async def main():
    manager = ShopManager(host="127.0.0.1", port=7556)
    await manager.run()
    await manager.set_items(
        [
            Item(name="foo", description="test", price=50.99, quantity=1),
            Item(name="bar", description="test123", price=89.99, quantity=5),
        ]
    )
    print(await manager.get_items())
    print(await manager.get_total_quantity())
    print(await manager.get_total_cost())
    await manager.flush()

if __name__ == "__main__":
    asyncio.run(main())

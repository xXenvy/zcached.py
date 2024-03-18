from zcached import ZCached, Result
from typing import TypedDict, List


class Item(TypedDict):
    name: str
    description: str
    price: float
    quantity: int


class ShopManager(ZCached):

    def set_items(self, items: list[Item]) -> str:
        if not self.is_alive():
            raise RuntimeError("Connection closed.")

        result: Result[str] = self.set(key="items", value=items)

        if error := result.error:
            raise RuntimeError(error)

        return result.value

    def get_items(self) -> List[Item]:
        if not self.is_alive():
            raise RuntimeError("Connection closed.")

        result: Result[List[Item]] = self.get(key="items")

        if error := result.error:
            raise RuntimeError(error)

        return result.value

    def get_total_quantity(self) -> int:
        items: List[Item] = self.get_items()
        return sum([item["quantity"] for item in items])


if __name__ == "__main__":
    manager = ShopManager(host="localhost", port=5555)
    manager.set_items(
        [
            Item(name="foo", description="test", price=50, quantity=1),
            Item(name="bar", description="test123", price=90, quantity=5),
        ]
    )
    print(manager.get_items())
    print(manager.get_total_quantity())
    manager.flush()

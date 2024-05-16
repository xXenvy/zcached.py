Advanced
===============

.. code-block:: python
   :caption: advanced.py
   :linenos:

   from zcached import ZCached, Result
   from typing import TypedDict, List


   class Item(TypedDict):
       name: str
       description: str
       price: float
       quantity: int


   class ShopManager(ZCached):

       def set_items(self, items: List[Item]) -> str:
           if not self.is_alive():
               raise RuntimeError("Connection closed.")

           result: Result[str] = self.set(key="items", value=items)
           if not result:
               raise RuntimeError(result.error)

           return result.value

       def get_items(self) -> List[Item]:
           if not self.is_alive():
               raise RuntimeError("Connection closed.")

           result: Result[List[Item]] = self.get(key="items")
           if not result:
               raise RuntimeError(result.error)

           return result.value

       def get_total_quantity(self) -> int:
           return sum([item["quantity"] for item in self.get_items()])

       def get_total_cost(self) -> float:
           return sum([item["price"] for item in self.get_items()])


   if __name__ == "__main__":
       manager = ShopManager(host="127.0.0.1", port=7556)
       manager.run()
       manager.set_items(
           [
            Item(name="foo", description="test", price=50.99, quantity=1),
            Item(name="bar", description="test123", price=89.99, quantity=5),
           ]
       )
       print(manager.get_items())
       print(manager.get_total_quantity())
       print(manager.get_total_cost())
       manager.flush()

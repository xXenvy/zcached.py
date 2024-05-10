Async Basic
===============

.. code-block:: python
   :caption: basic.py
   :linenos:

   import asyncio
   from zcached.asyncio import AsyncZCached
   from zcached import Result


   async def main():
       client: AsyncZCached = AsyncZCached(host="127.0.0.1", port=7556)
       await client.run()

       response: Result[str] = await client.ping()
       if response.error:
           raise RuntimeError(response.error)

       print(response.value)


   if __name__ == "__main__":
       asyncio.run(main())


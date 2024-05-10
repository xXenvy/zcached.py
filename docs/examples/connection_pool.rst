ConnectionPool
===============

.. code-block:: python
   :caption: connection_pool.py
   :linenos:

   import typing
   from zcached import Result, ZCached, Connection, ConnectionPool


   def main():
       connection_pool = ConnectionPool(
           # Connections in the pool. If we do not send a large number of requests, we can use only one.
           pool_size=1,
           # Some function that does not take any arguments, but returns the created connection.
           connection_factory=lambda: Connection(host="127.0.0.1", port=7556),
       )

       client: ZCached = ZCached.from_connection_pool(connection_pool)
       client.run()

       response: Result[typing.List[str]] = client.keys()
       if response.error:
           raise RuntimeError(response.error)

       print(response.value)


   if __name__ == "__main__":
       main()

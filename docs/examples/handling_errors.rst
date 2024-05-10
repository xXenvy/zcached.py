Handling Errors
===============

.. code-block:: python
   :caption: handling_errors.py
   :linenos:

   from zcached import ZCached, Result, Errors

   client = ZCached(host="localhost", port=1234)
   client.run()


   def handle_error(error_message: str) -> None:
       if error_message == Errors.ConnectionReestablished:
           return  # The connection was dropped, but managed to restore it.
       if error_message == Errors.NoAvailableConnections:
           connections: int = client.connection_pool.reconnect()
           if connections >= 1:  # It was able to connect the broken connections.
               return
       raise RuntimeError(error_message)


   result: Result[str] = client.get("key123")
   if result.error:
       handle_error(error_message=result.error)

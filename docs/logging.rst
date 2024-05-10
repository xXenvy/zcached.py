Logging
===============
A basic method of logging the lib.

.. code-block:: python
   :caption: logging.py
   :linenos:
   :emphasize-lines: 2, 4

   from zcached import ZCached, Result
   import logging

   logging.basicConfig(level=logging.DEBUG)

   client = ZCached(host="localhost", port=1234)
   client.run()

   result: Result[str] = client.ping()

   if not result:
       print("Error!")
       print(result.error)
   else:
       print("Ok!")
       print(result.value)

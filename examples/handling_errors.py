from typing import Union
from zcached import ZCached, Result, Errors

client = ZCached(host="localhost", port=1234)
client.run()


def handle_error(error_message: str) -> None:
    if error_message == Errors.ConnectionReestablished:
        return  # The connection was dropped, but managed to restore it.
    raise RuntimeError(error_message)


result: Result[str] = client.get("key123")
if result.error:
    handle_error(error_message=result.error)

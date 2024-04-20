from typing import Union
from zcached import ZCached, Result, Errors

client = ZCached(host="localhost", port=1234)
client.run()


def handle_error(error_message: str, key: Union[str, None] = None) -> None:
    if error_message == Errors.ConnectionClosed:
        raise ConnectionError("Connection closed.")
    if error_message == Errors.ConnectionReestablished:
        return  # The connection was dropped, but managed to restore it.
    if key and error_message == Errors.not_found(key):
        raise RuntimeError("Key not found.")


result: Result[str] = client.get("key123")
if result.error:
    handle_error(error_message=result.error, key="key123")

import threading
from zcached import ZCached, Result


def worker(worker_id: int, zcached: ZCached) -> None:
    result: Result[str] = zcached.ping()
    print(f"Worker {worker_id} | {result.value}")


client = ZCached(host="localhost", port=1234)
client.run()

if not client.is_alive():
    raise RuntimeError("Something went wrong :(")

threads = [threading.Thread(target=worker, args=(1, client)) for _ in range(5)]
for thread in threads:
    thread.start()


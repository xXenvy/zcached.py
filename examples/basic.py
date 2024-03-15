from zcached import ZCached, Result

client = ZCached(host="localhost", port=1234)
result: Result[str] = client.ping()

if result.error:
    print("Error!")
    print(result.error)
else:
    print("Ok!")
    print(result.value)

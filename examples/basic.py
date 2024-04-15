from zcached import ZCached, Result

client = ZCached(host="localhost", port=1234)
client.run()

result: Result[str] = client.ping()

if not result:
    print("Error!")
    print(result.error)
else:
    print("Ok!")
    print(result.value)

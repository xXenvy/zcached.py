from zcached import ZCached, Connection, Result

connection = Connection(host="localhost", port=5555)
client: ZCached[Connection] = ZCached(connection)

result: Result = client.ping()

if result.error:
    print("Error!")
    print(result.error)
else:
    print("Ok!")
    print(result.value)

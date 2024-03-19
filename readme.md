# Zcached.py - A client-side library for zcached.

![commits](https://img.shields.io/github/commit-activity/w/xXenvy/zcached.py?style=for-the-badge&color=%2315b328)
![license](https://img.shields.io/github/license/xXenvy/zcached.py?style=for-the-badge&color=%2315b328)

## `📜` Introduction
Zcached.py is a Python client-side library designed to interact with zcached, a high-performance caching system.
This library provides developers easy-to-use interface for integrating zcached into their Python applications, enabling efficient data caching.

For more information, please see [zcached repository](https://github.com/sectasy0/zcached).

## `🌟` Features
- **Simplified Caching:** Zcached.py simplifies the process of caching data by providing intuitive functions for storing and retrieving values.
- **Efficient Communication:** The library optimizes communication with the zcached server, ensuring minimal overhead and efficient data transfer.
- **Properly Typehinted:** The codebase of zcached.py is properly typehinted, enhancing code readability.

## `🔧` Installation
> [!IMPORTANT]  
> **Library requires python version 3.8 or newer.** (Older should also work, but untested).

Before installing zcached.py, ensure that you have the zcached server. Instructions for installing the server can be found [here](https://github.com/sectasy0/zcached).

Once the zcached server is installed, you can proceed to install zcached.py using pip:
```shell
pip install -U zcached.py
```

## `🖊️` Usage
Here's a basic example demonstrating how to use zcached.py in your Python code:
```py
from zcached import ZCached, Result

client = ZCached(host="localhost", port=1234)

result: Result[str] = client.ping()
print(result.value)
```
**See more examples [here](https://github.com/xXenvy/zcached.py/tree/master/examples)**

## `👥` Contributing
Contributions to zcached.py are welcome!
If you encounter any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.

## `📕` License
Zcached.py is licensed under the MIT License.

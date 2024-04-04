from enum import Enum


class Errors(str, Enum):
    ConnectionClosed = "The connection has been terminated."
    ConnectionReestablished = "The connection was terminated, but managed to reestablish it."
    LibraryBug = "This is probably a bug. Please report it here: https://github.com/xXenvy/zcached.py"
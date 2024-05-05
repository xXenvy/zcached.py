from enum import Enum

from .protocol import Serializer, SupportedTypes


class Errors(str, Enum):
    ConnectionClosed = "The connection has been terminated."
    ConnectionReestablished = (
        "The connection was terminated, but managed to reestablish it."
    )
    LibraryBug = "This is probably a library bug. Please report it here: https://github.com/xXenvy/zcached.py"
    TimeoutLimit = "The waiting time limit for a response has been reached."
    NoAvailableConnections = "No working connections available."

    # Server side errors:
    BadRequest = "ERR bad request"
    UnExpected = "ERR unexpected"
    MaxClientsReached = "ERR max number of clients reached"
    BulkTooLarge = "ERR bulk too large"
    NotWhitelisted = "ERR not whitelisted"
    KeyNotString = "TYPERR key not string"
    NotBoolean = "TYPERR not boolean"
    NotInteger = "TYPERR not integer"
    SaveFailure = "ERR there is no data to save"

    @staticmethod
    def not_found(key: str) -> str:
        """Generates an error message for a key that was not found."""
        return f"ERR '{key}' not found"

    @staticmethod
    def unknown_command(name: str) -> str:
        """Generates an error message for an unknown command."""
        return f"ERR unknown command '{name}'"


class Commands(bytes, Enum):
    PING = b"*1\r\n$4\r\nPING\r\n\x04"
    FLUSH = b"*1\r\n$5\r\nFLUSH\r\n\x04"
    DB_SIZE = b"*1\r\n$6\r\nDBSIZE\r\n\x04"
    SAVE = b"*1\r\n$4\r\nSAVE\r\n\x04"
    KEYS = b"*1\r\n$4\r\nKEYS\r\n\x04"
    LAST_SAVE = b"*1\r\n$8\r\nLASTSAVE\r\n\x04"

    @staticmethod
    def get(key: str) -> bytes:
        return f"*2\r\n$3\r\nGET\r\n${len(key)}\r\n{key}\r\n\x04".encode()

    @staticmethod
    def mget(*keys: str) -> bytes:
        command: str = f"*{1 + len(keys)}\r\n$4\r\nMGET\r\n"
        for key in keys:
            command += f"${len(key)}\r\n{key}\r\n"

        return (command + "\x04").encode()

    @staticmethod
    def set(key: str, value: SupportedTypes) -> bytes:
        serializer: Serializer = Serializer()
        command: str = (
            f"*3\r\n$3\r\nSET\r\n${len(key)}\r\n{key}\r\n{serializer.process(value)}\x04"
        )

        return command.encode()

    @staticmethod
    def mset(**params: SupportedTypes) -> bytes:
        serializer: Serializer = Serializer()
        command: str = f"*{1 + len(params) * 2}\r\n$4\r\nMSET\r\n"

        for key, value in params.items():
            command += f"${len(key)}\r\n{key}\r\n{serializer.process(value)}"

        return (command + "\x04").encode()

    @staticmethod
    def delete(key: str) -> bytes:
        return f"*2\r\n$6\r\nDELETE\r\n${len(key)}\r\n{key}\r\n\x04".encode()

from enum import Enum


class Errors(str, Enum):
    ConnectionClosed = "The connection has been terminated."
    ConnectionReestablished = (
        "The connection was terminated, but managed to reestablish it."
    )
    LibraryBug = "This is probably a library bug. Please report it here: https://github.com/xXenvy/zcached.py"

    # Server side errors:
    BadRequest = "ERR bad request"
    UnExpected = "ERR unexpected"
    MaxClientsReached = "ERR max number of clients reached"
    BulkTooLarge = "ERR bulk too large"
    NotWhitelisted = "ERR not whitelisted"
    KeyNotString = "TYPERR key not string"
    NotBoolean = "TYPERR not boolean"
    NotInteger = "TYPERR not integer"

    @staticmethod
    def not_found(key: str) -> str:
        """Generates an error message for a key that was not found."""
        return f"ERR '{key}' not found"

    @staticmethod
    def unknown_command(name: str) -> str:
        """Generates an error message for an unknown command."""
        return f"ERR unknown command '{name}'"


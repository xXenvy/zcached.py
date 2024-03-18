from typing import Union, Callable, Type, Any

SupportedTypes = Union[str, int, float, bool, list, tuple, dict, set, None]


class Serializer:
    """
    A class for serializing values of different data types.

    Parameters
    ----------
    value:
        A value to serialize.

    Attributes
    ----------
    raw_value:
        Provided value for serialization.

    Raises
    ------
    TypeError
        If the specified type is not supported by the serializer.
    """

    __slots__ = ("raw_value",)

    def __init__(self, value: Any) -> None:
        if not isinstance(value, SupportedTypes):
            raise TypeError(
                "Specified value for serialization has an unsupported type. "
                f"Currently the serializer supports: {SupportedTypes}"
            )

        self.raw_value: Any = value

    def __repr__(self) -> str:
        return f"<Serializer(type={self.raw_type.__name__}, raw={self.raw_value})>"

    @property
    def raw_type(self) -> Type:
        """The type of the raw value"""
        return type(self.raw_value)

    def serialize(self) -> str:
        """Automatically serializes the raw value."""
        if self.raw_value is None:
            return self.none()

        # Python versions 3.9, 3.8 do not support match statements ahh moment.
        types: dict[type, Callable[[], str]] = {
            str: lambda: self.string,
            int: lambda: self.integer,
            float: lambda: self.float,
            bool: lambda: self.bool,
            list: lambda: self.list,
            tuple: lambda: self.tuple,
            set: lambda: self.set,
            dict: lambda: self.dict,
        }

        return types[self.raw_type]()

    @property
    def string(self) -> str:
        """Returns the serialized value of type str."""
        assert isinstance(self.raw_value, str)
        return f"${len(self.raw_value)}\r\n{self.raw_value}\r\n"

    @property
    def integer(self) -> str:
        """Returns the serialized value of type int."""
        assert isinstance(self.raw_value, int)
        return f":{self.raw_value}\r\n"

    @property
    def float(self) -> str:
        """Returns the serialized value of type float."""
        assert isinstance(self.raw_value, float)
        return f",{self.raw_value}\r\n"

    @property
    def bool(self) -> str:
        """Returns the serialized value of type bool."""
        assert isinstance(self.raw_value, bool)
        return "#{}\r\n".format("t" if self.raw_value else "f")

    @property
    def list(self) -> str:
        """Returns the serialized value of type list."""
        assert isinstance(self.raw_value, (list, tuple, set))
        return f"*{len(self.raw_value)}\r\n" + "".join(
            (Serializer(item).serialize() for item in self.raw_value)
        )

    @property
    def tuple(self) -> str:
        """Returns the serialized value of type tuple."""
        return self.list

    @property
    def set(self) -> str:
        """Returns the serialized value of type set."""
        return self.list

    @property
    def dict(self) -> str:
        """Returns the serialized value of type dict."""
        assert isinstance(self.raw_value, dict)

        text: str = f"%{len(self.raw_value)}\r\n"

        for key, value in self.raw_value.items():
            text += f"${len(str(key))}\r\n{key}\r\n{Serializer(value).serialize()}"

        return text

    @staticmethod
    def none() -> str:
        """Returns the serialized value of type None."""
        return "_\r\n"

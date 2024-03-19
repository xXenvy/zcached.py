from typing import Union, Callable

SupportedTypes = Union[str, int, float, bool, list, tuple, dict, set, None]


class Serializer:
    # TODO: Docstrings
    """
    A class for serializing values of different data types.
    """

    def process(self, value: SupportedTypes) -> str:
        """Automatically serializes the raw value."""
        if value is None:
            return self.none()

        # Python versions 3.9, 3.8 do not support match statements ahh moment.
        handlers: dict[type, Callable[[SupportedTypes], str]] = {
            str: self.serialize_str,
            int: self.serialize_int,
            float: self.serialize_float,
            bool: self.serialize_bool,
            list: self.serialize_list,
            tuple: self.serialize_tuple,
            set: self.serialize_set,
            dict: self.serialize_dict,
        }
        return handlers[type(value)](value)

    @staticmethod
    def serialize_str(value: str) -> str:
        """Returns the serialized value of type str."""
        assert isinstance(value, str)
        return f"${len(value)}\r\n{value}\r\n"

    @staticmethod
    def serialize_int(value: SupportedTypes) -> str:
        """Returns the serialized value of type int."""
        assert isinstance(value, int)
        return f":{value}\r\n"

    @staticmethod
    def serialize_float(value: SupportedTypes) -> str:
        """Returns the serialized value of type float."""
        assert isinstance(value, float)
        return f",{value}\r\n"

    @staticmethod
    def serialize_bool(value: SupportedTypes) -> str:
        """Returns the serialized value of type bool."""
        assert isinstance(value, bool)
        return "#{}\r\n".format("t" if value else "f")

    def serialize_list(self, value: SupportedTypes) -> str:
        """Returns the serialized value of type list."""
        assert isinstance(value, (list, tuple, set))
        return f"*{len(value)}\r\n" + "".join((self.process(item) for item in value))

    def serialize_tuple(self, value: SupportedTypes) -> str:
        """Returns the serialized value of type tuple."""
        return self.serialize_list(value)

    def serialize_set(self, value: SupportedTypes) -> str:
        """Returns the serialized value of type set."""
        return self.serialize_list(value)

    def serialize_dict(self, value: SupportedTypes) -> str:
        """Returns the serialized value of type dict."""
        assert isinstance(value, dict)
        text: str = f"%{len(value)}\r\n"

        for k, v in value.items():
            text += f"${len(str(k))}\r\n{k}\r\n{self.process(v)}\r\n"

        return text

    @staticmethod
    def none() -> str:
        """Returns the serialized value of type None."""
        return "_\r\n"

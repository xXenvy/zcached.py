from typing import Any

import pytest
from zcached import Serializer

test_values: dict[Any, str] = {
    "test_string_new_abc_test": "$24\r\ntest_string_new_abc_test\r\n",
    52: ":52\r\n",
    0.01: ",0.01\r\n",
    0.5: ",0.5\r\n",
    None: "_\r\n",
    False: "#f\r\n",
    True: "#t\r\n",
    "5454": "$4\r\n5454\r\n",
    -1: ":-1\r\n",
    -0.001: ",-0.001\r\n",
}


def test_basic_serializer():
    with pytest.raises(TypeError):
        Serializer(object())

    serializer: Serializer[str] = Serializer("string_test")

    assert isinstance(serializer.raw_value, str)
    assert serializer.serialize() == "$11\r\nstring_test\r\n"

    with pytest.raises(AssertionError):
        _ = serializer.bool


def test_dict_serializer():
    dict_serializer: Serializer[dict] = Serializer(
        {
            "a": 10,
            "b": 1.0,
            "c": "text",
            "d": True,
            "e": False,
            "f": None
        }
    )
    assert isinstance(dict_serializer.raw_value, dict)
    assert dict_serializer.serialize() == ('%6\r\n$1\r\na\r\n:10\r\n$1\r\nb\r\n,1.0\r\n$1\r\nc\r\n'
                                           '$4\r\ntext\r\n$1\r\nd\r\n#t\r\n$1\r\ne\r\n#f\r\n$1\r\nf\r\n_\r\n')


@pytest.mark.parametrize('value', tuple(test_values.keys()))
def test_serializer(value: Any):
    serializer: Serializer = Serializer(value)

    assert isinstance(serializer.raw_value, type(value))
    assert serializer.serialize() == test_values[value]

    with pytest.raises(AssertionError):
        _ = serializer.list


def test_list_serializer():
    arrays: list[list[Any]] = []

    for index, value in enumerate(test_values.keys()):
        arrays.append(list(test_values.keys())[:index + 1])

    for array in arrays:
        expected_expression: str = f"*{len(array)}\r\n"

        for element in array:
            expected_expression += test_values[element]

        serializer: Serializer[list[Any]] = Serializer(array)

        assert isinstance(serializer.raw_value, list)

        with pytest.raises(AssertionError):
            _ = serializer.integer

        assert serializer.serialize() == expected_expression


@pytest.mark.parametrize('value', ("bul^)^+kstr#!ing$!%@#" * 25 * x for x in range(5)))
def test_bulk_serializer(value: str):
    expected_expression: str = f"${len(value)}\r\n{value}\r\n"

    serializer: Serializer[str] = Serializer(value)
    assert isinstance(serializer.raw_value, str)

    with pytest.raises(AssertionError):
        _ = serializer.float

    assert serializer.serialize() == expected_expression

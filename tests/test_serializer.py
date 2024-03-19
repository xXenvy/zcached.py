from typing import Any, List

import pytest
from zcached import Serializer

test_values = {
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
    serializer = Serializer()

    with pytest.raises(TypeError):
        serializer.process(object())  # type: ignore

    assert serializer.process("string_test") == "$11\r\nstring_test\r\n"

    with pytest.raises(AssertionError):
        serializer.serialize_bool("string_test")


def test_dict_serializer():
    value = {"a": 10, "b": 1.0, "c": "text", "d": True, "e": False, "f": None}
    serializer = Serializer()

    assert serializer.process(value) == (
        "%6\r\n$1\r\na\r\n:10\r\n$1\r\nb\r\n,1.0\r\n$1\r\nc\r\n"
        "$4\r\ntext\r\n$1\r\nd\r\n#t\r\n$1\r\ne\r\n#f\r\n$1\r\nf\r\n_\r\n"
    )


@pytest.mark.parametrize("value", tuple(test_values.keys()))
def test_serializer(value: Any):
    serializer = Serializer()

    assert serializer.process(value) == test_values[value]

    with pytest.raises(AssertionError):
        _ = serializer.serialize_list(value)


def test_list_serializer():
    arrays: List[List[Any]] = []

    for index, value in enumerate(test_values.keys()):
        arrays.append(list(test_values.keys())[: index + 1])

    for array in arrays:
        expected_expression: str = f"*{len(array)}\r\n"

        for element in array:
            expected_expression += test_values[element]

        serializer = Serializer()

        with pytest.raises(AssertionError):
            _ = serializer.serialize_int(array)

        assert serializer.process(array) == expected_expression


@pytest.mark.parametrize("value", ("bul^)^+kstr#!ing$!%@#" * 25 * x for x in range(5)))
def test_bulk_serializer(value: str):
    expected_expression: str = f"${len(value)}\r\n{value}\r\n"

    serializer = Serializer()

    with pytest.raises(AssertionError):
        _ = serializer.serialize_float(value)

    assert serializer.process(value) == expected_expression

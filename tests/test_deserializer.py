from __future__ import annotations

import pytest
from zcached import Deserializer, Reader

test_values = {
    b"%3\r\n$1\r\n2\r\n$5\r\nhello\r\n$1\r\n1\r\n:50\r\n$1\r\n5\r\n,-5\r\n": {
        "2": "hello",
        "1": 50,
        "5": -5.0,
    },
    b"$7\r\ntest123\r\n": "test123",
    b"*6\r\n,5\r\n,1\r\n#f\r\n:10\r\n_\r\n$5\r\narray\r\n": [
        5.0,
        1.0,
        False,
        10,
        None,
        "array",
    ],
    b"%1\r\n$3\r\npik\r\n*3\r\n_\r\n#f\r\n*2\r\n:1\r\n:2\r\n": {"pik": [None, False, [1, 2]]},
    b"#f\r\n": False,
    b"#t\r\n": True,
    b"_\r\n": None,
    b":420\r\n": 420,
    b"$11\r\nhello world\r\n": "hello world",
}


def test_basic() -> None:
    deserializer: Deserializer = Deserializer()

    assert deserializer.process(Reader(b"#t\r\n")) is True
    assert deserializer.process(Reader(b"#f\r\n")) is False
    assert deserializer.process(Reader(b"$3\r\nlol\r\n")) == "lol"


@pytest.mark.parametrize("buffer", tuple(test_values.keys()))
def test_advanced(buffer: bytes) -> None:
    deserializer: Deserializer = Deserializer()

    expected = test_values[buffer]
    reader = Reader(buffer)
    assert deserializer.process(reader) == expected

    with pytest.raises(KeyError):
        deserializer.process(reader)

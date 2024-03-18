from __future__ import annotations

import pytest
from zcached import Result


@pytest.mark.parametrize(
    "value,error",
    [
        (b"+foo\r\n", None),
        (b"", "Error!"),
        (b"$3\r\nfoo\r\n", None),
        (b":50\r\n", None),
    ],
)
def test_result(value: bytes, error: str | None):
    result: Result[bytes] = Result(value, error)
    result2: Result[bytes] = Result(b":50\r\n", None)

    if result.error:
        assert result.failure is True
        assert result.is_empty() is True
    else:
        assert result.success is True
        assert result.is_empty() is False

    if result == result2:
        assert result.value == result2.value
        assert result.error == result2.error

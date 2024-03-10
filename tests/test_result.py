from __future__ import annotations

import pytest
from zcached import Result


@pytest.mark.parametrize("value,error", [(b"foo", None), (b"", "Error!"), (b"\r\nfoo", None), (b"\r\n", None)])
def test_result(value: bytes, error: str | None):
    result = Result(value, error)
    result2 = Result(b"\r\n", None)

    assert bytes(result) == result.value

    if result.error:
        assert result.failure is True
        assert result.is_empty() is True
        assert len(result.value) == 0
    else:
        assert result.success is True
        assert result.is_empty() is False
        assert len(result.value) != 0

    if result == result2:
        assert result.value == result2.value
        assert result.error == result2.error


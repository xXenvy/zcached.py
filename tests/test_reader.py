import pytest
from zcached import Reader


def test_reader():
    reader = Reader(b"*3\r\n+test\r\n$3\r\nlol\r\n:590")

    assert reader.position == 0
    assert reader.buffer == b"*3\n+test\n$3\nlol\n:590"

    assert reader.read(1) == b"*"
    assert int(reader.read(1)) == 3
    assert reader.position == 2

    with pytest.raises(RuntimeError):
        assert reader.read_until(b"4343")

    assert reader.read_until(b"lol") == b"\n+test\n$3\n"

    with pytest.raises(RuntimeError):
        assert reader.read_until(b"lol")

    assert reader.position == 15

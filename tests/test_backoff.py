import pytest
from zcached import ExponentialBackoff


@pytest.mark.parametrize("initial", (1, 2, 20, 0.5, 0.1, 5))
def test_backoff(initial: int):
    exponential = ExponentialBackoff(initial, 2, 10)

    assert exponential.current == 0
    assert exponential.total == 0

    for value in exponential:
        if value != exponential.next:
            assert exponential.current != 10

        else:
            assert exponential.current == 10
            exponential.reset()
            break

    assert exponential.current == 0
    assert exponential.total == 0

import pytest
import time


def test_sleep1():
    time.sleep(1)


@pytest.mark.monitor_skip_test
def test_sleep2():
    time.sleep(2)


@pytest.mark.parametrize(('range_max', 'other'), [(10, "10"), (100, "100"), (1000, "1000"), (10000, "10000")])
def test_heavy(range_max, other):
    assert len(['a' * i for i in range(range_max)]) == range_max

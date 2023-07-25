import time

import pytest

pytestmark = pytest.mark.monitor_skip_test

pytest_monitor_component = "test"


def test_not_monitored():
    t_a = time.time()
    b_continue = True
    while b_continue:
        t_delta = time.time() - t_a
        b_continue = t_delta < 5


@pytest.mark.monitor_test()
def test_force_monitor():
    t_a = time.time()
    b_continue = True
    while b_continue:
        t_delta = time.time() - t_a
        b_continue = t_delta < 5

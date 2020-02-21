import time


def test_master_sleep():
    t_a = time.time()
    b_continue = True
    while b_continue:
        t_delta  = time.time() - t_a
        b_continue = t_delta < 5


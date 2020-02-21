============
Introduction
============

`pytest-monitor` tracks the resources (like memory and compute time) consumed by a test suite, so that you
can make sure that your code does not use too much of them.

Thanks to `pytest-monitor`, you can check resource consumption in particular through continuous integration, as this is done by monitoring the consumption of test functions. These tests can be functional (as usual) or be dedicated to the resource consumption checks.

Use cases
---------

Examples of use cases include technical stack updates, and code evolutions.

Technical stack updates
~~~~~~~~~~~~~~~~~~~~~~~

In the Python world, libraries often depends on several packages. By updating some (or all) of the dependencies,
you update code that you do not own and therefore do not control. Tracking your application's resource footprint
can prevent unwanted resource consumption, and can thus validate the versions of the packages that you depend on.

Code evolution
~~~~~~~~~~~~~~

Extending your application with new features, or fixing its bugs, might have an impact on the core of your program. The performance of large applications or libraries can be difficult to assess, but by monitoring resource consumption, `pytest-monitor` allows you to check that despite code udpates, the performance of your code remains within desirable limits.


Example
-------

.. code-block:: python

    import pytest
    import time


    # Tests are run and monitored by default: no boilerplate code needed
    def test_sleep1():
        time.sleep(1)

    # Run as a test, but do not monitor:
    @pytest.mark.monitor_skip_test
    def test_sleep2():
        time.sleep(2)

    # Support for parametrized tests (monitored by default):
    @pytest.mark.parametrize(('range_max', 'other'), [(10, "10"), (100, "100"), (1000, "1000"), (10000, "10000")])
    def test_heavy(range_max, other):
        assert len(['a' * i for i in range(range_max)]) == range_max

========================
Managing your test suite
========================

`pytest-monitor` does not require any specific setup: it is active by default.
Thus all your tests are by default analyzed in order to collect monitored information.


About collecting and storing results
------------------------------------

`pytest-monitor` makes a clear distinction between the execution context and the test metrics.
This distinction can been seen clearly in the code and the initialization sequence:

1. Collect environment values.
   Various pieces of information about the machine are collected.
2. Store the context.
   The Execution Context collected in step #1 is recorded if not yet known.
3. Prepare the run.
   In order to provide more accurate measurements, we "warm up" the context and take an initial set of measurements.
   Some will be used for adjusting later measurements.
4. Run tests and enable measurements.
   Depending on the item type (function, class or module), we launch the relevant measurements.
   Each time a monitored item ends, the measurement results (Metrics) are recorded right away.
5. End session.
   If sending the monitoring results to a remote server has been requested, this is when `pytest-monitor` does it.


Selecting tests to monitor
--------------------------

By default, all tests are monitored, even small ones which would not require any specific monitoring.
It is possible to control more finely which tests will be monitored by `pytest-monitor`. This is done through the use of `pytest` markers.

`pytest-monitor` offers two markers for this:

``@pytest.mark.monitor_skip_test``
  marks your test for execution, but without any monitoring.

``@pytest.mark.monitor_skip_test_if(cond)``
  tells `pytest-monitor` to execute the test but to monitor results
  if and only if the condition is true.

Here is an example:

.. code-block:: python

    import pytest
    import sys


    def test_execute_and_monitor():
        assert True

    @pytest.mark.monitor_skip_test
    def test_execute_do_not_monitor():
        assert True

    @pytest.mark.monitor_skip_test_if(sys.version_info >= (3,))
    def test_execute_and_monitor_py3_or_above():
        assert True


Disabling monitoring except for some tests
------------------------------------------

`pytest` offers global markers. For example, one can set the default to no monitoring:

.. code-block:: python

    import pytest

    # With the following global module marker,
    # monitoring is disabled by default:
    pytestmark = [pytest.mark.monitor_skip_test]

In this case, it is necessary to explicitly activate individual monitoring. This is
accomplished with:

``@pytest.mark.monitor_test``
  marks your test as to be executed and monitored, even if monitoring
  is disabled for the module.

``@pytest.mark.monitor_test_if(cond)``
  tells `pytest-monitor` to execute the test and to monitor results
  if and only if the condition is true, regardless of the
  module monitor setup.


Continuing the example above:

.. code-block:: python

    import time
    import sys


    def test_executed_not_monitored():
        time.sleep(1)
        assert True

    def test_executed_not_monitored_2():
        time.sleep(2)
        assert True

    @pytest.mark.monitor_test
    def test_executed_and_monitored():
        assert True

    @pytest.mark.monitor_test_if(sys.version_info >= (3, 7))
    def test_executed_and_monitored_if_py37():
        assert True


Associating your tests to a component
-------------------------------------

`pytest-monitor` allows you to *tag* each test in the database with a "**component**" name. This allows you to identify easily tests that come from a specific part of your application, or for distinguishing test results for two different projects that use the same `pytest-monitor` database.

Setting up a component name can be done at module level:

.. code-block:: python

    import time
    import pytest


    pytest_monitor_component = "my_component"  # Component name stored in the results database

    def test_monitored():
        t_a = time.time()
        b_continue = True
        while b_continue:
            t_delta = time.time() - t_a
            b_continue = t_delta < 1
        assert not b_continue

If no `pytest_monitor_component` variable is defined, the component is set to the empty string.
In projects with many modules, this can be tedious. `pytest-monitor` therefore allows you to force a fixed component name for the all the tests:

.. code-block:: bash

   $ pytest --force-component YOUR_COMPONENT_NAME

This will force the component value to be set to the one you provided, whatever the value of
*pytest_monitor_component* in your test module, if any.

If you need to use a global component name for all your tests while allowing some modules to have a specific component name, you can ask `pytest-monitor` to add a prefix to any module-level component name:

.. code-block:: bash

   $ pytest --component-prefix YOUR_COMPONENT_NAME

This way, all tests detected by `pytest` will have their component prefixed with the given value (tests for modules with no `pytest_monitor_component` variable are simply tagged with the prefix).

For instance the following test module:

.. code-block:: python

    import time
    import pytest


    pytest_monitor_component = "component_A"

    def test_monitored():
        t_a = time.time()
        b_continue = True
        while b_continue:
            t_delta = time.time() - t_a
            b_continue = t_delta < 1
        assert not b_continue

will yield the following value for the component fields, depending on the chosen command-line option:

+------------------------------------------+-----------------------+
|   Command line used                      |    Component value    |
+==========================================+=======================+
| pytest --force-component PROJECT_A       |       PROJECT_A       |
+------------------------------------------+-----------------------+
| pytest --component-prefix PROJECT_A      | PROJECT_A.component_A |
+------------------------------------------+-----------------------+


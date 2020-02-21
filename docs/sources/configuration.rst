========================
Configuring your session
========================

`pytest-monitor` gives you flexibility for running your test suite.
In this section, we will discuss the different available options, and how they influence the `pytest` session.

Scope Restriction
-----------------

`pytest-monitor` is able to restrict the scope of the analysis. As a default, 
any test object discovered by pytest is monitored (test functions and test classes).

Sometime, you might want to monitor a whole module or test session. This can be
achieved thanks to the *\-\-restrict-scope-to* option. 

If a scope restriction is set, then the monitoring will be performed at the selected levels.
For example, monitoring at both function and module level can be achieved by the following command:

.. code-block:: shell

    pytest --restrict-scope-to function,module

Accepted values are:
 
 * function: test functions will be monitored individually, leading to one entry per test function.
 * module: each discovered module will be monitored regardless of the others.
 * class: test class objects will be monitored individually.
 * session: monitor the whole session.

It is important to realize that using multiple scopes has an impact on the monitoring measures. For example, the `pytest-monitor` code that monitors functions does consume resources for each function (notably compute time). As a consequence, the resources consumed by their module will include the resources consumed by `pytest-monitor` for each function. If individual functions were not monitored, the resource consumption reported for the module would therefore be lower.

Due to the way `pytest` handles test modules, some specificities apply when monitoring modules:

 * The total measured elapsed time includes the setup/teardown process for each function.
   On the other hand, a function object measures only the duration of the function run (without the setup and teardown parts).
 * Consumed memory will be the peak of memory usage during the whole module run.


Handling parameterized tests
----------------------------

Parameterized tests can be introspected by `pytest-monitor` during the setup phase: their real
name is based on the parameter values. This uses the string representation of the parameters (so you  want to make sure that this representation suits your needs).

Let's consider the following test:

.. code-block:: python

    @pytest.mark.parametrize(('asint', 'asstr'), [(10, "10"), (100, "100"), (1000, "1000"), (10000, "10000")])
    def test_p(asint, asstr):
        assert asint == int(asstr)

By default, `pytest-monitor` will generate the following entries:

 * test_p[10-10]
 * test_p[100-100]
 * test_p[1000-1000]
 * test_p[10000-10000]


You can ask `pytest-monitor` to tag parameters with their names (as provided by ``@pytest.mark.parametrize``), with the following option:

.. code-block:: shell

    pytest --parametrization-explicit

which will lead to the following entries:

 * test_p[asint_10-asstr_10]
 * test_p[asint_100-asstr_100]
 * test_p[asint_1000-asstr_1000]
 * test_p[asint_10000-asstr_10000]


Disable monitoring
------------------

If you need for some reason to disable the monitoring, pass the *\-\-no-trace* option.



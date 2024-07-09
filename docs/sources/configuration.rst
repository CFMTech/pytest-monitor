========================
Configuring your session
========================

`pytest-monitor` gives you flexibility for running your test suite.
In this section, we will discuss the different available options, and how they influence the `pytest` session.

Scope Restriction
-----------------

`pytest-monitor` is able to restrict the scope of the analysis. As a default, 
only tests functions discovered by pytest are monitored.

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

If you need for some reason to disable the monitoring, pass the *\-\-no-monitor* option.


Disable failed tests
--------------------

By default failing tests are monitored in the database. The database has an additional column that
indicates if a test passed (boolean value). If you only need to monitor successful tests, pass
the *\-\-no-failed* option.


Describing a run
----------------

Sometimes, you might want to compare identical state of your code. In such cases, relying only on the scm
references and the run date of the session is not sufficient. For that, `pytest-monitor` can assist you by tagging
your session using description and tags.


Description and tags
~~~~~~~~~~~~~~~~~~~~
The description should be used to provide a brief summary of your run while tags can be used to
set special information you want to focus during your analysis. 
Setting a description is as simple as this:

.. code-block:: shell

    bash $> pytest --description "Any run description you want"


Flagging your session with specific information is as complex as setting the description:

.. code-block:: shell

    bash $> pytest --tag pandas=1.0.1 --tag numpy=1.17

This will result in a session with the following description:

.. code-block:: text

    {
        "pandas": "1.0.1",
        "numpy": "1.17"
    }


You can perfectly use both options to fully describe your session:

.. code-block:: shell

    bash $> pytest --tag pandas=1.0.1 --tag numpy=1.17 --description "Your summary"

This will result in a session with the following description:

.. code-block:: text

    {
        "msg": "Your summary",
        "pandas": "1.0.1",
        "numpy": "1.17"
    }

Describing a CI build
~~~~~~~~~~~~~~~~~~~~~
For convenience pytest-monitor automatically extends the session's description with some information
extracted from the CI build. For that purpose, pytest-monitor reads the environment
at the start of the test session in search for:
 * **pipeline_branch**, which can either represent a CI pipeline name (preferentially) or the source code branch name.
 * **pipeline_build_no**, which is the pipeline build number (if available) or the pipeline ID if any.
 * **__ci__** which provides you the ci system used.

Currently, pytest-monitor supports the following CI:
 * Gitlab CI
 * Travis CI
 * Jenkins
 * Drone CI
 * Circle CI
 * Bitbucket CI

The following table explains how both fields are mapped:

+--------------+-----------------------------------+-----------------------+---------------+
|       CI     |     pipeline_branch               | pipeline_build_no     |  __ci__       |
+==============+===================================+=======================+===============+
|  Jenkins CI  |  BRANCH_NAME if set else JOB_NAME | BUILD_NUMBER          |   jenkinsci   |
+--------------+-----------------------------------+-----------------------+---------------+
|  Drone CI    |  DRONE_REPO_BRANCH                | DRONE_BUILD_NUMBER    |   droneci     |
+--------------+-----------------------------------+-----------------------+---------------+
|  Circle CI   |  CIRCLE_JOB                       | CIRCLE_BUILD_NUM      |   circleci    |
+--------------+-----------------------------------+-----------------------+---------------+
|  Gitlab CI   |  CI_JOB_NAME                      | CI_PIPELINE_ID        |   gitlabci    |
+--------------+-----------------------------------+-----------------------+---------------+
|  Travis CI   |  TRAVIS_BUILD_ID                  | TRAVIS_BUILD_NUMBER   |   travisci    |
+--------------+-----------------------------------+-----------------------+---------------+
|  Bitbucket CI|  BITBUCKET_BRANCH                 | BITBUCKET_BUILD_NUMBER|   bitbucketci |
+--------------+-----------------------------------+-----------------------+---------------+

Note that none of these two fields will be added if:
 * the CI context is incomplete
 * the CI context cannot be computed.

Parameters affecting measures
-----------------------------
By default, pytest-monitor runs the garbage collector prior to execute the test function.
This leads to finer memory measurements. In the case where you want to disable this call to the
garbage collector, you just have to set the option `--no-gc` on the command line.

.. code-block:: shell

    bash $> pytest --no-gc

Forcing CPU frequency
---------------------
Under some circumstances, you may want to set the CPU frequency instead of asking `pytest-monitor` to compute it.
To do so, you can either:
 - ask `pytest-monitor` to use a preset value if it does not manage to compute the CPU frequency
 - or to not try computing the CPU frequency and use your preset value.

 Two environment variables controls this behaviour:
 - `PYTEST_MONITOR_CPU_FREQ` allows you to preset a value for the CPU frequency. It must be a float convertible value.
 This value will be used if `pytest-monitor` cannot compute the CPU frequency. Otherwise, `0.0` will be used as a
 default value.
 - `PYTEST_MONITOR_FORCE_CPU_FREQ` instructs `pytest-monitor` to try computing the CPU frequency or not. It expects an
 integer convertible value. If not set, or if the integer representation of the value is `0`, then `pytest-monitor` will
 try to compute the cpu frequency and defaults to the usecase describe for the previous environment variable.
 If it set and not equal to `0`, then we use the value that the environment variable `PYTEST_MONITOR_CPU_FREQ` holds
 (`0.0` if not set).

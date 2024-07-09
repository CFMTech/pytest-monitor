# -*- coding: utf-8 -*-
import json
import pathlib
import sqlite3

import pytest


def test_monitor_basic_test(testdir):
    """Make sure that pytest-monitor does the job without impacting user tests."""
    # create a temporary pytest test module
    testdir.makepyfile(
        """
    import time


    def test_ok():
        time.sleep(0.5)
        x = ['a' * i for i in range(100)]
        assert len(x) == 100

"""
    )

    # run pytest with the following cmd args
    result = testdir.runpytest("-vv", "--tag", "version=12.3.5")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(["*::test_ok PASSED*"])

    pymon_path = pathlib.Path(str(testdir)) / ".pymon"
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the test suite
    result.assert_outcomes(passed=1)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute("SELECT ITEM FROM TEST_METRICS;")
    assert len(cursor.fetchall()) == 1
    cursor = db.cursor()
    tags = json.loads(
        cursor.execute("SELECT RUN_DESCRIPTION FROM TEST_SESSIONS;").fetchone()[0]
    )
    assert "description" not in tags
    assert "version" in tags
    assert tags["version"] == "12.3.5"


def test_monitor_basic_test_failing(testdir):
    """Make sure that pytest-monitor handles failing tests properly (without ending in deadlock when nested)"""
    # create a temporary pytest test module
    testdir.makepyfile(
        """
    import time

    def test_fail():
        time.sleep(0.5)
        x = [ "hello" ]
        assert len(x) == 2

"""
    )

    # run pytest with the following cmd args
    result = testdir.runpytest("")

    pymon_path = pathlib.Path(str(testdir)) / ".pymon"
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the test suite
    result.assert_outcomes(failed=1)


def test_monitor_basic_test_description(testdir):
    """Make sure that pytest-monitor does the job without impacting user tests."""
    # create a temporary pytest test module
    testdir.makepyfile(
        """
    import time


    def test_ok():
        time.sleep(0.5)
        x = ['a' * i for i in range(100)]
        assert len(x) == 100

"""
    )

    # run pytest with the following cmd args
    result = testdir.runpytest(
        "-vv", "--description", '"Test"', "--tag", "version=12.3.5"
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(["*::test_ok PASSED*"])

    pymon_path = pathlib.Path(str(testdir)) / ".pymon"
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the test suite
    result.assert_outcomes(passed=1)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute("SELECT ITEM FROM TEST_METRICS;")
    assert len(cursor.fetchall()) == 1
    cursor = db.cursor()
    tags = json.loads(
        cursor.execute("SELECT RUN_DESCRIPTION FROM TEST_SESSIONS;").fetchone()[0]
    )
    assert "description" in tags
    assert tags["description"] == '"Test"'
    assert "version" in tags
    assert tags["version"] == "12.3.5"


def test_monitor_pytest_skip_marker(testdir):
    """Make sure that pytest-monitor does the job without impacting user tests."""
    # create a temporary pytest test module
    testdir.makepyfile(
        """
    import pytest
    import time

    @pytest.mark.skip("Some reason")
    def test_skipped():
        assert True

"""
    )

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(["*::test_skipped SKIPPED*"])

    pymon_path = pathlib.Path(str(testdir)) / ".pymon"
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(skipped=1)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute("SELECT ITEM FROM TEST_METRICS;")
    assert not len(cursor.fetchall())


def test_monitor_pytest_skip_marker_on_fixture(testdir):
    """Make sure that pytest-monitor does the job without impacting user tests."""
    # create a temporary pytest test module
    testdir.makepyfile(
        """
    import pytest
    import time

    @pytest.fixture
    def a_fixture():
        pytest.skip("because this is the scenario being tested")

    def test_skipped(a_fixture):
        assert True

"""
    )

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(["*::test_skipped SKIPPED*"])

    pymon_path = pathlib.Path(str(testdir)) / ".pymon"
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(skipped=1)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute("SELECT ITEM FROM TEST_METRICS;")
    assert not len(cursor.fetchall())


def test_bad_markers(testdir):
    """Make sure that pytest-monitor warns about unknown markers."""
    # create a temporary pytest test module
    testdir.makepyfile(
        """
        import pytest
        import time


        @pytest.mark.monitor_bad_marker
        def test_ok():
            time.sleep(0.1)
            x = ['a' * i for i in range(100)]
            assert len(x) == 100

    """
    )

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        ["*::test_ok PASSED*", "*Nothing known about marker monitor_bad_marker*"]
    )

    pymon_path = pathlib.Path(str(testdir)) / ".pymon"
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=1)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute("SELECT ITEM FROM TEST_METRICS;")
    assert len(cursor.fetchall()) == 1


def test_monitor_skip_module(testdir):
    """Make sure that pytest-monitor correctly understand the monitor_skip_test marker."""
    # create a temporary pytest test module
    testdir.makepyfile(
        """
import pytest
import time

pytestmark = pytest.mark.monitor_skip_test

def test_ok_not_monitored():
    time.sleep(0.1)
    x = ['a' * i for i in range(100)]
    assert len(x) == 100

def test_another_function_ok_not_monitored():
    assert True
"""
    )

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        [
            "*::test_ok_not_monitored PASSED*",
            "*::test_another_function_ok_not_monitored PASSED*",
        ]
    )

    pymon_path = pathlib.Path(str(testdir)) / ".pymon"
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=2)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute("SELECT ITEM FROM TEST_METRICS;")
    assert not len(cursor.fetchall())  # Nothing ran


def test_monitor_skip_test(testdir):
    """Make sure that pytest-monitor correctly understand the monitor_skip_test marker."""
    # create a temporary pytest test module
    testdir.makepyfile(
        """
    import pytest
    import time


    @pytest.mark.monitor_skip_test
    def test_not_monitored():
        time.sleep(0.1)
        x = ['a' * i for i in range(100)]
        assert len(x) == 100

"""
    )

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(["*::test_not_monitored PASSED*"])

    pymon_path = pathlib.Path(str(testdir)) / ".pymon"
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=1)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute("SELECT ITEM FROM TEST_METRICS;")
    assert not len(cursor.fetchall())  # nothing monitored


def test_monitor_skip_test_if(testdir):
    """Make sure that pytest-monitor correctly understand the monitor_skip_test_if marker."""
    # create a temporary pytest test module
    testdir.makepyfile(
        """
    import pytest
    import time


    @pytest.mark.monitor_skip_test_if(True)
    def test_not_monitored():
        time.sleep(0.1)
        x = ['a' * i for i in range(100)]
        assert len(x) == 100


    @pytest.mark.monitor_skip_test_if(False)
    def test_monitored():
        time.sleep(0.1)
        x = ['a' *i for i in range(100)]
        assert len(x) == 100

"""
    )

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        ["*::test_not_monitored PASSED*", "*::test_monitored PASSED*"]
    )

    pymon_path = pathlib.Path(str(testdir)) / ".pymon"
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=2)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute("SELECT ITEM FROM TEST_METRICS;")
    assert len(cursor.fetchall()) == 1


def test_monitor_no_db(testdir):
    """Make sure that pytest-monitor correctly understand the monitor_skip_test_if marker."""
    # create a temporary pytest test module
    testdir.makepyfile(
        """
    import pytest
    import time


    def test_it():
        time.sleep(0.1)
        x = ['a' * i for i in range(100)]
        assert len(x) == 100


    def test_that():
        time.sleep(0.1)
        x = ['a' *i for i in range(100)]
        assert len(x) == 100

"""
    )

    wrn = "pytest-monitor: No storage specified but monitoring is requested. Disabling monitoring."
    with pytest.warns(UserWarning, match=wrn):
        # run pytest with the following cmd args
        result = testdir.runpytest("--no-db", "-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(["*::test_it PASSED*", "*::test_that PASSED*"])

    pymon_path = pathlib.Path(str(testdir)) / ".pymon"
    assert not pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=2)


def test_monitor_basic_output(testdir):
    """Make sure that pytest-monitor does not repeat captured output (issue #26)."""
    # create a temporary pytest test module
    testdir.makepyfile(
        """
        def test_it():
            print('Hello World')
    """
    )

    wrn = "pytest-monitor: No storage specified but monitoring is requested. Disabling monitoring."
    with pytest.warns(UserWarning, match=wrn):
        # run pytest with the following cmd args
        result = testdir.runpytest("--no-db", "-s", "-vv")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(["*::test_it Hello World*"])
    assert "Hello World" != result.stdout.get_lines_after("*Hello World")[0]

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=1)


def test_monitor_with_doctest(testdir):
    """Make sure that pytest-monitor does not fail to run doctest."""
    # create a temporary pytest test module
    testdir.makepyfile(
        '''
        def run(a, b):
            """
            >>> run(3, 30)
            33
            """
            return a + b
    '''
    )

    # run pytest with the following cmd args
    result = testdir.runpytest("--doctest-modules", "-vv")

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=1)
    pymon_path = pathlib.Path(str(testdir)) / ".pymon"
    assert pymon_path.exists()

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute("SELECT ITEM FROM TEST_METRICS;")
    assert not len(cursor.fetchall())

    pymon_path.unlink()
    result = testdir.runpytest("--doctest-modules", "--no-monitor", "-vv")

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=1)
    assert not pymon_path.exists()


def test_monitor_monitor_failed_tests(testdir):
    """Check new standard behavior that monitors failed tests in database"""
    testdir.makepyfile(
        """
        def test_failing_test():
            assert False
        """
    )

    result = testdir.runpytest("")
    # # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(failed=1)

    pymon_path = pathlib.Path(str(testdir)) / ".pymon"
    assert pymon_path.exists()
    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()

    # TEST_METRICS table is supposed to be have 1 entry (1 failed test)
    cursor.execute("SELECT * FROM TEST_METRICS")
    test_metrics = cursor.fetchall()
    assert len(test_metrics) == 1


def test_monitor_no_monitor_failed(testdir):
    """Ensure cmd flag --no-failed works and turns of monitoring failed tests"""
    testdir.makepyfile(
        """
        def test_failing_test():
            assert False
        """
    )
    pymon_path = pathlib.Path(str(testdir)) / ".pymon"
    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()

    result = testdir.runpytest("--no-failed")
    result.assert_outcomes(failed=1)

    # TEST_METRICS table is supposed to be empty (only one failing test)
    cursor.execute("SELECT * FROM TEST_METRICS")
    ncursor = cursor.fetchall()
    print(ncursor)
    assert not len(ncursor)

    testdir.makepyfile(
        """
        def test_successful_test():
            assert True
        """
    )

    result = testdir.runpytest("--no-failed")
    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=1)

    # TEST_METRICS table is supposed to have 1 entry (2 tests, 1 successful)
    cursor.execute("SELECT * FROM TEST_METRICS")
    assert len(cursor.fetchall()) == 1

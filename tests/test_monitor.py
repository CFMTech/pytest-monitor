# -*- coding: utf-8 -*-
import pathlib
import pytest
import sqlite3


def test_monitor_basic_test(testdir):
    """Make sure that pytest-monitor does the job without impacting user tests."""
    # create a temporary pytest test module
    testdir.makepyfile("""
    import time
    
    
    def test_ok():
        time.sleep(0.5)
        x = ['a' * i for i in range(100)]
        assert len(x) == 100

""")

    # run pytest with the following cmd args
    result = testdir.runpytest('-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_ok PASSED*'])

    pymon_path = pathlib.Path(str(testdir)) / '.pymon'
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=1)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute('SELECT ITEM FROM TEST_METRICS;')
    assert 1 == len(cursor.fetchall())  # current test


def test_monitor_pytest_skip_marker(testdir):
    """Make sure that pytest-monitor does the job without impacting user tests."""

    # create a temporary pytest test module
    testdir.makepyfile("""
    import pytest
    import time

    @pytest.mark.skip("Some reason")
    def test_skipped():
        assert True

""")

    # run pytest with the following cmd args
    result = testdir.runpytest('-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_skipped SKIPPED*'])

    pymon_path = pathlib.Path(str(testdir)) / '.pymon'
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(skipped=1)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute('SELECT ITEM FROM TEST_METRICS;')
    assert not len(cursor.fetchall())


def test_bad_markers(testdir):
    """Make sure that pytest-monitor warns about unknown markers."""
    # create a temporary pytest test module
    testdir.makepyfile("""
        import pytest
        import time


        @pytest.mark.monitor_bad_marker
        def test_ok():
            time.sleep(0.1)
            x = ['a' * i for i in range(100)]
            assert len(x) == 100

    """)

    # run pytest with the following cmd args
    result = testdir.runpytest('-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_ok PASSED*',
                                 '*Nothing known about marker monitor_bad_marker*'])

    pymon_path = pathlib.Path(str(testdir)) / '.pymon'
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=1)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute('SELECT ITEM FROM TEST_METRICS;')
    assert 1 == len(cursor.fetchall())  # current test


def test_monitor_skip_module(testdir):
    """Make sure that pytest-monitor correctly understand the monitor_skip_test marker."""
    # create a temporary pytest test module
    testdir.makepyfile("""
import pytest
import time

pytestmark = pytest.mark.monitor_skip_test

def test_ok_not_monitored():
    time.sleep(0.1)
    x = ['a' * i for i in range(100)]
    assert len(x) == 100

def test_another_function_ok_not_monitored():
    assert True
""")

    # run pytest with the following cmd args
    result = testdir.runpytest('-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_ok_not_monitored PASSED*',
                                 '*::test_another_function_ok_not_monitored PASSED*'])

    pymon_path = pathlib.Path(str(testdir)) / '.pymon'
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=2)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute('SELECT ITEM FROM TEST_METRICS;')
    assert not len(cursor.fetchall())  # Nothing ran


def test_monitor_skip_test(testdir):
    """Make sure that pytest-monitor correctly understand the monitor_skip_test marker."""
    # create a temporary pytest test module
    testdir.makepyfile("""
    import pytest
    import time


    @pytest.mark.monitor_skip_test
    def test_not_monitored():
        time.sleep(0.1)
        x = ['a' * i for i in range(100)]
        assert len(x) == 100

""")

    # run pytest with the following cmd args
    result = testdir.runpytest('-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_not_monitored PASSED*'])

    pymon_path = pathlib.Path(str(testdir)) / '.pymon'
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=1)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute('SELECT ITEM FROM TEST_METRICS;')
    assert not len(cursor.fetchall())  # nothing monitored


def test_monitor_skip_test_if(testdir):
    """Make sure that pytest-monitor correctly understand the monitor_skip_test_if marker."""

    # create a temporary pytest test module
    testdir.makepyfile("""
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

""")

    # run pytest with the following cmd args
    result = testdir.runpytest('-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_not_monitored PASSED*',
                                 '*::test_monitored PASSED*'])

    pymon_path = pathlib.Path(str(testdir)) / '.pymon'
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=2)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute('SELECT ITEM FROM TEST_METRICS;')
    assert 1 == len(cursor.fetchall())

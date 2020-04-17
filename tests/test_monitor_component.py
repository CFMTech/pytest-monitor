# -*- coding: utf-8 -*-
import os
import pathlib
import sqlite3


def test_monitor_no_component(testdir):
    """Make sure that pytest-monitor has an empty component by default"""

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
    assert 1 == len(cursor.fetchall())
    cursor.execute("SELECT ITEM FROM TEST_METRICS WHERE COMPONENT != '' AND ITEM LIKE '%test_ok';")
    assert not len(cursor.fetchall())


def test_monitor_force_component(testdir):
    """Make sure that pytest-monitor forces the component name if required"""

    # create a temporary pytest test module
    testdir.makepyfile("""
    import time
    
    
    def test_force_ok():
        time.sleep(0.5)
        x = ['a' * i for i in range(100)]
        assert len(x) == 100

""")

    # run pytest with the following cmd args
    result = testdir.runpytest('--force-component', 'my_component', '-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_force_ok PASSED*'])

    pymon_path = pathlib.Path(str(testdir)) / '.pymon'
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=1)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute('SELECT ITEM FROM TEST_METRICS;')
    assert 1 == len(cursor.fetchall())
    cursor.execute("SELECT ITEM FROM TEST_METRICS"
                   " WHERE COMPONENT == 'my_component' AND ITEM LIKE '%test_force_ok%';")
    assert 1 == len(cursor.fetchall())


def test_monitor_prefix_component(testdir):
    """Make sure that pytest-monitor has a prefixed component """

    # create a temporary pytest test module
    testdir.makepyfile("""
    import time
    
    pytest_monitor_component = 'internal'
    
    def test_prefix_ok():
        time.sleep(0.5)
        x = ['a' * i for i in range(100)]
        assert len(x) == 100

""")

    # run pytest with the following cmd args
    result = testdir.runpytest('--component-prefix', 'my_component', '-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_prefix_ok PASSED*'])

    pymon_path = pathlib.Path(str(testdir)) / '.pymon'
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=1)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute('SELECT ITEM FROM TEST_METRICS;')
    assert 1 == len(cursor.fetchall())
    cursor.execute("SELECT ITEM FROM TEST_METRICS"
                   " WHERE COMPONENT == 'my_component' AND ITEM LIKE '%test_prefix_ok%';")
    assert not len(cursor.fetchall())
    cursor.execute("SELECT ITEM FROM TEST_METRICS"
                   " WHERE COMPONENT == 'my_component.internal' AND ITEM LIKE '%test_prefix_ok%';")
    assert 1 == len(cursor.fetchall())


def test_monitor_prefix_without_component(testdir):
    """Make sure that pytest-monitor has a prefixed component """

    # create a temporary pytest test module
    testdir.makepyfile("""
    import time


    def test_prefix_ok():
        time.sleep(0.5)
        x = ['a' * i for i in range(100)]
        assert len(x) == 100

""")

    # run pytest with the following cmd args
    result = testdir.runpytest('--component-prefix', 'my_component', '-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_prefix_ok PASSED*'])

    pymon_path = pathlib.Path(str(testdir)) / '.pymon'
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=1)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute('SELECT ITEM FROM TEST_METRICS;')
    assert 1 == len(cursor.fetchall())
    cursor.execute("SELECT ITEM FROM TEST_METRICS"
                   " WHERE COMPONENT == 'my_component' AND ITEM LIKE '%test_prefix_ok%';")
    assert 1 == len(cursor.fetchall())

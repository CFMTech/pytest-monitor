import mock
import os
import pathlib
import pytest
import sqlite3


CPU_FREQ_PATH = 'pytest_monitor.sys_utils.psutil.cpu_freq'

TEST_CONTENT = """
import time


def test_ok():
    time.sleep(0.5)
    x = ['a' * i for i in range(100)]
    assert len(x) == 100
"""

def get_nb_metrics_with_cpu_freq(path):
    pymon_path = pathlib.Path(str(path)) / '.pymon'
    db = sqlite3.connect(path.as_posix())
    cursor = db.cursor()
    cursor.execute('SELECT ITEM FROM TEST_METRICS;')
    nb_metrics = len(cursor.fetchall())
    cursor = db.cursor()
    cursor.execute('SELECT CPU_FREQUENCY_MHZ FROM EXECUTION_CONTEXTS;')
    rows = cursor.fetchall()
    assert 1 == len(rows)
    cpu_freq = rows[0][0]
    return nb_metrics, cpu_freq


def test_force_cpu_freq_set_0_use_psutil(testdir):
    """Test that when force mode is set, we do not call psutil to fetch CPU's frequency"""

    # create a temporary pytest test module
    testdir.makepyfile(TEST_CONTENT)

    with mock.patch(CPU_FREQ_PATH, return_value=1500) as cpu_freq_mock:
        os.environ['PYTEST_MONITOR_FORCE_CPU_FREQ'] = '0'
        os.environ['PYTEST_MONITOR_CPU_FREQ'] = '3000'
        # run pytest with the following cmd args
        result = testdir.runpytest('-vv')
        del os.environ['PYTEST_MONITOR_FORCE_CPU_FREQ']
        del os.environ['PYTEST_MONITOR_CPU_FREQ']
        cpu_freq_mock.assert_called()

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_ok PASSED*'])
    # make sure that that we get a '0' exit code for the test suite
    result.assert_outcomes(passed=1)

    assert 1, 3000 == get_nb_metrics_with_cpu_freq(testdir)


def test_force_cpu_freq(testdir):
    """Test that when force mode is set, we do not call psutil to fetch CPU's frequency"""

    # create a temporary pytest test module
    testdir.makepyfile(TEST_CONTENT)

    with mock.patch(CPU_FREQ_PATH, return_value=1500) as cpu_freq_mock:
        os.environ['PYTEST_MONITOR_FORCE_CPU_FREQ'] = '1'
        os.environ['PYTEST_MONITOR_CPU_FREQ'] = '3000'
        # run pytest with the following cmd args
        result = testdir.runpytest('-vv')
        del os.environ['PYTEST_MONITOR_FORCE_CPU_FREQ']
        del os.environ['PYTEST_MONITOR_CPU_FREQ']
        cpu_freq_mock.assert_not_called()

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_ok PASSED*'])
    # make sure that that we get a '0' exit code for the test suite
    result.assert_outcomes(passed=1)

    assert 1, 3000 == get_nb_metrics_with_cpu_freq(testdir)
    

@pytest.mark.parametrize('effect', [AttributeError, NotImplementedError, FileNotFoundError])
def test_when_cpu_freq_cannot_fetch_frequency_set_freq_by_using_fallback(effect, testdir):
    """Make sure that pytest-monitor fallback takes value of CPU FREQ from special env var"""
    # create a temporary pytest test module
    testdir.makepyfile(TEST_CONTENT)

    with mock.patch(CPU_FREQ_PATH, side_effect=effect) as cpu_freq_mock:
        os.environ['PYTEST_MONITOR_CPU_FREQ'] = '3000'
        # run pytest with the following cmd args
        result = testdir.runpytest('-vv')
        del os.environ['PYTEST_MONITOR_CPU_FREQ']
        cpu_freq_mock.assert_called()

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_ok PASSED*'])
    # make sure that that we get a '0' exit code for the test suite
    result.assert_outcomes(passed=1)

    assert 1, 3000 == get_nb_metrics_with_cpu_freq(testdir)

    
@pytest.mark.parametrize('effect', [AttributeError, NotImplementedError, FileNotFoundError])
def test_when_cpu_freq_cannot_fetch_frequency_set_freq_to_0(effect, testdir):
    """Make sure that pytest-monitor's fallback mechanism is efficient enough. """
    # create a temporary pytest test module
    testdir.makepyfile(TEST_CONTENT)

    with mock.patch(CPU_FREQ_PATH, side_effect=effect) as cpu_freq_mock:
        # run pytest with the following cmd args
        result = testdir.runpytest('-vv')
        cpu_freq_mock.assert_called()

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_ok PASSED*'])
    # make sure that that we get a '0' exit code for the test suite
    result.assert_outcomes(passed=1)

    assert 1, 0 == get_nb_metrics_with_cpu_freq(testdir)
    

@mock.patch('pytest_monitor.sys_utils.psutil.cpu_freq', return_value=None)
def test_when_cpu_freq_cannot_fetch_frequency(cpu_freq_mock, testdir):
    """Make sure that pytest-monitor does the job when we have issue in collecing context resources"""
    # create a temporary pytest test module
    testdir.makepyfile(TEST_CONTENT)

    # run pytest with the following cmd args
    result = testdir.runpytest('-vv')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_ok PASSED*'])
    # make sure that that we get a '0' exit code for the test suite
    result.assert_outcomes(passed=1)

    assert 1, 0 == get_nb_metrics_with_cpu_freq(testdir)


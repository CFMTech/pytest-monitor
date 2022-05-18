import mock
import pathlib
import sqlite3


@mock.patch('pytest_monitor.sys_utils.psutil.cpu_freq', return_value=None)
def test_when_cpu_freq_cannot_fetch_frequency(cpu_freq_mock, testdir):
    """Make sure that pytest-monitor does the job when we have issue in collecing context resources"""
    # create a temporary pytest test module
    testdir.makepyfile("""
    import time


    def test_ok():
        time.sleep(0.5)
        x = ['a' * i for i in range(100)]
        assert len(x) == 100

""")

    # run pytest with the following cmd args
    result = testdir.runpytest('-vv')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_ok PASSED*'])

    pymon_path = pathlib.Path(str(testdir)) / '.pymon'
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the test suite
    result.assert_outcomes(passed=1)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute('SELECT ITEM FROM TEST_METRICS;')
    assert 1 == len(cursor.fetchall())  # current test
    cursor = db.cursor()
    cursor.execute('SELECT CPU_FREQUENCY_MHZ FROM EXECUTION_CONTEXTS;')
    rows = cursor.fetchall()
    assert 1 == len(rows)
    assert rows[0][0] == 0
    

# -*- coding: utf-8 -*-
import os
import pathlib
import sqlite3


def test_monitor_no_ci(testdir):
    """Make sure that pytest-monitor does not insert CI information."""
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

    envs = {}
    for k in [
        "CIRCLE_BUILD_NUM",
        "CIRCLE_JOB",
        "DRONE_REPO_BRANCH",
        "DRONE_BUILD_NUMBER",
        "BUILD_NUMBER",
        "JOB_NUMBER",
        "JOB_NAME",
        "TRAVIS_BUILD_ID",
        "TRAVIS_BUILD_NUMBER",
        "CI_PIPELINE_ID",
        "CI_JOB_NAME",
        "BITBUCKET_BRANCH",
        "BITBUCKET_BUILD_NUMBER",
    ]:
        if k in os.environ:
            envs[k] = os.environ[k]
            del os.environ[k]

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(["*::test_ok PASSED*"])

    pymon_path = pathlib.Path(str(testdir)) / ".pymon"
    assert pymon_path.exists()

    # make sure that that we get a '0' exit code for the testsuite
    result.assert_outcomes(passed=1)

    db = sqlite3.connect(str(pymon_path))
    cursor = db.cursor()
    cursor.execute("SELECT RUN_DESCRIPTION FROM TEST_SESSIONS;")
    desc = cursor.fetchall()
    assert len(desc) == 1  # current test
    assert desc[0][0] == "{}"
    for k in envs.keys():
        os.environ[k] = envs[k]


def test_monitor_jenkins_ci(testdir):
    """Make sure that pytest-monitor correctly handle Jenkins CI information."""
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

    def check_that(the_result, match):
        # fnmatch_lines does an assertion internally
        the_result.stdout.fnmatch_lines(["*::test_ok PASSED*"])

        pymon_path = pathlib.Path(str(testdir)) / ".pymon"
        assert pymon_path.exists()

        # make sure that that we get a '0' exit code for the testsuite
        the_result.assert_outcomes(passed=1)

        db = sqlite3.connect(str(pymon_path))
        cursor = db.cursor()
        cursor.execute("SELECT RUN_DESCRIPTION FROM TEST_SESSIONS;")
        desc = cursor.fetchall()
        assert len(desc) == 1  # current test
        assert desc[0][0] == match
        pymon_path.unlink()

    run_description = '{"pipeline_branch": "test", "pipeline_build_no": "123", "__ci__": "jenkinsci"}'

    envs = {}
    for k in [
        "CIRCLE_BUILD_NUM",
        "CIRCLE_JOB",
        "DRONE_REPO_BRANCH",
        "DRONE_BUILD_NUMBER",
        "BUILD_NUMBER",
        "JOB_NUMBER",
        "JOB_NAME",
        "TRAVIS_BUILD_ID",
        "TRAVIS_BUILD_NUMBER",
        "CI_PIPELINE_ID",
        "CI_JOB_NAME",
        "BITBUCKET_BRANCH",
        "BITBUCKET_BUILD_NUMBER",
    ]:
        if k in os.environ:
            envs[k] = os.environ[k]
            del os.environ[k]

    for env, exp in [
        ({"BUILD_NUMBER": "123"}, "{}"),
        ({"BUILD_NUMBER": "123", "JOB_NAME": "test"}, run_description),
        ({"BUILD_NUMBER": "123", "BRANCH_NAME": "test"}, run_description),
        (
            {"BUILD_NUMBER": "123", "JOB_NAME": "test-123", "BRANCH_NAME": "test"},
            run_description,
        ),
    ]:
        if "BUILD_NUMBER" in os.environ:
            del os.environ["BUILD_NUMBER"]
        if "JOB_NUMBER" in os.environ:
            del os.environ["JOB_NAME"]
        if "BRANCH_NUMBER" in os.environ:
            del os.environ["BRANCH_NAME"]

        for k, v in env.items():
            os.environ[k] = v

        result = testdir.runpytest("-v")
        check_that(result, match=exp)

    if "BUILD_NUMBER" in os.environ:
        del os.environ["BUILD_NUMBER"]
    if "JOB_NUMBER" in os.environ:
        del os.environ["JOB_NAME"]
    if "BRANCH_NUMBER" in os.environ:
        del os.environ["BRANCH_NAME"]


def test_monitor_gitlab_ci(testdir):
    """Make sure that pytest-monitor correctly handle Gitlab CI information."""
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

    def check_that(the_result, match):
        # fnmatch_lines does an assertion internally
        the_result.stdout.fnmatch_lines(["*::test_ok PASSED*"])

        pymon_path = pathlib.Path(str(testdir)) / ".pymon"
        assert pymon_path.exists()

        # make sure that that we get a '0' exit code for the testsuite
        the_result.assert_outcomes(passed=1)

        db = sqlite3.connect(str(pymon_path))
        cursor = db.cursor()
        cursor.execute("SELECT RUN_DESCRIPTION FROM TEST_SESSIONS;")
        desc = cursor.fetchall()
        assert len(desc) == 1  # current test
        assert desc[0][0] == match
        pymon_path.unlink()

    run_description = '{"pipeline_branch": "test", "pipeline_build_no": "123", "__ci__": "gitlabci"}'
    envs = {}
    for k in [
        "CIRCLE_BUILD_NUM",
        "CIRCLE_JOB",
        "DRONE_REPO_BRANCH",
        "DRONE_BUILD_NUMBER",
        "BUILD_NUMBER",
        "JOB_NUMBER",
        "JOB_NAME",
        "TRAVIS_BUILD_ID",
        "TRAVIS_BUILD_NUMBER",
        "CI_PIPELINE_ID",
        "CI_JOB_NAME",
        "BITBUCKET_BRANCH",
        "BITBUCKET_BUILD_NUMBER",
    ]:
        if k in os.environ:
            envs[k] = os.environ[k]
            del os.environ[k]

    for env, exp in [
        ({"CI_PIPELINE_ID": "123"}, "{}"),
        ({"CI_PIPELINE_ID": "123", "CI_JOB_NAME": "test"}, run_description),
        ({"CI_JOB_NAME": "123"}, "{}"),
    ]:
        if "CI_PIPELINE_ID" in os.environ:
            del os.environ["CI_PIPELINE_ID"]
        if "CI_JOB_NAME" in os.environ:
            del os.environ["CI_JOB_NAME"]

        for k, v in env.items():
            os.environ[k] = v

        result = testdir.runpytest("-v")
        check_that(result, match=exp)

    if "CI_PIPELINE_ID" in os.environ:
        del os.environ["CI_PIPELINE_ID"]
    if "CI_JOB_NAME" in os.environ:
        del os.environ["CI_JOB_NAME"]


def test_monitor_travis_ci(testdir):
    """Make sure that pytest-monitor correctly handle Travis CI information."""
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

    def check_that(the_result, match):
        # fnmatch_lines does an assertion internally
        the_result.stdout.fnmatch_lines(["*::test_ok PASSED*"])

        pymon_path = pathlib.Path(str(testdir)) / ".pymon"
        assert pymon_path.exists()

        # make sure that that we get a '0' exit code for the testsuite
        the_result.assert_outcomes(passed=1)

        db = sqlite3.connect(str(pymon_path))
        cursor = db.cursor()
        cursor.execute("SELECT RUN_DESCRIPTION FROM TEST_SESSIONS;")
        desc = cursor.fetchall()
        assert len(desc) == 1  # current test
        assert desc[0][0] == match
        pymon_path.unlink()

    run_description = '{"pipeline_branch": "test", "pipeline_build_no": "123", "__ci__": "travisci"}'
    envs = {}
    for k in [
        "CIRCLE_BUILD_NUM",
        "CIRCLE_JOB",
        "DRONE_REPO_BRANCH",
        "DRONE_BUILD_NUMBER",
        "BUILD_NUMBER",
        "JOB_NUMBER",
        "JOB_NAME",
        "TRAVIS_BUILD_ID",
        "TRAVIS_BUILD_NUMBER",
        "CI_PIPELINE_ID",
        "CI_JOB_NAME",
        "BITBUCKET_BRANCH",
        "BITBUCKET_BUILD_NUMBER",
    ]:
        if k in os.environ:
            envs[k] = os.environ[k]
            del os.environ[k]

    for env, exp in [
        ({"TRAVIS_BUILD_NUMBER": "123"}, "{}"),
        ({"TRAVIS_BUILD_NUMBER": "123", "TRAVIS_BUILD_ID": "test"}, run_description),
        ({"TRAVIS_BUILD_ID": "test-123"}, "{}"),
    ]:
        if "TRAVIS_BUILD_NUMBER" in os.environ:
            del os.environ["TRAVIS_BUILD_NUMBER"]
        if "TRAVIS_BUILD_ID" in os.environ:
            del os.environ["TRAVIS_BUILD_ID"]

        for k, v in env.items():
            os.environ[k] = v

        result = testdir.runpytest("-v")
        check_that(result, match=exp)

    if "TRAVIS_BUILD_NUMBER" in os.environ:
        del os.environ["TRAVIS_BUILD_NUMBER"]
    if "TRAVIS_BUILD_ID" in os.environ:
        del os.environ["TRAVIS_BUILD_ID"]


def test_monitor_circle_ci(testdir):
    """Make sure that pytest-monitor correctly handle Circle CI information."""
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

    def check_that(the_result, match):
        # fnmatch_lines does an assertion internally
        the_result.stdout.fnmatch_lines(["*::test_ok PASSED*"])

        pymon_path = pathlib.Path(str(testdir)) / ".pymon"
        assert pymon_path.exists()

        # make sure that that we get a '0' exit code for the testsuite
        the_result.assert_outcomes(passed=1)

        db = sqlite3.connect(str(pymon_path))
        cursor = db.cursor()
        cursor.execute("SELECT RUN_DESCRIPTION FROM TEST_SESSIONS;")
        desc = cursor.fetchall()
        assert len(desc) == 1  # current test
        assert desc[0][0] == match
        pymon_path.unlink()

    run_description = '{"pipeline_branch": "test", "pipeline_build_no": "123", "__ci__": "circleci"}'
    envs = {}
    for k in [
        "CIRCLE_BUILD_NUM",
        "CIRCLE_JOB",
        "DRONE_REPO_BRANCH",
        "DRONE_BUILD_NUMBER",
        "BUILD_NUMBER",
        "JOB_NUMBER",
        "JOB_NAME",
        "TRAVIS_BUILD_ID",
        "TRAVIS_BUILD_NUMBER",
        "CI_PIPELINE_ID",
        "CI_JOB_NAME",
        "BITBUCKET_BRANCH",
        "BITBUCKET_BUILD_NUMBER",
    ]:
        if k in os.environ:
            envs[k] = os.environ[k]
            del os.environ[k]

    for env, exp in [
        ({"CIRCLE_BUILD_NUM": "123"}, "{}"),
        ({"CIRCLE_BUILD_NUM": "123", "CIRCLE_JOB": "test"}, run_description),
        ({"CIRCLE_JOB": "test"}, "{}"),
    ]:
        if "CIRCLE_BUILD_NUM" in os.environ:
            del os.environ["CIRCLE_BUILD_NUM"]
        if "CIRCLE_JOB" in os.environ:
            del os.environ["CIRCLE_JOB"]

        for k, v in env.items():
            os.environ[k] = v

        result = testdir.runpytest("-v")
        check_that(result, match=exp)

    if "CIRCLE_BUILD_NUM" in os.environ:
        del os.environ["CIRCLE_BUILD_NUM"]
    if "CIRCLE_JOB" in os.environ:
        del os.environ["CIRCLE_JOB"]


def test_monitor_drone_ci(testdir):
    """Make sure that pytest-monitor correctly handle Jenkins CI information."""
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

    def check_that(the_result, match):
        # fnmatch_lines does an assertion internally
        the_result.stdout.fnmatch_lines(["*::test_ok PASSED*"])

        pymon_path = pathlib.Path(str(testdir)) / ".pymon"
        assert pymon_path.exists()

        # make sure that that we get a '0' exit code for the testsuite
        the_result.assert_outcomes(passed=1)

        db = sqlite3.connect(str(pymon_path))
        cursor = db.cursor()
        cursor.execute("SELECT RUN_DESCRIPTION FROM TEST_SESSIONS;")
        desc = cursor.fetchall()
        assert len(desc) == 1  # current test
        assert desc[0][0] == match
        pymon_path.unlink()

    run_description = '{"pipeline_branch": "test", "pipeline_build_no": "123", "__ci__": "droneci"}'
    envs = {}
    for k in [
        "CIRCLE_BUILD_NUM",
        "CIRCLE_JOB",
        "DRONE_REPO_BRANCH",
        "DRONE_BUILD_NUMBER",
        "BUILD_NUMBER",
        "JOB_NUMBER",
        "JOB_NAME",
        "TRAVIS_BUILD_ID",
        "TRAVIS_BUILD_NUMBER",
        "CI_PIPELINE_ID",
        "CI_JOB_NAME",
        "BITBUCKET_BRANCH",
        "BITBUCKET_BUILD_NUMBER",
    ]:
        if k in os.environ:
            envs[k] = os.environ[k]
            del os.environ[k]

    for env, exp in [
        ({"DRONE_BUILD_NUMBER": "123"}, "{}"),
        ({"DRONE_BUILD_NUMBER": "123", "DRONE_REPO_BRANCH": "test"}, run_description),
        ({"DRONE_REPO_BRANCH": "test"}, "{}"),
    ]:
        if "DRONE_REPO_BRANCH" in os.environ:
            del os.environ["DRONE_REPO_BRANCH"]
        if "DRONE_BUILD_NUMBER" in os.environ:
            del os.environ["DRONE_BUILD_NUMBER"]

        for k, v in env.items():
            os.environ[k] = v

        result = testdir.runpytest("-v")
        check_that(result, match=exp)

    if "DRONE_REPO_BRANCH" in os.environ:
        del os.environ["DRONE_REPO_BRANCH"]
    if "DRONE_BUILD_NUMBER" in os.environ:
        del os.environ["DRONE_BUILD_NUMBER"]

def test_monitor_bitbucket_ci(testdir):
    """Make sure that pytest-monitor correctly handle Bitbucket CI information."""
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

    def check_that(the_result, match):
        # fnmatch_lines does an assertion internally
        the_result.stdout.fnmatch_lines(["*::test_ok PASSED*"])

        pymon_path = pathlib.Path(str(testdir)) / ".pymon"
        assert pymon_path.exists()

        # make sure that that we get a '0' exit code for the testsuite
        the_result.assert_outcomes(passed=1)

        db = sqlite3.connect(str(pymon_path))
        cursor = db.cursor()
        cursor.execute("SELECT RUN_DESCRIPTION FROM TEST_SESSIONS;")
        desc = cursor.fetchall()
        assert len(desc) == 1  # current test
        assert desc[0][0] == match
        pymon_path.unlink()

    run_description = '{"pipeline_branch": "test", "pipeline_build_no": "123", "__ci__": "bitbucketci"}'
    envs = {}
    for k in [
        "CIRCLE_BUILD_NUM",
        "CIRCLE_JOB",
        "DRONE_REPO_BRANCH",
        "DRONE_BUILD_NUMBER",
        "BUILD_NUMBER",
        "JOB_NUMBER",
        "JOB_NAME",
        "TRAVIS_BUILD_ID",
        "TRAVIS_BUILD_NUMBER",
        "CI_PIPELINE_ID",
        "CI_JOB_NAME",
        "BITBUCKET_BRANCH",
        "BITBUCKET_BUILD_NUMBER",
    ]:
        if k in os.environ:
            envs[k] = os.environ[k]
            del os.environ[k]

    for env, exp in [
        ({"BITBUCKET_BUILD_NUMBER": "123"}, "{}"),
        ({"BITBUCKET_BUILD_NUMBER": "123", "BITBUCKET_BRANCH": "test"}, run_description),
        ({"BITBUCKET_BRANCH": "test"}, "{}"),
    ]:
        if "BITBUCKET_BRANCH" in os.environ:
            del os.environ["BITBUCKET_BRANCH"]
        if "BITBUCKET_BUILD_NUMBER" in os.environ:
            del os.environ["BITBUCKET_BUILD_NUMBER"]

        for k, v in env.items():
            os.environ[k] = v

        result = testdir.runpytest("-v")
        check_that(result, match=exp)

    if "BITBUCKET_BRANCH" in os.environ:
        del os.environ["BITBUCKET_BRANCH"]
    if "BITBUCKET_BUILD_NUMBER" in os.environ:
        del os.environ["BITBUCKET_BUILD_NUMBER"]

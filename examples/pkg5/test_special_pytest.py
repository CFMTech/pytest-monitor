import pytest


@pytest.mark.skip(reason="Some special test to skip")
def test_is_skipped():
    assert True


def test_that_one_is_skipped_too():
    pytest.skip("Test executed and instructed to be skipped from its body")


def test_import_or_skip():
    pytest.importorskip("this_module_does_not_exists")

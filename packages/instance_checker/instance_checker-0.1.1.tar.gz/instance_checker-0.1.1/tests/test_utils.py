from unittest import mock

import pytest
from psutil import NoSuchProcess

from src.instance_checker.utils import CountHelper


@pytest.fixture
def helper():
    with mock.patch("src.instance_checker.utils.gettempdir", return_value="/tmp/locks"):
        yield CountHelper(lock_dir="/tmp/locks")


TEST_IDENTIFIER = "my_app"


@mock.patch("src.instance_checker.utils.process_iter")
def test_process_count_no_matches(mock_process_iter):
    mock_process_iter.return_value = []

    count = CountHelper.process_count(TEST_IDENTIFIER)
    assert count == 0


@mock.patch("src.instance_checker.utils.process_iter")
def test_process_count_one_match(mock_process_iter):
    mock_process_iter.return_value = [
        mock.MagicMock(
            cmdline=mock.MagicMock(return_value=["/usr/bin/python", "my_app.py"]),
        ),
        mock.MagicMock(
            cmdline=mock.MagicMock(return_value=["/bin/sh", "other_script.sh"]),
        ),
    ]

    count = CountHelper.process_count(TEST_IDENTIFIER)
    assert count == 1


@mock.patch("src.instance_checker.utils.process_iter")
def test_process_count_raised(mock_process_iter):
    mock_process_iter.return_value = [
        mock.MagicMock(cmdline=mock.MagicMock(side_effect=NoSuchProcess(123))),
    ]

    count = CountHelper.process_count(TEST_IDENTIFIER)
    assert count == 0


@mock.patch("src.instance_checker.utils.os.walk")
def test_pid_file_count_no_files(mock_walk, helper):
    mock_walk.return_value = [(".", [], [])]

    count = helper.pid_file_count(TEST_IDENTIFIER)
    assert count == 0


@mock.patch("src.instance_checker.utils.os.walk")
def test_pid_file_count_one_file(mock_walk, helper):
    mock_walk.return_value = [("/tmp/locks", [], ["my_app.lock.0"])]

    count = helper.pid_file_count(TEST_IDENTIFIER)
    assert count == 1

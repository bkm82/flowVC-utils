import os
import uuid
import json
import pytest
from unittest.mock import mock_open, patch
import logging.config
import logging.handlers
from flowvcutils.jsonlogger import settup_logging, print_last_logs
from flowvcutils.jsonlogger import main as jsonlogger_main
from flowvcutils.utils import get_project_root


@pytest.fixture
def mock_log_file():
    log_entries = [
        json.dumps({"message": "Log entry 1", "timestamp": "2023-01-01T00:00:00Z"}),
        json.dumps({"message": "Log entry 2", "timestamp": "2023-01-01T01:00:00Z"}),
        json.dumps({"message": "Log entry 3", "timestamp": "2023-01-01T02:00:00Z"}),
    ]
    return "\n".join(log_entries)


def test_print_last_logs(capfd, mock_log_file):
    with patch("builtins.open", mock_open(read_data=mock_log_file)):
        print_last_logs(2)
        captured = capfd.readouterr()
        expected_output = (
            json.dumps(
                {"message": "Log entry 2", "timestamp": "2023-01-01T01:00:00Z"},
                indent=4,
            )
            + "\n"
            + json.dumps(
                {"message": "Log entry 3", "timestamp": "2023-01-01T02:00:00Z"},
                indent=4,
            )
            + "\n"
        )

        assert captured.out == expected_output


def test_print_last_logs_with_error(capfd, mock_log_file):
    # Corrupt the last log entry to induce JSONDecodeError
    faulty_log = mock_log_file + "\n{"
    with patch("builtins.open", mock_open(read_data=faulty_log)):
        print_last_logs(2)
        captured = capfd.readouterr()
        assert "Error printing log" in captured.out


def test_logging_integration():

    logger = logging.getLogger("test_logging_integration")
    settup_logging()
    unique_id = str(uuid.uuid4())
    test_message = f"Test Log From test_logging_integration. unique ID: {unique_id}"
    logger.debug(test_message)
    root = get_project_root()
    log_file = os.path.join(root, "logs", "flowvcutils.log")

    found_message = False
    with open(log_file, "r") as f:
        if test_message in f.read():
            found_message = True

    assert found_message, "Test message not found in log file"

    assert True

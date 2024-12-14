import os
import uuid
import json
import pytest
from unittest.mock import mock_open, patch
import logging.config
import logging.handlers
from flowvcutils.jsonlogger import settup_logging, print_last_logs
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
    # test_message = f"Test Log From test_logging_integration. unique ID: {unique_id}"
    try:
        raise ValueError(f"Simulated error for {unique_id}")
    except ValueError as e:
        logger.error(
            f"Error occured:{e}",
            exc_info=True,
            stack_info=True,
            extra={"test_key": "test_results"},
        )
    root = get_project_root()
    log_file = os.path.join(root, "logs", "flowvcutils.log")
    json_file = os.path.join(root, "logs", "flowvcutils.log.jsonl")

    # Read the latest log file
    found_message = False
    with open(log_file, "r") as f:
        if unique_id in f.read():
            found_message = True

    assert found_message, "Test message not found in log file"

    # Check json log files
    found_message_json = False
    with open(json_file, "r") as f:
        for line in f:
            try:
                log_entry = json.loads(line)
                if unique_id in log_entry.get("message", ""):
                    found_message_json = True
                    actual_test_key = log_entry.get("test_key", "")
                    actual_exe_info = log_entry.get("exc_info", "")
                    actual_stack_info = log_entry.get("stack_info", "")
                    break

            except json.JSONDecodeError:
                continue

    assert actual_exe_info != "", "exc_info should not be empty but it is"
    assert actual_stack_info != "", "stack_info should not be empty but it is"
    assert actual_test_key == "test_results", "test key doesnt match"
    assert found_message_json, "Test message not found in json log file"


def test_init():
    from flowvcutils import jsonlogger as module

    with patch.object(module, "main", return_value=42):
        with patch.object(module, "__name__", "__main__"):
            with patch.object(module.sys, "exit") as mock_exit:
                module.init()
                assert mock_exit.call_args[0][0] == 42

import logging
import uuid
import pytest
import json
import sys
from tempfile import TemporaryDirectory
from unittest import mock
from click.testing import CliRunner
from unittest.mock import patch
from flowvcutils.cli import jsonlogger
from flowvcutils.cli import inigenerator
from flowvcutils.cli import simulationgenerator
from flowvcutils.cli import main as cli_main
from flowvcutils.jsonlogger import settup_logging


logger = logging.getLogger(__name__)


@pytest.fixture
def runner():
    return CliRunner()


@patch("flowvcutils.cli.jsonlogger_main")
def test_default_num_lines(mock_jsonlogger_main, runner):
    """Test that the default value of num_lines is passed."""
    result = runner.invoke(jsonlogger, [])
    assert result.exit_code == 0
    mock_jsonlogger_main.assert_called_once_with(10)


@patch("flowvcutils.cli.jsonlogger_main")
def test_custom_num_lines(mock_jsonlogger_main, runner):
    """Test that a custom value for num_lines is passed."""
    result = runner.invoke(jsonlogger, ["20"])
    assert result.exit_code == 0
    mock_jsonlogger_main.assert_called_once_with(20)


def test_integration_main_jsonlogger(monkeypatch, capsys):
    """Integration test ensuring running json logger calls last log."""
    monkeypatch.setattr(sys, "argv", ["flowvcutils", "jsonlogger", "1"])

    logger = logging.getLogger("test_logging_integration")
    settup_logging()
    unique_id = str(uuid.uuid4())
    test_message = f"Integration Test Log from cli_main. unique ID: {unique_id}"
    logger.debug(test_message)
    with pytest.raises(SystemExit):
        cli_main()

    captured = capsys.readouterr()

    try:
        log_entry = json.loads(captured.out.strip())
    except json.JSONDecodeError:
        pytest.fail("Captured output is not valid json")
    assert test_message in log_entry.get("message", "")


@patch("flowvcutils.cli.inigenerator_main")
def test_default_ini_generator(mock_ini_generator_main, runner):
    """Test that the default value of num_lines is passed."""
    with TemporaryDirectory() as tmp_dir:
        result = runner.invoke(inigenerator, [f"-d{tmp_dir}"])
        assert result.exit_code == 0
        mock_ini_generator_main.assert_called_once_with(
            tmp_dir, True, 0.001, "backward", False
        )


@patch("flowvcutils.cli.simulationgenerator_main")
def test_default_simulationgenerator(mock_simulationgenerator_main, runner):
    """Test that the default value of num_lines is passed."""
    with TemporaryDirectory() as tmp_dir:
        result = runner.invoke(simulationgenerator, [f"-d{tmp_dir}"])
        assert result.exit_code == 0
        mock_simulationgenerator_main.assert_called_once_with(tmp_dir, [])


def test_init():
    from flowvcutils import cli

    with mock.patch.object(cli, "main", return_value=42):
        with mock.patch.object(cli, "__name__", "__main__"):
            with mock.patch.object(cli.sys, "exit") as mock_exit:
                cli.init()
                assert mock_exit.call_args[0][0] == 42

import pytest
from click.testing import CliRunner
from click.exceptions import BadParameter
from unittest.mock import patch
from flowvcutils.cli import jsonlogger


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

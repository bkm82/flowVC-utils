import pytest
from unittest import mock
from click.testing import CliRunner
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


def test_init():
    from flowvcutils import cli

    with mock.patch.object(cli, "main", return_value=42):
        with mock.patch.object(cli, "__name__", "__main__"):
            with mock.patch.object(cli.sys, "exit") as mock_exit:
                cli.init()
                assert mock_exit.call_args[0][0] == 42

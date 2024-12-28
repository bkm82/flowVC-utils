import os
import pytest
from unittest.mock import patch
from tempfile import TemporaryDirectory
from flowvcutils import simulationgenerator


@pytest.fixture
def setup_test_environment(tmp_path):
    with TemporaryDirectory() as tmp_dir:
        base_dir = tmp_dir

        # base_dir.mkdir()
        os.makedirs(os.path.join(base_dir, "generic_file"))
        inlet_velocity_dir = os.path.join(base_dir, "inlet_velocity")
        os.makedirs(inlet_velocity_dir)
        # Add a steady.txt file
        steady_file_path = os.path.join(inlet_velocity_dir, "steady_.txt")
        with open(steady_file_path, "w") as f:
            f.write("0.0 -4.16e-05\n1.01400006 -4.16e-05\n")

        # Add an exclude.txt file
        exclude_file_path = os.path.join(inlet_velocity_dir, "exclude.txt")
        with open(exclude_file_path, "w") as f:
            f.write("exclude.txt\n")
        generic_file_path = os.path.join(base_dir, "generic_file.sjb")
        with open(generic_file_path, "w"):
            pass
        yield base_dir


def test_create_directories(setup_test_environment):
    """Test that the copy_directory works."""
    src = setup_test_environment
    dest = os.path.join(setup_test_environment, "steady_")
    simulationgenerator.create_directories(src)
    assert os.path.exists(dest)


def test_create_directories_exclude(setup_test_environment):
    """Test that the create_dirctorys respects exclude.txt."""
    src = setup_test_environment
    dest = os.path.join(setup_test_environment, "exclude")
    simulationgenerator.create_directories(src)
    assert not os.path.exists(dest)


@pytest.mark.skip
def test_replace_file(setup_test_environment):
    source_file = setup_test_environment / "source.txt"
    destination_file = setup_test_environment / "destination.txt"
    with open(source_file, "w") as f:
        f.write("Sample text.")

    simulationgenerator.replace_file(source_file, destination_file)
    with open(destination_file, "r") as f:
        content = f.read()

    assert content == "Sample text."


@pytest.mark.skip
@patch("flowvcutils.simulationgenerator.subprocess.run")
def test_run_command(mock_run):
    simulationgenerator.run_command("echo test", "/path/to/cwd")
    mock_run.assert_called_once_with(
        "echo test", shell=True, cwd="/path/to/cwd", env=os.environ
    )

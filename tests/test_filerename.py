import os
import shutil
import pytest
from flowvcutils.filerename import rename_files, renumber_files
from tempfile import TemporaryDirectory


@pytest.fixture
def temp_directory():
    """
    pytest fixture to create a temp directory populated with file names

    files:
      all_results_00000.vtu
      all_results_00050.vtu
      all_results_00100.vtu
    """
    temp_dir = "/tmp/A_0.000065_T_1.014_peak_0.51_"
    os.makedirs(temp_dir, exist_ok=True)
    try:
        # Add test files
        test_files = [
            "all_results_00001.vtu",
            "all_results_00002.vtu",
            "all_results_00003.vtu",
            "new_name_00001.vtu",
        ]
        for file_name in test_files:
            open(os.path.join(temp_dir, file_name), "w").close()
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


def test_rename_files_no_prefex(temp_directory):

    rename_files(temp_directory)

    # Get the renamed files
    renamed_files = sorted(os.listdir(temp_directory))
    expected_files = [
        "A_0.000065_T_1.014_peak_0.51_00001.vtu",
        "A_0.000065_T_1.014_peak_0.51_00002.vtu",
        "A_0.000065_T_1.014_peak_0.51_00003.vtu",
        "new_name_00001.vtu",
    ]

    # Check that the renamed files match the expected output
    assert renamed_files == expected_files


def test_rename_files_with_prefex(temp_directory):

    rename_files(temp_directory, prefix="steady")

    # Get the renamed files
    renamed_files = sorted(os.listdir(temp_directory))
    expected_files = [
        "new_name_00001.vtu",
        "steady_00001.vtu",
        "steady_00002.vtu",
        "steady_00003.vtu",
    ]

    # Check that the renamed files match the expected output
    assert renamed_files == expected_files


def test_rename_files_with_name(temp_directory):

    rename_files(temp_directory, prefix="steady", current_name="new_name")

    # Get the renamed files
    renamed_files = sorted(os.listdir(temp_directory))
    expected_files = [
        "all_results_00001.vtu",
        "all_results_00002.vtu",
        "all_results_00003.vtu",
        "steady_00001.vtu",
    ]

    # Check that the renamed files match the expected output
    assert renamed_files == expected_files


@pytest.fixture
def renumber_directory(file_name):
    """
    pytest fixture to create a temp directory
    directory populated with enumaerated files starting from 0

    files:
      file_name.0.vtk
      file_name.1.vtk
      ...
      file_name.39.vtk
    """
    with TemporaryDirectory() as tmp_dir:
        for i in range(40):
            test_file = f"{file_name}.{i}.vtk"
            with open(os.path.join(tmp_dir, test_file), "w") as f:
                f.write("sample data")
        yield tmp_dir


@pytest.mark.parametrize(
    "file_name",
    ["A_0.000131_T_0.507_peak_0.76_backward", "A_0.000131_T_0.507_peak_0.51_backward"],
)
def test_renumber_files(renumber_directory, file_name):

    expected_files = []
    for i in range(40):
        new_number = 3000 + (i * 50)
        expected_file = f"{file_name}.{new_number}.vtk"
        expected_files.append(expected_file)
    tmp_dir = renumber_directory
    renumber_files(tmp_dir, file_name)
    expected_file_set = set(expected_files)
    actual_files_set = set(os.listdir(tmp_dir))
    assert actual_files_set == expected_file_set


@pytest.mark.parametrize(
    "file_name",
    ["A_0.000131_T_0.507_peak_0.76_backward", "A_0.000131_T_0.507_peak_0.51_backward"],
)
def test_renumber_files_without_file_name(renumber_directory, file_name):

    expected_files = []
    for i in range(40):
        new_number = 3000 + (i * 50)
        expected_file = f"{file_name}.{new_number}.vtk"
        expected_files.append(expected_file)
    tmp_dir = renumber_directory
    renumber_files(tmp_dir)
    expected_file_set = set(expected_files)
    actual_files_set = set(os.listdir(tmp_dir))
    assert actual_files_set == expected_file_set

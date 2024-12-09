import os
import shutil
import pytest
from flowvcutils.filerename import rename_files


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

    rename_files(temp_directory, prefix="steady", currentname="new_name")

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

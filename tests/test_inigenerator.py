import pytest
import vtk
import os
from tempfile import TemporaryDirectory
from flowvcutils.inigenerator import resultsProcessor, directoryHandler
from unittest.mock import MagicMock


@pytest.fixture
def create_sample_vtu_file():
    """
    Creates a temporary .vtu file with sample data for testing using vtk.
    """
    with TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "test.vtu")

        # Create points
        points = vtk.vtkPoints()
        points.InsertNextPoint(1.0, 2.0, 3.0)
        points.InsertNextPoint(4.0, 5.0, 6.0)
        points.InsertNextPoint(-1.0, -2.0, -3.0)

        # Create an unstructured grid and add the points
        grid = vtk.vtkUnstructuredGrid()
        grid.SetPoints(points)

        # Write to a .vtu file
        writer = vtk.vtkXMLUnstructuredGridWriter()
        writer.SetFileName(file_path)
        writer.SetInputData(grid)
        writer.Write()

        yield file_path


def test_find_data_range(create_sample_vtu_file):
    """
    Test the find_data_range function.
    """
    file_path = create_sample_vtu_file

    mock_directory_handler = MagicMock()
    processor = resultsProcessor(mock_directory_handler)

    # Run the function on the test file
    x_range, y_range, z_range = processor.find_data_range(file_path)

    # Assert the expected results
    assert x_range == (-1.0, 4.0), f"Unexpected X range: {x_range}"
    assert y_range == (-2.0, 5.0), f"Unexpected Y range: {y_range}"
    assert z_range == (-3.0, 6.0), f"Unexpected Z range: {z_range}"


def test_find_data_state(create_sample_vtu_file):
    """
    Test that initializing a file processor stores the x, y and z range state.
    """
    file_path = create_sample_vtu_file
    mock_directory_handler = MagicMock()
    mock_directory_handler.find_vtu.return_value = file_path
    processor = resultsProcessor(mock_directory_handler)

    # Call the find_data_range without a filepath
    processor.find_data_range()

    # Assert the expected results
    assert processor.min_x == -1.0, f"Unexpected X range: {processor.min_x}"
    assert processor.max_x == 4.0, f"Unexpected x max: {processor.max_x}"
    assert processor.min_y == -2.0, f"Unexpected X range: {processor.min_y}"
    assert processor.max_y == 5.0, f"Unexpected x max: {processor.max_y}"
    assert processor.min_z == -3.0, f"Unexpected X range: {processor.min_z}"
    assert processor.max_z == 6.0, f"Unexpected x max: {processor.max_z}"


def test_validate_directory_exists():
    """
    Test case where the directory exists.
    """
    # Create a temporary directory using tempfile
    with TemporaryDirectory() as temp_dir:
        # Assert that the validate_directory function returns True for a valid directory
        valid_dir = directoryHandler(temp_dir)
        assert valid_dir.directory == temp_dir


def test_validate_directory_does_not_exist():
    """
    Test case where the directory does not exist.
    """
    non_existent_dir = "/path/to/nonexistent/directory"
    with pytest.raises(FileNotFoundError):
        directoryHandler(non_existent_dir)


def test_vtu_file_exist():
    """
    Test case where the vtu file exists.
    """
    with TemporaryDirectory() as temp_dir:
        expected = os.path.join(temp_dir, "test_file.vtu")
        with open(expected, "w") as f:
            f.write("dummy content")
        dir_handler = directoryHandler(temp_dir)
        actual = dir_handler.find_vtu()
        assert actual == expected


def test_vtu_file_doesnt_exist():
    """
    Test case where the vtu file does not exist to ensure error is raised.
    """
    with TemporaryDirectory() as temp_dir:
        dir_handler = directoryHandler(temp_dir)
        with pytest.raises(FileNotFoundError):
            dir_handler.find_vtu()

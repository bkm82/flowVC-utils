import vtk
import pytest
import os
from unittest.mock import MagicMock
import tempfile
from flowvcutils.vtu_2_bin import (
    reader_selection,
    coordinates_file,
    create_vel_file_path,
    strip_trailing_underscore,
    create_file_path,
)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (".vtu", vtk.vtkXMLUnstructuredGridReader().GetClassName()),
        (".vtk", vtk.vtkDataSetReader().GetClassName()),
        (".vtp", vtk.vtkXMLPolyDataReader().GetClassName()),
        (".pvtu", vtk.vtkXMLPUnstructuredGridReader().GetClassName()),
    ],
)
def test_reader_selection_list(test_input, expected):
    assert reader_selection(test_input).GetClassName() == expected


def test_reader_selection_notsupported():
    with pytest.raises(ValueError):
        reader_selection(".unsuported")


@pytest.fixture
def mock_data():
    # Create a MagicMock for the data object
    data_mock = MagicMock()
    # Set the return value of GetNumberOfPoints to 2
    data_mock.GetNumberOfPoints.return_value = 2
    data_mock.GetNumberOfCells.return_value = 10
    return data_mock


def test_set_n_nodes(mock_data):
    # test that the number of nodes is set
    obj = coordinates_file(mock_data)
    obj.create_file()
    assert obj.n_nodes == 2


def test_coordinates_shape(mock_data):
    # test that the shape of the cordinates file is 3 times the number of nodes
    obj = coordinates_file(mock_data)
    obj.create_file()
    assert obj.coordinates.shape == (6,)


@pytest.mark.parametrize(
    "file_name, expected", [("test_name", "test_name"), ("test_name_", "test_name")]
)
def test_strip_trailing_underscore(file_name, expected):
    assert strip_trailing_underscore(file_name) == expected


@pytest.mark.parametrize(
    "file_name, file_num, expected",
    [
        ("file_name_", 50, "file_name_vel.50.bin"),
        ("file_name", 50, "file_name_vel.50.bin"),
    ],
)
def test_create_vel_file_path(file_name, file_num, expected):
    temp_dir = tempfile.mkdtemp()

    expected_path = os.path.join(temp_dir, expected)
    assert create_vel_file_path(temp_dir, file_name, file_num) == expected_path


@pytest.mark.parametrize(
    "file_name, file_type, expected",
    [
        (
            "file_name_",
            "coordinates",
            "file_name_coordinates.bin",
        ),
        (
            "file_name",
            "coordinates",
            "file_name_coordinates.bin",
        ),
        (
            "file_name_",
            "adjacency",
            "file_name_adjacency.bin",
        ),
        (
            "file_name",
            "adjacency",
            "file_name_adjacency.bin",
        ),
        (
            "file_name_",
            "connectivity",
            "file_name_connectivity.bin",
        ),
        (
            "file_name",
            "connectivity",
            "file_name_connectivity.bin",
        ),
    ],
)
def test_create_file_path(file_name, file_type, expected):
    temp_dir = tempfile.mkdtemp()

    expected_path = os.path.join(temp_dir, expected)
    actual = create_file_path(root=temp_dir, file_name=file_name, file_type=file_type)
    assert actual == expected_path

import vtk
import pytest
from unittest.mock import MagicMock
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
    "root, file_name, file_num, expected",
    [
        ("/some/directory", "file_name_", 50, "/some/directory/file_name_vel.50.bin"),
        ("/some/directory", "file_name", 50, "/some/directory/file_name_vel.50.bin"),
    ],
)
def test_create_vel_file_path(root, file_name, file_num, expected):
    assert create_vel_file_path(root, file_name, file_num) == expected


@pytest.mark.parametrize(
    "root, file_name, file_type, expected",
    [
        (
            "/some/directory",
            "file_name_",
            "coordinates",
            "/some/directory/file_name_coordinates.bin",
        ),
        (
            "/some/directory",
            "file_name",
            "coordinates",
            "/some/directory/file_name_coordinates.bin",
        ),
        (
            "/some/directory",
            "file_name_",
            "adjacency",
            "/some/directory/file_name_adjacency.bin",
        ),
        (
            "/some/directory",
            "file_name",
            "adjacency",
            "/some/directory/file_name_adjacency.bin",
        ),
        (
            "/some/directory",
            "file_name_",
            "connectivity",
            "/some/directory/file_name_connectivity.bin",
        ),
        (
            "/some/directory",
            "file_name",
            "connectivity",
            "/some/directory/file_name_connectivity.bin",
        ),
    ],
)
def test_create_file_path(root, file_name, file_type, expected):
    actual = create_file_path(root=root, file_name=file_name, file_type=file_type)
    assert actual == expected

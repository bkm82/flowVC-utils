import vtk
import pytest
from unittest.mock import MagicMock
from flowvcutils.vtu_2_bin import reader_selection
from flowvcutils.vtu_2_bin import coordinates_file


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

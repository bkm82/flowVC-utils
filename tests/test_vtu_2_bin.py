import vtk
import pytest
import os
from unittest.mock import MagicMock, patch
import tempfile
from flowvcutils.vtu_2_bin import (
    reader_selection,
    coordinates_file,
    create_vel_file_path,
    strip_trailing_underscore,
    create_file_path,
    Parser,
    Router,
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


class TestParser:
    """Unit tests for the parser class"""

    def setup_method(self):
        self.parser = Parser()

    def test_default_arguments(self):
        """Test that default arguments are set correctly."""
        args = self.parser.parse_arguments(["0", "100"])
        assert args.root == os.getcwd()
        assert args.output == os.getcwd()
        assert args.extension == ".vtu"
        assert args.increment == 50
        assert args.num_digits == 5
        assert args.field_name == "velocity"
        assert args.process == "folder"

    def test_custom_arguments(self):
        """Test parsing with custom arguments."""
        args = self.parser.parse_arguments(
            [
                "--root",
                "/input/dir",
                "--output",
                "/output/dir",
                "--extension",
                ".vtk",
                "--increment",
                "2",
                "--num_digits",
                "4",
                "--field_name",
                "velocity_noslip",
                "--process",
                "folder",
                "--file_name",
                "test_file_name",
                "0",
                "20",
            ]
        )
        assert args.root == "/input/dir"
        assert args.output == "/output/dir"
        assert args.extension == ".vtk"
        assert args.increment == 2
        assert args.num_digits == 4
        assert args.field_name == "velocity_noslip"
        assert args.process == "folder"

    # @pytest.mark.xfail()
    def test_directory_path(self):
        """
        Test parsing with path = directory.
        This should make file_name not required
        """
        args = self.parser.parse_arguments(
            [
                "--process",
                "directory",
                "0",
                "20",
            ]
        )
        assert args.process == "directory"

    def test_invalid_process_option(self):
        """Test that an invalid process option raises a SystemExit."""
        with pytest.raises(SystemExit):
            self.parser.parse_arguments(
                ["--process", "invalid", "file_name", "0", "10"]
            )


class TestRouter:
    @patch("flowvcutils.vtu_2_bin.process_folder")
    @patch("flowvcutils.vtu_2_bin.process_directory")
    def test_route_to_process_folder(self, mock_process_directory, mock_process_folder):
        # Mock arguments for 'folder' processing
        args = MagicMock()
        args.process = "folder"

        # Create Router and call route
        router = Router(args)
        router.route()

        # Assert process_folder is called with correct arguments
        mock_process_folder.assert_called_once()
        mock_process_directory.assert_not_called()

    @patch("flowvcutils.vtu_2_bin.process_folder")
    @patch("flowvcutils.vtu_2_bin.process_directory")
    def test_route_to_process_dirctory(
        self, mock_process_directory, mock_process_folder
    ):
        # Mock arguments for 'folder' processing
        args = MagicMock()
        args.process = "directory"

        # Create Router and call route
        router = Router(args)
        router.route()

        # Assert process_folder is called with correct arguments
        mock_process_folder.assert_not_called()
        mock_process_directory.assert_called_once()

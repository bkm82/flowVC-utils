import pytest
import vtk
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from flowvcutils.inigenerator import (
    resultsProcessor,
    directoryHandler,
    Config,
    main as inigenerator_main,
)
from unittest.mock import MagicMock
import logging
from flowvcutils.jsonlogger import settup_logging

logger = logging.getLogger(__name__)
settup_logging()


@pytest.fixture
def create_sample_vtu_file():
    """
    Creates a temporary .vtu file with sample data for testing using vtk.
    """
    with TemporaryDirectory() as temp_dir:
        sub_dir = os.path.join(temp_dir, "input_vtu")
        os.makedirs(sub_dir)
        file_path = os.path.join(sub_dir, "test.vtu")
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


@pytest.fixture()
def setup_processor():
    """Fixture to create a resultsProcessor instance."""
    directoryHandler = None
    return resultsProcessor(directoryHandler)


# Paramaterize when cell size does and does not evenly divide domain
@pytest.mark.parametrize(
    "pt_min, pt_max, cell_size, expected_max, expected_points",
    [
        (0.0, 10.0, 2.0, 10.0, 5),  # (10-0)/2 = 5 cells
        (0.0, 10.0, 3.0, 12.0, 4),  # (12-0)/3 = 4 cells
    ],
)
def test_streach_bounds_normal(
    setup_processor, pt_min, pt_max, cell_size, expected_max, expected_points
):
    processor = setup_processor
    new_max, points = processor.streach_bounds(pt_min, pt_max, cell_size)
    assert new_max == expected_max
    assert points == expected_points


def test_streach_bounds_invalid_min_max(setup_processor):
    processor = setup_processor
    with pytest.raises(ValueError):
        processor.streach_bounds(10.0, 0.0, 1.0)


def test_streach_bounds_invalid_cell_size(setup_processor):
    processor = setup_processor
    with pytest.raises(ValueError, match="Cell Size must be >0"):
        processor.streach_bounds(0.0, 10.0, 0.0)


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


def test_get_sub_directory_path():
    """
    Test case to get a subdirectory
    """
    # Create a temporary directory using tempfile
    with TemporaryDirectory() as temp_dir:
        subdir_name = "test_subdir"
        expected = os.path.join(temp_dir, subdir_name)
        os.mkdir(expected)
        directoryhandler = directoryHandler(temp_dir)
        actual = directoryhandler.get_sub_directory_path(subdir_name)

        assert actual == expected


def test_get_bad__directory_path():
    """
    Test case to get a subdirectory
    """
    # Create a temporary directory using tempfile
    with TemporaryDirectory() as temp_dir:
        subdir_name = "test_subdir"
        expected = os.path.join(temp_dir, subdir_name)
        os.mkdir(expected)
        directoryhandler = directoryHandler(temp_dir)
        with pytest.raises(FileNotFoundError):
            directoryhandler.get_sub_directory_path("nonexistent")


def test_get_directory_name_without_trailing_underscore():
    """
    Test the get_directory_name method without a trailing underscore.
    """
    with TemporaryDirectory() as temp_dir:
        test_dir = os.path.join(temp_dir, "test_directory")
        os.mkdir(test_dir)  # Create a real directory
        handler = directoryHandler(test_dir)
        assert handler.get_directory_name() == "test_directory"


def test_get_directory_name_with_trailing_underscore():
    """
    Test the get_directory_name method without a trailing underscore.
    """
    with TemporaryDirectory() as temp_dir:
        test_dir = os.path.join(temp_dir, "test_directory_")
        os.mkdir(test_dir)  # Create a real directory
        handler = directoryHandler(test_dir)
        assert handler.get_directory_name() == "test_directory"


def test_vtu_file_exist():
    """
    Test case where the vtu file exists.
    """
    with TemporaryDirectory() as temp_dir:
        sub_dir = os.path.join(temp_dir, "input_vtu")
        os.makedirs(sub_dir)
        expected = os.path.join(sub_dir, "test_file.vtu")

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


def test_Data_Tmax():
    """
    Integration test to ensure final config looks good
    This re-implements the "Data_Tmax" check in parameters.c
    """
    with TemporaryDirectory() as temp_dir:

        sub_dir = os.path.join(temp_dir, "input_bin")
        os.makedirs(sub_dir)
        directory_handler = directoryHandler(temp_dir)
        processor = resultsProcessor(directory_handler)
        config = Config(processor)
        config.set_backwards_defaults()
        config.update_settings()
        Data_TMin = float(config.config["Outputs"]["Data_TMin"])
        Data_TRes = int(config.config["Outputs"]["Data_TRes"])
        Data_TDelta = float(config.config["Outputs"]["Data_TDelta"])
        Output_TStart = float(config.config["Outputs"]["Output_TStart"])

        Int_TimeDirection = int(config.config["Outputs"]["Int_TimeDirection"])
        Output_TRes = int(config.config["Outputs"]["Output_TRes"])
        Output_TDelta = float(config.config["Outputs"]["Output_TDelta"])
        Data_TMax = Data_TMin + (Data_TRes - 1) * Data_TDelta
        Output_TEnd = (
            Output_TStart + (Output_TRes - 1) * Int_TimeDirection * Output_TDelta
        )
        # Assert T_Start is between Data_Tmin and TMax
        # Note the not is because this condition causes an error in ftle
        # I want to assert an error condition is not met
        logger.info(f"Output_TRes: {Output_TRes}")
        assert not Output_TStart < Data_TMin
        assert not Output_TStart > Data_TMax

        assert Int_TimeDirection == -1
        assert Output_TDelta > 0
        assert not (Output_TEnd > Data_TMax)
        assert not (Output_TEnd < Data_TMin)


def load_config(file_path, var_list):
    config_values = {}
    with open(file_path, "r") as file:
        for line in file:
            # Strip whitespace and ignore empty lines
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            logger.info(f"{key}:{value}")

            if key in var_list:
                config_values[key] = value
    return config_values


def test_integration_full_config(create_sample_vtu_file):
    """
    Integration test to ensure final config looks goood
    This re-implements the "Data_Tmax" check in parameters.c
    """
    vtu_file = create_sample_vtu_file  # created in tmp/input_vtu
    directory = Path(vtu_file).parent.parent
    bin_directory = os.path.join(directory, "input_bin")
    directory_name = os.path.basename(directory)
    os.makedirs(bin_directory)
    inigenerator_main(directory, auto_range=True, cell_size=0.001, direction="backward")
    output_bin = os.path.join(directory, "output_bin")

    ## Start by making sure it created the output_bin directory
    assert os.path.exists(output_bin), f"The path {output_bin} does not exist."

    ##Load the created .in file for data of interest
    var_list = [
        "data_tmin",
        "data_tres",
        "data_tdelta",
        "output_tstart",
        "int_timedirection",
        "output_tres",
        "output_tdelta",
    ]
    in_file_path = os.path.join(bin_directory, f"{directory_name}.in")
    config = load_config(in_file_path, var_list)

    Data_TMin = float(config["data_tmin"])
    Data_TRes = int(config["data_tres"])
    Data_TDelta = float(config["data_tdelta"])
    Output_TStart = float(config["output_tstart"])

    Int_TimeDirection = int(config["int_timedirection"])
    Output_TRes = int(config["output_tres"])
    Output_TDelta = float(config["output_tdelta"])

    Data_TMax = Data_TMin + (Data_TRes - 1) * Data_TDelta
    Output_TEnd = Output_TStart + (Output_TRes - 1) * Int_TimeDirection * Output_TDelta
    # Assert T_Start is between Data_Tmin and TMax
    # Note the not is because this condition causes an error in ftle
    # I want to assert an error condition is not met
    logger.info(f"Output_TRes: {Output_TRes}")
    assert not Output_TStart < Data_TMin
    assert not Output_TStart > Data_TMax

    assert Int_TimeDirection == -1
    assert Output_TDelta > 0
    assert not (Output_TEnd > Data_TMax)
    assert not (Output_TEnd < Data_TMin)

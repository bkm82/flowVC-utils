import vtk
import logging.config
import logging.handlers
from flowvcutils.jsonlogger import settup_logging
import configparser
from .utils import get_project_root
import os
import math

logger = logging.getLogger(__name__)


class directoryHandler:
    def __init__(self, directory):
        self.directory = directory
        self.__validate_directory(directory)
        self.__set_directory_name()

    def __set_directory_name(self):
        """
        Sets directory_name atribute to the directory without trailing underscore.
        """
        self.directory_name = os.path.basename(self.directory)
        if self.directory_name.endswith("_"):
            self.directory_name = self.directory_name[:-1]

    def get_directory_name(self):
        """
        Returns the directory_name atribute
        """
        return self.directory_name

    def get_data_path(self, data_dir_name="input_bin"):
        return self.get_sub_directory_path(data_dir_name)

    def get_output_path(self, dir_name="output_bin", create_if_missing=True):
        return self.get_sub_directory_path(dir_name, create_if_missing)

    def __validate_directory(self, directory, create_if_missing=False):
        if not os.path.isdir(directory):
            if create_if_missing:
                try:
                    os.makedirs(directory)
                except Exception:
                    logger.error(
                        f"Failed to create directory {directory}", exc_info=True
                    )
                    raise

            else:
                logger.error(f"{directory} is not a valid directory.")
                raise FileNotFoundError(f"{directory} is not a valid directory")
        return True

    def get_sub_directory_path(self, sub_dir_name, create_if_missing=False):
        """Returns the full path to the subdirectory of interest"""
        sub_directory = os.path.join(self.directory, sub_dir_name)
        self.__validate_directory(sub_directory, create_if_missing)
        return os.path.join(self.directory, sub_dir_name)

    def find_vtu(self, dir_name="input_vtu", create_if_missing=False):
        """
        Search the current directory and return the first file with a ".vtu" extension.

        Returns:
            str: The filepath of the first .vtu file found.
        """
        subdir = self.get_sub_directory_path(dir_name, create_if_missing)
        for file in os.listdir(subdir):
            logger.info(f"Searching {subdir} for a vtu file")
            file_path = os.path.join(subdir, file)
            if os.path.isfile(file_path) and file.endswith(".vtu"):
                return file_path
        raise FileNotFoundError(f"No .vtu file found in the directory: {subdir}")


class resultsProcessor:
    def __init__(self, directory_handler):
        self.directory_handler = directory_handler
        self.x_points = 0
        self.y_points = 0
        self.z_points = 0
        self.min_x, self.max_x = float("inf"), float("-inf")
        self.min_y, self.max_y = float("inf"), float("-inf")
        self.min_z, self.max_z = float("inf"), float("-inf")

    def streach_bounds(self, pt_min, pt_max, cell_size):
        """Extend data bounds to be evenly divisible.

        Parameters
        ----------
        pt_min : float
            The minimum value of the x, y or z point
        pt_max : float
            The maximum value of the x, y or z point
        cell_size : float
            the size of cell to evenly divide the domain

        Returns
        ------
        (new_max, n_pts)
        new_max: float
            The new maximum value of the x, y, or z point.
        n_points:
            The number of cells that evenly divide the domain

        """
        current_point = pt_min
        if current_point >= pt_max:
            raise ValueError("min must be less than max")
        if cell_size <= 0:
            raise ValueError("Cell Size must be >0")

        domain = pt_max - pt_min
        # ceil the domain / cell_size to find how many cells needed to cover the domain:
        n_cells = math.ceil(domain / cell_size)

        # compute the new max
        new_max = pt_min + n_cells * cell_size

        # Rounding to 8 decimal places to reduce floating-point artifacts
        new_max = round(new_max, 8)

        return (new_max, n_cells)

    def set_data_range_manual(self, min_xyz, max_xyz, streach=False, cell_size=0):
        # Manually set
        min_x, min_y, min_z = min_xyz
        max_x, max_y, max_z = max_xyz
        self.min_x, self.max_x = min_x, max_x
        self.min_y, self.max_y = min_y, max_y
        self.min_z, self.max_z = min_z, max_z

        if streach:
            self.max_x, self.x_points = self.streach_bounds(
                self.min_x, self.max_x, cell_size
            )
            self.max_y, self.y_points = self.streach_bounds(
                self.min_y, self.max_y, cell_size
            )
            self.max_z, self.z_points = self.streach_bounds(
                self.min_z, self.max_z, cell_size
            )

        return (
            (self.min_x, self.max_x),
            (self.min_y, self.max_y),
            (self.min_z, self.max_z),
        )

    def find_data_range(self, file_path=None, streach=False, cell_size=0):
        """
        Find the min and max x, y, and z coordinates in a .vtu file.

        Args:
            file_path (str): Path to the .vtu file.
            streach (bool): extend data to evenly divide by cell size?
            cell_size (float): Size of cell to ensure evenly divides the data range
        Returns:
            tuple: Min and max ranges for x, y, and z coordinates.
        """
        if file_path is None:
            file_path = self.directory_handler.find_vtu()
        # Read the .vtu file
        reader = vtk.vtkXMLUnstructuredGridReader()
        reader.SetFileName(file_path)
        reader.Update()

        # Get points from the unstructured grid
        data = reader.GetOutput()
        logger.debug(f"Data {data}")
        points = data.GetPoints()

        # Initialize min and max values

        # Iterate over all points
        for i in range(points.GetNumberOfPoints()):
            x, y, z = points.GetPoint(i)
            self.min_x = min(self.min_x, x)
            self.max_x = max(self.max_x, x)
            self.min_y = min(self.min_y, y)
            self.max_y = max(self.max_y, y)
            self.min_z = min(self.min_z, z)
            self.max_z = max(self.max_z, z)

        if streach:
            self.max_x, self.x_points = self.streach_bounds(
                self.min_x, self.max_x, cell_size
            )
            self.max_y, self.y_points = self.streach_bounds(
                self.min_y, self.max_y, cell_size
            )
            self.max_z, self.z_points = self.streach_bounds(
                self.min_z, self.max_z, cell_size
            )
        return (
            (self.min_x, self.max_x),
            (self.min_y, self.max_y),
            (self.min_z, self.max_z),
        )


class Config:
    def __init__(self, results_processor):
        self.results_processor = results_processor
        self.data_path = self.results_processor.directory_handler.get_data_path()
        self.output_path = self.results_processor.directory_handler.get_output_path()
        self.directory_name = (
            self.results_processor.directory_handler.get_directory_name()
        )
        self.load_config()
        self.__update_dict = {}

    def set_data_range_defaults(
        self, auto_range, cell_size, manual_bounds=None, streach=False
    ):
        """
        1. If auto_range is True, compute Data_MeshBounds from .vtu.
           Otherwise, leave Data_MeshBounds unchanged.
        2. If manual_bounds is provided, update FTLE_MeshBounds from it.
           Otherwise, if auto_range is True, copy from Data_MeshBounds.
           Otherwise, do not overwrite FTLE_MeshBounds.
        """

        def _update_bounds(prefix, x_range, y_range, z_range):
            """Update __update_dict with mesh bounds for prefix (e.g. 'Data_MeshBounds')."""
            self.__update_dict.update(
                {
                    f"{prefix}.xmin": str(x_range[0]),
                    f"{prefix}.xmax": str(x_range[1]),
                    f"{prefix}.ymin": str(y_range[0]),
                    f"{prefix}.ymax": str(y_range[1]),
                    f"{prefix}.zmin": str(z_range[0]),
                    f"{prefix}.zmax": str(z_range[1]),
                }
            )

        def _update_res(prefix):
            """Update __update_dict with xres, yres, zres for prefix (e.g. 'FTLE_MeshBounds')."""
            self.__update_dict.update(
                {
                    f"{prefix}.xres": str(self.results_processor.x_points),
                    f"{prefix}.yres": str(self.results_processor.y_points),
                    f"{prefix}.zres": str(self.results_processor.z_points),
                }
            )

        # 1) If auto_range => pull Data_MeshBounds from .vtu
        if auto_range:
            x_range, y_range, z_range = self.results_processor.find_data_range(
                streach=streach, cell_size=cell_size
            )
            _update_bounds("Data_MeshBounds", x_range, y_range, z_range)

        # 2) If manual_bounds => use it for FTLE_MeshBounds
        if manual_bounds:
            (ftle_xr, ftle_yr, ftle_zr) = self.results_processor.set_data_range_manual(
                manual_bounds[0],
                manual_bounds[1],
                streach=streach,
                cell_size=cell_size,
            )
            _update_bounds("FTLE_MeshBounds", ftle_xr, ftle_yr, ftle_zr)
            _update_res("FTLE_MeshBounds")

        # Otherwise, if auto_range is on but no manual bounds => copy from Data to FTLE
        elif auto_range:
            _update_bounds("FTLE_MeshBounds", x_range, y_range, z_range)
            _update_res("FTLE_MeshBounds")

    def set_path_defaults(self):
        self.__update_dict.update(
            {
                "Path_Data": self.data_path,
                "Path_Output": self.output_path,
                "Data_InFilePrefix": self.directory_name,
            }
        )

    def set_forward_defaults(self):
        pass

    def set_backwards_defaults(self):
        self.__update_dict.update(
            {
                "FTLE_OutFilePrefix": f"{self.directory_name}_backward",
                "Int_TimeDirection": "-1",
                "Output_TDelta": "0.05",
                "Output_TStart": "5.0",
            }
        )

    def load_config(self, file_name="config.inigenerator.cfg"):
        config_path = os.path.join(get_project_root(), "config", file_name)
        self.config = configparser.ConfigParser()
        self.config.read_file(open(config_path))

    def __get_update_dict(self):
        return self.__update_dict

    def update_settings(self, updates=None):
        """Update the configuration settings with a dictionary

        Parameters
        ----------
        updates : dict
            Dictionary containing key value pairs

        """
        if updates is None:
            updates = self.__get_update_dict()

        for key, value in updates.items():
            if key not in self.config["Outputs"]:
                raise ValueError(
                    f"The key '{key}' does not exist in the default. Check the spelling"
                )
            logger.info(f"Updating {key} with {value}")
            self.config["Outputs"][key] = value

    def write_config_file(self, file_path=None, file_name=None):
        """Write the configuration.in file.

        Parameters
        ----------
        file_path : string
            directory to save the file (default current_dir/input_bin)
        file_name : string
            filename to save (default current_dir_name.in)

        """
        if file_path is None:
            file_path = self.data_path
        if file_name is None:
            file_name = f"{self.directory_name}.in"

        full_path = os.path.join(file_path, file_name)
        logger.debug(f"full_path {full_path}")
        with open(full_path, "w") as configfile:
            for key, value in self.config.items("Outputs"):
                configfile.write(f"{key} = {value} \n")

    def process_directory(self, auto_range, cell_size, direction, manual_bounds=None):
        self.set_path_defaults()
        # if auto_range:
        self.set_data_range_defaults(
            auto_range=auto_range,
            cell_size=cell_size,
            streach=True,
            manual_bounds=manual_bounds,
        )
        if direction == "backward":
            self.set_backwards_defaults()
        elif direction == "forward":
            self.set_forward_defaults()
        self.update_settings()
        self.write_config_file()


class ConfigBatch:
    """Config factory
    create a config object for each subdirectory in the parent directory
    """

    def __init__(self, parent_directory):
        self.parent_directory = parent_directory
        self.configs = []

    def discover_subdirectories(self):

        subdirs = [
            os.path.join(self.parent_directory, d)
            for d in os.listdir(self.parent_directory)
            if os.path.isdir(os.path.join(self.parent_directory, d))
        ]
        return subdirs

    def process_directory(self, *args, **kwargs):
        subdirs = self.discover_subdirectories()
        for subdir in subdirs:
            logger.info(f"Processing  {subdir}")
            directory_handler = directoryHandler(subdir)
            processor = resultsProcessor(directory_handler)
            config = Config(processor)
            config.process_directory(*args, **kwargs)


def main(directory, auto_range, cell_size, direction, batch=False, manual_bounds=None):
    settup_logging()
    logger.info("Starting inigenerator")
    if batch:
        batch_config = ConfigBatch(parent_directory=directory)
        batch_config.process_directory(auto_range, cell_size, direction, manual_bounds)
    else:
        directory_handler = directoryHandler(directory)
        processor = resultsProcessor(directory_handler)
        config = Config(processor)
        config.process_directory(auto_range, cell_size, direction, manual_bounds)

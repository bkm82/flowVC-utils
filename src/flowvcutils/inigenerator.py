import vtk
import logging.config
import logging.handlers
from flowvcutils.jsonlogger import settup_logging
import configparser
from .utils import get_project_root
import os
import json


logger = logging.getLogger(__name__)


class directoryHandler:
    def __init__(self, directory):
        self.directory = directory
        self.validate_directory()
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

    def validate_directory(self):
        """
        Validates that the given directory exists.

        Args:
            directory (str): Directory to validate.

        Returns:
            bool: True if the directory is valid.
        """
        if not os.path.isdir(self.directory):

            logger.error(f"{self.directory} is not a valid directory.")
            raise FileNotFoundError(f"{self.directory} is not a valid directory")

        return True

    def get_data_path(self, data_dir_name="in_bin"):
        return self.get_sub_directory_path(data_dir_name)

    def get_sub_directory_path(self, sub_dir_name):
        """Returns the full path to the subdirectory of interest"""
        self.validate_sub_directory(sub_dir_name)
        return os.path.join(self.directory, sub_dir_name)

    def validate_sub_directory(self, sub_dir_name):
        """
        Validates that the directory has a sub_directory.
        TODO Ensure that the required files are there
        """
        sub_directory = os.path.join(self.directory, sub_dir_name)
        if not os.path.isdir(sub_directory):
            logger.error(f"{sub_directory} is not a valid directory")
            raise FileNotFoundError(f"{sub_directory} is not a valid directory")

    def find_vtu(self):
        """
        Search the current directory and return the first file with a ".vtu" extension.

        Returns:
            str: The filepath of the first .vtu file found.
        """
        for file in os.listdir(self.directory):
            file_path = os.path.join(self.directory, file)
            if os.path.isfile(file_path) and file.endswith(".vtu"):
                return file_path
        raise FileNotFoundError(
            f"No .vtu file found in the directory: {self.directory}"
        )


class resultsProcessor:
    def __init__(self, directory_handler):
        self.directory_handler = directory_handler
        self.min_x, self.max_x = float("inf"), float("-inf")
        self.min_y, self.max_y = float("inf"), float("-inf")
        self.min_z, self.max_z = float("inf"), float("-inf")

    def find_data_range(self, file_path=None):
        """
        Find the min and max x, y, and z coordinates in a .vtu file using vtk.

        Args:
            file_path (str): Path to the .vtu file.

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

        return (
            (self.min_x, self.max_x),
            (self.min_y, self.max_y),
            (self.min_z, self.max_z),
        )


def prompt_settings(settings, prefix=""):
    for key, value in settings.items():
        if isinstance(value, dict):
            prompt_settings(value, f"{prefix}{key}")  # recurse the dictinary
        else:

            user_input = input(f"{prefix}{key} (default = {value})")
            save_prompt = "no"
            if user_input:  # New value provided
                settings[key] = user_input
                save_prompt = (
                    input("Do you want to save this value? (yes/no): ").strip().lower()
                )

            if save_prompt == "yes":
                logger.debug(f"Saving setting:{prefix}{key}, Value: {value}")
            else:  # No input, keep the default
                settings[key] = value


class Config:
    def __init__(self, directory_handler):
        self.directory_handler = directory_handler
        self.data_path = self.directory_handler.get_data_path()
        self.directory_name = self.directory_handler.get_directory_name()
        self.load_config()

    def load_config(self, file_name="config.inigenerator.cfg"):
        config_path = os.path.join(get_project_root(), "config", file_name)
        self.config = configparser.ConfigParser()
        self.config.read_file(open(config_path))

    def write_config_file(self, file_path=None, file_name=None):
        """
        Write the configuration to the .in file.

        args
        config: the configuration object
        file_path: path to save the file
        file_name: filename to save (default: current_dir_name.in
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


def set_preferences():
    # use_case = input("Select use case (FTLE/Trace/VelOut): ")
    with open("ini_default.json", "r") as file:
        defaults = json.load(file)
    prompt_settings(defaults)


def main(directory):
    settup_logging()
    logger.info("Starting inigenerator")

    directory_handler = directoryHandler(directory)

    # processor = resultsProcessor(directory_handler)

    # x_range, y_range, z_range = processor.find_data_range()
    # logger.info(f"X Range: {x_range}")
    # logger.info(f"Y Range: {y_range}")
    # logger.info(f"Z Range: {z_range}")
    # logger.info("Done!")

    config = Config(directory_handler)
    # config.directory_handler.validate_sub_directory("in_bin")
    path = config.directory_handler.get_sub_directory_path("in_bin")
    config.write_config_file(path)


if __name__ == "__main__":
    directory = os.getcwd()
    main(directory)

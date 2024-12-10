import vtk
import logging.config
import logging.handlers
from flowvcutils.jsonlogger import settup_logging
import argparse
import os

logger = logging.getLogger("inigenerator")


class directoryHandler:
    def __init__(self, directory):
        self.directory = directory
        self.validate_directory()

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


def main():
    settup_logging()
    logger.info("Starting inigenerator")

    parser = argparse.ArgumentParser(description="Generate ini file from directory")
    parser.add_argument(
        "-d",
        "--directory",
        default=os.getcwd(),
        help="Directory containing the .vtu files (default: current dir)",
    )
    args = parser.parse_args()
    directory_handler = directoryHandler(args.directory)

    processor = resultsProcessor(directory_handler)
    x_range, y_range, z_range = processor.find_data_range()
    logger.info(f"X Range: {x_range}")
    logger.info(f"Y Range: {y_range}")
    logger.info(f"Z Range: {z_range}")
    logger.info("Done!")


if __name__ == "__main__":
    main()

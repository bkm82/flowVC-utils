import vtk
import logging.config
import logging.handlers
from flowvcutils.jsonlogger import settup_logging
import argparse
import os

logger = logging.getLogger("inigenerator")


class resultsProcessor:
    def __init__(self, directory):
        self.directory = directory
        self.min_x, self.max_x = float("inf"), float("-inf")
        self.min_y, self.max_y = float("inf"), float("-inf")
        self.min_z, self.max_z = float("inf"), float("-inf")

    def find_first_vtu(self):
        """
        Search the current directory and return the first file with a ".vtu" extension.

        Returns:
            str: The filepath of the first .vtu file found.
        """
        pass

    def find_data_range(self, file_path):
        """
        Find the min and max x, y, and z coordinates in a .vtu file using vtk.

        Args:
            file_path (str): Path to the .vtu file.

        Returns:
            tuple: Min and max ranges for x, y, and z coordinates.
        """
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


def validate_directory(directory):
    """
    Validates that the given directory exists.

    Args:
        directory (str): Directory to validate.

    Returns:
        bool: True if the directory is valid, False otherwise.
    """
    if not os.path.isdir(directory):
        logger.error(f"{directory} is not a valid directory.")
        return False
    return True


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
    directory = args.directory
    # validate directory
    if not validate_directory(directory):
        return

        # Process the directory and print results
    x_range, y_range, z_range = find_data_range(directory)
    logger.info(f"Directory: {directory}")
    logger.info(f"X Range: {x_range}")
    logger.info(f"Y Range: {y_range}")
    logger.info(f"Z Range: {z_range}")
    logger.info("Done!")


if __name__ == "__main__":
    main()

import logging.config
import logging.handlers
from flowvcutils.jsonlogger import settup_logging
import os

logger = logging.getLogger(__name__)


def rename_files(directory, prefix=None, current_name="all_results_"):
    """
    Rename all .vtu files in the specified directory.

    Args:
        directory (str): Path to the directory containing .vtu files.
        prefix (str): Optional prefix for renaming. Defaults to directory name.
    """
    # Get the directory name for default prefix
    if prefix is None:
        prefix = os.path.basename(os.path.abspath(directory))

    if prefix.endswith("_"):
        prefix = prefix[:-1]

    # Ensure the directory exists
    if not os.path.isdir(directory):
        logger.error(f"Error: Directory '{directory}' does not exist.")
        return

    # Process each file
    for filename in os.listdir(directory):
        if filename.startswith(current_name) and filename.endswith(".vtu"):
            # Extract the unique identifier from the filename
            identifier = filename.split("_")[-1].replace(".vtu", "")

            # Construct the new filename
            new_name = f"{prefix}_{identifier}.vtu"

            # Rename the file
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, new_name)
            os.rename(old_path, new_path)
            logger.info(f"Renamed: {filename} -> {new_name}")


def renumber_files(
    directory,
    prefix=None,
    current_start=0,
    current_end=39,
    new_start=3000,
    increment=50,
):
    if prefix is None:
        for filename in os.listdir(directory):
            if filename.endswith(".vtk"):
                prefix = filename.rsplit(".", 2)[0]  # remove last 2 dots
                break  # Exit after finding the first .vtk file
    for i in range(current_start, current_end + 1):
        old_filename = f"{prefix}.{i}.vtk"
        new_number = new_start + (i * increment)
        new_filename = f"{prefix}.{new_number}.vtk"

        old_filepath = os.path.join(directory, old_filename)
        new_filepath = os.path.join(directory, new_filename)

        if os.path.exists(old_filepath):
            os.rename(old_filepath, new_filepath)


def main(route, directory, prefix, current_name):
    settup_logging()
    if route == "file_name":
        logger.info("Starting file renaming")
        rename_files(directory=directory, prefix=prefix, current_name=current_name)
        logger.info("Done!")

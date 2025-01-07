import logging.config
import logging.handlers
from flowvcutils.jsonlogger import settup_logging
from shutil import move
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


def create_rename_map(
    current_start, current_end, current_increment, new_start, increment
):
    """
    Create a map of old_number :new_number
    """
    mapping = {}
    current_numbers = range(current_start, current_end + 1, current_increment)
    for current in current_numbers:
        new = new_start + ((current - current_start) // current_increment) * increment
        mapping[current] = new
    return mapping


def renumber_files(
    directory,
    prefix=None,
    current_start=0,
    current_end=39,
    current_increment=1,
    new_start=3000,
    increment=50,
):
    if prefix is None:
        for filename in os.listdir(directory):
            if filename.endswith(".vtk"):
                prefix = filename.rsplit(".", 2)[0]  # remove last 2 dots
                break  # Exit after finding the first .vtk file

    mapping = create_rename_map(
        current_start=current_start,
        current_end=current_end,
        current_increment=current_increment,
        new_start=new_start,
        increment=increment,
    )
    temp_suffix = ".tmp"
    for old in mapping:
        old_file = os.path.join(directory, f"{prefix}.{old}.vtk")
        temp_file = os.path.join(directory, f"{prefix}.{old}{temp_suffix}.vtk")
        if os.path.exists(old_file):
            logger.debug(f"Temporaraly renaming: {old_file} -> {temp_file}")
            move(str(old_file), str(temp_file))

    for old, new in mapping.items():
        temp_file = os.path.join(directory, f"{prefix}.{old}{temp_suffix}.vtk")
        new_file = os.path.join(directory, f"{prefix}.{new}.vtk")
        if os.path.exists(temp_file):
            logger.debug(f"Renaming: {temp_file} -> {new_file}")
            logger.info(f"Renaming: {old} -> {new}")
            move(str(temp_file), str(new_file))


def main(route, **kwags):
    settup_logging()
    if route == "file_name":
        logger.info("Starting file renaming")
        rename_files(**kwags)
        logger.info("Done!")
    if route == "file_number":
        logger.info("Starting File Renumbering")
        renumber_files(**kwags)
        logger.info("Files Renumbered")

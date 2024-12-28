import os
import shutil
import logging
import subprocess
from flowvcutils.jsonlogger import settup_logging

logger = logging.getLogger(__name__)


def create_directories(base_dir, exclude_files=None):
    inlet_velocity_directory = os.path.join(base_dir, "inlet_velocity")
    generic_dir = os.path.join(base_dir, "generic_file")

    # populate an exclude files list
    exclude_file_path = os.path.join(inlet_velocity_directory, "exclude.txt")
    exclude_files = get_exclude_files(exclude_file_path, exclude_files)

    for txt_file in os.listdir(inlet_velocity_directory):
        if txt_file.endswith(".txt") and txt_file not in exclude_files:
            txt_file_path = os.path.join(inlet_velocity_directory, txt_file)
            file_name_base = os.path.splitext(txt_file)[0]

            # Step 1: Copy generic_file and rename it
            new_dir_path = os.path.join(base_dir, file_name_base)
            shutil.copytree(generic_dir, new_dir_path)

            # Step 2: Replace catheter.flow with the contents of the txt file
            catheter_flow_path = os.path.join(new_dir_path, "catheter.flow")
            replace_file(source=txt_file_path, destination=catheter_flow_path)

            # Step 3: Copy and rename generic_file.sjb
            generic_file_sjb = os.path.join(base_dir, "generic_file.sjb")
            new_sjb_file = os.path.join(base_dir, f"{file_name_base}.sjb")
            shutil.copy2(generic_file_sjb, new_sjb_file)

            # Step 4: Run the svpre command
            command = "/usr/local/sv/svsolver/2022-07-22/bin/svpre generic_file.svpre"
            run_command(command=command, path=new_dir_path)


def replace_file(source, destination):
    with open(source, "r") as source_content, open(
        destination, "w"
    ) as destination_file:
        destination_file.write(source_content.read())


def get_exclude_files(exclude_file_path, exclude_files=None):
    """
    Reads the exclude.txt file in the inlet_velocity directory
    and returns a list of files to exclude. Optionally,
    it can append to an existing exclude_files list.

    Args:
        base_dir (str): Base directory containing the inlet_velocity directory.
        exclude_files (list, optional): List of files to exclude. Defaults to None.

    Returns:
        list: Updated list of exclude files.
    """
    if exclude_files is None:
        exclude_files = []
    if os.path.isfile(exclude_file_path):
        with open(exclude_file_path, "r") as ef:
            exclude_files += [line.strip() for line in ef if line.strip()]

    return exclude_files


def run_command(command, path):
    subprocess.run(command, shell=True, cwd=path, env=os.environ)


def main(directory, exclude):
    settup_logging()
    logger.info("Creating Simulation Directories")
    create_directories(base_dir=directory, exclude_files=exclude)
    logger.info("Simulation Directories Created")

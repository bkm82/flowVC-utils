import os
import shutil
import logging
from flowvcutils.jsonlogger import settup_logging

logger = logging.getLogger(__name__)


def process_files(base_dir, exclude_files):
    """
    Coppies the generic directory and updates inlet velocity"
    """

    generic_dir = os.path.join(base_dir, "generic_file")
    inlet_velocity_directory = os.path.join(base_dir, "inlet_velocity")
    generic_file_sjb = os.path.join(base_dir, "generic_file.sjb")

    # if not os.path.isdir(generic_dir):
    #     logger.error(f"{generic_dir} does not exist")
    #     return
    for txt_file in os.listdir(inlet_velocity_directory):
        if txt_file.endswith(".txt") and txt_file not in exclude_files:
            txt_file_path = os.path.join(inlet_velocity_directory, txt_file)
            file_name_base = os.path.splitext(txt_file)[0]

            # Step 1: Copy generic_file and rename it
            new_dir_path = os.path.join(base_dir, file_name_base)
            shutil.copytree(generic_dir, new_dir_path)

            # Step 2: Replace catheter.flow with the contents of the txt file
            catheter_flow_path = os.path.join(new_dir_path, "catheter.flow")
            with open(txt_file_path, "r") as txt_content, open(
                catheter_flow_path, "w"
            ) as catheter_file:
                catheter_file.write(txt_content.read())

            # Step 3: Copy and rename generic_file.sjb
            new_sjb_file = os.path.join(base_dir, f"{file_name_base}.sjb")
            shutil.copy2(generic_file_sjb, new_sjb_file)
    logger.info("directorys coppied")


def main(directory, exclude):
    settup_logging()
    process_files(base_dir=directory, exclude_files=exclude)

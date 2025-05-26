import sys
import logging
import click
import os
from flowvcutils.jsonlogger import settup_logging
from .jsonlogger import main as jsonlogger_main
from .vtu_2_bin import process_folder, process_directory
from .inigenerator import main as inigenerator_main
from .simulationgenerator import main as simulationgenerator_main
from .filerename import main as filerename_main

logger = logging.getLogger(__name__)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli():
    pass


@cli.command()
@click.argument("num_lines", default=10, type=int)
def jsonlogger(num_lines):
    """
    Print a specified number of log lines.

    NUM_LINES: the number of logs to print (default 10).
    """
    jsonlogger_main(num_lines)


@cli.command()
@click.argument("start", type=int)
@click.argument("stop", type=int)
@click.option(
    "--root",
    default=os.getcwd(),
    help=(
        "Directory with the VTU files (default: current directory)."
        "In batch mode ensure vtu files are in root/subdir/input_vtu/"
    ),
)
@click.option(
    "--output",
    default=os.getcwd(),
    help=(
        "Output directory target to store bin files (default: current directory)."
        "In batch mode this will be root/subdir/input_bin/"
    ),
)
@click.option(
    "--file_name",
    default=os.path.basename(os.getcwd()),
    help=(
        "Base file name (e.g., steady_ for steady_00000.vtu) "
        "(default: current directory name)."
        "Note: In batch mode this will be the subdirectory names"
        "ensure files are named root/subdirname/input_vtu/subdirname_xxxxx.vtu"
    ),
)
@click.option(
    "--batch",
    is_flag=True,
    default=False,
    help=(
        "Process subdirectories (directory mode) if set "
        "otherwise process a single folder."
    ),
)
@click.option(
    "--extension",
    default=".vtu",
    help="File extension (default: '.vtu').",
)
@click.option(
    "--increment",
    default=50,
    type=int,
    help="Increment between each vtu file (default: 50).",
)
@click.option(
    "--num_digits",
    default=5,
    type=int,
    help="Digits in file name (e.g., 5 for test_00100.vtu). (default: 5).",
)
@click.option(
    "--field_name",
    default="velocity",
    help="Field name for velocity data within the .vtu files (default: 'velocity').",
)
def vtu2bin(
    start,
    stop,
    batch,
    root,
    output,
    file_name,
    extension,
    increment,
    num_digits,
    field_name,
):
    """
    Convert .vtu files into .bin format for FlowVC.

    START: Starting index for the processing (positional argument).
    STOP : Stopping index for the processing (positional argument).
    """
    # If file_name was None, we can do the same fallback:
    if not file_name:
        file_name = os.path.basename(os.path.normpath(root))

    if batch:
        process_directory(
            root=root,
            extension=extension,
            start=start,
            stop=stop,
            increment=increment,
            num_digits=num_digits,
            field_name=field_name,
        )

    else:
        process_folder(
            root=root,
            output=output,
            file_name=file_name,
            extension=extension,
            start=start,
            stop=stop,
            increment=increment,
            num_digits=num_digits,
            field_name=field_name,
        )


@cli.command()
@click.option(
    "-d",
    "--directory",
    default=os.getcwd(),
    help="Directory to run program (default: current dir)",
)
@click.option(
    "--auto_range",
    default=True,
    help=(
        "Get data and FTLE range(min-max) using a .vtu file?"
        "Ensure there is at least 1 .vtu file in in a input_vtu dir"
    ),
)
@click.option(
    "--cell_size", type=float, default=0.001, help="size of FTLE element, default 0.001"
)
@click.option(
    "--direction",
    type=click.Choice(["forward", "backward"], case_sensitive=False),
    default="backward",
    help="forward or backward ftle",
)
@click.option("--batch", is_flag=True, default=False, help="run for each subdirectory")
@click.option(
    "--manual_bounds",
    nargs=6,
    type=float,
    default=None,
    help="Manually specify [min_x min_y min_z max_x max_y max_z].",
)
def inigenerator(directory, auto_range, cell_size, direction, batch, manual_bounds):
    """
    Generate a .ini file for the flow vc.
    """
    if manual_bounds:
        # parse 6 numbers into two (x,y,z) points
        (min_x, min_y, min_z, max_x, max_y, max_z) = manual_bounds
        manual_bounds_tuple = ((min_x, min_y, min_z), (max_x, max_y, max_z))
    else:
        manual_bounds_tuple = None
    inigenerator_main(
        directory, auto_range, cell_size, direction, batch, manual_bounds_tuple
    )


@cli.command()
@click.option(
    "-d",
    "--directory",
    default=os.getcwd(),
    help="Directory to run program (default: current dir)",
)
@click.option(
    "--svpre_exe",
    type=str,
    default="/usr/local/sv/svsolver/2022-07-22/bin/svpre generic_file.svpre",
    help="Path to the svpre executable.",
)
@click.option(
    "--exclude",
    type=str,
    multiple=True,
    default=[],
    help="Optional list of file names to exclude (space-separated).",
)
def simulationgenerator(directory, exclude, svpre_exe):
    """
    Generate the simulation directorys.
    """
    simulationgenerator_main(directory, list(exclude), svpre_exe)


@cli.command()
@click.option(
    "-d",
    "--directory",
    default=os.getcwd(),
    help="Directory to run program (default: current dir)",
)
@click.option(
    "--prefix",
    default=None,
    help="New file name (default:current directory name).",
)
@click.option(
    "--current_name",
    default="all_results_",
    help="Current file name (default:all_results).",
)
def filerename(directory, prefix, current_name):
    """Rename the files in a directory

    Example\n
    Take the files in a directory\n
    -------\n
    directory \n
    ├── all_results_00000.vtu \n
    ├── all_results_00050.vtu \n
    ├── all_results_00100.vtu \n

    and renames them to \n
    directory \n
    ├── directory_00000.vtu \n
    ├── directory_00050.vtu \n
    ├── directory_00100.vtu \n
    """
    route = "file_name"
    filerename_main(
        route=route, directory=directory, prefix=prefix, current_name=current_name
    )


@cli.command()
@click.option(
    "-d",
    "--directory",
    default=os.getcwd(),
    help="Directory to run program (default: current dir)",
)
@click.option(
    "--prefix",
    default=None,
    help="new file name (default:current directory name).",
)
@click.option(
    "--current_start",
    default=0,
    help="Current file numbering start.",
)
@click.option(
    "--current_end",
    default=39,
    help="Current file numbering end.",
)
@click.option(
    "--current_increment",
    default=1,
    help="Current file increment.",
)
@click.option(
    "--new_start",
    default=3050,
    help="New file numbering start.",
)
@click.option(
    "--increment",
    default=50,
    help="New file numbering increment.",
)
def filerenumber(
    directory,
    prefix,
    current_start,
    current_end,
    current_increment,
    new_start,
    increment,
):
    """Renumber the files in a directory

    takes a directory with files
    file_name.0.vtk
    file_name.1.vtk
    ...
    file_name.39.vtk

    and renames them to

    file_name.3050.vtk
    file_name.3100.vtk
    ...
    file_name.5000.vtk

    """
    route = "file_number"
    filerename_main(
        route=route,
        directory=directory,
        prefix=prefix,
        current_start=current_start,
        current_end=current_end,
        current_increment=current_increment,
        new_start=new_start,
        increment=increment,
    )


def main():
    settup_logging()
    cli()


def init():
    if __name__ == "__main__":
        sys.exit(main())


init()

import sys
import logging
import click
import os
from flowvcutils.jsonlogger import settup_logging
from .jsonlogger import main as jsonlogger_main
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
def inigenerator(directory, auto_range, cell_size, direction, batch):
    """
    Generate a .ini file for the flow vc.
    """
    inigenerator_main(directory, auto_range, cell_size, direction, batch)


@cli.command()
@click.option(
    "-d",
    "--directory",
    default=os.getcwd(),
    help="Directory to run program (default: current dir)",
)
@click.option(
    "--exclude",
    type=str,
    multiple=True,
    default=[],
    help="Optional list of file names to exclude (space-separated).",
)
def simulationgenerator(directory, exclude):
    """
    Generate the simulation directorys.
    """
    simulationgenerator_main(directory, list(exclude))


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
    "--current_name",
    default="all_results_",
    help="current file name (default:current directory name).",
)
@click.option(
    "--route",
    default="file_name",
    help="Update file name [file_name] or numbering scheme [file_number].",
)
def filerename(route, directory, prefix, current_name):
    filerename_main(
        route=route, directory=directory, prefix=prefix, current_name=current_name
    )


def main():
    settup_logging()
    cli()


def init():
    if __name__ == "__main__":
        sys.exit(main())


init()

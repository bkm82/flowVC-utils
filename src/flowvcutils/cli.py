import sys
import logging
import click
import os
from flowvcutils.jsonlogger import settup_logging
from .jsonlogger import main as jsonlogger_main
from .inigenerator import main as inigenerator_main

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
def inigenerator(directory):
    """
    Generate a .ini file for the flow vc.
    """
    inigenerator_main(directory)


def main():
    settup_logging()
    cli()


def init():
    if __name__ == "__main__":
        sys.exit(main())


init()

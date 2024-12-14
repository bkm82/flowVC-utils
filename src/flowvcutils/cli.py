import logging
import click
from flowvcutils.jsonlogger import settup_logging
from .jsonlogger import main as jsonlogger_main

logger = logging.getLogger(__name__)


@click.group()
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


def main():
    settup_logging()
    cli()


if __name__ == "__main__":
    main()

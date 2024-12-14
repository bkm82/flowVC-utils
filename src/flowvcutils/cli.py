import logging
import click
from flowvcutils.jsonlogger import settup_logging
from .jsonlogger import scratch as jsonlogger_scratch

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
@click.argument("args")
def jsonlogger(args):
    jsonlogger_scratch(args)


def main():
    settup_logging()
    cli()


if __name__ == "__main__":
    main()

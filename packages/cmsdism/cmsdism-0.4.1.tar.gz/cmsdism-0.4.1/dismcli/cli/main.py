import logging

import click

from .._version import __version__
from .commands.build import build_command
from .commands.package import package_command
from .commands.start_api import start_api_command


@click.group()
@click.version_option(version=__version__)
@click.option("--debug", is_flag=True, default=False, help="Enable debug logs.")
def cli(debug):
    """CLI for managing DIALS Inference Services."""
    root_logger = logging.getLogger()
    log_level = logging.DEBUG if debug else logging.INFO
    root_logger.setLevel(log_level)


cli.add_command(build_command, name="build")
cli.add_command(start_api_command, name="start-api")
cli.add_command(package_command, name="package")


if __name__ == "__main__":
    cli()

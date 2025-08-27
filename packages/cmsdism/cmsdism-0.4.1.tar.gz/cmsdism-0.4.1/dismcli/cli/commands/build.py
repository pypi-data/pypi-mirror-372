import click

from ...config import Config
from ...lib.builder.builder import ApplicationBuilder
from ...lib.utils import get_credentials


@click.command()
@click.option("-f", "--filename", default=Config.template_name, help="Path to template.")
@click.option(
    "-u",
    "--dials_base_url",
    help="DIALS base URL, in case you are using a local installation.",
)
def build_command(filename, dials_base_url):
    creds = get_credentials(dials_base_url)
    builder = ApplicationBuilder(filename, creds)
    builder()

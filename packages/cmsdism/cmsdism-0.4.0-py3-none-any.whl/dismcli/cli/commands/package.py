import click

from ...lib.package.packager import ApplicationPackager
from ...lib.utils import get_credentials


@click.command()
@click.option(
    "-u",
    "--dials_base_url",
    help="DIALS base URL, in case you are using a local installation.",
)
@click.option(
    "-i",
    "--ignore-duplicates",
    is_flag=True,
    default=False,
    help="Ignore model duplicate warning and continue packaging.",
)
def package_command(dials_base_url, ignore_duplicates):
    creds = get_credentials(dials_base_url)
    packager = ApplicationPackager(creds, ignore_duplicates=ignore_duplicates)
    packager()

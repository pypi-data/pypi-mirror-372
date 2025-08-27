"""
Invokable Module for CLI

python -m dismcli
"""

from dismcli.cli.main import cli


if __name__ == "__main__":
    cli(prog_name="dism")

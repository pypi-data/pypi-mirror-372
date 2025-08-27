"""Command Line Interface for Legacy Import Migrator."""

import click

from .baseline import baseline_command
from .check import check_command
from .scan import scan_command


@click.group()
@click.version_option()
def main():
    """Legacy Import Migration Toolkit (LIM).
    
    AST-based legacy import tracking and migration toolkit for Python codebases.
    """
    pass


main.add_command(scan_command)
main.add_command(check_command)
main.add_command(baseline_command)


if __name__ == "__main__":
    main()
"""
Nginx StatsD Sidecar Command Line Interface.

This module provides the main CLI entry point for the nginx_statsd_sidecar application.
It uses Click to define the command structure and provides options for version
information and subcommands.
"""

import sys

import click

import nginx_statsd


@click.group(invoke_without_command=True)
@click.option(
    "--version/--no-version",
    "-v",
    default=False,
    help="Print the current version and exit.",
)
def cli(version: bool) -> None:
    """
    Nginx StatsD Sidecar command line interface.

    This is the main entry point for the nginx_statsd_sidecar CLI. It provides
    access to various subcommands for monitoring nginx statistics and managing
    the application.

    Args:
        version: If True, print the current version and exit. Defaults to False.

    Returns:
        None

    Examples:
        To see available commands::

        .. code-block:: bash

            nginx_statsd_sidecar --help

        To check the version::

        .. code-block:: bash

            nginx_statsd_sidecar --version

        To run the monitor::

        .. code-block:: bash

            nginx_statsd_sidecar run

    """
    if version:
        print(nginx_statsd.__version__)
        sys.exit(0)

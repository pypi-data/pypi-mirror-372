"""
Nginx StatsD Sidecar CLI Server Commands.

This module provides CLI commands for managing and monitoring the nginx_statsd_sidecar
application. It includes commands for viewing settings, checking current statistics,
and running the main monitoring process.
"""

import asyncio
import pprint

from ..app import NginxMonitor, NginxStatusScraper
from ..settings import Settings
from .cli import cli


@cli.command("settings", short_help="Print our application settings.")
def settings():
    """
    Print application settings to stdout.

    This command displays the complete, evaluated application settings including
    those imported from environment variables. It's useful for debugging
    configuration issues and verifying that environment variables are being
    properly loaded.

    Returns:
        None

    Examples:
        To view all current settings:

        .. code-block:: bash

            nginx_statsd_sidecar settings

        This will output something like:

        .. code-block:: json

            {
              'debug': False,
              'nginx_host': 'localhost',
              'nginx_is_https': True,
              'nginx_port': 443,
              'nginx_status_path': '/server-status',
              'interval': 10,
              'statsd_host': '127.0.0.1',
              'statsd_port': 8125,
              'statsd_prefix': 'nginx',
              'sentry_url': None
            }

    """
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(Settings().dict())


@cli.command("stats", short_help="Print current stats from our nginx server")
def stats():
    """
    Display current nginx server statistics.

    This command fetches the current statistics from the configured nginx
    server and displays them in a human-readable format. It's useful for
    verifying that the nginx server is accessible and that the status
    page is working correctly.

    The command will show:

    - Whether stats were successfully retrieved
    - Current active connections
    - Total requests served
    - Current worker states (reading, writing, waiting)

    Returns:
        None

    Examples:
        To view current nginx statistics:

        .. code-block:: bash

            nginx_statsd_sidecar stats

        This will output something like:

        .. code-block:: python

            NginxStats(
                retrieved=True,
                active_connections=291,
                requests=31070465,
                reading=6,
                writing=179,
                waiting=106,
            )

    Note:
        This command requires that the nginx server is running and accessible
        at the configured status URL. If the server is not accessible,
        the retrieved flag will be False and all other values will be 0.

    """
    scraper = NginxStatusScraper(Settings().status_url)
    print(asyncio.run(scraper.get_stats()))


@cli.command("run", short_help="Run the monitor process")
def run():
    """
    Start the main monitoring process.

    This command runs the nginx monitoring process that continuously
    scrapes nginx statistics and reports them to the configured StatsD
    server. The process runs indefinitely until interrupted.

    The monitoring process:

    1. Connects to the configured nginx server
    2. Scrapes the status page at regular intervals
    3. Parses the statistics and calculates metrics
    4. Reports the metrics to StatsD
    5. Handles errors gracefully and continues monitoring

    Returns:
        None

    Examples:
        To start the monitoring process:
            nginx_statsd_sidecar run

        The process will start logging information about:
        - Initialization with configured settings
        - Successful metric reporting
        - Any errors encountered during monitoring

    Note:
        This command runs indefinitely. Use Ctrl+C to stop the process.
        Ensure that the nginx server and StatsD server are accessible
        before running this command.

    """
    asyncio.run(NginxMonitor(Settings()).run())

"""
Nginx StatsD Sidecar Main Entry Point.

This module serves as the main entry point for the nginx_statsd_sidecar application.
It configures the event loop policy to use uvloop for improved performance and
provides the main function that launches the CLI interface.

The module uses uvloop as the event loop implementation, which provides
significant performance improvements over the standard asyncio event loop,
especially for I/O-bound applications like this nginx monitoring tool.
"""

# Use uvloop as our event loop
# https://uvloop.readthedocs.io/user/index.html
import asyncio

import uvloop

# Configure the event loop policy to use uvloop for improved performance
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def main() -> None:
    """
    Main entry point for the nginx_statsd_sidecar application.

    This function initializes the CLI interface and starts the Click command
    processor. It imports the CLI module dynamically to avoid circular import
    issues and launches the command line interface with an empty context object.

    The function:
    1. Dynamically imports the CLI module to avoid import conflicts
    2. Launches the Click command processor
    3. Handles command execution and user interaction

    Returns:
        None

    Examples:
        This function is typically called when the module is run as a script:
            python -m nginx_statsd.main

        Or when the package is installed and run as a command:
            nginx_statsd_sidecar --help

    Note:
        The CLI module is imported dynamically to prevent circular import
        issues that could arise from importing it at the module level.

    """
    from .cli import cli  # noqa: PLC0415

    cli(obj={})  # pylint: disable=no-value-for-parameter


if __name__ == "__main__":
    main()

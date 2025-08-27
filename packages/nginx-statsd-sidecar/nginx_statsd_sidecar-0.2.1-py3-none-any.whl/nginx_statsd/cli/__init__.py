"""
Nginx StatsD Sidecar CLI Package.

This package provides the command line interface for the nginx_statsd_sidecar
application. It imports and exposes the main CLI commands and functionality.

The package includes:
- cli: Main CLI entry point with Click command group
- server: Server management commands (settings, stats, run)
"""

from .cli import cli  # noqa:F401
from .server import *  # noqa:F403,F401

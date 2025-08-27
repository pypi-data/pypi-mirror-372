"""
Nginx StatsD Sidecar Logging Configuration.

This module configures the logging system for the nginx_statsd_sidecar application.
It sets up JSON-formatted logging to stdout with appropriate log levels and
provides a configured logger instance for use throughout the application.

The logging configuration:
- Uses JSON formatting for structured log output
- Outputs to stdout for container-friendly logging
- Sets the root logger level to INFO
- Provides a dedicated logger for the application
"""

import logging
import sys

from pythonjsonlogger import jsonlogger

# Configure the root logger with JSON formatting and stdout output
root = logging.getLogger()
root.setLevel(logging.INFO)
log_handler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter()
log_handler.setFormatter(formatter)
root.addHandler(log_handler)

#: Application-specific logger instance for nginx_statsd_sidecar
#: This logger is configured with JSON formatting and can be used
#: throughout the application for consistent logging output.
logger = logging.getLogger("nginx_statsd_sidecar")

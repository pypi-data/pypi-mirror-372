"""
Nginx StatsD Sidecar Application Settings.

This module provides configuration management for the nginx_statsd_sidecar
application.  It uses Pydantic Settings to handle environment variable loading
and validation, providing a clean interface for accessing configuration values
throughout the application.

The settings are organized into logical groups:

- nginx: Configuration for connecting to the nginx server
- statsd: Configuration for the StatsD server connection
- sentry: Optional Sentry integration for error reporting

"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings.

    This class manages all configuration for the nginx_statsd_sidecar
    application.  It inherits from Pydantic's BaseSettings to provide automatic
    environment variable loading and validation. All settings can be overridden
    via environment variables, named like ``NGINX_HOST``, ``NGINX_IS_HTTPS``, etc.

    """

    model_config = SettingsConfigDict()

    #: Enable debug mode for additional logging and development features
    debug: bool = False

    # --------
    # nginx
    # --------
    #: the name of the host with nginx
    nginx_host: str = "localhost"
    #: Will we be speaking HTTPS to nginx to get to the status URL?
    nginx_is_https: bool = True
    #: The port on which nginx offers the status url
    nginx_port: int = 443
    #: The path within nginx that serves our status page
    nginx_status_path: str = "/server-status"
    #: how often (in seconds) should we report
    interval: int = 10

    # -------
    # statsd
    # -------
    #: Hostname for the statsd server
    statsd_host: str = "127.0.0.1"
    #: The UDP port for the statsd server
    statsd_port: int = 8125
    #: The prefix to use for our metrics
    statsd_prefix: str = "nginx"

    #: Optional Sentry DSN for error reporting and monitoring
    sentry_url: str | None = ""

    @property
    def status_url(self) -> str:
        """
        Generate the full URL for the nginx status page.

        This property constructs the complete URL that the application will
        use to scrape nginx statistics. It combines the host, port, and
        path information with the appropriate protocol (HTTP or HTTPS).

        The URL format follows the pattern:
        - HTTPS: https://{host}:{port}{path}
        - HTTP: http://{host}:{port}{path}

        Returns:
            A complete URL string for the nginx status page.

        Examples:
            With default settings (HTTPS):
                >>> settings = Settings()
                >>> settings.status_url
                'https://localhost:443/server-status'

            With custom HTTP configuration:
                >>> settings = Settings(nginx_is_https=False, nginx_port=8080)
                >>> settings.status_url
                'http://localhost:8080/server-status'
        """
        url = f"//{self.nginx_host}:{self.nginx_port}{self.nginx_status_path}"
        if self.nginx_is_https:
            return f"https:{url}"
        return f"http:{url}"

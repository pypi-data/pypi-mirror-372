"""
Nginx StatsD Sidecar Application Module.

This module provides the core functionality for monitoring nginx server statistics
and reporting them to a StatsD server. It includes classes for scraping nginx
status pages, parsing the data, and reporting metrics to StatsD.

Classes:
    NginxStats: Data class representing nginx server statistics.
    NginxStatusScraper: Scrapes and parses nginx status page data.
    StatsdReporter: Reports parsed statistics to a StatsD server.
    NginxMonitor: Main monitoring task that runs continuously.
"""

import asyncio
from dataclasses import asdict, dataclass

import aiodogstatsd
import httpx
from aiodogstatsd.compat import get_event_loop

from .logging import logger
from .settings import Settings


@dataclass
class NginxStats:
    """
    Data class representing nginx server statistics.

    This class holds the parsed statistics from an nginx status page,
    including connection counts and request metrics.
    """

    #: This will be ``True`` if we actually retrieved stats
    retrieved: bool = False
    #: How many active connections does nginx currently have
    active_connections: int = 0
    #: The current request counter.  This is a running total of requests
    #: served by nginx since it started.
    requests: int = 0
    #: How many of our connections are currently in reading state
    reading: int = 0
    #: How many of our connections are currently in writing state
    writing: int = 0
    #: How many of our connections are currently in waiting state
    waiting: int = 0


class NginxStatusScraper:
    """
    Scrapes and parses nginx status page data.

    This class is responsible for fetching the nginx status page from the
    configured URL and parsing the HTML response to extract relevant statistics.
    It handles connection errors and HTTP status errors gracefully.

    Args:
        status_url: The URL for the nginx status page that provides
                   server statistics via the `ngx_http_stub_status_module`.

    """

    def __init__(self, status_url: str) -> None:
        """
        Initialize the NginxStatusScraper.

        Args:
            status_url: The URL to scrape for nginx status information.

        """
        #: The URL to scrape for nginx status information.
        self.status_url: str = status_url
        logger.info("scraper.init url=%s", self.status_url)

    async def get_status_page(self) -> str:
        """
        Retrieve the raw status data from the nginx status page.

        This method makes an HTTP request to the configured status URL and
        returns the raw text response. It handles connection and HTTP errors
        gracefully, returning an empty string if the request fails.

        The expected response format looks like:

        .. code-block:: text

            Active connections: 291
            server accepts handled requests
            16630948 16630948 31070465
            Reading: 6 Writing: 179 Waiting: 106

        Returns:
            The text content from the status page, or an empty string
            if the request failed.

        Raises:
            httpx.ConnectError: If there's a connection error to the nginx server.
            httpx.HTTPStatusError: If the nginx server returns an error status code.

        """
        async with httpx.AsyncClient(http2=True, verify=False) as client:  # noqa: S501
            try:
                response = await client.get(self.status_url)
                response.raise_for_status()
            except httpx.ConnectError as e:
                logger.warning(
                    "scraper.get_status_page.connecterror url=%s err=%s",
                    e.request.url,
                    str(e),
                )
                return ""
            except httpx.HTTPStatusError as e:
                logger.warning(
                    "scraper.get_status_page.bad_status url=%s err=%s",
                    e.request.url,
                    e.response.status_code,
                )
                return ""
        return response.text

    async def get_stats(self) -> NginxStats:
        """
        Retrieve and parse nginx status page data.

        This method fetches the status page, parses the HTML response, and
        returns a populated NginxStats object. If the data cannot be retrieved,
        the returned object will have its `retrieved` flag set to False.

        The parsing logic expects a specific format from the nginx status page
        and extracts the following metrics:

        - Active connections count
        - Total requests count
        - Reading, writing, and waiting worker counts

        Returns:
            A NginxStats object containing the parsed statistics.
            The `retrieved` attribute indicates whether parsing was successful.

        """
        data = NginxStats()
        html = await self.get_status_page()
        if not html:
            return data
        data.retrieved = True
        lines = html.split("\n")
        data.active_connections = int(lines[0].split(":")[1].strip())
        data.requests = int(lines[2].strip().split()[2])
        items = lines[3].split()
        data.reading = int(items[1])
        data.writing = int(items[3])
        data.waiting = int(items[5])
        return data


class StatsdReporter:
    """
    Reports nginx statistics to a StatsD server.

    This class is responsible for sending parsed nginx statistics to a StatsD
    server. It tracks the previous request count to calculate request rate
    differences and handles nginx restarts gracefully by resetting counters
    when the request count decreases.

    Args:
        scraper: The NginxStatusScraper instance to get statistics from.
        settings: Application settings containing StatsD configuration.

    """

    def __init__(self, scraper: NginxStatusScraper, settings: Settings) -> None:
        """
        Initialize the StatsdReporter.

        Args:
            scraper: The scraper instance to get statistics from.
            settings: Application settings containing StatsD configuration.

        """
        #: The scraper instance to get statistics from.
        self.scraper = scraper
        #: The application settings containing StatsD configuration.
        self.settings = settings
        #: The request count for the last status object retrieved
        self.last_request_count: int = -1

    async def report(self) -> None:
        """
        Retrieve current statistics and report them to StatsD.

        This method fetches the latest nginx statistics, validates them,
        and sends the metrics to the configured StatsD server. It handles
        edge cases such as nginx restarts by resetting counters when the
        request count decreases.

        The following metrics are reported to StatsD:

        - requests: Incremental request count difference
        - active_connections: Current active connection count
        - workers.reading: Current reading worker count
        - workers.writing: Current writing worker count
        - workers.waiting: Current waiting worker count

        If statistics cannot be retrieved or if nginx has restarted,
        appropriate logging is performed and no metrics are sent.
        """
        stats = await self.scraper.get_stats()
        if not stats.retrieved:
            logger.error("reporter.failed.no-stats-retrieved")
            return
        if self.last_request_count == -1 or stats.requests < self.last_request_count:
            # Either this is our first iteration (last_request_count is -1), or
            # nginx rebooted (current request count is less than our last
            # request count) so just save our current counter and don't report
            # for this iteration
            self.last_request_count = stats.requests
            logger.error(
                "reporter.reset last_request_count=%d", self.last_request_count
            )
            return
        async with aiodogstatsd.Client(
            host=self.settings.statsd_host,
            port=self.settings.statsd_port,
            namespace=self.settings.statsd_prefix,
        ) as statsd:
            # We only want to send the diff between last sample and this sample
            statsd.increment("requests", value=stats.requests - self.last_request_count)
            self.last_request_count = stats.requests
            statsd.increment("active_connections", value=stats.active_connections)
            statsd.increment("workers.reading", value=stats.reading)
            statsd.increment("workers.writing", value=stats.writing)
            statsd.increment("workers.waiting", value=stats.waiting)
        logger.info("reporter.success", extra=asdict(stats))


class NginxMonitor:
    """
    Main monitoring task that runs continuously.

    This class orchestrates the monitoring process by running an infinite loop
    that periodically scrapes nginx statistics and reports them to StatsD.
    It uses asyncio TaskGroup for concurrent execution of reporting and
    sleeping tasks, and dynamically adjusts sleep timing to maintain the
    configured reporting interval.

    Args:
        settings: Application settings containing monitoring configuration.

    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize the NginxMonitor.

        Args:
            settings: Application settings containing monitoring configuration.

        """
        #: The scraper instance for retrieving nginx statistics.
        self.scraper = NginxStatusScraper(settings.status_url)
        #: The application settings for configuration.
        self.settings = settings
        #: The reporter instance for sending metrics to StatsD.
        self.reporter = StatsdReporter(self.scraper, settings)
        #: The reporting interval in seconds.
        self.interval = settings.interval

    async def run(self) -> None:
        """
        Run the main monitoring loop.

        This method runs indefinitely, reporting nginx statistics to StatsD
        at the configured interval. It uses asyncio TaskGroup to run the
        reporting task concurrently with a sleep task, and dynamically
        adjusts the sleep duration to compensate for any processing lag.

        The loop continues until the event loop is stopped. Each iteration:
        1. Records the start time
        2. Creates concurrent tasks for reporting and sleeping
        3. Calculates the actual time taken
        4. Adjusts the next sleep duration to maintain the target interval

        Logging is performed at startup to record the configured interval
        and StatsD prefix.
        """
        loop = get_event_loop()
        logger.info(
            "monitor.start",
            extra={"interval": self.interval, "prefix": self.settings.statsd_prefix},
        )
        sleep_time = self.interval
        while loop.is_running():
            start = loop.time()
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self.reporter.report(), name="reporter")
                tg.create_task(asyncio.sleep(sleep_time), name="sleep")
            # Get our current lag
            time_slept = loop.time() - start
            lag = time_slept - self.interval
            sleep_time = self.interval - lag

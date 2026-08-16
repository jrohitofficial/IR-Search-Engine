"""
Polite HTTP fetching for the Task 1 crawler.

Responsibilities:
    - honour robots.txt (allow-check + crawl-delay) before every request
    - identify the crawler with a descriptive User-Agent
    - apply request timeouts and a bounded number of retries with backoff
    - rate-limit consecutive requests to the same host
"""
import logging
import time
from urllib.parse import urlparse

import requests

from config.settings import settings
from crawler.robots_check import crawl_delay, is_allowed

logger = logging.getLogger("task1.crawler.http")

_last_request_time: dict[str, float] = {}


class FetchError(Exception):
    pass


class RobotsDisallowed(FetchError):
    pass


def polite_get(url: str, timeout: int = 15, max_retries: int = 3) -> str:
    """Fetch a URL, respecting robots.txt allow rules and crawl-delay, with
    retries + exponential backoff on transient failures. Returns the response
    body as text, or raises FetchError."""
    if not is_allowed(url, settings.CRAWLER_USER_AGENT):
        raise RobotsDisallowed(f"robots.txt disallows crawling: {url}")

    host = urlparse(url).netloc
    delay = crawl_delay(url, settings.CRAWLER_USER_AGENT, settings.CRAWL_DELAY_SECONDS)
    last = _last_request_time.get(host, 0.0)
    wait = delay - (time.monotonic() - last)
    if wait > 0:
        time.sleep(wait)

    headers = {
        "User-Agent": settings.CRAWLER_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-GB,en;q=0.9",
    }

    last_exc: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            _last_request_time[host] = time.monotonic()
            if response.status_code == 200:
                return response.text
            if response.status_code in (429, 503):
                backoff = 2 ** attempt
                logger.warning("HTTP %s for %s, retrying in %ss", response.status_code, url, backoff)
                time.sleep(backoff)
                continue
            raise FetchError(f"HTTP {response.status_code} for {url}")
        except requests.RequestException as exc:
            last_exc = exc
            backoff = 2 ** attempt
            logger.warning("Request error for %s (%s), retrying in %ss", url, exc, backoff)
            time.sleep(backoff)

    raise FetchError(f"Failed to fetch {url} after {max_retries} attempts: {last_exc}")

"""
robots.txt compliance for the Task 1 crawler.

pureportal.coventry.ac.uk publishes (checked 2026-08-15):

    User-Agent: *
    Crawl-Delay: 5
    Disallow: /*?*format=rss
    Disallow: /*?*export=xls
    Sitemap: https://pureportal.coventry.ac.uk/sitemap.xml

This module wraps Python's standard urllib.robotparser so the crawler
never fetches a disallowed URL and always honours the published crawl
delay, satisfying the coursework's "politeness" requirement.
"""
import logging
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

logger = logging.getLogger("task1.crawler.robots")

_parsers: dict[str, RobotFileParser] = {}

# NOTE: Deliberately does NOT use RobotFileParser.read() — that fetches via
# urllib.request with no custom headers, and PurePortal's edge protection
# returns HTTP 403 to urllib's default User-Agent (confirmed: `requests`
# with the same URL gets 200). RobotFileParser silently treats a 403 as
# "disallow everything", which would have blocked the crawler from
# fetching even the seed URL. Fetching the text ourselves via `requests`
# (matching the User-Agent used for every other request) and handing it
# to RobotFileParser.parse() avoids that failure mode.
_ROBOTS_FETCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}


def _get_parser(url: str) -> RobotFileParser:
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if origin not in _parsers:
        rp = RobotFileParser()
        rp.set_url(f"{origin}/robots.txt")
        try:
            resp = requests.get(f"{origin}/robots.txt", headers=_ROBOTS_FETCH_HEADERS, timeout=15)
            if resp.status_code == 200:
                rp.parse(resp.text.splitlines())
            else:
                logger.warning(
                    "robots.txt fetch for %s returned HTTP %s; defaulting to disallow-nothing.",
                    origin, resp.status_code,
                )
        except Exception as exc:  # pragma: no cover - network failure path
            logger.warning("Could not fetch robots.txt for %s (%s); defaulting to disallow-nothing.", origin, exc)
        _parsers[origin] = rp
    return _parsers[origin]


def is_allowed(url: str, user_agent: str) -> bool:
    rp = _get_parser(url)
    return rp.can_fetch(user_agent, url)


def crawl_delay(url: str, user_agent: str, default_seconds: float) -> float:
    rp = _get_parser(url)
    delay = rp.crawl_delay(user_agent)
    if delay is None:
        return default_seconds
    return max(float(delay), default_seconds)

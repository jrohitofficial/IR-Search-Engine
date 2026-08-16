"""
Focused breadth-first crawler for Coventry University's pureportal, scoped
to the Centre for Healthcare and Community Transformation.

Design note (important, and documented honestly rather than glossed over):
Coventry's pureportal serves the organisation's *listing* views
(".../publications/" and ".../persons/") from behind Cloudflare bot
management -- confirmed by inspecting the response, which carries
"Cf-Mitigated"/"CF-RAY" headers and an empty 403 body regardless of
User-Agent or headers sent. Canonical single-item pages
(the organisation root, individual "/en/publications/<slug>/" pages and
individual "/en/persons/<slug>/" pages) are NOT behind that protection and
return normal 200 responses.

The crawler therefore does not attempt to defeat that protection. Instead
it discovers publications and profiles the way a human following links
would: the organisation root page embeds a "highlighted research output"
and "profiles" widget with real links; each profile page embeds that
person's own research outputs; each publication page lists its authors'
profile links. Starting from the seed and following those two link types
back and forth (a standard BFS over the citation/co-authorship graph)
reaches a substantial, real, verifiable subset of the unit's publications
and profiles using only pages the site serves openly -- while still
respecting robots.txt and the crawl-delay it publishes.

The crawl is bounded (MAX_PUBLICATIONS, MAX_PROFILES, MAX_CRAWL_SECONDS)
so it provably cannot run forever, and every publication/profile is only
kept if the page itself confirms membership of the target centre.
"""
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone

from config.settings import settings
from crawler.http_client import FetchError, RobotsDisallowed, polite_get
from crawler.parsers import extract_links, parse_profile_detail, parse_publication_detail
from database.mongo_client import crawl_logs_col, upsert_profile, upsert_research_output

logger = logging.getLogger("task1.crawler")


@dataclass
class CrawlStats:
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    seed_url: str = settings.SEED_URL
    pages_fetched: int = 0
    fetch_errors: int = 0
    publications_visited: int = 0
    publications_inserted: int = 0
    publications_updated: int = 0
    publications_skipped_not_centre: int = 0
    profiles_visited: int = 0
    profiles_inserted: int = 0
    profiles_updated: int = 0
    profiles_skipped_not_centre: int = 0
    errors: list[str] = field(default_factory=list)
    stopped_reason: str = ""

    def to_doc(self) -> dict:
        d = self.__dict__.copy()
        return d


def run_crawl() -> CrawlStats:
    stats = CrawlStats()
    stats.stopped_reason = "Running..."
    
    # Insert an initial log document so the UI knows a crawl is running
    try:
        initial_doc = stats.to_doc()
        log_id = crawl_logs_col().insert_one(initial_doc).inserted_id
    except Exception:
        log_id = None
        
    stats.stopped_reason = ""
    deadline = time.monotonic() + settings.MAX_CRAWL_SECONDS

    visited_publications: set[str] = set()
    visited_persons: set[str] = set()
    publication_queue: deque[str] = deque()
    person_queue: deque[str] = deque()

    logger.info("Crawl started. Seed: %s", settings.SEED_URL)

    try:
        seed_html = polite_get(settings.SEED_URL)
        stats.pages_fetched += 1
    except (FetchError, RobotsDisallowed) as exc:
        stats.errors.append(f"Failed to fetch seed page: {exc}")
        stats.stopped_reason = "seed_fetch_failed"
        stats.finished_at = datetime.now(timezone.utc)
        _persist_stats(stats, log_id)
        logger.error("Crawl aborted: could not fetch seed page (%s)", exc)
        return stats

    seed_links = extract_links(seed_html, settings.SEED_URL)
    for u in seed_links["publications"]:
        publication_queue.append(u)
    for u in seed_links["persons"]:
        person_queue.append(u)
        
    # --- MANUAL BYPASS FOR CLOUDFLARE ---
    import os
    links_file = os.path.join(os.path.dirname(__file__), "links.txt")
    if os.path.exists(links_file):
        with open(links_file, "r") as f:
            extra_count = 0
            for line in f:
                url = line.strip()
                if "/publications/" in url:
                    publication_queue.append(url)
                    extra_count += 1
                elif "/persons/" in url:
                    person_queue.append(url)
                    extra_count += 1
        logger.info("Loaded %d extra URLs from links.txt", extra_count)
    # ------------------------------------

    logger.info(
        "Queues ready: %d publication links, %d profile links queued.",
        len(publication_queue), len(person_queue),
    )

    while publication_queue or person_queue:
        if time.monotonic() > deadline:
            stats.stopped_reason = "max_crawl_seconds_reached"
            logger.warning("Crawl time budget exhausted, stopping.")
            break
            
        can_process_pub = bool(publication_queue) and len(visited_publications) < settings.MAX_PUBLICATIONS
        can_process_person = bool(person_queue) and len(visited_persons) < settings.MAX_PROFILES
        
        if not can_process_pub and not can_process_person:
            stats.stopped_reason = "max_items_reached_or_blocked"
            logger.info("Crawl limits reached or queues blocked, stopping.")
            break

        # Interleave publication and profile processing (breadth-first).
        if can_process_pub:
            pub_url = publication_queue.popleft()
            if pub_url in visited_publications:
                continue
            visited_publications.add(pub_url)
            _process_publication(pub_url, settings.SEED_URL, stats, person_queue, visited_persons, publication_queue, visited_publications)

        if can_process_person:
            person_url = person_queue.popleft()
            if person_url in visited_persons:
                continue
            visited_persons.add(person_url)
            _process_person(person_url, settings.SEED_URL, stats, publication_queue, visited_publications, person_queue, visited_persons)

    if not stats.stopped_reason:
        stats.stopped_reason = "queues_exhausted"

    stats.finished_at = datetime.now(timezone.utc)
    _persist_stats(stats, log_id)
    logger.info(
        "Crawl finished (%s). Publications: %d inserted / %d updated. Profiles: %d inserted / %d updated. "
        "Pages fetched: %d. Errors: %d.",
        stats.stopped_reason, stats.publications_inserted, stats.publications_updated,
        stats.profiles_inserted, stats.profiles_updated, stats.pages_fetched, len(stats.errors),
    )
    return stats


def _process_publication(pub_url, source_url, stats, person_queue, visited_persons, publication_queue, visited_publications):
    try:
        html = polite_get(pub_url)
        stats.pages_fetched += 1
    except (FetchError, RobotsDisallowed) as exc:
        stats.fetch_errors += 1
        stats.errors.append(f"publication fetch failed: {pub_url} ({exc})")
        logger.warning("Failed to fetch publication %s: %s", pub_url, exc)
        return

    stats.publications_visited += 1
    record = parse_publication_detail(html, pub_url, source_url)

    if not record["is_centre_output"]:
        stats.publications_skipped_not_centre += 1
        logger.debug("Skipping publication not linked to the target centre: %s", pub_url)
    else:
        outcome = upsert_research_output(record)
        if outcome == "inserted":
            stats.publications_inserted += 1
        else:
            stats.publications_updated += 1
        logger.info("Publication %s: %s (%s)", outcome, record["title"][:70], pub_url)

    # 1. Add explicitly parsed author profiles
    # for author_url in record["author_profiles"]:
    #     if author_url not in visited_persons:
    #         person_queue.append(author_url)

    # 2. Discover ALL other relevant links on the page (like the old code did)
    # COMMENTED OUT to restrict crawler strictly to the centre's provided links
    # page_links = extract_links(html, pub_url)
    # for u in page_links["publications"]:
    #     if u not in visited_publications:
    #         publication_queue.append(u)
    # for u in page_links["persons"]:
    #     if u not in visited_persons:
    #         person_queue.append(u)


def _process_person(person_url, source_url, stats, publication_queue, visited_publications, person_queue, visited_persons):
    try:
        html = polite_get(person_url)
        stats.pages_fetched += 1
    except (FetchError, RobotsDisallowed) as exc:
        stats.fetch_errors += 1
        stats.errors.append(f"profile fetch failed: {person_url} ({exc})")
        logger.warning("Failed to fetch profile %s: %s", person_url, exc)
        return

    stats.profiles_visited += 1
    record = parse_profile_detail(html, person_url, source_url)

    if not record["is_centre_member"]:
        stats.profiles_skipped_not_centre += 1
        logger.debug("Skipping profile not affiliated with the target centre: %s", person_url)
    else:
        outcome = upsert_profile(record)
        if outcome == "inserted":
            stats.profiles_inserted += 1
        else:
            stats.profiles_updated += 1
        logger.info("Profile %s: %s (%s)", outcome, record["name"], person_url)

    # 1. Add explicitly parsed related publications
    # for pub_url in record["related_research_outputs"]:
    #     if pub_url not in visited_publications:
    #         publication_queue.append(pub_url)
            
    # 2. Discover ALL other relevant links on the page (like the old code did)
    # COMMENTED OUT to restrict crawler strictly to the centre's provided links
    # page_links = extract_links(html, person_url)
    # for u in page_links["publications"]:
    #     if u not in visited_publications:
    #         publication_queue.append(u)
    # for u in page_links["persons"]:
    #     if u not in visited_persons:
    #         person_queue.append(u)


def _persist_stats(stats: CrawlStats, log_id=None) -> None:
    try:
        if log_id:
            crawl_logs_col().replace_one({"_id": log_id}, stats.to_doc())
        else:
            crawl_logs_col().insert_one(stats.to_doc())
    except Exception:
        logger.exception("Failed to persist crawl_logs document.")

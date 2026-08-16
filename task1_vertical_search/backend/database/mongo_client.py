"""
MongoDB connection and collection access for the vertical search engine.

Collections used:
    research_outputs  - one document per crawled publication
    profiles           - one document per crawled Coventry pureportal profile
    crawl_logs         - one document per crawl run (statistics, timing, errors)
    search_logs         - one document per search query issued by a user
"""
import logging
from datetime import datetime, timezone

from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection

from config.settings import settings

logger = logging.getLogger("task1.database")

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=15000)
    return _client


def get_db():
    return get_client()[settings.DATABASE_NAME]


def research_outputs_col() -> Collection:
    return get_db()["research_outputs"]


def profiles_col() -> Collection:
    return get_db()["profiles"]


def crawl_logs_col() -> Collection:
    return get_db()["crawl_logs"]


def search_logs_col() -> Collection:
    return get_db()["search_logs"]


def ensure_indexes() -> None:
    """Create indexes required for duplicate prevention and fast lookup.

    document_url / profile_url are unique so that re-crawling the same page
    updates (upserts) the existing record instead of creating a duplicate.
    """
    research_outputs_col().create_index([("document_url", ASCENDING)], unique=True)
    research_outputs_col().create_index([("title", ASCENDING)])
    profiles_col().create_index([("profile_url", ASCENDING)], unique=True)
    crawl_logs_col().create_index([("started_at", ASCENDING)])
    search_logs_col().create_index([("timestamp", ASCENDING)])
    logger.info("MongoDB indexes ensured.")


def upsert_research_output(doc: dict) -> str:
    """Insert a research output, or update it in place if document_url already
    exists (duplicate prevention). Returns 'inserted' or 'updated'."""
    doc["crawl_timestamp"] = datetime.now(timezone.utc)
    result = research_outputs_col().update_one(
        {"document_url": doc["document_url"]},
        {"$set": doc},
        upsert=True,
    )
    if result.upserted_id is not None:
        return "inserted"
    return "updated"


def upsert_profile(doc: dict) -> str:
    doc["crawl_timestamp"] = datetime.now(timezone.utc)
    result = profiles_col().update_one(
        {"profile_url": doc["profile_url"]},
        {"$set": doc},
        upsert=True,
    )
    if result.upserted_id is not None:
        return "inserted"
    return "updated"

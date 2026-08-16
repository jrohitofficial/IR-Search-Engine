"""
MongoDB connection and collection access for the document clustering system.

Collections used:
    clustering_documents   - the labelled training corpus (Economics /
                              Entertainment / Politics)
    clustering_predictions - one document per user classification request
"""
import logging
from datetime import datetime, timezone

from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection

from config.settings import settings

logger = logging.getLogger("task2.database")

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=15000)
    return _client


def get_db():
    return get_client()[settings.DATABASE_NAME]


def documents_col() -> Collection:
    return get_db()["clustering_documents"]


def predictions_col() -> Collection:
    return get_db()["clustering_predictions"]


def ensure_indexes() -> None:
    documents_col().create_index([("document_id", ASCENDING)], unique=True)
    documents_col().create_index([("category", ASCENDING)])
    predictions_col().create_index([("timestamp", ASCENDING)])
    logger.info("MongoDB indexes ensured (Task 2).")


def save_prediction(record: dict) -> str:
    record["timestamp"] = datetime.now(timezone.utc)
    result = predictions_col().insert_one(record)
    return str(result.inserted_id)

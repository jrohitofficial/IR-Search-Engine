"""
Integration tests against the real MongoDB Atlas cluster configured in
.env, using a dedicated 'pytest_scratch' collection namespace so they
never touch the real research_outputs/profiles data crawled from
pureportal. Verifies duplicate prevention (upsert-by-URL semantics).
"""
import pytest

from database.mongo_client import get_db


@pytest.fixture
def scratch_collection():
    col = get_db()["pytest_scratch_research_outputs"]
    col.delete_many({})
    yield col
    col.delete_many({})


def test_upsert_by_url_prevents_duplicates(scratch_collection):
    doc_url = "https://pureportal.coventry.ac.uk/en/publications/duplicate-test/"

    scratch_collection.create_index("document_url", unique=True)
    scratch_collection.update_one(
        {"document_url": doc_url}, {"$set": {"document_url": doc_url, "title": "First crawl"}}, upsert=True
    )
    scratch_collection.update_one(
        {"document_url": doc_url}, {"$set": {"document_url": doc_url, "title": "Second crawl (updated)"}}, upsert=True
    )

    matches = list(scratch_collection.find({"document_url": doc_url}))
    assert len(matches) == 1
    assert matches[0]["title"] == "Second crawl (updated)"


def test_mongodb_connection_is_reachable():
    db = get_db()
    # A trivial round-trip command confirms real Atlas connectivity.
    result = db.command("ping")
    assert result.get("ok") == 1.0

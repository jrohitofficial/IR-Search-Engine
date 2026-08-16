"""
Flask API integration tests, run against the real MongoDB Atlas-backed
app (so they exercise the actual crawled data once scripts have been run,
and simply assert weaker structural properties if the database happens to
be empty on a fresh checkout).
"""
import pytest

from app import create_app
from config.settings import settings


@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    with app.test_client() as c:
        yield c


def test_search_requires_query_param(client):
    resp = client.get("/api/search")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_search_returns_top_k_page_size(client):
    resp = client.get("/api/search?q=health&page=1")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["limit"] == settings.TOP_K == 10
    assert len(body["results"]) <= 10


def test_search_nonsense_query_returns_empty_results_not_error(client):
    resp = client.get("/api/search?q=zzzzznonexistentqueryterm9999")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total_results"] == 0
    assert body["results"] == []


def test_search_result_shape_includes_required_fields(client):
    resp = client.get("/api/search?q=health")
    body = resp.get_json()
    if body["total_results"] == 0:
        pytest.skip("No crawled documents matched 'health' yet; run the crawler first.")
    result = body["results"][0]
    for field in ("title", "authors", "publication_date", "document_url", "cosine_similarity"):
        assert field in result


def test_research_output_invalid_id_returns_400(client):
    resp = client.get("/api/research-output/not-a-valid-objectid")
    assert resp.status_code == 400


def test_research_output_missing_id_returns_404(client):
    resp = client.get("/api/research-output/000000000000000000000000")
    assert resp.status_code == 404


def test_crawler_status_endpoint_shape(client):
    resp = client.get("/api/crawler/status")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "research_output_count" in body
    assert "profile_count" in body
    assert "scheduler" in body
    assert "interval_weeks" in body["scheduler"] or body["scheduler"]["jobs"] == []

"""
Flask API integration tests for Task 2, run against the real MongoDB
Atlas-backed app and the real persisted model artifacts (trained on the
540-document Economics/Entertainment/Politics corpus).
"""
import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    with app.test_client() as c:
        yield c


def test_classify_economics_example_from_brief(client):
    resp = client.post("/api/classify", json={
        "text": "The central bank increased interest rates to control inflation."
    })
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["predicted_category"] == "Economics"
    assert "prediction_id" in body


def test_classify_entertainment_example(client):
    resp = client.post("/api/classify", json={
        "text": "The award-winning actress will star in a new film premiering at theatres this fall."
    })
    assert resp.status_code == 200
    assert resp.get_json()["predicted_category"] == "Entertainment"


def test_classify_empty_input_returns_400(client):
    resp = client.post("/api/classify", json={"text": "   "})
    assert resp.status_code == 400


def test_classify_missing_field_returns_400(client):
    resp = client.post("/api/classify", json={})
    assert resp.status_code == 400


def test_classify_invalid_json_body_returns_400(client):
    resp = client.post("/api/classify", data="not json", content_type="text/plain")
    assert resp.status_code == 400


def test_classify_long_input_is_accepted(client):
    long_text = "The government announced new fiscal policy measures today. " * 100
    resp = client.post("/api/classify", json={"text": long_text})
    assert resp.status_code == 200


def test_classify_over_max_length_returns_400(client):
    resp = client.post("/api/classify", json={"text": "a" * 20001})
    assert resp.status_code == 400


def test_dataset_stats_endpoint(client):
    resp = client.get("/api/dataset/stats")
    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body["categories"]) == 3
    assert body["total_status"] in ("PASS", "FAIL")


def test_model_evaluation_endpoint(client):
    resp = client.get("/api/model/evaluation")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "silhouette_score" in body
    assert "accuracy" in body


def test_predictions_history_endpoint(client):
    client.post("/api/classify", json={"text": "Parliament debated the new immigration bill today."})
    resp = client.get("/api/predictions/history?limit=5")
    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body["predictions"]) >= 1
    assert "predicted_category" in body["predictions"][0]

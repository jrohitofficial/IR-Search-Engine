"""
Unit tests for the K-Means training pipeline, run on a small synthetic
labelled corpus and writing model artifacts to a temporary directory so
the REAL persisted model (trained on the 540-document BBC-derived corpus
and used by the live API) is never overwritten by a test run.
"""
import numpy as np
import pytest

import clustering.kmeans_model as kmeans_module
from config.settings import settings

ECONOMICS_DOCS = [
    "The central bank raised interest rates to fight rising inflation across the economy.",
    "Stock markets rallied after strong quarterly earnings from major banks and investors.",
    "The government unveiled a new budget with tax cuts aimed at boosting economic growth.",
    "Unemployment figures fell this quarter as the labour market continued to recover.",
    "Oil prices surged amid concerns over falling global supply and rising demand.",
    "The finance minister announced measures to reduce the national trade deficit.",
]
ENTERTAINMENT_DOCS = [
    "The blockbuster superhero movie shattered box office records this opening weekend.",
    "The pop star's surprise album release sent fans into a frenzy across social media.",
    "Critics praised the new drama series for its compelling performances and writing.",
    "The award-winning actress will star in a new film premiering at theatres this fall.",
    "The music festival announced a star-studded lineup for its summer concert series.",
    "A popular streaming platform renewed the hit comedy show for another season.",
]
POLITICS_DOCS = [
    "Voters headed to the polls in record numbers for the national election today.",
    "The opposition candidate launched a nationwide campaign promising sweeping reforms.",
    "Parliament remained deadlocked after lawmakers failed to agree on new legislation.",
    "The prime minister faced tough questions from journalists over foreign policy.",
    "A new coalition government was formed after weeks of tense political negotiations.",
    "The president signed an executive order following months of political debate.",
]


def _synthetic_documents():
    docs = []
    for text in ECONOMICS_DOCS:
        docs.append({"content": text, "category": "Economics"})
    for text in ENTERTAINMENT_DOCS:
        docs.append({"content": text, "category": "Entertainment"})
    for text in POLITICS_DOCS:
        docs.append({"content": text, "category": "Politics"})
    return docs


@pytest.fixture
def isolated_model_paths(tmp_path, monkeypatch):
    """Redirect all model-artifact paths to a temp directory for this test."""
    monkeypatch.setattr(settings, "VECTORIZER_PATH", tmp_path / "tfidf_vectorizer.joblib")
    monkeypatch.setattr(settings, "KMEANS_MODEL_PATH", tmp_path / "kmeans_model.joblib")
    monkeypatch.setattr(settings, "CLUSTER_MAPPING_PATH", tmp_path / "cluster_to_category.joblib")
    monkeypatch.setattr(settings, "EVALUATION_REPORT_PATH", tmp_path / "evaluation_report.json")
    # Force load_artifacts() to re-read from the new (temp) paths.
    kmeans_module._vectorizer = None
    kmeans_module._kmeans = None
    kmeans_module._cluster_to_category = None
    yield
    kmeans_module._vectorizer = None
    kmeans_module._kmeans = None
    kmeans_module._cluster_to_category = None


def test_train_produces_three_clusters_and_full_mapping(isolated_model_paths):
    result = kmeans_module.train(_synthetic_documents())
    assert result["kmeans"].n_clusters == 3
    assert set(result["cluster_to_category"].values()) == {"Economics", "Entertainment", "Politics"}


def test_train_evaluation_reports_required_metrics(isolated_model_paths):
    result = kmeans_module.train(_synthetic_documents())
    ev = result["evaluation"]
    for key in ("inertia", "silhouette_score", "cluster_distribution", "confusion_matrix",
                "accuracy", "precision_macro", "recall_macro", "f1_macro"):
        assert key in ev
    assert 0.0 <= ev["accuracy"] <= 1.0


def test_classify_uses_persisted_model_without_retraining(isolated_model_paths):
    kmeans_module.train(_synthetic_documents())
    result = kmeans_module.classify("The chancellor announced a rise in the interest rate to tackle inflation.")
    assert result["predicted_category"] in {"Economics", "Entertainment", "Politics"}
    assert "distance_to_centroid" in result
    assert set(result["distances_all_clusters"].keys()) == {"Economics", "Entertainment", "Politics"}


def test_empty_and_whitespace_text_still_produce_a_prediction(isolated_model_paths):
    # classify() itself doesn't reject empty text (that validation lives in
    # the API layer, tested in test_api.py); it should not crash on an
    # all-stopword / empty-after-preprocessing input.
    kmeans_module.train(_synthetic_documents())
    result = kmeans_module.classify("the a an of")
    assert result["predicted_category"] in {"Economics", "Entertainment", "Politics"}

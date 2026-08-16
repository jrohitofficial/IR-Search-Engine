"""
K-Means clustering of the Economics / Entertainment / Politics corpus.

How K-Means works here (K = 3, as required by the coursework brief):
    1. Initial centroids: scikit-learn's KMeans uses "k-means++" seeding,
       which picks initial centroids spread out across the data (rather
       than purely at random) to reduce the chance of poor local minima.
       n_init=10 additionally reruns the whole algorithm 10 times from
       different seedings and keeps the run with lowest inertia.
    2. Distance calculation: for every document vector, its Euclidean
       distance to each of the 3 current centroids is computed.
    3. Assignment: each document is assigned to the cluster whose
       centroid is nearest (this is the "expectation" step).
    4. Centroid update: each centroid is recomputed as the mean of the
       document vectors currently assigned to it (the "maximisation"
       step).
    5. Iteration: steps 2-4 repeat.
    6. Convergence: iteration stops once assignments stop changing
       (or centroid movement falls below scikit-learn's tolerance, or
       max_iter is reached).

Cluster label mapping: K-Means only ever outputs integer cluster ids
(0, 1, 2) with no inherent meaning. Because the *training* corpus here
happens to carry known ground-truth category labels (used only for
evaluation, never fed into K-Means itself), each cluster id is mapped to
the category that occurs most frequently among the documents K-Means put
into that cluster ("majority vote"). This mapping is computed once at
training time and reused unchanged for every later prediction.
"""
import json
import logging

import joblib
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    silhouette_score,
)

from config.settings import settings
from preprocessing.text_preprocessing import preprocess

logger = logging.getLogger("task2.clustering")

RANDOM_STATE = 42


def train(documents: list[dict]) -> dict:
    """Fit TF-IDF + K-Means on the supplied labelled documents
    ({"content": ..., "category": ...}), derive the cluster-to-category
    mapping, evaluate against the known labels, persist all artifacts to
    disk, and return an evaluation report dict."""
    contents = [preprocess(d["content"]) for d in documents]
    true_categories = [d["category"] for d in documents]

    vectorizer = TfidfVectorizer(min_df=2, max_df=0.9)
    X = vectorizer.fit_transform(contents)
    logger.info("TF-IDF matrix for clustering: %s documents x %s terms.", X.shape[0], X.shape[1])

    kmeans = KMeans(n_clusters=settings.N_CLUSTERS, init="k-means++", n_init=10, random_state=RANDOM_STATE)
    cluster_labels = kmeans.fit_predict(X)

    cluster_to_category = _build_cluster_mapping(cluster_labels, true_categories)
    predicted_categories = [cluster_to_category[c] for c in cluster_labels]

    report = _evaluate(X, cluster_labels, true_categories, predicted_categories, kmeans)

    joblib.dump(vectorizer, settings.VECTORIZER_PATH)
    joblib.dump(kmeans, settings.KMEANS_MODEL_PATH)
    joblib.dump(cluster_to_category, settings.CLUSTER_MAPPING_PATH)
    with open(settings.EVALUATION_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info("Model trained and persisted. Cluster mapping: %s", cluster_to_category)
    logger.info("Evaluation: %s", {k: v for k, v in report.items() if k != "confusion_matrix"})

    return {
        "vectorizer": vectorizer,
        "kmeans": kmeans,
        "cluster_to_category": cluster_to_category,
        "cluster_labels": cluster_labels,
        "evaluation": report,
        "X": X,
    }


def _build_cluster_mapping(cluster_labels: np.ndarray, true_categories: list[str]) -> dict:
    mapping = {}
    for cluster_id in sorted(set(cluster_labels.tolist())):
        indices = [i for i, c in enumerate(cluster_labels) if c == cluster_id]
        votes = [true_categories[i] for i in indices]
        majority = max(set(votes), key=votes.count)
        mapping[int(cluster_id)] = majority
    return mapping


def _evaluate(X, cluster_labels, true_categories, predicted_categories, kmeans) -> dict:
    labels_order = settings.CATEGORIES
    cm = confusion_matrix(true_categories, predicted_categories, labels=labels_order)

    distribution = {}
    for cid in sorted(set(cluster_labels.tolist())):
        distribution[int(cid)] = int((cluster_labels == cid).sum())

    return {
        "n_documents": int(X.shape[0]),
        "n_terms": int(X.shape[1]),
        "k": settings.N_CLUSTERS,
        "inertia": float(kmeans.inertia_),
        "silhouette_score": float(silhouette_score(X, cluster_labels)),
        "cluster_distribution": distribution,
        "confusion_matrix": {"labels": labels_order, "matrix": cm.tolist()},
        "accuracy": float(accuracy_score(true_categories, predicted_categories)),
        "precision_macro": float(precision_score(true_categories, predicted_categories, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(true_categories, predicted_categories, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(true_categories, predicted_categories, average="macro", zero_division=0)),
    }


_vectorizer = None
_kmeans = None
_cluster_to_category = None


def load_artifacts():
    global _vectorizer, _kmeans, _cluster_to_category
    if _vectorizer is None:
        _vectorizer = joblib.load(settings.VECTORIZER_PATH)
        _kmeans = joblib.load(settings.KMEANS_MODEL_PATH)
        _cluster_to_category = joblib.load(settings.CLUSTER_MAPPING_PATH)
        logger.info("Loaded persisted TF-IDF vectorizer, K-Means model and cluster mapping from disk.")
    return _vectorizer, _kmeans, _cluster_to_category


def classify(text: str) -> dict:
    """Classify a brand-new document using the ALREADY-TRAINED vectorizer
    and K-Means model (the model is never retrained on a user submission).

    Pipeline: user input -> preprocessing -> existing TF-IDF vectoriser ->
    vector -> distance to K-Means centroids -> nearest cluster -> cluster
    mapping -> category name.
    """
    vectorizer, kmeans, cluster_to_category = load_artifacts()

    cleaned = preprocess(text)
    vector = vectorizer.transform([cleaned])
    distances = kmeans.transform(vector)[0]  # distance to each of the 3 centroids
    cluster_id = int(np.argmin(distances))
    category = cluster_to_category[cluster_id]

    return {
        "cluster_id": cluster_id,
        "predicted_category": category,
        "distance_to_centroid": float(distances[cluster_id]),
        "distances_all_clusters": {
            cluster_to_category[i]: float(d) for i, d in enumerate(distances)
        },
    }

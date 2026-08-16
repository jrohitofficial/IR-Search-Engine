import json
import logging

from bson import ObjectId
from flask import Blueprint, jsonify, request

from clustering.kmeans_model import classify
from config.settings import settings
from database.mongo_client import documents_col, predictions_col, save_prediction

logger = logging.getLogger("task2.api")
api_bp = Blueprint("api", __name__)

MAX_INPUT_CHARS = 20000


@api_bp.post("/classify")
def classify_document():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Field 'text' is required and cannot be empty."}), 400
    if len(text) > MAX_INPUT_CHARS:
        return jsonify({"error": f"Input too long (max {MAX_INPUT_CHARS} characters)."}), 400

    try:
        result = classify(text)
    except FileNotFoundError:
        return jsonify({"error": "Model has not been trained yet. Run scripts/train_model.py first."}), 503

    prediction_id = save_prediction({
        "input_text": text,
        "predicted_category": result["predicted_category"],
        "cluster_id": result["cluster_id"],
        "distance_to_centroid": result["distance_to_centroid"],
        "distances_all_clusters": result["distances_all_clusters"],
    })

    return jsonify({"prediction_id": prediction_id, **result})


@api_bp.get("/dataset/stats")
def dataset_stats():
    stats = []
    for category in settings.CATEGORIES:
        count = documents_col().count_documents({"category": category})
        stats.append({
            "category": category,
            "required": settings.MIN_DOCS_PER_CATEGORY,
            "actual": count,
            "status": "PASS" if count >= settings.MIN_DOCS_PER_CATEGORY else "FAIL",
        })
    total = sum(s["actual"] for s in stats)
    return jsonify({
        "categories": stats,
        "total": total,
        "total_required": settings.MIN_DOCS_PER_CATEGORY * len(settings.CATEGORIES),
        "total_status": "PASS" if total >= settings.MIN_DOCS_PER_CATEGORY * len(settings.CATEGORIES) else "FAIL",
    })


@api_bp.get("/model/evaluation")
def model_evaluation():
    if not settings.EVALUATION_REPORT_PATH.exists():
        return jsonify({"error": "Model has not been trained yet."}), 503
    with open(settings.EVALUATION_REPORT_PATH, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))


@api_bp.get("/predictions/history")
def predictions_history():
    try:
        limit = min(50, max(1, int(request.args.get("limit", 20))))
    except ValueError:
        limit = 20
    docs = list(predictions_col().find({}).sort("timestamp", -1).limit(limit))
    for d in docs:
        d["_id"] = str(d["_id"])
        ts = d["timestamp"]
        if ts.tzinfo is None:
            from datetime import timezone
            ts = ts.replace(tzinfo=timezone.utc)
        d["timestamp"] = ts.isoformat()
    return jsonify({"predictions": docs})

import re

@api_bp.get("/suggest")
def suggest():
    query = request.args.get("q", "").strip()
    if not query or len(query) < 2:
        return jsonify([])

    regex = re.compile(f"{re.escape(query)}", re.IGNORECASE)
    suggestions = []
    
    for d in documents_col().find({"content": regex}).limit(8):
        if "content" in d:
            text = d["content"]
            snippet = text[:90] + ("..." if len(text) > 90 else "")
            snippet = snippet.replace('\n', ' ').strip()
            suggestions.append(snippet)
            
    return jsonify(list(dict.fromkeys(suggestions)))

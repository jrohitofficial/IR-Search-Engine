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
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

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

@api_bp.get("/model/pca")
def model_pca():
    pca_path = settings.MODELS_DIR / "pca_data.json"
    if not pca_path.exists():
        return jsonify({"error": "PCA data not found. Run train_model.py."}), 404
    with open(pca_path, "r", encoding="utf-8") as f:
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


@api_bp.delete("/predictions/history")
def clear_predictions_history():
    predictions_col().delete_many({})
    return jsonify({"message": "History cleared successfully."})

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

@api_bp.post("/retrain")
def retrain_model():
    import subprocess
    import sys
    import threading
    from config.settings import settings
    
    def run_scripts():
        try:
            logger.info("Starting dataset collection...")
            subprocess.run([sys.executable, str(settings.BACKEND_DIR.parent / "scripts" / "build_dataset.py")], check=True)
            logger.info("Starting model retraining...")
            subprocess.run([sys.executable, str(settings.BACKEND_DIR.parent / "scripts" / "train_model.py")], check=True)
            logger.info("Retraining complete.")
        except Exception as e:
            logger.error(f"Retrain pipeline failed: {e}")

    thread = threading.Thread(target=run_scripts)
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "Retraining pipeline started in the background."})

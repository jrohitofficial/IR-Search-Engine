import logging
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, jsonify, request

from config.settings import settings
from crawler.pure_crawler import run_crawl
from database.mongo_client import (
    crawl_logs_col,
    profiles_col,
    research_outputs_col,
    search_logs_col,
)
from ranking.vector_space_model import search_engine
from scheduler.crawl_scheduler import get_scheduler_status

logger = logging.getLogger("task1.api")
api_bp = Blueprint("api", __name__)


@api_bp.get("/search")
def search():
    query = request.args.get("q", "").strip()
    try:
        page = max(1, int(request.args.get("page", 1)))
    except ValueError:
        page = 1
    limit = settings.TOP_K  # coursework requires K = 10 results per page

    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    result = search_engine.search(query, page=page, limit=limit)

    search_logs_col().insert_one({
        "query": query,
        "page": page,
        "total_results": result["total_results"],
        "timestamp": datetime.now(timezone.utc),
    })

    return jsonify(result)


@api_bp.get("/research-output/<doc_id>")
def get_research_output(doc_id):
    try:
        doc = research_outputs_col().find_one({"_id": ObjectId(doc_id)})
    except InvalidId:
        return jsonify({"error": "Invalid id."}), 400
    if not doc:
        return jsonify({"error": "Not found."}), 404
    doc["_id"] = str(doc["_id"])
    return jsonify(doc)


@api_bp.get("/profile/<profile_id>")
def get_profile(profile_id):
    try:
        doc = profiles_col().find_one({"_id": ObjectId(profile_id)})
    except InvalidId:
        return jsonify({"error": "Invalid id."}), 400
    if not doc:
        return jsonify({"error": "Not found."}), 404
    doc["_id"] = str(doc["_id"])
    return jsonify(doc)


@api_bp.get("/crawler/status")
def crawler_status():
    last_log = crawl_logs_col().find_one(sort=[("started_at", -1)])
    if last_log:
        last_log["_id"] = str(last_log["_id"])
    return jsonify({
        "last_crawl": last_log,
        "research_output_count": research_outputs_col().count_documents({}),
        "profile_count": profiles_col().count_documents({}),
        "scheduler": get_scheduler_status(),
        "index_ready": search_engine.is_ready,
    })


@api_bp.post("/crawler/run")
def crawler_run():
    stats = run_crawl()
    indexed = search_engine.build_index()
    return jsonify({
        "stopped_reason": stats.stopped_reason,
        "pages_fetched": stats.pages_fetched,
        "publications_inserted": stats.publications_inserted,
        "publications_updated": stats.publications_updated,
        "profiles_inserted": stats.profiles_inserted,
        "profiles_updated": stats.profiles_updated,
        "errors": stats.errors,
        "indexed_documents": indexed,
    })

import re

@api_bp.get("/suggest")
def suggest():
    query = request.args.get("q", "").strip()
    if not query or len(query) < 2:
        return jsonify([])

    regex = re.compile(f"^{re.escape(query)}", re.IGNORECASE)
    suggestions = []
    
    for p in profiles_col().find({"name": regex}).limit(5):
        if "name" in p:
            suggestions.append(p["name"])
            
    for p in research_outputs_col().find({"title": regex}).limit(5):
        if "title" in p:
            suggestions.append(p["title"])
            
    # Remove duplicates and return
    return jsonify(list(dict.fromkeys(suggestions)))


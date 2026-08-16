import logging

from flask import Flask
from flask_cors import CORS

from config.settings import settings
from database.mongo_client import ensure_indexes
from ranking.vector_space_model import search_engine
from utils.logging_setup import configure_logging

logger = logging.getLogger("task1.app")


def create_app() -> Flask:
    configure_logging()

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    CORS(app)

    ensure_indexes()
    indexed = search_engine.build_index()
    logger.info("Flask app created. Search index initialised with %d documents.", indexed)

    from routes.api import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    return app

import logging

from flask import Flask
from flask_cors import CORS

from database.mongo_client import ensure_indexes
from utils.logging_setup import configure_logging

logger = logging.getLogger("task2.app")


def create_app() -> Flask:
    configure_logging()

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    CORS(app)

    ensure_indexes()

    from routes.api import api_bp
    from flask import send_file
    from config.settings import settings

    @app.route("/figure")
    def serve_figure():
        return send_file(settings.FIGURES_DIR / "figure_task2_kmeans_clusters.png", mimetype='image/png')

    app.register_blueprint(api_bp, url_prefix="/api")

    logger.info("Task 2 Flask app created.")
    return app

"""
Entry point for the Task 1 vertical search engine backend.

Usage:
    python run.py            # start the Flask web app + background scheduler
    python run.py --crawl    # run a single crawl synchronously then exit
"""
import sys

from app import create_app
from config.settings import settings
from scheduler.crawl_scheduler import start_scheduler


def main():
    if "--crawl" in sys.argv:
        from crawler.pure_crawler import run_crawl
        from ranking.vector_space_model import search_engine
        from database.mongo_client import ensure_indexes
        from utils.logging_setup import configure_logging

        configure_logging()
        ensure_indexes()
        stats = run_crawl()
        indexed = search_engine.build_index()
        print(f"Crawl finished: {stats.stopped_reason}. Indexed {indexed} documents.")
        return

    app = create_app()
    start_scheduler()
    app.run(host="0.0.0.0", port=settings.TASK1_PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()

"""
Central configuration for the Task 1 vertical search engine backend.

All values are read from environment variables (see .env.example at the
project root). Nothing sensitive is hard-coded here.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load the .env file that sits at the IR_COURSEWORK project root, two levels
# above this file (backend/config/settings.py -> backend -> task1_vertical_search -> IR_COURSEWORK).
PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    # --- MongoDB ---
    MONGODB_URI: str = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.environ.get("TASK1_DATABASE_NAME", "Task_1_Vertical_Search")

    # --- Crawl target ---
    # The exact seed URL mandated by the ST7071CEM coursework brief. Do not
    # change this to a different organisation.
    SEED_URL: str = os.environ.get(
        "SEED_URL",
        "https://pureportal.coventry.ac.uk/en/organisations/"
        "centre-for-healthcare-and-community-transformation/",
    )
    CRAWLER_USER_AGENT: str = os.environ.get(
        "CRAWLER_USER_AGENT",
        "IRCourseworkBot/1.0 (Coventry ST7071CEM coursework crawler)",
    )
    # robots.txt for pureportal.coventry.ac.uk publishes "Crawl-delay: 5".
    # This value is read at runtime rather than hard-coded so it can be
    # raised if the site's policy changes.
    CRAWL_DELAY_SECONDS: float = float(os.environ.get("CRAWL_DELAY_SECONDS", "5"))

    # Breadth-first crawl bounds so the crawler provably cannot run forever
    # (coursework requirement: "must not endlessly crawl the Coventry website").
    MAX_PROFILES: int = int(os.environ.get("MAX_PROFILES", "200"))
    MAX_PUBLICATIONS: int = int(os.environ.get("MAX_PUBLICATIONS", "200"))
    MAX_CRAWL_SECONDS: int = int(os.environ.get("MAX_CRAWL_SECONDS", "1800"))

    # --- Scheduler ---
    # The interval is kept as an explicit, documented, *configurable* value.
    # The coursework now requires a 3-month default schedule.
    CRAWL_INTERVAL_MONTHS: int = int(os.environ.get("CRAWL_INTERVAL_MONTHS", "3"))
    RUN_CRAWL_ON_STARTUP: bool = os.environ.get("RUN_CRAWL_ON_STARTUP", "false").lower() == "true"

    # --- API / ranking ---
    TOP_K: int = int(os.environ.get("TOP_K", "10"))
    TASK1_PORT: int = int(os.environ.get("TASK1_PORT", "5001"))

    LOG_DIR: Path = Path(__file__).resolve().parents[1] / "logs"


settings = Settings()
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)

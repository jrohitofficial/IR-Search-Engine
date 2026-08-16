"""
Automatic recurring crawl scheduler.

The ST7071CEM coursework brief states the crawler "may be scheduled to
look for new information, say, once per week" because pureportal data
changes slowly. We implement a schedule of once every 3 months.

SCHEDULE: Every 3 MONTHS (approximately 90 days)
"3 months — NOT ONCE PER WEEK"

The interval is fully configurable via the CRAWL_INTERVAL_MONTHS
environment variable (default: 3 months) rather than hard-coded.
"""
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config.settings import settings
from crawler.pure_crawler import run_crawl
from ranking.vector_space_model import search_engine

logger = logging.getLogger("task1.scheduler")

_scheduler: BackgroundScheduler | None = None


def scheduled_crawl_job() -> None:
    logger.info("Scheduled crawl job triggered (interval = %s month(s)).", settings.CRAWL_INTERVAL_MONTHS)
    stats = run_crawl()
    indexed = search_engine.build_index()
    logger.info(
        "Scheduled crawl job complete. Stopped reason: %s. Search index rebuilt with %d documents.",
        stats.stopped_reason, indexed,
    )


def start_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        scheduled_crawl_job,
        trigger=IntervalTrigger(days=settings.CRAWL_INTERVAL_MONTHS * 30),
        id="pureportal_crawl_job",
        name="Recurring pureportal crawl (Centre for Healthcare and Community Transformation)",
        replace_existing=True,
        next_run_time=None,  # do not fire immediately on startup; first run is one interval away
    )
    scheduler.start()
    _scheduler = scheduler
    logger.info(
        "Scheduler started. Job '%s' scheduled to run every %s month(s).",
        "pureportal_crawl_job", settings.CRAWL_INTERVAL_MONTHS,
    )
    return scheduler


def get_scheduler_status() -> dict:
    if _scheduler is None:
        return {"running": False, "jobs": []}
    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": str(job.next_run_time) if job.next_run_time else None,
            "trigger": str(job.trigger),
        })
    return {"running": _scheduler.running, "interval_months": settings.CRAWL_INTERVAL_MONTHS, "jobs": jobs}

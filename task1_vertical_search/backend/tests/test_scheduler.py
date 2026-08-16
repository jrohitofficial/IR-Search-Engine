from datetime import timedelta

import scheduler.crawl_scheduler as scheduler_module
from config.settings import settings


def test_scheduler_job_interval_matches_configured_months():
    scheduler = scheduler_module.start_scheduler()
    try:
        job = scheduler.get_job("pureportal_crawl_job")
        assert job is not None
        assert job.trigger.interval == timedelta(days=settings.CRAWL_INTERVAL_MONTHS * 30)
    finally:
        scheduler.shutdown(wait=False)
        scheduler_module._scheduler = None


def test_scheduler_status_reports_running_state():
    scheduler_module.start_scheduler()
    try:
        status = scheduler_module.get_scheduler_status()
        assert status["running"] is True
        assert status["interval_months"] == settings.CRAWL_INTERVAL_MONTHS
        assert any(j["id"] == "pureportal_crawl_job" for j in status["jobs"])
    finally:
        scheduler_module._scheduler.shutdown(wait=False)
        scheduler_module._scheduler = None

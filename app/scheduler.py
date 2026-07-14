import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.services.sync_service import sync_all

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def run_sync_job():
    logger.info("Starting scheduled sync")
    await sync_all()


def start_scheduler():
    trigger = CronTrigger.from_crontab(settings.sync_cron)
    scheduler.add_job(run_sync_job, trigger=trigger, id="daily_sync")
    scheduler.start()
    logger.info("Scheduler started with cron: %s", settings.sync_cron)


def stop_scheduler():
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")

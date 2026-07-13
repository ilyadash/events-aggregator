from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.services.sync_service import sync_all

scheduler = AsyncIOScheduler()


async def run_sync_job():
    await sync_all()


def start_scheduler():
    trigger = CronTrigger.from_crontab(settings.sync_cron)
    scheduler.add_job(run_sync_job, trigger=trigger, id="daily_sync")
    scheduler.start()


def stop_scheduler():
    scheduler.shutdown(wait=False)

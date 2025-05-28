# apps/api/scheduler.py
import asyncio
from loguru import logger
from apps.crawler.crawler import crawl

_crawl_lock = False

async def safe_crawl():
    global _crawl_lock
    if _crawl_lock:
        logger.warning("Scheduled crawl skipped: already running")
        return

    try:
        _crawl_lock = True
        logger.info("Scheduled crawl started")
        await crawl()
        logger.info("Scheduled crawl finished")
    except Exception as e:
        logger.exception("Scheduled crawl failed")
    finally:
        _crawl_lock = False

# Adapter function for APScheduler
def schedule_daily_crawl(scheduler, interval_minutes: int):
    scheduler.add_job(
        lambda: asyncio.run(safe_crawl()),
        trigger="interval",
        minutes=interval_minutes,
        id="daily_crawl",
        replace_existing=True
    )
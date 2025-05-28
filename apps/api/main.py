# apps/api/main.py
import os
import asyncio
import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger
from apps.crawler.db import get_last_id
from apps.crawler.crawler import crawl
from apps.api.scheduler import schedule_daily_crawl
from pathlib import Path
import sys
from apps.crawler.db import init_db

load_dotenv()

CRAWL_INTERVAL_MINUTES = int(os.getenv("CRAWL_EVERY_MINUTES", 1440))


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
    except Exception as e:
        logger.error(f"[Startup Error] Failed to init DB: {e}")
        sys.exit(1)

    if not Path("data/crawler_session.session").exists():
        logger.error("[Startup Error] Telegram session file not found.")
        sys.exit(1)

    if not Path("data/media").exists():
        logger.error("[Startup Error] Media folder not found.")
        sys.exit(1)

    logger.info("[Startup] All systems healthy.")
    yield
    logger.info("[Shutdown] Cleanup complete.")

app = FastAPI(title="Forró Media Crawler Control Panel", lifespan=lifespan)


scheduler = BackgroundScheduler()
scheduler.start()
schedule_daily_crawl(scheduler, CRAWL_INTERVAL_MINUTES)

crawl_status = {
    "is_running": False,
    "last_run": None,
    "last_result": None,
}

@app.get("/status")
def get_status():
    return {
        "is_running": crawl_status["is_running"],
        "last_run": crawl_status["last_run"],
        "last_result": crawl_status["last_result"],
        "last_message_id": get_last_id(),
    }

@app.post("/crawl")
async def manual_crawl(background_tasks: BackgroundTasks):
    if crawl_status["is_running"]:
        return JSONResponse(status_code=409, content={"detail": "Crawl already running"})

    def start_crawl():
        asyncio.run(run_crawl())

    background_tasks.add_task(start_crawl)
    return {"detail": "Crawl started"}

async def run_crawl():
    try:
        logger.info("Starting crawl...")
        crawl_status["is_running"] = True
        await crawl(interactive=False)
        crawl_status["last_result"] = "success"
    except Exception as e:
        logger.exception("Crawl failed")
        crawl_status["last_result"] = f"error: {e}"
    finally:
        crawl_status["is_running"] = False
        crawl_status["last_run"] = str(asyncio.get_event_loop().time())

@app.get("/media")
def get_all_media():
    conn = sqlite3.connect("data/db.sqlite")
    c = conn.cursor()
    c.execute("SELECT message_id, date, sender_id, text, file_path FROM media ORDER BY date DESC LIMIT 100")
    results = [
        {
            "message_id": row[0],
            "date": row[1],
            "sender_id": row[2],
            "text": row[3],
            "file_path": row[4]
        }
        for row in c.fetchall()
    ]
    conn.close()
    return results

@app.get("/duplicates")
def get_duplicates():
    conn = sqlite3.connect("data/db.sqlite")
    c = conn.cursor()
    c.execute("SELECT file_hash, COUNT(*) as cnt FROM media GROUP BY file_hash HAVING cnt > 1")
    duplicates = []
    for file_hash, count in c.fetchall():
        c.execute("SELECT message_id, file_path FROM media WHERE file_hash = ?", (file_hash,))
        files = c.fetchall()
        duplicates.append({
            "file_hash": file_hash,
            "count": count,
            "files": [
                {"message_id": f[0], "file_path": f[1]} for f in files
            ]
        })
    conn.close()
    return duplicates

import asyncio
import os
import signal
from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument
from dotenv import load_dotenv

from apps.crawler.db import init_db, save_media, get_last_id, update_last_id, hash_exists
from apps.crawler.utils import hash_file

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
GROUP = os.getenv("GROUP")
SESSION_PATH = os.path.join("data", "crawler_session")

client = TelegramClient(SESSION_PATH, API_ID, API_HASH)

DOWNLOADS_DIR = "data/media"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

downloaded_tmp_files = []

def handle_exit(*_):
    for f in downloaded_tmp_files:
        if os.path.exists(f):
            os.remove(f)
            print(f"Cleaned up: {f}")
    print("Graceful shutdown complete.")
    exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

def is_media_message(msg):
    return msg.media and isinstance(msg.media, MessageMediaDocument)

def get_original_filename(msg):
    if msg.media and hasattr(msg.media, "document"):
        for attr in msg.media.document.attributes:
            if hasattr(attr, "file_name"):
                return attr.file_name
    return None

async def crawl(interactive=True):
    if interactive:
        await client.start()
        init_db()
    else:
        await client.connect()
        if not await client.is_user_authorized():
            raise RuntimeError("Telegram session not found — run manually once to create it.")

    last_id = get_last_id()
    print(f"Starting from message ID: {last_id}")

    async for msg in client.iter_messages(GROUP, min_id=last_id, reverse=True):
        if is_media_message(msg):
            chat_id = msg.chat_id or getattr(msg.peer_id, "channel_id", 0)
            base_filename = f"{chat_id}_{msg.id}.mp3"
            tmp_path = os.path.join(DOWNLOADS_DIR, base_filename + ".part")
            final_path = os.path.join(DOWNLOADS_DIR, base_filename)

            downloaded_tmp_files.append(tmp_path)
            await client.download_media(msg, file=tmp_path)

            file_hash = hash_file(tmp_path)
            if hash_exists(file_hash):
                print(f"Duplicate found: {msg.id}, skipping")
                os.remove(tmp_path)
                continue

            os.rename(tmp_path, final_path)
            downloaded_tmp_files.remove(tmp_path)

            save_media(msg, final_path, file_hash, base_filename, chat_id, text=get_original_filename(msg))
            update_last_id(msg.id)
            print(f"Saved media {msg.id} as {base_filename}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(crawl())
import sqlite3
import os

DB_PATH = "data/db.sqlite"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create the media table with extended fields and composite PK
    c.execute('''
        CREATE TABLE IF NOT EXISTS media (
            message_id INTEGER,
            date TEXT,
            sender_id TEXT,
            text TEXT,
            file_path TEXT,
            file_hash TEXT UNIQUE,
            original_filename TEXT,
            chat_id INTEGER,
            PRIMARY KEY (message_id, chat_id)
        )
    ''')
    
    # Create the state table for tracking last message
    c.execute('''
        CREATE TABLE IF NOT EXISTS state (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Ensure default value for last_id
    c.execute("INSERT OR IGNORE INTO state (key, value) VALUES ('last_id', '0')")
    
    conn.commit()
    conn.close()

def get_last_id():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT)")
    c.execute("SELECT value FROM state WHERE key = 'last_id'")
    row = c.fetchone()
    conn.close()
    return int(row[0]) if row else 0

def update_last_id(msg_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE state SET value = ? WHERE key = 'last_id'", (str(msg_id),))
    conn.commit()
    conn.close()

def save_media(msg, file_path, file_hash, original_filename=None, chat_id=None, text=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO media 
        (message_id, date, sender_id, text, file_path, file_hash, original_filename, chat_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            msg.id,
            msg.date.isoformat(),
            str(msg.sender_id),
            text,
            file_path,
            file_hash,
            original_filename,
            chat_id,
        )
    )
    conn.commit()
    conn.close()

def hash_exists(file_hash):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM media WHERE file_hash = ?", (file_hash,))
    exists = c.fetchone() is not None
    conn.close()
    return exists
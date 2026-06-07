import os
import sqlite3

# Render.com da Environment Variables bo'limida TOKEN ni qo'shasiz
TOKEN = os.environ.get("TOKEN", "")

if not TOKEN:
    raise ValueError("❌ TOKEN topilmadi! Render > Environment Variables ga TOKEN qo'shing.")

def init_db():
    """Ma'lumotlar bazasini yaratish va jadvallarni sozlash"""
    conn = sqlite3.connect("smart_coach.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        current_day TEXT DEFAULT 'A',
        missed_days INTEGER DEFAULT 0,
        current_week INTEGER DEFAULT 1
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nutrition (
        user_id INTEGER,
        date TEXT DEFAULT (DATE('now')),
        protein REAL DEFAULT 0.0,
        PRIMARY KEY (user_id, date)
    )""")

    conn.commit()
    conn.close()

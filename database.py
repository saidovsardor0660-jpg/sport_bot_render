import sqlite3
from datetime import datetime

DB_NAME = "smart_coach.db"

def register_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_workout_day(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT current_day FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 'A'

def get_current_week(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT current_week FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 1

def complete_workout(user_id):
    current = get_workout_day(user_id)
    next_day = {'A': 'B', 'B': 'C', 'C': 'A'}[current]

    # C tugaganda yangi tsikl — haftani oshiramiz
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if current == 'C':
        cursor.execute(
            "UPDATE users SET current_day = ?, current_week = MIN(current_week + 1, 12) WHERE user_id = ?",
            (next_day, user_id)
        )
    else:
        cursor.execute(
            "UPDATE users SET current_day = ? WHERE user_id = ?",
            (next_day, user_id)
        )
    conn.commit()
    conn.close()

def add_protein_data(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO nutrition (user_id, date, protein)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, date) DO UPDATE SET protein = protein + ?
    """, (user_id, today, amount, amount))
    conn.commit()
    cursor.execute(
        "SELECT protein FROM nutrition WHERE user_id = ? AND date = ?",
        (user_id, today)
    )
    total = cursor.fetchone()[0]
    conn.close()
    return total

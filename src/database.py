import os
import sqlite3
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_NAME = os.getenv("DATABASE_PATH", str(PROJECT_ROOT / "water_tracker.db"))


def create_tables():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
    CREATE TABLE IF NOT EXISTS water_intake(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    intake_ml INTEGER,
    date TEXT)
 
    """)


def log_intake(user_id, intake_ml):
    date_today = datetime.today().strftime("%Y-%m-%d")
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO water_intake (user_id, intake_ml, date) VALUES (?, ?, ?)",
            (user_id, intake_ml, date_today),
        )


def get_intake_history(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute(
            "SELECT intake_ml, date FROM water_intake WHERE user_id = ? ORDER BY date DESC, id DESC",
            (user_id,),
        ).fetchall()


create_tables()
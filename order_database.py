
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "nexora_orders.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS order_updates (
                order_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)


def get_saved_status(order_id, default_status="Pending"):
    initialize_database()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT status FROM order_updates WHERE order_id = ?",
            (str(order_id),)
        ).fetchone()
    return row["status"] if row else default_status


def update_order_status(order_id, status):
    initialize_database()
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO order_updates (order_id, status, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(order_id) DO UPDATE SET
                status = excluded.status,
                updated_at = excluded.updated_at
        """, (
            str(order_id),
            str(status),
            datetime.now().isoformat(timespec="seconds")
        ))


def get_all_order_updates():
    initialize_database()
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT order_id, status, updated_at
            FROM order_updates
            ORDER BY updated_at DESC
        """).fetchall()
    return [dict(row) for row in rows]

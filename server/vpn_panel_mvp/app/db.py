import sqlite3
from pathlib import Path

DB_PATH = Path("data/vpn.db")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_column(cur: sqlite3.Cursor, table: str, column: str, ddl: str) -> None:
    cols = cur.execute(f"PRAGMA table_info({table})").fetchall()
    names = {row[1] for row in cols}
    if column not in names:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            uuid TEXT NOT NULL UNIQUE,
            email TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            note TEXT DEFAULT ''
        )
        '''
    )

    _ensure_column(cur, "clients", "traffic_up_mb", "traffic_up_mb REAL NOT NULL DEFAULT 0")
    _ensure_column(cur, "clients", "traffic_down_mb", "traffic_down_mb REAL NOT NULL DEFAULT 0")
    _ensure_column(cur, "clients", "raw_up_bytes", "raw_up_bytes INTEGER NOT NULL DEFAULT 0")
    _ensure_column(cur, "clients", "raw_down_bytes", "raw_down_bytes INTEGER NOT NULL DEFAULT 0")

    conn.commit()
    conn.close()

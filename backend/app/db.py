"""SQLite connection helper + lightweight schema migrations."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .config import get_settings

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      starts_at TEXT NOT NULL,
      ends_at TEXT,
      location TEXT,
      notes TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_events_starts_at ON events(starts_at)",
    """
    CREATE TABLE IF NOT EXISTS vault_files (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      original_name TEXT NOT NULL,
      mime TEXT NOT NULL,
      size INTEGER NOT NULL,
      sha256 TEXT NOT NULL UNIQUE,
      path TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS activity (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      kind TEXT NOT NULL,
      message TEXT NOT NULL,
      meta_json TEXT,
      profile_key TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_activity_created_at ON activity(created_at DESC)",
    """
    CREATE TABLE IF NOT EXISTS profiles (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      key TEXT NOT NULL UNIQUE,
      name TEXT NOT NULL,
      role TEXT NOT NULL DEFAULT 'member',
      emoji TEXT NOT NULL DEFAULT 'D',
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS assistant_actions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      slug TEXT NOT NULL UNIQUE,
      label TEXT NOT NULL,
      prompt TEXT NOT NULL,
      category TEXT NOT NULL DEFAULT 'general',
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
]

SEED_PROFILES = [
    ("daniel", "Daniel", "owner", "D"),
    ("partner", "Partner", "co-founder", "P"),
]

SEED_ASSISTANT_ACTIONS = [
    (
        "jobcarver-summary",
        "Summarise JobCarver today",
        "Give me a one-paragraph summary of today's JobCarver activity using the latest stats.",
        "jobcarver",
    ),
    (
        "vault-find",
        "Search the vault",
        "Search the storage vault for files matching: ",
        "vault",
    ),
    (
        "calendar-week",
        "Plan my week",
        "Look at my calendar for the next 7 days and propose a focused plan for the week.",
        "calendar",
    ),
    (
        "ops-checkin",
        "Daily ops check-in",
        "Run a daily ops check-in: pull JobCarver stats, list any anomalies, and remind me of upcoming events.",
        "general",
    ),
]


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


_conn: sqlite3.Connection | None = None


def get_connection() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        settings = get_settings()
        _conn = _connect(settings.db_path)
        _migrate(_conn)
        _seed(_conn)
    return _conn


def reset_connection_for_tests(db_path: Path) -> sqlite3.Connection:
    """Replace the cached connection (used in tests)."""
    global _conn
    if _conn is not None:
        try:
            _conn.close()
        except Exception:
            pass
    _conn = _connect(db_path)
    _migrate(_conn)
    _seed(_conn)
    return _conn


def _migrate(conn: sqlite3.Connection) -> None:
    for stmt in SCHEMA:
        conn.execute(stmt)
    # Idempotent column adds for upgrades from earlier versions.
    cols = {row["name"] for row in conn.execute("PRAGMA table_info(activity)")}
    if "profile_key" not in cols:
        conn.execute("ALTER TABLE activity ADD COLUMN profile_key TEXT")


def _seed(conn: sqlite3.Connection) -> None:
    cur = conn.execute("SELECT COUNT(*) AS c FROM assistant_actions")
    if cur.fetchone()["c"] == 0:
        conn.executemany(
            "INSERT INTO assistant_actions (slug, label, prompt, category) VALUES (?, ?, ?, ?)",
            SEED_ASSISTANT_ACTIONS,
        )
    cur = conn.execute("SELECT COUNT(*) AS c FROM profiles")
    if cur.fetchone()["c"] == 0:
        conn.executemany(
            "INSERT INTO profiles (key, name, role, emoji) VALUES (?, ?, ?, ?)",
            SEED_PROFILES,
        )


@contextmanager
def cursor() -> Iterator[sqlite3.Cursor]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield cur
    finally:
        cur.close()


def log_activity(
    kind: str,
    message: str,
    meta_json: str | None = None,
    profile_key: str | None = None,
) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO activity (kind, message, meta_json, profile_key) VALUES (?, ?, ?, ?)",
        (kind, message, meta_json, profile_key),
    )

"""
Database Manager — SQLite backend with encrypted log storage.
"""

import os
import sqlite3
import logging
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any

import config
from security.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Thread-safe SQLite manager for users, sessions, chat history, and activity logs."""

    _local = threading.local()

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or config.DATABASE_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.encryption = EncryptionManager()

    # ── connection helpers ───────────────────────────────────────────────
    @property
    def _conn(self) -> sqlite3.Connection:
        """Return a per-thread connection."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA foreign_keys=ON")
        return self._local.conn

    def close(self) -> None:
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None

    # ── schema ───────────────────────────────────────────────────────────
    def initialise(self) -> None:
        """Create tables if they don't exist."""
        cur = self._conn.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    UNIQUE NOT NULL,
                password    TEXT    NOT NULL,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id),
                token       TEXT    UNIQUE NOT NULL,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                expires_at  TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chat_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id),
                role        TEXT    NOT NULL,
                message     TEXT    NOT NULL,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS activity_logs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id),
                action      TEXT    NOT NULL,
                details     TEXT,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );
        """)
        self._conn.commit()
        logger.info("Database tables initialised.")

    # ── user operations ──────────────────────────────────────────────────
    def add_user(self, username: str, hashed_password: str) -> int:
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password),
        )
        self._conn.commit()
        return cur.lastrowid  # type: ignore[return-value]

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        return dict(row) if row else None

    # ── session operations ───────────────────────────────────────────────
    def add_session(self, user_id: int, token: str, expires_at: str) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user_id, token, expires_at),
        )
        self._conn.commit()

    def get_session(self, token: str) -> Optional[Dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM sessions WHERE token = ?", (token,))
        row = cur.fetchone()
        return dict(row) if row else None

    def delete_session(self, token: str) -> None:
        self._conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        self._conn.commit()

    def cleanup_expired_sessions(self) -> int:
        cur = self._conn.cursor()
        cur.execute(
            "DELETE FROM sessions WHERE expires_at < ?",
            (datetime.utcnow().isoformat(),),
        )
        self._conn.commit()
        return cur.rowcount

    # ── chat history (encrypted) ─────────────────────────────────────────
    def save_chat(self, user_id: int, role: str, message: str) -> None:
        encrypted = self.encryption.encrypt(message)
        self._conn.execute(
            "INSERT INTO chat_history (user_id, role, message) VALUES (?, ?, ?)",
            (user_id, role, encrypted),
        )
        self._conn.commit()

    def get_chat_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT * FROM chat_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        )
        rows = [dict(r) for r in cur.fetchall()]
        for row in rows:
            try:
                row["message"] = self.encryption.decrypt(row["message"])
            except Exception:
                pass  # already plain-text (legacy data)
        rows.reverse()
        return rows

    # ── activity logs (encrypted) ────────────────────────────────────────
    def log_activity(self, user_id: int, action: str, details: str = "") -> None:
        encrypted_details = self.encryption.encrypt(details) if details else ""
        self._conn.execute(
            "INSERT INTO activity_logs (user_id, action, details) VALUES (?, ?, ?)",
            (user_id, action, encrypted_details),
        )
        self._conn.commit()

    def get_activity_logs(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT * FROM activity_logs WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        )
        rows = [dict(r) for r in cur.fetchall()]
        for row in rows:
            if row.get("details"):
                try:
                    row["details"] = self.encryption.decrypt(row["details"])
                except Exception:
                    pass
        rows.reverse()
        return rows

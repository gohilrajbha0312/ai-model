"""
Login System — bcrypt-based authentication with session management.
"""

import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import bcrypt

import config
from database.db_manager import DatabaseManager
from security.input_validation import validate_username, validate_password

logger = logging.getLogger(__name__)


class AuthManager:
    """Handles registration, login, session validation, and logout."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    # ── registration ─────────────────────────────────────────────────────
    def register(self, username: str, password: str) -> Dict[str, Any]:
        """
        Register a new user.
        Returns {"success": bool, "message": str}.
        """
        ok, msg = validate_username(username)
        if not ok:
            return {"success": False, "message": msg}

        ok, msg = validate_password(password)
        if not ok:
            return {"success": False, "message": msg}

        if self.db.get_user(username):
            return {"success": False, "message": "Username already exists."}

        hashed = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=config.BCRYPT_ROUNDS),
        ).decode("utf-8")

        self.db.add_user(username, hashed)
        logger.info("User registered: %s", username)
        return {"success": True, "message": "Registration successful."}

    # ── authentication ───────────────────────────────────────────────────
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and create a session.
        Returns {"success": bool, "message": str, "token": str | None, "user_id": int | None}.
        """
        user = self.db.get_user(username)
        if not user:
            logger.warning("Login failed — unknown user: %s", username)
            return {"success": False, "message": "Invalid credentials.", "token": None, "user_id": None}

        if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            logger.warning("Login failed — wrong password for user: %s", username)
            return {"success": False, "message": "Invalid credentials.", "token": None, "user_id": None}

        # Create session
        token = secrets.token_hex(32)
        expires = (datetime.utcnow() + timedelta(minutes=config.SESSION_TIMEOUT_MINUTES)).isoformat()
        self.db.add_session(user["id"], token, expires)
        self.db.log_activity(user["id"], "LOGIN", f"User {username} logged in.")
        logger.info("User logged in: %s", username)

        return {"success": True, "message": "Login successful.", "token": token, "user_id": user["id"]}

    # ── session validation ───────────────────────────────────────────────
    def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a session token.
        Returns session dict if valid, None otherwise.
        """
        if not token:
            return None

        session = self.db.get_session(token)
        if not session:
            return None

        if datetime.fromisoformat(session["expires_at"]) < datetime.utcnow():
            self.db.delete_session(token)
            logger.info("Expired session cleaned up.")
            return None

        return session

    # ── logout ───────────────────────────────────────────────────────────
    def logout(self, token: str) -> Dict[str, Any]:
        """Invalidate a session."""
        session = self.db.get_session(token)
        if session:
            self.db.log_activity(session["user_id"], "LOGOUT", "User logged out.")
            self.db.delete_session(token)
            logger.info("User logged out (session removed).")
        return {"success": True, "message": "Logged out."}

    # ── helpers ──────────────────────────────────────────────────────────
    def has_users(self) -> bool:
        """Check if any users exist (for first-run setup)."""
        user = self.db.get_user("admin")
        return user is not None

    def get_username(self, user_id: int) -> str:
        """Get username by user_id by scanning users table."""
        conn = self.db._conn
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        return row["username"] if row else "unknown"

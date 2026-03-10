"""
Central configuration for the AI Cybersecurity Assistant.
All paths, secrets, and tunables live here.
"""

import os
import json
import secrets

# ── Paths ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "assistant.db")
ENCRYPTION_KEY_PATH = os.path.join(BASE_DIR, "data", "encryption.key")
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")
LOG_FILE = os.path.join(BASE_DIR, "data", "app.log")
SETTINGS_FILE = os.path.join(BASE_DIR, "data", "settings.json")

# ── Flask ────────────────────────────────────────────────────────────────
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = False

# ── Auth / Sessions ─────────────────────────────────────────────────────
SESSION_TIMEOUT_MINUTES = 60
BCRYPT_ROUNDS = 12

# ── Security ─────────────────────────────────────────────────────────────
MAX_INPUT_LENGTH = 4096
ALLOWED_SCAN_PORTS_MAX = 65535

# ── AI Provider Settings ────────────────────────────────────────────────
# Modes: "local" (KB only), "chatgpt", "gemini", "hybrid"
AI_MODE = os.environ.get("AI_MODE", "local")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

# ── AI System Prompt ─────────────────────────────────────────────────────
AI_SYSTEM_PROMPT = """You are an expert AI cybersecurity assistant. You help with:
- Penetration testing techniques and methodology
- Red teaming and blue teaming workflows
- Vulnerability analysis and exploit research
- Malware analysis basics
- OSINT research techniques
- Network reconnaissance
- Active Directory attacks and defenses
- Log analysis and incident response
- Security tool usage (Nmap, Metasploit, Burp Suite, etc.)
- Linux and Windows security

Provide detailed, educational, and accurate answers. Include commands, code examples, and tool recommendations when relevant.
Always remind users to only test on systems they have authorization to test.
Refuse requests for illegal activities."""

# ── Ensure data directory exists ─────────────────────────────────────────
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)


def load_settings() -> dict:
    """Load persisted settings from JSON file."""
    defaults = {
        "ai_mode": AI_MODE,
        "openai_api_key": OPENAI_API_KEY,
        "gemini_api_key": GEMINI_API_KEY,
        "openai_model": OPENAI_MODEL,
        "gemini_model": GEMINI_MODEL,
    }
    if os.path.isfile(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                saved = json.load(f)
            defaults.update(saved)
        except Exception:
            pass
    return defaults


def save_settings(settings: dict) -> None:
    """Persist settings to JSON file."""
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

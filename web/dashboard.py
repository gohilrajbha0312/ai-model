"""
Flask Web Dashboard — chat, tools, and activity logs.
No authentication required — all features accessible directly.
"""

import logging
from flask import (
    Flask, render_template, request, redirect,
    url_for, jsonify,
)

from ai.chatbot_engine import ChatbotEngine
from ai.knowledge_base import KnowledgeBase
from database.db_manager import DatabaseManager
import config

logger = logging.getLogger(__name__)

# Default user_id for no-auth mode
DEFAULT_USER_ID = 1


def create_app(db: DatabaseManager) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.secret_key = config.FLASK_SECRET_KEY

    kb = KnowledgeBase()
    engine = ChatbotEngine(db, kb)

    # Ensure a default user exists for logging purposes
    _ensure_default_user(db)

    import markdown
    import bleach

    def render_markdown(text):
        raw_html = markdown.markdown(text, extensions=['fenced_code', 'tables'])
        allowed_tags = bleach.ALLOWED_TAGS.union({
            'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'hr',
            'pre', 'code', 'span', 'blockquote', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
        })
        allowed_attrs = {**bleach.ALLOWED_ATTRIBUTES, '*': ['class']}
        return bleach.clean(raw_html, tags=allowed_tags, attributes=allowed_attrs)

    app.jinja_env.filters['markdown'] = render_markdown

    # ── routes ───────────────────────────────────────────────────────
    @app.route("/")
    def index():
        return redirect(url_for("chat"))

    @app.route("/chat")
    def chat():
        history = db.get_chat_history(DEFAULT_USER_ID, limit=50)
        return render_template("chat.html", history=history)

    @app.route("/tools")
    def tools():
        return render_template("tools.html")

    @app.route("/logs")
    def logs():
        activity = db.get_activity_logs(DEFAULT_USER_ID, limit=100)
        return render_template("logs.html", logs=activity)

    @app.route("/settings", methods=["GET", "POST"])
    def settings():
        if request.method == "POST":
            new_settings = {
                "ai_mode": request.form.get("ai_mode", "local"),
                "openai_api_key": request.form.get("openai_api_key", ""),
                "openai_model": request.form.get("openai_model", "gpt-3.5-turbo"),
                "gemini_api_key": request.form.get("gemini_api_key", ""),
                "gemini_model": request.form.get("gemini_model", "gemini-1.5-flash"),
                "ollama_url": request.form.get("ollama_url", "http://localhost:11434"),
                "ollama_model": request.form.get("ollama_model", "llama3"),
            }
            config.save_settings(new_settings)
            engine.reload_config()  # Reload AI router clients
            return redirect(url_for("settings", saved=1))
            
        current_settings = config.load_settings()
        return render_template("settings.html", settings=current_settings)

    # ── API endpoints ────────────────────────────────────────────────
    @app.route("/api/chat", methods=["POST"])
    def api_chat():
        data = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()
        if not message:
            return jsonify({"error": "Empty message"}), 400

        response = engine.process_message(DEFAULT_USER_ID, message)
        html_response = render_markdown(response)
        return jsonify({"response": response, "html": html_response})

    @app.route("/api/tool", methods=["POST"])
    def api_tool():
        data = request.get_json(silent=True) or {}
        tool = data.get("tool", "")
        target = data.get("target", "").strip()

        if not tool:
            return jsonify({"error": "Missing tool name"}), 400

        tool_commands = {
            "port_scan": f"scan ports on {target}",
            "subdomain_enum": f"enumerate subdomains of {target}",
            "whois": f"whois {target}",
            "dns": f"dns lookup {target}",
            "vuln_check": f"vulnerability check {target}",
            "hash_crack": f"crack hash {target}",
            "log_analyze": f"analyze logs {target}" if target else "analyze logs",
            "cve_lookup": f"lookup cve {target}",
            "pass_strength": f"check password {target}",
            "recon_run": f"run recon on {target}",
        }

        command = tool_commands.get(tool)
        if not command:
            return jsonify({"error": f"Unknown tool: {tool}"}), 400

        # Run through the engine (which dispatches tool via patterns)
        response = engine.process_message(DEFAULT_USER_ID, command)
        html_response = render_markdown(response)
        return jsonify({"response": response, "html": html_response})

    @app.route("/api/clear", methods=["POST"])
    def api_clear():
        """Clear chat history."""
        conn = db._conn
        conn.execute("DELETE FROM chat_history WHERE user_id = ?", (DEFAULT_USER_ID,))
        conn.commit()
        return jsonify({"success": True})

    return app


def _ensure_default_user(db: DatabaseManager) -> None:
    """Create a default user entry for logging (no password needed)."""
    user = db.get_user("default")
    if not user:
        db.add_user("default", "no-auth-mode")
        logger.info("Default user created for no-auth mode.")

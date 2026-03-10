#!/usr/bin/env python3
"""
AI Cybersecurity Assistant — Entry Point
=========================================
Launch with:
    python main.py --mode cli      # terminal interface
    python main.py --mode web      # Flask web dashboard (default)
"""

import argparse
import logging
import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from database.db_manager import DatabaseManager


def setup_logging() -> None:
    """Configure application-wide logging."""
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  [%(levelname)s]  %(name)s — %(message)s",
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler(sys.stdout),
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Cybersecurity Assistant Chatbot"
    )
    parser.add_argument(
        "--mode",
        choices=["cli", "web"],
        default="web",
        help="Interface mode: 'cli' for terminal, 'web' for Flask dashboard (default: web)",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Web server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=config.FLASK_PORT, help="Web server port")
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger("main")
    logger.info("Initialising AI Cybersecurity Assistant…")

    # Initialise database
    db = DatabaseManager()
    db.initialise()
    logger.info("Database ready at %s", config.DATABASE_PATH)

    if args.mode == "cli":
        from cli.cli_interface import run_cli
        run_cli(db)
    else:
        from web.dashboard import create_app
        app = create_app(db)
        logger.info("Starting web dashboard on http://%s:%s", args.host, args.port)
        from waitress import serve
        serve(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()

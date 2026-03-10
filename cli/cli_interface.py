"""
CLI Interface — Rich-powered terminal UI for the AI Cybersecurity Assistant.
No authentication required — launches directly into the chat.
"""

import sys
import logging

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.text import Text

from ai.chatbot_engine import ChatbotEngine
from ai.knowledge_base import KnowledgeBase
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)
console = Console()


BANNER = r"""
   ╔═══════════════════════════════════════════════════════════════╗
   ║          🛡️  AI CYBERSECURITY ASSISTANT  🛡️                  ║
   ║         Secure • Private • Offline-Ready                     ║
   ╚═══════════════════════════════════════════════════════════════╝
"""


def _print_banner() -> None:
    console.print(Text(BANNER, style="bold cyan"))


def _chat_loop(engine: ChatbotEngine) -> None:
    """Main interactive chat loop."""
    console.print(
        Panel(
            "Type your question or command. Use [bold]help[/bold] for available commands.\n"
            "Type [bold]exit[/bold] or [bold]quit[/bold] to close.",
            title="💬 Chat",
            border_style="green",
        )
    )

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]👋 Goodbye![/yellow]")
            break

        stripped = user_input.strip().lower()
        if stripped in ("exit", "quit", "/exit", "/quit"):
            console.print("[yellow]👋 Goodbye![/yellow]")
            break

        if stripped.startswith("/mode"):
            parts = stripped.split()
            if len(parts) == 2 and parts[1] in ("local", "chatgpt", "gemini", "ollama", "hybrid"):
                import config
                settings = config.load_settings()
                settings["ai_mode"] = parts[1]
                config.save_settings(settings)
                engine.reload_config()
                console.print(f"[green]✅ AI Mode changed to: {parts[1]}[/green]")
            else:
                console.print("[yellow]Usage: /mode [local|chatgpt|gemini|ollama|hybrid][/yellow]")
            continue

        if not user_input.strip():
            continue

        try:
            with console.status("[bold green]Thinking…[/bold green]", spinner="dots"):
                response = engine.process_message(1, user_input)

            console.print()
            console.print(
                Panel(
                    Markdown(response),
                    title="🤖 Assistant",
                    border_style="bright_blue",
                    padding=(1, 2),
                )
            )
        except Exception as e:
            console.print(f"\n[red]❌ Error: {e}[/red]")


def run_cli(db: DatabaseManager) -> None:
    """Entry point for the CLI interface."""
    _print_banner()

    kb = KnowledgeBase()
    engine = ChatbotEngine(db, kb)

    console.print("[green]✅ Assistant ready! No login required.[/green]\n")
    _chat_loop(engine)

"""
Chatbot Engine — processes user messages, dispatches tools, routes AI queries.
"""

import re
import logging
from typing import Dict, Any, Optional

from ai.knowledge_base import KnowledgeBase
from ai.ai_router import AIRouter
from database.db_manager import DatabaseManager
from security.input_validation import sanitize_input, is_safe_query, validate_target
from tools.tool_executor import ToolExecutor
from recon.recon_engine import ReconEngine

logger = logging.getLogger(__name__)


class ChatbotEngine:
    """
    AI Cybersecurity Assistant engine.

    Flow:
        1. Sanitise & safety-check the query.
        2. Check for tool-trigger patterns → run the matching module via ToolExecutor.
        3. Try routing the query to an external AI (ChatGPT/Gemini/Ollama) via AIRouter.
        4. If local mode or AI fails, search the local knowledge base.
        5. Fall back to built-in responses.
    """

    # ── tool-trigger patterns ────────────────────────────────────────────
    TOOL_PATTERNS = [
        (re.compile(r"(?:scan|check)\s+(?:ports?|port)\s+(?:on\s+)?(\S+)", re.I), "port_scan"),
        (re.compile(r"(?:scan\s+ports?)\s+(\d+)\s*-\s*(\d+)\s+(?:on\s+)?(\S+)", re.I), "port_scan_range"),
        (re.compile(r"(?:enum(?:erate)?|find|discover)\s+subdomains?\s+(?:of\s+|for\s+)?(\S+)", re.I), "subdomain_enum"),
        (re.compile(r"whois\s+(\S+)", re.I), "whois"),
        (re.compile(r"(?:dns|nslookup|dig)\s+(?:lookup\s+)?(\S+)", re.I), "dns"),
        (re.compile(r"(?:vuln(?:erability)?|security)\s+(?:check|scan|assess)\s+(\S+)", re.I), "vuln_check"),
        (re.compile(r"(?:crack|identify|analy[sz]e)\s+hash\s+(\S+)", re.I), "hash_crack"),
        (re.compile(r"(?:analy[sz]e|check|parse)\s+logs?(?:\s+(.+))?", re.I), "log_analyze"),
        (re.compile(r"(?:lookup|check|info)\s+cve\s+(CVE-\d{4}-\d+)", re.I), "cve_lookup"),
        (re.compile(r"(?:check|test)\s+(?:password|strength)\s+(\S+)", re.I), "pass_strength"),
        (re.compile(r"(?:run|start|do)\s+(?:recon|reconnaissance)\s+(?:on\s+|for\s+)?(\S+)", re.I), "recon_run"),
    ]

    GREETING_PATTERNS = re.compile(
        r"^(hi|hello|hey|greetings|good\s+(?:morning|afternoon|evening)|sup|yo)\b", re.I
    )

    def __init__(self, db: DatabaseManager, knowledge: Optional[KnowledgeBase] = None):
        self.db = db
        self.kb = knowledge or KnowledgeBase()
        self.router = AIRouter()
        self.executor = ToolExecutor()
        self.recon = ReconEngine()

    def reload_config(self) -> None:
        """Reload the AI router config (API keys, modes)."""
        self.router.reload_clients()

    # ── public API ───────────────────────────────────────────────────────
    def process_message(self, user_id: int, message: str) -> str:
        """Process a user message and return the assistant's response."""
        # 1. Sanitise
        clean = sanitize_input(message)
        if not clean:
            return "⚠️  Please enter a valid message."

        # Log user message
        self.db.save_chat(user_id, "user", clean)

        # 2. Safety check
        safe, reason = is_safe_query(clean)
        if not safe:
            self.db.save_chat(user_id, "assistant", reason)
            self.db.log_activity(user_id, "BLOCKED_QUERY", clean[:100])
            return reason

        # 3. Check for greetings
        if self.GREETING_PATTERNS.match(clean):
            response = self._greeting_response()
            self.db.save_chat(user_id, "assistant", response)
            return response

        # 4. Check for help command
        if clean.lower().strip() in ("help", "/help", "?"):
            response = self._help_response()
            self.db.save_chat(user_id, "assistant", response)
            return response

        # 5. Check for topic list
        if clean.lower().strip() in ("topics", "/topics", "list topics"):
            response = self._topics_response()
            self.db.save_chat(user_id, "assistant", response)
            return response

        # 6. Tool dispatch (intercept intent to run a tool)
        tool_response = self._try_tool_dispatch(clean, user_id)
        if tool_response:
            self.db.save_chat(user_id, "assistant", tool_response)
            return tool_response

        # 7. AI API Routing (ChatGPT / Gemini / Local LLM)
        ai_response = self.router.route_query(clean)
        if ai_response:
            self.db.save_chat(user_id, "assistant", ai_response)
            self.db.log_activity(user_id, "AI_QUERY", f"mode={self.router.get_mode()} q={clean[:50]}")
            return ai_response

        # 8. Local Knowledge base search fallback
        kb_response = self._search_knowledge(clean)
        if kb_response:
            self.db.save_chat(user_id, "assistant", kb_response)
            self.db.log_activity(user_id, "KB_QUERY", clean[:100])
            return kb_response

        # 9. Final Fallback
        fallback = (
            "🤔 I'm not sure about that. Try:\n"
            "• Asking about a cybersecurity topic (e.g. 'What is SQL injection?')\n"
            "• Using a tool (e.g. 'scan ports on 127.0.0.1')\n"
            "• Running recon (e.g. 'run recon on example.com')\n"
            "• Type 'help' for available commands\n\n"
            "*Note: If you want smarter conversational answers, you can add an OpenAI or Gemini API key in Settings.*"
        )
        self.db.save_chat(user_id, "assistant", fallback)
        return fallback

    # ── tool dispatch ────────────────────────────────────────────────────
    def _try_tool_dispatch(self, message: str, user_id: int) -> Optional[str]:
        """Match message against tool patterns and run the tool."""
        for pattern, tool_key in self.TOOL_PATTERNS:
            match = pattern.search(message)
            if not match:
                continue

            try:
                if tool_key == "port_scan":
                    target = match.group(1)
                    ok, validated = validate_target(target)
                    if not ok: return f"❌ {validated}"
                    res = self.executor.execute_tool("port_scan", validated)
                    self.db.log_activity(user_id, "TOOL_PORT_SCAN", f"target={validated}")
                    return res

                elif tool_key == "port_scan_range":
                    start, end, target = match.group(1), match.group(2), match.group(3)
                    ok, validated = validate_target(target)
                    if not ok: return f"❌ {validated}"
                    res = self.executor.execute_tool("port_scan", validated, start_port=int(start), end_port=int(end))
                    self.db.log_activity(user_id, "TOOL_PORT_SCAN", f"target={validated} ports={start}-{end}")
                    return res

                elif tool_key == "subdomain_enum":
                    target = match.group(1)
                    ok, validated = validate_target(target)
                    if not ok: return f"❌ {validated}"
                    res = self.executor.execute_tool("subdomain_enum", validated)
                    self.db.log_activity(user_id, "TOOL_SUBDOMAIN_ENUM", f"target={validated}")
                    return res

                elif tool_key == "whois":
                    target = match.group(1)
                    res = self.executor.execute_tool("whois", target)
                    self.db.log_activity(user_id, "TOOL_WHOIS", f"target={target}")
                    return res

                elif tool_key == "dns":
                    target = match.group(1)
                    res = self.executor.execute_tool("dns", target)
                    self.db.log_activity(user_id, "TOOL_DNS", f"target={target}")
                    return res

                elif tool_key == "vuln_check":
                    target = match.group(1)
                    ok, validated = validate_target(target)
                    if not ok: return f"❌ {validated}"
                    res = self.executor.execute_tool("vuln_check", validated)
                    self.db.log_activity(user_id, "TOOL_VULN_CHECK", f"target={validated}")
                    return res

                elif tool_key == "hash_crack":
                    hash_value = match.group(1)
                    res = self.executor.execute_tool("hash_crack", hash_value)
                    self.db.log_activity(user_id, "TOOL_HASH_CRACK", "hash analysis")
                    return res

                elif tool_key == "log_analyze":
                    log_path = match.group(1) if match.lastindex and match.group(1) else None
                    res = self.executor.execute_tool("log_analyze", log_path or "/var/log")
                    self.db.log_activity(user_id, "TOOL_LOG_ANALYZE", f"path={log_path}")
                    return res

                elif tool_key == "cve_lookup":
                    cve_id = match.group(1)
                    res = self.executor.execute_tool("cve_lookup", cve_id)
                    self.db.log_activity(user_id, "TOOL_CVE_LOOKUP", f"cve={cve_id}")
                    return res

                elif tool_key == "pass_strength":
                    password = match.group(1)
                    res = self.executor.execute_tool("pass_strength", password)
                    self.db.log_activity(user_id, "TOOL_PASS_STRENGTH", "pwd strength check")
                    return res

                elif tool_key == "recon_run":
                    target = match.group(1)
                    ok, validated = validate_target(target)
                    if not ok: return f"❌ {validated}"
                    res = self.recon.run_recon(validated)
                    self.db.log_activity(user_id, "TOOL_RECON_ENGI", f"target={validated}")
                    return res

            except Exception as exc:
                logger.error("Tool '%s' failed: %s", tool_key, exc, exc_info=True)
                return f"❌ Tool error: {exc}"

        return None

    # ── knowledge search ─────────────────────────────────────────────────
    def _search_knowledge(self, query: str) -> Optional[str]:
        """Search the knowledge base and format results."""
        results = self.kb.search(query, top_n=5)
        if not results:
            return None

        # Low threshold so most cybersecurity questions get an answer
        top_key, top_content, top_score = results[0]
        if top_score < 1.0:
            return None

        topic_data = self.kb.topics.get(top_key, {})
        title = topic_data.get("title", top_key)

        lines = [f"📚 **{title}** *(Local DB)*", ""]
        lines.append(top_content)

        # Show related topics if they also scored well
        related = [r for r in results[1:] if r[2] >= 1.0]
        if related:
            lines.append("")
            lines.append("---")
            lines.append("📌 **Related topics:**")
            for key, _, _ in related[:4]:
                rel_data = self.kb.topics.get(key, {})
                lines.append(f"  • {rel_data.get('title', key)}")

        return "\n".join(lines)

    # ── built-in responses ───────────────────────────────────────────────
    @staticmethod
    def _greeting_response() -> str:
        return (
            "👋 Hello! I'm your **AI Cybersecurity Assistant**.\n\n"
            "I can help you with:\n"
            "🔍 **Cybersecurity knowledge** — ask using ChatGPT, Gemini, or my local database\n"
            "🛠️ **Security tools** — port scanning, DNS, CVE lookup, automated recon\n"
            "📖 **Learning** — pentesting workflows, malware analysis, red teaming\n\n"
            "Type **help** for available commands!"
        )

    @staticmethod
    def _help_response() -> str:
        return (
            "📋 **Available Commands & Queries**\n\n"
            "**Knowledge Queries (AI/Local):**\n"
            "  • Ask anything! (e.g. 'What is Log4Shell?', 'Explain privilege escalation')\n"
            "  • 'topics' — list local knowledge base topics\n\n"
            "**Security Tools & Automation:**\n"
            "  • 'run recon on <domain>' — Automated DNS, WHOIS, subdomains, and vulns\n"
            "  • 'scan ports on <target>'\n"
            "  • 'whois <domain>'\n"
            "  • 'dns lookup <domain>'\n"
            "  • 'lookup cve <CVE-ID>' (e.g. CVE-2021-44228)\n"
            "  • 'check password <password>'\n"
            "  • 'vulnerability check <target>'\n"
            "  • 'crack hash <hash>'\n"
            "  • 'analyze logs'\n\n"
            "**System:**\n"
            "  • Configure OpenAI/Gemini API keys in the Web Dashboard Settings\n"
            "  • 'exit' / 'quit' — close the assistant"
        )

    def _topics_response(self) -> str:
        topics = self.kb.list_topics()
        if not topics:
            return "📚 No local knowledge base topics loaded."
        lines = ["📚 **Local Knowledge Base Topics:**", ""]
        for i, t in enumerate(topics, 1):
            lines.append(f"  {i}. {t['title']}")
        lines.append("\nAsk about any topic for detailed information.")
        return "\n".join(lines)

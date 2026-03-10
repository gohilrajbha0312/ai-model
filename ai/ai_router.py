"""
AI Router — routes queries to ChatGPT, Gemini, local LLM, or hybrid mode.
Falls back to local knowledge base if no AI provider is available.
"""

import logging
from typing import Optional, Dict, Any

import config
from ai.chatgpt_client import ChatGPTClient
from ai.gemini_client import GeminiClient
from ai.local_llm_client import LocalLLMClient

logger = logging.getLogger(__name__)


class AIRouter:
    """
    Routes AI queries based on the configured mode.

    Modes:
        - local:     Knowledge base only (no external API)
        - chatgpt:   OpenAI ChatGPT API
        - gemini:    Google Gemini API
        - ollama:    Local LLM via Ollama
        - hybrid:    Try all available, pick best response
    """

    def __init__(self):
        self.chatgpt = ChatGPTClient()
        self.gemini = GeminiClient()
        self.local_llm = LocalLLMClient()
        self.system_prompt = config.AI_SYSTEM_PROMPT

    def reload_clients(self) -> None:
        """Reload AI clients with latest settings."""
        self.chatgpt = ChatGPTClient()
        self.gemini = GeminiClient()
        self.local_llm = LocalLLMClient()

    def get_mode(self) -> str:
        """Get current AI mode from settings."""
        settings = config.load_settings()
        return settings.get("ai_mode", "local")

    def get_status(self) -> Dict[str, Any]:
        """Return availability status of all providers."""
        return {
            "mode": self.get_mode(),
            "chatgpt": {"configured": self.chatgpt.is_available()},
            "gemini": {"configured": self.gemini.is_available()},
            "ollama": {"available": self.local_llm.is_available()},
        }

    def route_query(self, prompt: str) -> Optional[str]:
        """Route a query based on the current AI mode."""
        mode = self.get_mode()
        logger.info("AI Router: mode=%s, query=%s", mode, prompt[:60])

        if mode == "chatgpt":
            return self.route_to_chatgpt(prompt)
        elif mode == "gemini":
            return self.route_to_gemini(prompt)
        elif mode == "ollama":
            return self.route_to_ollama(prompt)
        elif mode == "hybrid":
            return self.hybrid_ai_response(prompt)
        else:
            # "local" mode — return None so chatbot uses KB
            return None

    def route_to_chatgpt(self, prompt: str) -> Optional[str]:
        """Send query to ChatGPT."""
        if not self.chatgpt.is_available():
            return "⚠️ ChatGPT API key not configured. Go to Settings to add your OpenAI API key."
        response = self.chatgpt.query(prompt, self.system_prompt)
        if response:
            return f"🤖 **ChatGPT:**\n\n{response}"
        return None

    def route_to_gemini(self, prompt: str) -> Optional[str]:
        """Send query to Gemini."""
        if not self.gemini.is_available():
            return "⚠️ Gemini API key not configured. Go to Settings to add your Google AI API key."
        response = self.gemini.query(prompt, self.system_prompt)
        if response:
            return f"✨ **Gemini:**\n\n{response}"
        return None

    def route_to_ollama(self, prompt: str) -> Optional[str]:
        """Send query to local Ollama."""
        if not self.local_llm.is_available():
            return "⚠️ Ollama not running. Start it with: ollama serve"
        response = self.local_llm.query(prompt, self.system_prompt)
        if response:
            return f"🏠 **Local LLM:**\n\n{response}"
        return None

    def hybrid_ai_response(self, prompt: str) -> Optional[str]:
        """Try all available AI providers, return the best response."""
        responses = []

        # Try ChatGPT
        if self.chatgpt.is_available():
            r = self.chatgpt.query(prompt, self.system_prompt)
            if r:
                responses.append(("ChatGPT 🤖", r))

        # Try Gemini
        if self.gemini.is_available():
            r = self.gemini.query(prompt, self.system_prompt)
            if r:
                responses.append(("Gemini ✨", r))

        # Try local LLM
        if self.local_llm.is_available():
            r = self.local_llm.query(prompt, self.system_prompt)
            if r:
                responses.append(("Local LLM 🏠", r))

        if not responses:
            return None

        # Pick the longest/most detailed response
        best = max(responses, key=lambda x: len(x[1]))
        name, text = best

        if len(responses) > 1:
            others = [r[0] for r in responses if r[0] != name]
            return f"**{name}** *(also queried: {', '.join(others)})*\n\n{text}"
        return f"**{name}**\n\n{text}"

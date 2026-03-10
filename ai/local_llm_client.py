"""
Local LLM Client — Ollama integration for privacy-focused local AI.
"""

import logging
from typing import Optional

import config

logger = logging.getLogger(__name__)


class LocalLLMClient:
    """Send prompts to a local LLM via Ollama HTTP API."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        settings = config.load_settings()
        self.base_url = settings.get("ollama_url", base_url).rstrip("/")
        self.model = settings.get("ollama_model", model)

    def is_available(self) -> bool:
        """Check if Ollama is running locally."""
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
            resp = urllib.request.urlopen(req, timeout=2)
            return resp.status == 200
        except Exception:
            return False

    def query(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """
        Send a prompt to the local Ollama instance.
        Returns None on failure.
        """
        try:
            import urllib.request
            import json

            payload = json.dumps({
                "model": self.model,
                "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
                "stream": False,
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            resp = urllib.request.urlopen(req, timeout=120)
            data = json.loads(resp.read().decode("utf-8"))
            answer = data.get("response", "").strip()

            if answer:
                logger.info("Ollama response received (%d chars)", len(answer))
                return answer
            return None

        except Exception as exc:
            logger.error("Local LLM (Ollama) error: %s", exc)
            return f"❌ **Local LLM error:** {exc}"

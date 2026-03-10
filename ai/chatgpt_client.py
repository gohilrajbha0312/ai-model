"""
ChatGPT Client — OpenAI API integration for cybersecurity queries.
"""

import logging
from typing import Optional

import config

logger = logging.getLogger(__name__)


class ChatGPTClient:
    """Send prompts to OpenAI ChatGPT API."""

    def __init__(self, api_key: str = "", model: str = ""):
        settings = config.load_settings()
        self.api_key = api_key or settings.get("openai_api_key", "")
        self.model = model or settings.get("openai_model", "gpt-3.5-turbo")
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise RuntimeError("openai package not installed. Run: pip install openai")
        return self._client

    def is_available(self) -> bool:
        """Check if ChatGPT is configured with an API key."""
        return bool(self.api_key and self.api_key.startswith("sk-"))

    def query(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """
        Send a prompt to ChatGPT and return the response.
        Returns None on failure.
        """
        if not self.is_available():
            return None

        try:
            client = self._get_client()
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2048,
                temperature=0.7,
            )
            answer = response.choices[0].message.content.strip()
            logger.info("ChatGPT response received (%d chars)", len(answer))
            return answer

        except Exception as exc:
            logger.error("ChatGPT API error: %s", exc)
            return f"❌ **ChatGPT API error:** {exc}"

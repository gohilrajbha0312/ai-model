"""
Gemini Client — Google Generative AI integration for cybersecurity queries.
"""

import logging
from typing import Optional

import config

logger = logging.getLogger(__name__)


class GeminiClient:
    """Send prompts to Google Gemini API."""

    def __init__(self, api_key: str = "", model: str = ""):
        settings = config.load_settings()
        self.api_key = api_key or settings.get("gemini_api_key", "")
        self.model_name = model or settings.get("gemini_model", "gemini-1.5-flash")
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self.model_name)
            except ImportError:
                raise RuntimeError("google-generativeai not installed. Run: pip install google-generativeai")
        return self._model

    def is_available(self) -> bool:
        """Check if Gemini is configured with an API key."""
        return bool(self.api_key and len(self.api_key) > 10)

    def query(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """
        Send a prompt to Gemini and return the response.
        Returns None on failure.
        """
        if not self.is_available():
            return None

        try:
            model = self._get_model()
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            response = model.generate_content(
                full_prompt,
                generation_config={
                    "max_output_tokens": 2048,
                    "temperature": 0.7,
                },
            )
            answer = response.text.strip()
            logger.info("Gemini response received (%d chars)", len(answer))
            return answer

        except Exception as exc:
            logger.error("Gemini API error: %s", exc)
            return f"❌ **Gemini API error:** {exc}"

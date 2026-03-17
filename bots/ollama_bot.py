# bots/ollama_bot.py — Open-source Ollama fallback (local LLM)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from .base import BotProvider
import requests


class OllamaBotProvider(BotProvider):
    """Ollama provider: local open-source LLM (no API key required)."""

    @property
    def name(self) -> str:
        return "Ollama"

    def chat(self, user_message: str, context: str = "") -> str:
        prompt = user_message
        if context:
            prompt = (
                "You are an Incident Knowledge Assistant. Use the following error log / incident data as context. "
                "Provide clear, actionable recommended fixes.\n\n"
                f"Context:\n{context}\n\nUser question: {user_message}"
            )
        try:
            r = requests.post(
                f"{config.OLLAMA_BASE_URL.rstrip('/')}/api/generate",
                json={
                    "model": config.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120,
            )
            r.raise_for_status()
            data = r.json()
            return data.get("response", "").strip()
        except Exception as e:
            return (
                f"Ollama error: {e}. "
                "Ensure Ollama is running (e.g. ollama run llama3.2) and OLLAMA_BASE_URL is correct."
            )

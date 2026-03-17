# bots/nanobot.py — Nanobot integration (Giggso mandatory option)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from .base import BotProvider
import requests


class NanobotProvider(BotProvider):
    """Nanobot provider: calls Giggso Nanobot API when NANOBOT_URL is set."""

    @property
    def name(self) -> str:
        return "Nanobot"

    def chat(self, user_message: str, context: str = "") -> str:
        prompt = user_message
        if context:
            prompt = f"Context (error log / incident data):\n{context}\n\nUser question: {user_message}"
        try:
            r = requests.post(
                f"{config.NANOBOT_URL.rstrip('/')}/chat",
                json={"message": prompt, "context": context},
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
            return data.get("reply") or data.get("text") or data.get("response") or str(data)
        except Exception as e:
            return f"Nanobot error: {e}. Check NANOBOT_URL and network."

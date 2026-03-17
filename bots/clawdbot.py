# bots/clawdbot.py — ClawDBot integration (Giggso mandatory option)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from .base import BotProvider
import requests


class ClawDBotProvider(BotProvider):
    """ClawDBot provider: calls Giggso ClawDBot API when CLAWDBOT_URL is set."""

    @property
    def name(self) -> str:
        return "ClawDBot"

    def chat(self, user_message: str, context: str = "") -> str:
        prompt = user_message
        if context:
            prompt = f"Context (error log / incident data):\n{context}\n\nUser question: {user_message}"
        try:
            r = requests.post(
                f"{config.CLAWDBOT_URL.rstrip('/')}/chat",
                json={"message": prompt, "context": context},
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
            return data.get("reply") or data.get("text") or data.get("response") or str(data)
        except Exception as e:
            return f"ClawDBot error: {e}. Check CLAWDBOT_URL and network."

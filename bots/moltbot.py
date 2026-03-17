# bots/moltbot.py — MoltBot integration (Giggso mandatory option)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from .base import BotProvider
import requests


class MoltBotProvider(BotProvider):
    """MoltBot provider: calls Giggso MoltBot API when MOLTBOT_URL is set."""

    @property
    def name(self) -> str:
        return "MoltBot"

    def chat(self, user_message: str, context: str = "") -> str:
        # Build payload; adapt to actual MoltBot API when documented
        prompt = user_message
        if context:
            prompt = f"Context (error log / incident data):\n{context}\n\nUser question: {user_message}"
        try:
            # Generic POST to MoltBot endpoint; adjust path/body per Giggso API
            r = requests.post(
                f"{config.MOLTBOT_URL.rstrip('/')}/chat",
                json={"message": prompt, "context": context},
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
            # Assume response has 'reply' or 'text' or 'response'; normalize
            return data.get("reply") or data.get("text") or data.get("response") or str(data)
        except Exception as e:
            return f"MoltBot error: {e}. Check MOLTBOT_URL and network."

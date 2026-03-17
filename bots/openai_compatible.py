# bots/openai_compatible.py — OpenAI-compatible API (open-source or hosted)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from .base import BotProvider
import requests


class OpenAICompatibleProvider(BotProvider):
    """OpenAI-compatible API (e.g. LiteLLM, local LLM servers)."""

    @property
    def name(self) -> str:
        return "OpenAI-compatible"

    def chat(self, user_message: str, context: str = "") -> str:
        prompt = user_message
        if context:
            prompt = (
                "You are an Incident Knowledge Assistant. Context (error log):\n"
                f"{context}\n\nUser: {user_message}"
            )
        headers = {"Content-Type": "application/json"}
        if config.OPENAI_COMPATIBLE_API_KEY:
            headers["Authorization"] = f"Bearer {config.OPENAI_COMPATIBLE_API_KEY}"
        try:
            r = requests.post(
                f"{config.OPENAI_COMPATIBLE_URL.rstrip('/')}/v1/chat/completions",
                json={
                    "model": config.OPENAI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                },
                headers=headers,
                timeout=60,
            )
            r.raise_for_status()
            data = r.json()
            choice = (data.get("choices") or [{}])[0]
            return (choice.get("message") or {}).get("content", "").strip()
        except Exception as e:
            return f"OpenAI-compatible API error: {e}"

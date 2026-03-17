# config.py — Central configuration and environment loading
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent / ".env")

# API auth (for public POST endpoint)
API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN", "dev-token-change-in-production")

# Bot provider: moltbot | clawdbot | nanobot | openclaw | ollama | openai_compatible | auto
# "auto" or empty = use first available of MoltBot / ClawDBot / Nanobot (by URL); no Ollama default
BOT_PROVIDER_RAW = (os.getenv("BOT_PROVIDER") or "auto").lower().strip()

# Giggso bot base URLs (set when you have access). Production: inject via env (e.g. Kubernetes Secret).
# For local testing: run `python scripts/mock_bot_server.py` and use localhost:9090 URLs.
MOLTBOT_URL = (os.getenv("MOLTBOT_URL") or "").strip()
CLAWDBOT_URL = (os.getenv("CLAWDBOT_URL") or "").strip()
NANOBOT_URL = (os.getenv("NANOBOT_URL") or "").strip()


def _first_available_giggso_bot() -> str:
    """Return first of moltbot/clawdbot/nanobot that has URL set (production default)."""
    if MOLTBOT_URL:
        return "moltbot"
    if CLAWDBOT_URL:
        return "clawdbot"
    if NANOBOT_URL:
        return "nanobot"
    return ""


# Resolved provider: explicit choice or first available of the 3 bots. No Ollama unless set.
if BOT_PROVIDER_RAW and BOT_PROVIDER_RAW != "auto":
    BOT_PROVIDER = BOT_PROVIDER_RAW
else:
    BOT_PROVIDER = _first_available_giggso_bot()
    # If still empty, app will fail at startup with clear message (see bots/base.py)

# OpenClaw (openclaw.ai) — local gateway, formerly Clawdbot/Moltbot; default port 18789
# Enable chat in OpenClaw: gateway.http.endpoints.chatCompletions.enabled: true
OPENCLAW_GATEWAY_URL = (os.getenv("OPENCLAW_GATEWAY_URL") or "http://localhost:18789").strip()
OPENCLAW_AUTH_TOKEN = (os.getenv("OPENCLAW_AUTH_TOKEN") or "").strip()
OPENCLAW_AGENT_ID = (os.getenv("OPENCLAW_AGENT_ID") or "main").strip()

# Open-source fallbacks
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()
OPENAI_COMPATIBLE_URL = (os.getenv("OPENAI_COMPATIBLE_URL") or "").strip()
OPENAI_COMPATIBLE_API_KEY = (os.getenv("OPENAI_COMPATIBLE_API_KEY") or "").strip()

# Default model names for fallback providers
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Multi-bot mode: ask all configured bots and show each reply (for hackathon / demo)
MULTI_BOT_ENABLED = os.getenv("MULTI_BOT_ENABLED", "false").lower().strip() in ("true", "1", "yes")

# When true, multi-bot mode includes Ollama/OpenClaw/OpenAI-compatible. When false, only 3 bots (MoltBot/ClawDBot/Nanobot).
INCLUDE_FALLBACK_BOTS_IN_MULTI = os.getenv("INCLUDE_FALLBACK_BOTS_IN_MULTI", "false").lower().strip() in ("true", "1", "yes")


def validate_bot_config() -> None:
    """
    Call at startup to fail fast if bot config is invalid (production-ready).
    Raises RuntimeError with a clear message when no bot can be used.
    """
    from bots.base import get_bot
    get_bot()
